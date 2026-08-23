# venus-os_shelly-pro3em-emulator - Emulates a Shelly Pro 3EM from Venus OS meter data

GitHub repository: [venus-os_shelly-pro3em-emulator](https://github.com/mikeungers/venus-os_shelly-pro3em-emulator)

## Index

1. [Disclaimer](#disclaimer)
2. [Purpose](#purpose)
3. [Features](#features)
4. [Install / Update](#install--update)
5. [Configuration](#configuration)
6. [Uninstall](#uninstall)
7. [Restart](#restart)
8. [Debugging](#debugging)
9. [Compatibility](#compatibility)
10. [Screenshots](#screenshots)

## Disclaimer

I wrote this script for myself. I'm not responsible, if you damage something using my script.

## Purpose

The script emulates a **Shelly Pro 3EM** energy meter in Venus OS for **Marstek** battery integration. It reads real-time data from your existing Venus OS energy meter via D-Bus and exposes it as a Shelly Pro 3EM device that Marstek can discover and use.

This allows Marstek devices (Venus E, Venus C, B-2500) to read your grid meter data without requiring a physical Shelly Pro 3EM.

### How it works:

1. Reads meter data from Venus OS D-Bus (`com.victronenergy.grid.*`, `com.victronenergy.pvinverter.*`, etc.)
2. Exposes data via:
   - **UDP RPC on port 1010** (Marstek's discovery protocol)
   - **HTTP API on port 8080** (Shelly REST API)
3. Marstek discovers the emulated Shelly and reads real-time power data

## Features

- ✅ **Reads real Venus OS meter data** via D-Bus
- ✅ **UDP RPC on port 1010** - Marstek's required port
- ✅ **HTTP API on port 8080** - Full Shelly API compatibility
- ✅ **Runs as system service** - Auto-starts on boot
- ✅ **Based on uni-meter** - Proven working configuration
- ✅ **Supports 3-phase meters** - L1, L2, L3
- ✅ **Energy counters** - Forward and reverse energy
- ✅ **No additional hardware** - Pure software solution

## Install / Update

1. Login to your Venus OS device via SSH. See [Venus OS:Root Access](https://www.victronenergy.com/live/ccgx:root_access) for more details.

2. Execute these commands to download and install:

   ```bash
   # Download files
   wget -O /tmp/shelly-emulator.py https://raw.githubusercontent.com/yourusername/venus-os_shelly-pro3em-emulator/main/venus-service/shelly-emulator.py
   wget -O /tmp/install.sh https://raw.githubusercontent.com/yourusername/venus-os_shelly-pro3em-emulator/main/venus-service/install.sh

   # Make installer executable
   chmod +x /tmp/install.sh

   # Run installation
   bash /tmp/install.sh
   ```

3. The installer will:
   - Copy the emulator to `/data/etc/shelly-emulator/`
   - Create a Venus OS service in `/service/shelly-emulator/`
   - Start the service automatically
   - Configure logging to `/var/log/shelly-emulator/`

4. Verify installation:

   ```bash
   svstat /service/shelly-emulator
   ```

   Should show: `up (pid XXXX) XX seconds`

### Manual Installation

If you prefer manual installation:

```bash
# Create directory
mkdir -p /data/etc/shelly-emulator

# Copy script
cp shelly-emulator.py /data/etc/shelly-emulator/
chmod +x /data/etc/shelly-emulator/shelly-emulator.py

# Create service
mkdir -p /service/shelly-emulator
mkdir -p /service/shelly-emulator/log

# Create run script
cat > /service/shelly-emulator/run << 'EOF'
#!/bin/sh
exec 2>&1
exec python3 /data/etc/shelly-emulator/shelly-emulator.py
EOF
chmod +x /service/shelly-emulator/run

# Create log script
cat > /service/shelly-emulator/log/run << 'EOF'
#!/bin/sh
exec multilog t s25000 n4 /var/log/shelly-emulator
EOF
chmod +x /service/shelly-emulator/log/run

# Start service
svc -u /service/shelly-emulator
```

## Configuration

Edit `/data/etc/shelly-emulator/shelly-emulator.py` to customize:

### Device Identity

```python
DEVICE_ID = "shellypro3em-aadeadbeefaa"  # Device ID
MAC = "AADEADBEEFAA"                     # MAC address
```

### Ports

```python
UDP_PORT = 1010   # Marstek discovery port (do not change)
HTTP_PORT = 8080  # HTTP API port (change if port 80 is in use)
```

After changes, restart the service:

```bash
svc -t /service/shelly-emulator
```

## Uninstall

```bash
bash /data/etc/shelly-emulator/uninstall.sh
```

This will:

- Stop the service
- Remove the service directory
- Remove log files
- Keep installation files in `/data/etc/shelly-emulator` (remove manually if needed)

## Restart

```bash
bash /data/etc/shelly-emulator/restart.sh
```

This will restart the service and show the current status.

## Debugging

### Check Logs

```bash
tail -n 100 -F /var/log/shelly-emulator/current | tai64nlocal
```

### Check Service Status

```bash
svstat /service/shelly-emulator
```

This will output something like:

```
/service/shelly-emulator: up (pid 5845) 185 seconds
```

If the seconds are under 5, the service is crashing and restarting.

### Test UDP (Marstek uses this)

```bash
echo '{"id":1,"method":"Shelly.GetDeviceInfo"}' | socat - UDP-DATAGRAM:127.0.0.1:1010
```

Expected response:

```json
{"id":1,"src":"shellypro3em-aadeadbeefaa","result":{...}}
```

### Test HTTP API

```bash
# Device info
curl http://127.0.0.1:8080/shelly

# EM status
curl http://127.0.0.1:8080/rpc/EM.GetStatus?id=0
```

### Check D-Bus Meter Service

The emulator automatically discovers your meter service. Check logs:

```bash
tail -f /var/log/shelly-emulator/current | grep "meter service"
```

Should show:

```
Found meter service: com.victronenergy.grid.mqtt_grid_31
Using meter service: com.victronenergy.grid.mqtt_grid_31
```

### Increase Log Level

Edit `/data/etc/shelly-emulator/shelly-emulator.py` and change:

```python
logging.basicConfig(
    level=logging.INFO,  # Change to logging.DEBUG for more details
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Then restart:

```bash
svc -t /service/shelly-emulator
```

### Common Issues

#### Port 80 Already in Use

Change `HTTP_PORT` to `8080` in the script and restart.

#### No Meter Service Found

Check available services:

```bash
dbus -y com.victronenergy.system /ServiceMapping GetValue
```

Or list all services:

```bash
dbus -y | grep victronenergy
```

#### Marstek Not Discovering

1. Check service is running: `svstat /service/shelly-emulator`
2. Check logs for UDP requests: `tail -f /var/log/shelly-emulator/current`
3. Restart Marstek device (power cycle)
4. Check network connectivity: `ping marstek-ip`

## Compatibility

This software supports the latest three stable versions of Venus OS. It may also work on older versions, but this is not guaranteed.

### Tested with:

- ✅ Venus OS v2.x
- ✅ Venus OS v3.x
- ✅ Marstek Venus E
- ✅ Marstek Venus C
- ✅ Marstek B-2500

### Requirements:

- Venus OS with D-Bus support
- Python 3.x (included in Venus OS)
- `python-dbus` package (included in Venus OS)
- Existing grid meter or energy meter in Venus OS

## Screenshots

### Venus OS - Service Running

```
root@raspberrypi4:~# svstat /service/shelly-emulator
/service/shelly-emulator: up (pid 12345) 3600 seconds
```

### Marstek App - Device Discovered

_[Screenshot would show Shelly Pro 3EM discovered in Marstek app]_

### Logs - Real-time Data

```
2026-06-25 13:29:07 - shelly-emulator - INFO - Shelly Pro 3EM Emulator for Venus OS
2026-06-25 13:29:07 - shelly-emulator - INFO - Found meter service: com.victronenergy.grid.mqtt_grid_31
2026-06-25 13:29:08 - shelly-emulator - INFO - UDP server listening on port 1010
2026-06-25 13:29:08 - shelly-emulator - INFO - HTTP server listening on port 8080
2026-06-25 13:29:08 - shelly-emulator - INFO - Reading real-time data from Venus OS
2026-06-25 13:29:08 - shelly-emulator - INFO - UDP request from ('192.168.1.97', 22222): em.getstatus
2026-06-25 13:29:08 - shelly-emulator - INFO - Sent Status to ('192.168.1.97', 22222)
```

## About

This Venus OS service emulates a Shelly Pro 3EM energy meter by reading real-time data from your existing Venus OS meter via D-Bus and exposing it through UDP RPC and HTTP API for Marstek battery integration.

Based on the [uni-meter](https://github.com/sdeigm/uni-meter) project by sdeigm.

## License

MIT License - Free to use and modify
