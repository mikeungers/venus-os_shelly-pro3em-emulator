# File Structure

## Repository Files

```
venus-service/
├── shelly-emulator.py    # Main emulator script
├── install.sh            # Installation script
├── uninstall.sh          # Uninstallation script
├── restart.sh            # Restart script
├── README.md             # Documentation
└── FILES.md              # This file
```

## Installed Files on Venus OS

After installation, files are located at:

```
/data/etc/shelly-emulator/
├── shelly-emulator.py    # Main emulator script
├── uninstall.sh          # Uninstallation script
├── restart.sh            # Restart script
└── service/              # Service directory
    ├── run               # Service run script
    └── log/
        └── run           # Log run script

/service/shelly-emulator/ # Symlink to /data/etc/shelly-emulator/service

/var/log/shelly-emulator/
└── current               # Current log file
```

## Usage

### Install

```bash
bash install.sh
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

### install.sh

Installation script that:

- Creates `/data/etc/shelly-emulator/` directory
- Copies all necessary files
- Creates Venus OS service in `/data/etc/shelly-emulator/service/`
- Symlinks to `/service/shelly-emulator/`
- Adds to `/data/rc.local` for auto-start on boot
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
