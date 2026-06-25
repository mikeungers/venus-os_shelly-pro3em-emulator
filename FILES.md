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
/data/shelly-emulator/
├── shelly-emulator.py    # Main emulator script
├── uninstall.sh          # Uninstallation script
└── restart.sh            # Restart script

/service/shelly-emulator/
├── run                   # Service run script
└── log/
    └── run               # Log run script

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
bash /data/shelly-emulator/restart.sh
```

### Uninstall
```bash
bash /data/shelly-emulator/uninstall.sh
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
- Publishes mDNS service

### install.sh
Installation script that:
- Creates `/data/shelly-emulator/` directory
- Copies all necessary files
- Creates Venus OS service in `/service/shelly-emulator/`
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
