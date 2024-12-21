#!/bin/bash

source ".env"

# Check the value of APPLICATION_ID and navigate accordingly
if [ "$applicationId" = "885984139315122206" ]; then
    echo "Navigating to /home/tanjun..."
    cd /home/tanjun
    source /home/tanjun/bin/activate
    systemctl stop tanjun.service
elif [ "$applicationId" = "1000673977406070864" ]; then
    echo "Navigating to /home/sayoka..."
    cd /home/sayoka
    source /home/sayoka/bin/activate
    systemctl stop sayoka.service
elif [ "$applicationId" = "1255607578722046015" ]; then
    echo "Navigating to /home/demo-tanjun..."
    cd /home/demo-tanjun
    source /home/demo-tanjun/bin/activate
    systemctl stop demo-tanjun.service
else
    echo "Unknown APPLICATION_ID: $applicationId"
    exit 1
fi

# Confirm the current directory
echo "Current directory: $(pwd)"

# Fetch the latest updates from the remote repository
git fetch --all

# Overwrite local changes and reset to the remote state
git reset --hard origin/Development

# Pull latest changes from GitHub (this is essentially redundant after the reset, but included for clarity)
git pull

# Install dependencies
pip install -r requirements.txt

echo "Update completed successfully. Starting bot..."

# Restart the appropriate service
if [ "$applicationId" = "885984139315122206" ]; then
    systemctl start tanjun.service
elif [ "$applicationId" = "1000673977406070864" ]; then
    systemctl start sayoka.service
elif [ "$applicationId" = "1255607578722046015" ]; then
    systemctl start demo-tanjun.service
fi

echo "Bot started successfully."
