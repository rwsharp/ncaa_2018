#!/bin/bash

output_file=all_valid_rankers.txt

if [ $# -gt 0 ]
then
    start_year=$1
else
    start_year=0
fi


cd /Users/rsharp/Dropbox/Uncertain\ Principles/Articles/NCAA\ bracketeering/NCAA\ Bracket\ 2018/data/prepared_data/
i=0
for filename in valid_rankers_*.txt
do

    year=$(echo $filename | sed 's/[^0-9]*//g')
    if [ $year -ge $start_year ]
    then
        if [ $i -eq 0 ]
        then
            cp $filename $output_file
        else
            comm -12 $output_file $filename > temp
            cp temp $output_file
        fi

        i=$((i+1))
    fi
done

rm temp
