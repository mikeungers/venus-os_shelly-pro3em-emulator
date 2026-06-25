#!/bin/bash

# Remove script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "Uninstalling Shelly Pro 3EM Emulator..."

# Stop service
echo "Stopping service..."
svc -d /service/shelly-emulator

# Wait for service to stop
sleep 2

# Remove service
echo "Removing service..."
rm -rf /service/shelly-emulator

# Remove logs
echo "Removing logs..."
rm -rf /var/log/shelly-emulator

echo "Uninstall complete!"
echo ""
echo "Note: Installation files in /data/shelly-emulator are kept."
echo "To remove them, run: rm -rf /data/shelly-emulator"
