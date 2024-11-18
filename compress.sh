#!/bin/bash

# Check if a filename is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <filename>"
    exit 1
fi

# Input filename
input_file="$1"

# Get the duration of the video in seconds
duration=$(ffmpeg -i "$input_file" 2>&1 | grep Duration | awk '{print $2}' | tr -d ,)
IFS=: read -r hours minutes seconds <<< "$duration"
duration_total=$(echo "$hours * 3600 + $minutes * 60 + $seconds" | bc)

# Calculate target bitrate for 1.8 GB
target_size_mb=1800
target_bitrate_kbps=$(echo "scale=2; ($target_size_mb * 8192) / $duration_total" | bc)

# Output filename
output_file="compressed_${input_file}"

# Compress the video using ffmpeg with the calculated bitrate
# ffmpeg -i "$input_file" -b:v "${target_bitrate_kbps}k" -vcodec libx264 -acodec aac -b:a 128k "$output_file"

ffmpeg -i "$input_file" -vf "scale=1280:720" -preset ultrafast -b:v "${target_bitrate_kbps}k" -acodec aac -b:a 128k "$output_file"

# Check if the output was successful
if [ $? -eq 0 ]; then
    echo "Video compressed successfully: $output_file"
else
    echo "Error during video compression."
fi