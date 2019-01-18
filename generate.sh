#!/bin/bash

for filename in $(ls ./xmls/*.xml)
do
  array=( XXS XS S M L XL XXL )
  for size in "${array[@]}"
  do
    GENERATED_FILE="${filename%.*}_${size}_x.xml"
    pianoplayer "${filename}" --debug -b -x -$size -o $GENERATED_FILE
  done
done
