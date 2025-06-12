#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 --devices device1.qcow2,device2.qcow2,device3.qcow2"
    echo "Example: $0 --devices Ubuntu-Branch2.final.qcow2,CentOS-Test.final.qcow2"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --devices)
            DEVICES="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Check if devices parameter was provided
if [[ -z "$DEVICES" ]]; then
    echo "Error: --devices parameter is required"
    usage
fi

# Split devices by comma and process each one
IFS=',' read -ra DEVICE_ARRAY <<< "$DEVICES"

echo "system repository home shell"
echo "cd firmwares/"

# Generate mv commands for each device (original to .custom)
for device in "${DEVICE_ARRAY[@]}"; do
    # Trim whitespace
    device=$(echo "$device" | xargs)

    # Extract base name without .qcow2 extension
    base_name="${device%.qcow2}"

    echo "mv $device ${base_name}.custom.qcow2"
done

echo "exit"
echo "system repository home refresh"
echo "system repository home shell"
echo "cd firmwares/"

# Generate mv commands for each device (.custom back to original)
for device in "${DEVICE_ARRAY[@]}"; do
    # Trim whitespace
    device=$(echo "$device" | xargs)

    # Extract base name without .qcow2 extension
    base_name="${device%.qcow2}"

    echo "mv ${base_name}.custom.qcow2 $device"
done

echo "exit"
echo "system repository home refresh"