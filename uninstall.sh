#!/bin/bash

# Remove script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "Uninstalling Shelly Pro 3EM Emulator..."

# Stop service
echo "Stopping service..."
svc -d /service/shelly-emulator

# Wait for service to stop
sleep 2

# Remove service symlink
echo "Removing service..."
rm -f /service/shelly-emulator

# Remove rc.local entry
echo "Removing rc.local entry..."
RC_LOCAL="/data/rc.local"
if [ -f "$RC_LOCAL" ]; then
    sed -i '/shelly-emulator\/install.sh/d' "$RC_LOCAL"
fi

# Remove logs
echo "Removing logs..."
rm -rf /var/log/shelly-emulator

echo "Uninstall complete!"
echo ""
echo "Note: Installation files in /data/etc/shelly-emulator are kept."
echo "To remove them, run: rm -rf /data/etc/shelly-emulator"
