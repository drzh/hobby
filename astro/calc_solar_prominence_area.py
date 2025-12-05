'''
Read in a fits file containing the intensity of the sun's surface. It removes the sun disk and then calculates the area of solar prominences.

Usage: 
    python calc_solar_prominence_area.py -e <pixels_to_extend_for_sun_disk> -c <intensity_cutoff> -m <minimal_pixels_of_connected_region> --cap <cap_value_of_the_intensity> -i <fits_file> -o <output_file> -w <plot_width> -h <plot_height> -p <plot_file> -d <output_data_file>

'''

import click
import numpy as np
from astropy.io import fits
from astropy import units as u
from scipy import ndimage
from sunpy.visualization.colormaps import color_tables
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from datetime import datetime, timezone

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
@click.option('-d', '--data', 'output_data_file', default=None, help='Optional file to save the output data.')

def calculate_prominence_area(pixels_to_extend_for_sun_disk=0, intensity_cutoff=0, minimal_pixels_of_connected_region=1, cap_value_of_the_intensity=None, plot_width=3, plot_height=3, fits_file=None, output_file=None, plot_file=None, output_data_file=None):
    # Read the FITS file
    with fits.open(fits_file) as ff:
        #print(ff[1].header)
        #print(ff[1].data.shape)
        ff_header = ff[1].header
        ff_data = ff[1].data

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
            
            plt.figure(figsize=(plot_width, plot_height))
            cmap = color_tables.aia_color_table(304 * u.angstrom)
            plt.imshow(ff_data, cmap=cmap, origin="lower", aspect=1, norm=LogNorm(vmin=1, vmax=ff_data.max()))
            plt.axis('off')
            #plt.colorbar(label="Intensity")
            #plt.title(f"Solar Prominence (Intensity>{intensity_cutoff})", fontsize=8)
            # Add date and time to the bottom left corner
            obs_time_str = ff_header.get('DATE-OBS', 'Unknown')
            # Replace 'T' with space. Remove '.\d\d\d' if present
            obs_time_str = obs_time_str.replace('T', '  ').split('.')[0]
            plt.text(1, 1, f"{obs_time_str}", color='white', fontsize=6, ha='left', va='bottom')
            plt.savefig(plot_file, dpi=300, bbox_inches="tight", pad_inches=0)
            plt.close()


if __name__ == "__main__":
    calculate_prominence_area()