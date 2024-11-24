#!/bin/bash

# Define color codes
GREEN='\033[0;32m'  # Green color
NC='\033[0m'       # No Color (reset)

# File to store URLs and filenames
url_file="downloads.txt"

# Initialize the URL file
# echo -n "" > "$url_file"

function wait_for_sessions() {
    local dir="using/"
    local session_count

    while true; do
        session_count=$(find "$dir" -maxdepth 1 -type f | wc -l)
        if [ "$session_count" -le 1 ]; then
            break
        fi
        printf "(${GREEN}%s active sessions${NC}) Waiting for active sessions to complete...\n" "$session_count"
        sleep 5
    done
    printf "Proceeding as there are %s active sessions.\n" "$session_count"
}

function store_url() {
    local url="$1"
    local filename="$2"
    
    # Ensure filename does not have unwanted characters
    filename=$(echo "$filename" | tr -d '[:space:]')  # Remove spaces if needed

    echo "$url -> $filename" >> "$url_file"
}
# Function to check if we have enough URLs to start downloads
function check_ready_to_download() {
    local url_count
    url_count=$(wc -l < "$url_file")  # Separate assignment
    
    if [ "$url_count" -ge 3 ]; then
        start_downloads
    fi
}

# Function to confirm the input
function confirm_input() {
    echo url "$url"
    echo filename "$filename"
    read -rp "Are these entries correct? (y/n): " confirmation

    if [[ "$confirmation" != "y" && "$confirmation" != "Y" ]]; then
        echo "Please re-enter the details."
        return 1
    fi

    echo "Confirmed."
    ./mcurl.sh -o "$filename" "$url"

    echo "check downloaded file"
    read -rp "cek download udah? (y/n): " confirmation

    if [[ "$confirmation" != "y" && "$confirmation" != "Y" ]]; then
        echo "Please re-enter the details."
        return 1
    fi
    python main.py "$filename"
}

# Function to start downloads
function start_downloads() {
    # Read all lines into an array
    mapfile -t urls < "$url_file"

    # Process each URL
    for entry in "${urls[@]}"; do
        IFS=" -> " read -r url filename <<< "$entry"

        wait_for_sessions
        echo "Starting download of $url to $filename"

        confirm_input
        # Download logic goes here (similar to original script)
        # Initialize slices and other parameters as needed

        # Trigger Python script after download finishes
    done

    # Remove the processed entries from the original file
    sed -i '1,3d' "$url_file"  # Remove the first 10 lines
}

# Main script logic to handle command line arguments
while getopts ":hv:s:o:" opt; do
    case $opt in
        h|help ) 
            usage
            exit 0 
            ;;
        v|version ) 
            echo "Multi tasks downloader for curl, version $__ScriptVersion"
            exit 0 
            ;;
        s|slice ) 
            slices=$OPTARG 
            ;;
        o|output ) 
            output=$OPTARG 
            ;;
        \? )  # Handle unknown options
            echo -e "\n  Option does not exist: -$OPTARG\n"
            usage
            exit 1 
            ;;
        : )  # Handle missing option arguments
            echo "Option -$OPTARG requires an argument."
            usage
            exit 1 
            ;;
    esac
done

# Shift processed options
shift $((OPTIND - 1))

# Check if there's a URL provided
if [ $# -lt 1 ]; then
    echo "A URL must be provided."
    usage
    exit 1
fi

url=${1}
shift $((OPTIND-1))

# url=${*: -1}

if ! [[ $url =~ ^https?://.*$ ]]; then
    printf "\e[31mInvalid URL '..%s..' \e[0m\n" "$url"
    usage
    exit 1
fi

url_no_query=${url%%\?*}
file_to_save=${url_no_query##*/}

[ x"$output" != x ] && file_to_save=$output

# Store the URL and filename
store_url "$url" "$file_to_save"
check_ready_to_download