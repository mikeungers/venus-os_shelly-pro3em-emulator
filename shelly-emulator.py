#!/usr/bin/env python3
"""
Shelly Pro 3EM Emulator for Venus OS
Emulates a Shelly Pro 3EM energy meter for Marstek integration
Reads real data from Venus OS D-Bus
Based on uni-meter implementation
"""

import socket
import json
import time
import threading
import logging
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess

try:
    import dbus
    DBUS_AVAILABLE = True
except ImportError:
    DBUS_AVAILABLE = False
    logging.warning("python-dbus not available, using dummy values")

# Configuration
DEVICE_ID = "shellypro3em-aadeadbeefaa"
MAC = "AADEADBEEFAA"
UDP_PORT = 1010
HTTP_PORT = 8080  # Changed from 80 to avoid conflict

# Venus OS D-Bus connection
bus = None
meter_service = None
meter_data = {
    'voltage_l1': 230.0,
    'voltage_l2': 230.0,
    'voltage_l3': 230.0,
    'current_l1': 0.0,
    'current_l2': 0.0,
    'current_l3': 0.0,
    'power_l1': 0.0,
    'power_l2': 0.0,
    'power_l3': 0.0,
    'power_total': 0.0,
    'energy_forward': 0.0,
    'energy_reverse': 0.0,
    'frequency': 50.0
}
meter_lock = threading.Lock()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('shelly-emulator')


def find_meter_service():
    """Find the grid meter service on Venus OS D-Bus"""
    global bus
    
    if not DBUS_AVAILABLE:
        return None
    
    try:
        bus = dbus.SystemBus()
        
        # Look for grid meter services
        service_names = [
            'com.victronenergy.grid',
            'com.victronenergy.pvinverter',
            'com.victronenergy.vebus'
        ]
        
        for service_prefix in service_names:
            # Get all services
            dbus_obj = bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus')
            dbus_iface = dbus.Interface(dbus_obj, 'org.freedesktop.DBus')
            services = dbus_iface.ListNames()
            
            # Find matching services
            for service in services:
                if service.startswith(service_prefix):
                    logger.info(f"Found meter service: {service}")
                    return service
        
        logger.warning("No meter service found, using default values")
        return None
        
    except Exception as e:
        logger.error(f"Error finding meter service: {e}")
        return None


def read_dbus_value(service, path, default=0.0):
    """Read a value from D-Bus"""
    if not DBUS_AVAILABLE or not bus:
        return default
        
    try:
        obj = bus.get_object(service, path)
        iface = dbus.Interface(obj, 'com.victronenergy.BusItem')
        value = iface.GetValue()
        return float(value) if value is not None else default
    except:
        return default


def update_meter_data():
    """Update meter data from Venus OS D-Bus"""
    global meter_service
    
    if not DBUS_AVAILABLE:
        return
    
    if not meter_service:
        meter_service = find_meter_service()
        if not meter_service:
            return
    
    try:
        with meter_lock:
            # Read AC values
            meter_data['voltage_l1'] = read_dbus_value(meter_service, '/Ac/L1/Voltage', 230.0)
            meter_data['voltage_l2'] = read_dbus_value(meter_service, '/Ac/L2/Voltage', 230.0)
            meter_data['voltage_l3'] = read_dbus_value(meter_service, '/Ac/L3/Voltage', 230.0)
            
            meter_data['current_l1'] = read_dbus_value(meter_service, '/Ac/L1/Current', 0.0)
            meter_data['current_l2'] = read_dbus_value(meter_service, '/Ac/L2/Current', 0.0)
            meter_data['current_l3'] = read_dbus_value(meter_service, '/Ac/L3/Current', 0.0)
            
            meter_data['power_l1'] = read_dbus_value(meter_service, '/Ac/L1/Power', 0.0)
            meter_data['power_l2'] = read_dbus_value(meter_service, '/Ac/L2/Power', 0.0)
            meter_data['power_l3'] = read_dbus_value(meter_service, '/Ac/L3/Power', 0.0)
            
            meter_data['power_total'] = read_dbus_value(meter_service, '/Ac/Power', 0.0)
            
            # Read energy values (in kWh, convert to Wh)
            meter_data['energy_forward'] = read_dbus_value(meter_service, '/Ac/Energy/Forward', 0.0) * 1000
            meter_data['energy_reverse'] = read_dbus_value(meter_service, '/Ac/Energy/Reverse', 0.0) * 1000
            
            meter_data['frequency'] = read_dbus_value(meter_service, '/Ac/L1/Frequency', 50.0)
            
    except Exception as e:
        logger.error(f"Error reading meter data: {e}")
        meter_service = None  # Reset to retry discovery


class ShellyHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Shelly API"""
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info("%s - %s" % (self.address_string(), format % args))
    
    def do_GET(self):
        """Handle GET requests"""
        
        if self.path == '/shelly':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "type": "SPEM-003CEBEU120",
                "mac": MAC,
                "auth": False,
                "fw": "20250924-062729/1.7.1-gd336f31",
                "discoverable": True,
                "longid": 1,
                "gen": 2,
                "app": "Pro3EM"
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path.startswith('/rpc/EM.GetStatus'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            with meter_lock:
                response = {
                    "id": 0,
                    "a_current": meter_data['current_l1'],
                    "a_voltage": meter_data['voltage_l1'],
                    "a_act_power": meter_data['power_l1'],
                    "a_aprt_power": 0.0,
                    "a_pf": 1.0,
                    "a_freq": meter_data['frequency'],
                    "b_current": meter_data['current_l2'],
                    "b_voltage": meter_data['voltage_l2'],
                    "b_act_power": meter_data['power_l2'],
                    "b_aprt_power": 0.0,
                    "b_pf": 1.0,
                    "b_freq": meter_data['frequency'],
                    "c_current": meter_data['current_l3'],
                    "c_voltage": meter_data['voltage_l3'],
                    "c_act_power": meter_data['power_l3'],
                    "c_aprt_power": 0.0,
                    "c_pf": 1.0,
                    "c_freq": meter_data['frequency'],
                    "n_current": None,
                    "total_current": meter_data['current_l1'] + meter_data['current_l2'] + meter_data['current_l3'],
                    "total_act_power": meter_data['power_total'],
                    "total_aprt_power": 0.0
                }
            
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests (RPC)"""
        
        if self.path == '/rpc':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request = json.loads(post_data.decode())
                method = request.get('method', '')
                req_id = request.get('id', 1)
                
                if method == 'Shelly.GetDeviceInfo':
                    response = {
                        "id": req_id,
                        "src": DEVICE_ID,
                        "result": {
                            "name": DEVICE_ID,
                            "id": DEVICE_ID,
                            "mac": MAC,
                            "model": "SPEM-003CEBEU120",
                            "gen": 2,
                            "fw_id": "20250924-062729/1.7.1-gd336f31",
                            "ver": "1.7.1",
                            "app": "Pro3EM",
                            "auth_en": False
                        }
                    }
                    
                elif method == 'EM.GetStatus':
                    with meter_lock:
                        response = {
                            "id": req_id,
                            "src": DEVICE_ID,
                            "result": {
                                "id": 0,
                                "a_current": meter_data['current_l1'],
                                "a_voltage": meter_data['voltage_l1'],
                                "a_act_power": meter_data['power_l1'],
                                "total_act_power": meter_data['power_total']
                            }
                        }
                else:
                    response = {
                        "id": req_id,
                        "error": {"code": -32601, "message": "Method not found"}
                    }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                logger.error(f"Error handling POST: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


def handle_udp_request(data, addr, sock):
    """Handle incoming UDP RPC requests"""
    
    try:
        # Ignore our own broadcasts
        if data.startswith(b'{"src":"shellypro3em'):
            return
        
        request = json.loads(data.decode('utf-8'))
        method = request.get('method', '').lower()
        
        if not method:
            return
        
        logger.info(f"UDP request from {addr}: {method}")
        
        if 'getdeviceinfo' in method:
            response = {
                "id": request.get('id', 1),
                "src": DEVICE_ID,
                "result": {
                    "name": DEVICE_ID,
                    "id": DEVICE_ID,
                    "mac": MAC,
                    "model": "SPEM-003CEBEU120",
                    "gen": 2,
                    "fw_id": "20250924-062729/1.7.1-gd336f31",
                    "ver": "1.7.1",
                    "app": "Pro3EM",
                    "auth_en": False,
                    "auth_domain": None,
                    "discoverable": True
                }
            }
            sock.sendto(json.dumps(response).encode('utf-8'), addr)
            logger.info(f"Sent DeviceInfo to {addr}")
            
        elif 'getstatus' in method:
            with meter_lock:
                response = {
                    "id": request.get('id', 1),
                    "src": DEVICE_ID,
                    "result": {
                        "em:0": {
                            "id": 0,
                            "a_current": meter_data['current_l1'],
                            "a_voltage": meter_data['voltage_l1'],
                            "a_act_power": meter_data['power_l1'],
                            "a_aprt_power": 0.0,
                            "a_pf": 1.0,
                            "a_freq": meter_data['frequency'],
                            "b_current": meter_data['current_l2'],
                            "b_voltage": meter_data['voltage_l2'],
                            "b_act_power": meter_data['power_l2'],
                            "b_aprt_power": 0.0,
                            "b_pf": 1.0,
                            "b_freq": meter_data['frequency'],
                            "c_current": meter_data['current_l3'],
                            "c_voltage": meter_data['voltage_l3'],
                            "c_act_power": meter_data['power_l3'],
                            "c_aprt_power": 0.0,
                            "c_pf": 1.0,
                            "c_freq": meter_data['frequency'],
                            "n_current": None,
                            "total_current": meter_data['current_l1'] + meter_data['current_l2'] + meter_data['current_l3'],
                            "total_act_power": meter_data['power_total'],
                            "total_aprt_power": 0.0,
                            "user_calibrated_phase": []
                        },
                        "emdata:0": {
                            "id": 0,
                            "a_total_act_energy": meter_data['energy_forward'],
                            "a_total_act_ret_energy": meter_data['energy_reverse'],
                            "b_total_act_energy": 0.0,
                            "b_total_act_ret_energy": 0.0,
                            "c_total_act_energy": 0.0,
                            "c_total_act_ret_energy": 0.0,
                            "total_act": meter_data['energy_forward'],
                            "total_act_ret": meter_data['energy_reverse']
                        }
                    }
                }
            sock.sendto(json.dumps(response).encode('utf-8'), addr)
            logger.info(f"Sent Status to {addr}")
            
    except Exception as e:
        logger.error(f"Error handling UDP request: {e}")


def udp_server():
    """UDP server thread"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', UDP_PORT))
    
    logger.info(f"UDP server listening on port {UDP_PORT}")
    
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            handle_udp_request(data, addr, sock)
        except Exception as e:
            logger.error(f"UDP server error: {e}")


def http_server():
    """HTTP server thread"""
    server = HTTPServer(('0.0.0.0', HTTP_PORT), ShellyHTTPHandler)
    logger.info(f"HTTP server listening on port {HTTP_PORT}")
    server.serve_forever()


def meter_data_updater():
    """Meter data updater thread - reads from Venus OS D-Bus"""
    
    while True:
        update_meter_data()
        time.sleep(1)  # Update every second

def main():
    """Main entry point"""
    global meter_service
    
    logger.info("=" * 60)
    logger.info("Shelly Pro 3EM Emulator for Venus OS")
    logger.info("=" * 60)
    logger.info(f"Device ID: {DEVICE_ID}")
    logger.info(f"MAC: {MAC}")
    logger.info(f"Model: SPEM-003CEBEU120")
    logger.info(f"UDP Port: {UDP_PORT}")
    logger.info(f"HTTP Port: {HTTP_PORT}")
    logger.info(f"D-Bus: {'Available' if DBUS_AVAILABLE else 'Not available'}")
    logger.info("=" * 60)
    
    # Find meter service
    if DBUS_AVAILABLE:
        logger.info("Searching for Venus OS meter service...")
        meter_service = find_meter_service()
        if meter_service:
            logger.info(f"Using meter service: {meter_service}")
        else:
            logger.warning("No meter service found - using default values")
    else:
        logger.warning("D-Bus not available - using default values")
    
    logger.info("=" * 60)
      
    # Start threads
    udp_thread = threading.Thread(target=udp_server, daemon=True)
    udp_thread.start()
    
    http_thread = threading.Thread(target=http_server, daemon=True)
    http_thread.start()
    
    meter_thread = threading.Thread(target=meter_data_updater, daemon=True)
    meter_thread.start()
    
    logger.info("All services started successfully")
    if DBUS_AVAILABLE and meter_service:
        logger.info("Reading real-time data from Venus OS")
    else:
        logger.info("Using default values (230V, 0W)")
    logger.info("Press Ctrl+C to stop")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)


if __name__ == '__main__':
    main()