#!/bin/bash

# Download script for Shelly Pro 3EM Emulator
# This downloads all necessary files to /data/etc/shelly-emulator

GITHUB_REPO="mikeungers/venus-os_shelly-pro3em-emulator"
GITHUB_BRANCH="main"
INSTALL_DIR="/data/etc/shelly-emulator"

echo
echo "Downloading Shelly Pro 3EM Emulator..."
echo

# Create installation directory
mkdir -p "$INSTALL_DIR/service/log"

# Download main files
echo "Downloading main files..."
wget -q -O "$INSTALL_DIR/shelly-emulator.py" "https://github.com/$GITHUB_REPO/raw/$GITHUB_BRANCH/shelly-emulator.py"
wget -q -O "$INSTALL_DIR/install.sh" "https://github.com/$GITHUB_REPO/raw/$GITHUB_BRANCH/install.sh"
wget -q -O "$INSTALL_DIR/uninstall.sh" "https://github.com/$GITHUB_REPO/raw/$GITHUB_BRANCH/uninstall.sh"
wget -q -O "$INSTALL_DIR/restart.sh" "https://github.com/$GITHUB_REPO/raw/$GITHUB_BRANCH/restart.sh"

# Download service files
echo "Downloading service files..."
wget -q -O "$INSTALL_DIR/service/run" "https://github.com/$GITHUB_REPO/raw/$GITHUB_BRANCH/service/run"
wget -q -O "$INSTALL_DIR/service/log/run" "https://github.com/$GITHUB_REPO/raw/$GITHUB_BRANCH/service/log/run"

echo
echo "Download complete!"
echo
echo "Starting installation..."
bash "$INSTALL_DIR/install.sh"
