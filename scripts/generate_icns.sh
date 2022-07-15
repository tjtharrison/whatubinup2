#!/bin/bash

input_filepath="img/icon.png" 
output_iconset_name="img/wubu2.iconset"
mkdir $output_iconset_name

sizes="16,32,64,128,256,512"

IFS=','

for size in $sizes; do
    sips -z $size $size     $input_filepath --out "${output_iconset_name}/icon_${size}x${size}.png"
done

iconutil -c icns $output_iconset_name

rm -rf $output_iconset_name
