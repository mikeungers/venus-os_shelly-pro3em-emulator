#!/bin/bash
# Installation script for Shelly Pro 3EM Emulator on Venus OS

set -e

echo "=========================================="
echo "Shelly Pro 3EM Emulator - Venus OS Setup"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use: sudo bash install.sh)"
    exit 1
fi

# Installation directory
INSTALL_DIR="/data/shelly-emulator"
SERVICE_FILE="/service/shelly-emulator/run"
LOG_DIR="/var/log/shelly-emulator"

echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$LOG_DIR"

echo "Copying files..."
cp shelly-emulator.py "$INSTALL_DIR/"
cp uninstall.sh "$INSTALL_DIR/"
cp restart.sh "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/shelly-emulator.py"
chmod +x "$INSTALL_DIR/uninstall.sh"
chmod +x "$INSTALL_DIR/restart.sh"

echo "Creating service directory..."
mkdir -p /service/shelly-emulator
mkdir -p /service/shelly-emulator/log

echo "Creating service run script..."
cat > "$SERVICE_FILE" << 'EOF'
#!/bin/sh
exec 2>&1
exec python3 /data/shelly-emulator/shelly-emulator.py
EOF

chmod +x "$SERVICE_FILE"

echo "Creating log run script..."
cat > /service/shelly-emulator/log/run << 'EOF'
#!/bin/sh
exec multilog t s25000 n4 /var/log/shelly-emulator
EOF

chmod +x /service/shelly-emulator/log/run

echo "Starting service..."
svc -u /service/shelly-emulator

echo ""
echo "=========================================="
echo "Installation complete!"
echo "=========================================="
echo ""
echo "Service status:"
svstat /service/shelly-emulator
echo ""
echo "To view logs:"
echo "  tail -f /var/log/shelly-emulator/current | tai64nlocal"
echo ""
echo "To restart service:"
echo "  bash /data/shelly-emulator/restart.sh"
echo ""
echo "To uninstall:"
echo "  bash /data/shelly-emulator/uninstall.sh"
echo ""
echo "The emulator is now running on:"
echo "  - UDP port 1010 (for Marstek)"
echo "  - HTTP port 80 (for web access)"
echo "  - mDNS: shellypro3em-aadeadbeefaa"
echo ""
