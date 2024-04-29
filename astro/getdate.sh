#!/bin/bash

startdate=$1
enddate=$2

for (( date="$startdate"; date <= enddate; )); do
    echo $date
    date="$(date --date="$date + 1 days" +'%Y%m%d')"
done
