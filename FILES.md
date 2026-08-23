# File Structure

## Repository Files

```
venus-service/
├── shelly-emulator.py    # Main emulator script
├── download.sh           # Download script
├── install.sh            # Installation script
├── uninstall.sh          # Uninstallation script
├── restart.sh            # Restart script
├── README.md             # Documentation
├── FILES.md              # This file
└── service/              # Service directory
    ├── run               # Service run script
    └── log/
        └── run           # Log run script
```

## Installed Files on Venus OS

After installation, files are located at:

```
/data/etc/shelly-emulator/
├── shelly-emulator.py    # Main emulator script
├── install.sh            # Installation script (copied during install)
├── uninstall.sh          # Uninstallation script
├── restart.sh            # Restart script
└── service/              # Service directory
    ├── run               # Service run script
    └── log/
        └── run           # Log run script

/service/shelly-emulator/ # Symlink to /data/etc/shelly-emulator/service

/var/log/shelly-emulator/
└── current               # Current log file

/data/rc.local            # Contains auto-start entry
```

## Usage

### Install

```bash
wget -O /tmp/download_shelly_emulator.sh https://raw.githubusercontent.com/mikeungers/venus-os_shelly-pro3em-emulator/main/download.sh && bash /tmp/download_shelly_emulator.sh && rm /tmp/download_shelly_emulator.sh
```

### Restart

```bash
bash /data/etc/shelly-emulator/restart.sh
```

### Uninstall

```bash
bash /data/etc/shelly-emulator/uninstall.sh
```

### View Logs

```bash
tail -f /var/log/shelly-emulator/current | tai64nlocal
```

## Script Descriptions

### shelly-emulator.py

Main Python script that:

- Reads meter data from Venus OS D-Bus
- Exposes UDP RPC on port 1010
- Exposes HTTP API on port 8080

### download.sh

Download script that:

- Downloads all files to `/data/etc/shelly-emulator/`
- Downloads service run scripts
- Automatically runs install.sh after download

### install.sh

Installation script that:

- Sets correct permissions on all files
- Creates symlink from `/service/shelly-emulator/` to service directory
- Adds entry to `/data/rc.local` for auto-start on boot
- Starts the service automatically

### uninstall.sh

Uninstallation script that:

- Stops the service
- Removes service directory
- Removes log files
- Keeps installation files (for manual removal)

### restart.sh

Restart script that:

- Restarts the service
- Shows service status
- Provides log viewing instructions
