#!/bin/bash

# Restart script
echo "Restarting Shelly Pro 3EM Emulator..."

svc -t /service/shelly-emulator

sleep 2

svstat /service/shelly-emulator

echo ""
echo "Service restarted. Check logs with:"
echo "  tail -f /var/log/shelly-emulator/current | tai64nlocal"
