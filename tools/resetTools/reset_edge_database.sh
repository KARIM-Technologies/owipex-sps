#!/bin/bash

# Function to check the exit status of the last command and exit if it failed
check_status() {
  if [ $? -ne 0 ]; then
    echo "Error: $1 failed. Exiting."
    exit 1
  fi
}

# Stop the tb-edge server
sudo systemctl stop tb-edge
check_status "Stopping tb-edge server"

echo "tb-edge server stopped."

# Delete the PostgreSQL database 'owipex_db'
sudo -u postgres psql -c "DROP DATABASE IF EXISTS \"owipex_db\";"
check_status "Dropping database 'owipex_db'"

echo "Database 'owipex_db' deleted."

# Create a new PostgreSQL database 'owipex_db'
sudo -u postgres psql -c "CREATE DATABASE \"owipex_db\";"
check_status "Creating database 'owipex_db'"

echo "New database 'owipex_db' created."

# Load the example data
sudo /usr/share/tb-edge/bin/install/install.sh
check_status "Loading example data"

echo "Example data loaded successfully."

# Reload systemd manager configuration
sudo systemctl daemon-reload
check_status "Reloading systemd manager configuration"

echo "Systemd manager configuration reloaded."

# Restart the tb-edge server
sudo systemctl start tb-edge
check_status "Starting tb-edge server"

echo "tb-edge server restarted successfully."