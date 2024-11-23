#!/bin/bash

# Define color codes
GREEN='\033[0;32m'  # Green color
NC='\033[0m'       # No Color (reset)

# File to store URLs and filenames
url_file="downloads.txt"

# Initialize the URL file
echo -n "" > "$url_file"

# Function to wait for active sessions to complete
function wait_for_sessions() {
    local dir="using/"
    local session_count

    while true; do
        session_count=$(ls -1 "${dir}" | wc -l)
        if [ "$session_count" -le 1 ]; then
            break
        fi
        printf "(${GREEN}$session_count active sessions${NC}) Waiting for active sessions to complete...\n"
        sleep 5
    done
    echo "Proceeding as there are $session_count active sessions."
}

# Function to store the download URL and filename
function store_url() {
    local url="$1"
    local filename="$2"
    
    echo "$url -> $filename" >> "$url_file"
}

# Function to check if we have enough URLs to start downloads
function check_ready_to_download() {
    local url_count=$(wc -l < "$url_file")
    if [ "$url_count" -ge 10 ]; then
        start_downloads
    fi
}

# Function to start downloads
function start_downloads() {
    while IFS=" -> " read -r url filename; do
        wait_for_sessions
        echo "Starting download of $url to $filename"
        
        # Download logic goes here (similar to original script)
        # Initialize slices and other parameters as needed
        
        # Trigger Python script after download finishes
        python main.py "$filename"
        
        # Remove the processed entry
        sed -i '1d' "$url_file"  # Remove the first line
    done < "$url_file"
}

# Main script logic to handle command line arguments
while getopts ":hv:s:o:" opt; do
    case $opt in
        h|help ) usage; exit 0 ;;
        v|version ) echo "Multi tasks downloader for curl, version $__ScriptVersion"; exit 0 ;;
        s|slice ) slices=$OPTARG ;;
        o|output ) output=$OPTARG ;;
        * ) echo -e "\n  Option does not exist : $OPTARG\n"; usage; exit 1 ;;
    esac
done
shift $(($OPTIND-1))

url=${@: -1}

if ! [[ $url =~ ^https?://.*$ ]]; then
    printf "\e[31mInvalid URL $url\e[0m\n"
    usage
    exit 1
fi

url_no_query=${url%%\?*}
file_to_save=${url_no_query##*/}

[ x$output != x ] && file_to_save=$output

# Store the URL and filename
store_url "$url" "$file_to_save"
check_ready_to_download