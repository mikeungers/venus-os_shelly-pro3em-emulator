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
INSTALL_DIR="/data/etc/shelly-emulator"
SERVICE_DIR="/data/etc/shelly-emulator/service"
SERVICE_LINK="/service/shelly-emulator"
LOG_DIR="/var/log/shelly-emulator"

echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$LOG_DIR"

echo "Copying files..."
cp shelly-emulator.py "$INSTALL_DIR/"
cp install.sh "$INSTALL_DIR/"
cp uninstall.sh "$INSTALL_DIR/"
cp restart.sh "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/shelly-emulator.py"
chmod +x "$INSTALL_DIR/install.sh"
chmod +x "$INSTALL_DIR/uninstall.sh"
chmod +x "$INSTALL_DIR/restart.sh"

echo "Creating service directory in /data..."
mkdir -p "$SERVICE_DIR"
mkdir -p "$SERVICE_DIR/log"

echo "Creating service run script..."
cat > "$SERVICE_DIR/run" << 'EOF'
#!/bin/sh
exec 2>&1
exec python3 /data/etc/shelly-emulator/shelly-emulator.py
EOF

chmod +x "$SERVICE_DIR/run"

echo "Creating log run script..."
cat > "$SERVICE_DIR/log/run" << 'EOF'
#!/bin/sh
exec multilog t s25000 n4 /var/log/shelly-emulator
EOF

chmod +x "$SERVICE_DIR/log/run"

echo "Creating symlink to /service..."
if [ -L "$SERVICE_LINK" ]; then
    rm "$SERVICE_LINK"
fi
ln -s "$SERVICE_DIR" "$SERVICE_LINK"

echo "Adding to rc.local for auto-start on boot..."
RC_LOCAL="/data/rc.local"
if ! grep -q "shelly-emulator/install.sh" "$RC_LOCAL" 2>/dev/null; then
    echo "" >> "$RC_LOCAL"
    echo "bash /data/etc/shelly-emulator/install.sh" >> "$RC_LOCAL"
    chmod +x "$RC_LOCAL"
fi

echo "Starting service..."
svc -u "$SERVICE_LINK"

echo ""
echo "=========================================="
echo "Installation complete!"
echo "=========================================="
echo ""
echo "Service status:"
svstat "$SERVICE_LINK"
echo ""
echo "To view logs:"
echo "  tail -f /var/log/shelly-emulator/current | tai64nlocal"
echo ""
echo "To restart service:"
echo "  bash /data/etc/shelly-emulator/restart.sh"
echo ""
echo "To uninstall:"
echo "  bash /data/etc/shelly-emulator/uninstall.sh"
echo ""
echo "The emulator is now running on:"
echo "  - UDP port 1010 (for Marstek)"
echo "  - HTTP port 80 (for web access)"
echo ""
