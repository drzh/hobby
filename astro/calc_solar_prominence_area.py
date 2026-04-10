'''
Read in a fits file containing the intensity of the sun's surface. It removes the sun disk and then calculates the area of solar prominences.

Usage: 
    python calc_solar_prominence_area.py -e <pixels_to_extend_for_sun_disk> -c <intensity_cutoff> -m <minimal_pixels_of_connected_region> --cap <cap_value_of_the_intensity> -i <fits_file> -o <output_file> -w <plot_width> -h <plot_height> -p <plot_file> --overlay <overlay_plot_file> -d <output_data_file>

'''

import click
import numpy as np
from astropy.io import fits
from astropy import units as u
from astropy.coordinates import SkyCoord
from scipy import ndimage
from sunpy.coordinates import frames
from sunpy.map import Map, maputils
from sunpy.visualization.colormaps import color_tables
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from datetime import datetime, timezone


OVERLAY_GRID_SPACING_DEGREES = 15
OVERLAY_LINE_COLOR = '#ffe0a6'
OVERLAY_LIMB_COLOR = '#fff4d4'
OVERLAY_LINE_WIDTH = 0.35
OVERLAY_LIMB_WIDTH = 0.45
OVERLAY_ALPHA = 0.45
OVERLAY_LABEL_ALPHA = 0.55
OVERLAY_LABEL_FONT_SIZE = 4.0
OVERLAY_LABEL_PADDING = 10
OVERLAY_LONGITUDE_LABEL_LATITUDE = 0


def format_obs_time(obs_time_str):
    return obs_time_str.replace('T', '  ').split('.')[0]


def add_obs_time_text(ax, obs_time_str, color='white', alpha=1.0):
    ax.text(
        1,
        1,
        format_obs_time(obs_time_str),
        color=color,
        alpha=alpha,
        fontsize=6,
        ha='left',
        va='bottom',
    )


def sample_heliographic_line(solar_map, longitudes_deg, latitudes_deg):
    radius = np.full(len(longitudes_deg), solar_map.rsun_meters.to_value(u.m)) * u.m
    hgs = SkyCoord(
        lon=np.asarray(longitudes_deg) * u.deg,
        lat=np.asarray(latitudes_deg) * u.deg,
        radius=radius,
        frame=frames.HeliographicStonyhurst,
        obstime=solar_map.date,
    )
    hpc = hgs.transform_to(solar_map.coordinate_frame)
    visible = maputils.coordinate_is_on_solar_disk(hpc)
    pixel_x, pixel_y = solar_map.world_to_pixel(hpc)
    pixel_x = np.asarray(pixel_x.value, dtype=float)
    pixel_y = np.asarray(pixel_y.value, dtype=float)
    pixel_x[~visible] = np.nan
    pixel_y[~visible] = np.nan
    return pixel_x, pixel_y


def format_degree_label(value):
    if value > 0:
        return f'+{int(value)}\N{DEGREE SIGN}'
    if value < 0:
        return f'{int(value)}\N{DEGREE SIGN}'
    return f'0\N{DEGREE SIGN}'


def add_overlay_label(ax, x, y, label, ha, va):
    ax.text(
        x,
        y,
        label,
        color=OVERLAY_LINE_COLOR,
        alpha=OVERLAY_LABEL_ALPHA,
        fontsize=OVERLAY_LABEL_FONT_SIZE,
        ha=ha,
        va=va,
        clip_on=True,
    )


def label_latitude_line(ax, pixel_x, pixel_y, latitude):
    valid = np.isfinite(pixel_x) & np.isfinite(pixel_y)
    if not np.any(valid):
        return

    first_idx = np.flatnonzero(valid)[0]
    add_overlay_label(
        ax,
        pixel_x[first_idx] + OVERLAY_LABEL_PADDING,
        pixel_y[first_idx],
        format_degree_label(latitude),
        ha='left',
        va='center',
    )


def label_longitude_line(ax, pixel_x, pixel_y, longitude, latitudes_deg):
    valid = np.isfinite(pixel_x) & np.isfinite(pixel_y)
    if not np.any(valid):
        return

    label_idx = int(np.abs(latitudes_deg - OVERLAY_LONGITUDE_LABEL_LATITUDE).argmin())
    if not valid[label_idx]:
        valid_indices = np.flatnonzero(valid)
        top_idx = valid_indices[np.nanargmax(pixel_y[valid])]
    else:
        top_idx = label_idx

    add_overlay_label(
        ax,
        pixel_x[top_idx],
        pixel_y[top_idx] + OVERLAY_LABEL_PADDING,
        format_degree_label(longitude),
        ha='center',
        va='bottom',
    )


def plot_lat_lon_overlay(ax, ff_data, ff_header):
    solar_map = Map(ff_data, ff_header)
    ylen, xlen = ff_data.shape

    ax.imshow(np.zeros_like(ff_data), origin='lower', aspect=1, alpha=0)
    ax.set_xlim(-0.5, xlen - 0.5)
    ax.set_ylim(-0.5, ylen - 0.5)
    ax.set_aspect(1)
    ax.axis('off')

    latitude_samples = np.linspace(-90, 90, 721)
    longitude_samples = np.linspace(-90, 90, 721)
    grid_values = range(
        -90 + OVERLAY_GRID_SPACING_DEGREES,
        90,
        OVERLAY_GRID_SPACING_DEGREES,
    )

    for latitude in grid_values:
        pixel_x, pixel_y = sample_heliographic_line(
            solar_map,
            longitude_samples,
            np.full(longitude_samples.shape, latitude, dtype=float),
        )
        ax.plot(
            pixel_x,
            pixel_y,
            color=OVERLAY_LINE_COLOR,
            linewidth=OVERLAY_LINE_WIDTH,
            alpha=OVERLAY_ALPHA,
            solid_capstyle='round',
        )
        label_latitude_line(ax, pixel_x, pixel_y, latitude)

    for longitude in grid_values:
        pixel_x, pixel_y = sample_heliographic_line(
            solar_map,
            np.full(latitude_samples.shape, longitude, dtype=float),
            latitude_samples,
        )
        ax.plot(
            pixel_x,
            pixel_y,
            color=OVERLAY_LINE_COLOR,
            linewidth=OVERLAY_LINE_WIDTH,
            alpha=OVERLAY_ALPHA,
            solid_capstyle='round',
        )
        label_longitude_line(ax, pixel_x, pixel_y, longitude, latitude_samples)

    limb_theta = np.linspace(0, 2 * np.pi, 1441)
    sun_center_x = ff_header['CRPIX1'] - 1
    sun_center_y = ff_header['CRPIX2'] - 1
    rsun_arcsec = ff_header['RSUN_OBS']
    cdelt1 = ff_header['CDELT1']
    cdelt2 = ff_header['CDELT2']
    rsun_pixels = rsun_arcsec / ((cdelt1 + cdelt2) / 2)
    ax.plot(
        sun_center_x + rsun_pixels * np.cos(limb_theta),
        sun_center_y + rsun_pixels * np.sin(limb_theta),
        color=OVERLAY_LIMB_COLOR,
        linewidth=OVERLAY_LIMB_WIDTH,
        alpha=OVERLAY_ALPHA,
    )


def save_plot(fig, output_path, transparent=False):
    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches='tight',
        pad_inches=0,
        transparent=transparent,
    )
    plt.close(fig)

@click.command()
@click.option('-e', '--extend', 'pixels_to_extend_for_sun_disk', default=0, help='Number of pixels to extend the sun disk mask.')
@click.option('-c', '--cutoff', 'intensity_cutoff', default=0, help='Intensity cutoff for prominence detection.')
@click.option('-m', '--minimal', 'minimal_pixels_of_connected_region', default=1, help='Minimal number of pixels in a connected region to be considered a prominence.')
@click.option('--cap', 'cap_value_of_the_intensity', default=None, type=float, help='Optional cap value for the intensity to limit extreme values.')
@click.option('-w', '--width', 'plot_width', default=3, help='Width of the plot in inches.')
@click.option('-h', '--height', 'plot_height', default=3, help='Height of the plot in inches.')
@click.option('-i', '--input', 'fits_file', required=True, help='Input FITS file containing solar image data.')
@click.option('-o', '--output', 'output_file', default=None, help='Output file to save the calculated prominence area.')
@click.option('-p', '--plot', 'plot_file', default=None, help='Optional plot file to save the prominence area visualization.')
@click.option('--overlay', 'overlay_plot_file', default=None, help='Optional transparent overlay file to save the solar latitude/longitude grid.')
@click.option('-d', '--data', 'output_data_file', default=None, help='Optional file to save the output data.')

def calculate_prominence_area(pixels_to_extend_for_sun_disk=0, intensity_cutoff=0, minimal_pixels_of_connected_region=1, cap_value_of_the_intensity=None, plot_width=3, plot_height=3, fits_file=None, output_file=None, plot_file=None, overlay_plot_file=None, output_data_file=None):
    # Read the FITS file
    with fits.open(fits_file) as ff:
        #print(ff[1].header)
        #print(ff[1].data.shape)
        ff_header = ff[1].header
        ff_data = ff[1].data

        # Get the statistics of the data
        intensity_max = np.nanmax(ff_data)

        # Cap the intensity values if specified
        if cap_value_of_the_intensity is not None:
            ff_data = np.minimum(ff_data, cap_value_of_the_intensity)

        # Export the data to a file if specified
        if output_data_file:
            np.savetxt(output_data_file, ff_data, fmt='%.2f', delimiter='\t')

        # Extract length and width of image from 'NAXIS1' and 'NAXIS2'
        xlen = ff_header['NAXIS1']
        ylen = ff_header['NAXIS2']

        # Extract the center of the sun from 'CRPIX1' and 'CRPIX2'
        sun_center_x = ff_header['CRPIX1']
        sun_center_y = ff_header['CRPIX2']

        # Calculate the radius of the sun in pixels
        rsun_arcsec = ff_header['RSUN_OBS']  # Radius of the sun in arcseco
        cdelt1 = ff_header['CDELT1']
        cdelt2 = ff_header['CDELT2']
        rsun_pixels = rsun_arcsec / ((cdelt1 + cdelt2) / 2)

        # Mask the sun disk (pixcel values within the sun radius)
        y, x = np.ogrid[:ylen, :xlen]
        rmask = rsun_pixels + pixels_to_extend_for_sun_disk
        if rmask > 0:
            sun_disk_mask = (x - sun_center_x) ** 2 + (y - sun_center_y) ** 2 < (rsun_pixels + pixels_to_extend_for_sun_disk) ** 2
            ff_data[sun_disk_mask] = 1  # Set the sun disk pixels to zero

        # Find the maximum distance of pixels with intensity greater than the cutoff
        prominence_mask = ff_data > intensity_cutoff

        # Label connected components in the prominence mask
        structure = np.ones((3, 3), dtype=int)  # Define a structure for connectivity
        labeled_prominence, num_features = ndimage.label(prominence_mask, structure=structure)

        # Calculate the sizes of each connected component
        sizes = ndimage.sum(prominence_mask, labeled_prominence, range(1, num_features + 1))

        # select only the components with > minimal_pixels_of_connected_region pixels
        large_components = np.where(sizes >= minimal_pixels_of_connected_region)[0] + 1
        prominence_mask_filtered = np.isin(labeled_prominence, large_components)
       
        # Calculate the number of pixels with intensity greater than the intensity cutoff
        bright_pixels = np.sum(prominence_mask_filtered)
        
        # Calculate the maximum distance of prominence pixels from the sun center
        if bright_pixels == 0:
            prominence_max_distance = 0
        else:
            # Get the indices of the prominence pixels
            y_indices, x_indices = np.where(prominence_mask_filtered)
            prominence_max_distance = np.max(np.sqrt((x_indices - sun_center_x) ** 2 + (y_indices - sun_center_y) ** 2)) - rsun_pixels

        # Output the values
        if output_file:
            with open(output_file, 'w') as f:
                # Print current time in the format '2025-08-21T04:32:53.130'
                f.write(f"current_time\t{datetime.now(timezone.utc).isoformat()}\n")
                f.write(f"obs_time\t{ff_header.get('DATE-OBS', 'Unknown')}\n")
                f.write(f"pixels_to_extend_for_sun_disk\t{pixels_to_extend_for_sun_disk}\n")
                f.write(f"intensity_max\t{intensity_max}\n")
                f.write(f"intensity_cutoff\t{intensity_cutoff}\n")
                f.write(f"sun_center_x\t{sun_center_x}\n")
                f.write(f"sun_center_y\t{sun_center_y}\n")
                f.write(f"sun_radius_pixels\t{rsun_pixels:.1f}\n")
                f.write(f"prominence_area_pixels\t{bright_pixels:.1f}\n")
                f.write(f"prominence_max_distance_pixels\t{prominence_max_distance:.1f}\n")

        # Plot the fits_data
        if plot_file:
            # Set the intensity outside of the prominence area to zero
            ff_data[~prominence_mask_filtered] = 1
            
            fig, ax = plt.subplots(figsize=(plot_width, plot_height))
            cmap = color_tables.aia_color_table(304 * u.angstrom)
            #plt.imshow(ff_data, cmap=cmap, origin="lower", aspect=1, norm=LogNorm(vmin=1, vmax=ff_data.max()))
            vmax = cap_value_of_the_intensity if cap_value_of_the_intensity is not None else ff_data.max()
            ax.imshow(ff_data, cmap=cmap, origin="lower", aspect=1, norm=LogNorm(vmin=1, vmax=vmax))
            ax.axis('off')
            #plt.colorbar(label="Intensity")
            #plt.title(f"Solar Prominence (Intensity>{intensity_cutoff})", fontsize=8)
            # Add date and time to the bottom left corner
            obs_time_str = ff_header.get('DATE-OBS', 'Unknown')
            add_obs_time_text(ax, obs_time_str)
            save_plot(fig, plot_file)

        if overlay_plot_file:
            fig, ax = plt.subplots(figsize=(plot_width, plot_height))
            fig.patch.set_alpha(0)
            ax.patch.set_alpha(0)
            plot_lat_lon_overlay(ax, ff_data, ff_header)
            # Keep the invisible timestamp footprint so the saved overlay matches the main image size.
            add_obs_time_text(ax, ff_header.get('DATE-OBS', 'Unknown'), alpha=0)
            save_plot(fig, overlay_plot_file, transparent=True)


if __name__ == "__main__":
    calculate_prominence_area()
