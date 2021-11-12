#!/bin/bash

python pacman.py -p ApproximateQAgent -a extractor=NewExtractor -x 50 -n 60 -l mediumClassic -q > temp.txt &
python pacman.py -p ApproximateQAgent -a extractor=NewExtractor -x 50 -n 60 -l mediumClassic -q > temp2.txt &
python pacman.py -p ApproximateQAgent -a extractor=NewExtractor -x 50 -n 60 -l mediumClassic -q > temp3.txt &
python pacman.py -p ApproximateQAgent -a extractor=NewExtractor -x 50 -n 60 -l mediumClassic -q > temp4.txt &
python pacman.py -p ApproximateQAgent -a extractor=NewExtractor -x 50 -n 60 -l mediumClassic -q > temp5.txt &
python pacman.py -p ApproximateQAgent -a extractor=NewExtractor -x 50 -n 60 -l mediumClassic -q > temp6.txt &
python pacman.py -p ApproximateQAgent -a extractor=NewExtractor -x 50 -n 60 -l mediumClassic -q > temp7.txt &
python pacman.py -p ApproximateQAgent -a extractor=NewExtractor -x 50 -n 60 -l mediumClassic -q > temp8.txt &


wait
echo "alldone"