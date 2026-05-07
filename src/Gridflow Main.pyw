import os
import sys

# This handles the difference between running as a script and running as an EXE
if getattr(sys, 'frozen', False):
    # If running as an EXE, BASE_DIR is the folder where the EXE is located
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # If running as a normal .py script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
LOG_FILE = os.path.join(BASE_DIR, 'debug_log.txt')

import logging
import re  # Added for coordinate parsing
import webbrowser # Added for opening URLs

# --- 1. IMMEDIATE LOGGING SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'debug_log.txt')

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("--- Script Startup ---")

# --- 2. SECURE MODULE IMPORTS ---
try:
    import serial
    import time
    import psutil
    import pynvml 
    import pyautogui
    import threading
    import subprocess
    import asyncio
    import json
    import ctypes
    from datetime import datetime
    import pystray
    from PIL import Image, ImageDraw
    import winrt.windows.media.control as wmc
    logging.info("All modules loaded successfully.")
except ImportError as e:
    logging.error(f"CRITICAL: Missing library! {e}")
    sys.exit(1)
except Exception as e:
    logging.error(f"Unexpected error during import: {e}")
    sys.exit(1)

# --- 3. CONFIGURATION WITH HOT RELOAD ---
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
last_config_mtime = 0
config = {}

def load_config():
    global last_config_mtime, config
    if not os.path.exists(CONFIG_FILE):
        logging.error(f"Config file not found at: {CONFIG_FILE}")
        return config if config else {"settings": {}, "keys": {}}
    
    try:
        current_mtime = os.path.getmtime(CONFIG_FILE)
        if current_mtime > last_config_mtime:
            with open(CONFIG_FILE, 'r') as f:
                new_data = json.load(f)
                if isinstance(new_data, dict):
                    config = new_data
                    last_config_mtime = current_mtime
                    logging.info("Config (re)loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading config (using last valid version): {e}")
    
    return config

# Initial load
config = load_config()

current_mode = 0 
modes = ["TIME/DATE", "SYSTEM STATS", "STORAGE/NET", "MEDIA MODE", "CUSTOM TEXT"]
running = True
is_afk = False

# --- AFK DETECTION ---
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

def get_idle_duration():
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
    millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
    return millis / 1000.0

# --- CUSTOM INTERNAL COMMANDS ---
def send_message(trigger_key, message_text):
    try:
        pyautogui.press(trigger_key) 
        time.sleep(0.1)              
        pyautogui.typewrite(message_text)
        pyautogui.press('enter')     
    except Exception as e:
        logging.error(f"Error in send_message: {e}")   

# GPU Check
try:
    pynvml.nvmlInit()
    nvml_available = True
except:
    nvml_available = False

# --- LOGIC ---
def execute_command(key_code, ser):
    """Processes keypress and sends the command type back to Arduino"""
    current_conf = load_config() 
    key_configs = current_conf.get('keys', {})
    
    # If the key isn't in config, tell Arduino it's unmapped
    if key_code not in key_configs:
        try:
            ser.write(b"KT:none\n")
            ser.flush()
        except: pass
        return

    cmd = key_configs[key_code]
    cmd_type = cmd.get('type', 'unknown')
    
    # Send the type back to the Arduino to be displayed: KT:[type]
    try:
        ser.write(f"KT:{cmd_type}\n".encode())
        ser.flush()
    except Exception as e:
        logging.error(f"Failed to send KT feedback: {e}")

    # Execute the actual action
    try:
        if cmd_type == "app": 
            subprocess.Popen(cmd['path'])
        elif cmd_type == "url":
            webbrowser.open(cmd['path'])
        elif cmd_type == "hotkey": 
            pyautogui.press(cmd['action'])
        elif cmd_type == "combo": 
            pyautogui.hotkey(*cmd['keys'])
        elif cmd_type == "internal":
            if cmd['action'] == "change_mode":
                global current_mode
                current_mode = (current_mode + 1) % len(modes)
            
            elif cmd['action'] == "send_message":
                trigger = cmd.get('trigger', 't')
                content = cmd.get('content', '')
                send_message(trigger, content)
            
            elif cmd['action'] == "work_flow":
                mode_id = cmd.get('mode') # e.g. "mode_1"
                workflow = current_conf.get('work_flow', {}).get(mode_id, {})
                
                logging.info(f"Triggering Workflow: {workflow.get('name', mode_id)}")
                
                # Iterate through all items in the chosen workflow mode
                for item_key, value in workflow.items():
                    if not value or item_key == "name":
                        continue
                    
                    try:
                        # 1. Handle Apps (Paths)
                        if item_key.startswith("path"):
                            subprocess.Popen(value)
                        
                        # 2. Handle Websites (URLs)
                        elif item_key.startswith("url"):
                            webbrowser.open(value)

                        # 3. Handle Key Combos
                        elif item_key.startswith("combo"):
                            if isinstance(value, list):
                                # The * unpacks the list ["win", "e"] into pyautogui.hotkey("win", "e")
                                pyautogui.hotkey(*value)
                            else:
                                logging.error(f"Combo error: {item_key} must be a list in config.json")
                        
                        # 4. Handle Hotkeys / Clicks
                        elif item_key.startswith("hotkey"):
                            if "Click" in value:
                                # Extract numbers from Click(900, 1060)
                                coords = re.findall(r'\d+', value)
                                if len(coords) == 2:
                                    pyautogui.click(int(coords[0]), int(coords[1]))
                            else:
                                pyautogui.press(value)
                    except Exception as item_err:
                        logging.error(f"Workflow item error ({item_key}): {item_err}")

    except Exception as e:
        logging.error(f"Action execution error ({key_code}): {e}")

async def get_media_info():
    try:
        manager = await wmc.GlobalSystemMediaTransportControlsSessionManager.request_async()
        session = manager.get_current_session()
        if session:
            props = await session.try_get_media_properties_async()
            return f"{props.artist} - {props.title}"[:16] 
        return "No Media Playing"
    except: return "Media: Idle"

def arduino_listener(ser):
    while running:
        try:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                if data:
                    execute_command(data, ser)
        except Exception as e:
            logging.error(f"Listener loop error: {e}")
            break
        time.sleep(0.01)

def send_telemetry(ser):
    global is_afk
    while running:
        try:
            current_conf = load_config() 
            settings = current_conf.get('settings', {})
            custom_text = current_conf.get('custom_text', {})
            threshold = settings.get('idle_timeout_seconds', 300)
            
            idle_time = get_idle_duration()
            if idle_time > threshold and not is_afk:
                ser.write(b"BL:0\n")
                ser.flush()
                is_afk = True
            elif idle_time < threshold and is_afk:
                ser.write(b"BL:1\n")
                ser.flush()
                is_afk = False

            if not is_afk:
                if current_mode == 0: 
                    now = datetime.now()
                    ser.write(f"L1:{now.strftime('%a, %b %d')}\n".encode())
                    ser.write(f"L2:{now.strftime('%I:%M:%S %p')}\n".encode())
                elif current_mode == 1: 
                    cpu = psutil.cpu_percent()
                    ram = psutil.virtual_memory().percent
                    gpu_load = 0
                    if nvml_available:
                        try:
                            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                            res = pynvml.nvmlDeviceGetUtilizationRates(handle)
                            gpu_load = res.gpu
                        except: gpu_load = 0
                    ser.write(f"L1:C:{cpu:.1f}% R:{ram:.1f}%\n".encode())
                    ser.write(f"L2:G:{gpu_load:.1f}%\n".encode())
                elif current_mode == 2: 
                    disk = psutil.disk_usage('C:')
                    net_1 = psutil.net_io_counters().bytes_recv
                    time.sleep(0.1) 
                    net_2 = psutil.net_io_counters().bytes_recv
                    speed = (net_2 - net_1) / 1024 / 0.1 
                    ser.write(f"L1:Disk C: {disk.percent}%\n".encode())
                    ser.write(f"L2:Net: {speed:.1f} KB/s\n".encode())
                elif current_mode == 3: 
                    song_title = asyncio.run(get_media_info())
                    ser.write(f"L1:Now Playing:\n".encode())
                    ser.write(f"L2:{song_title}\n".encode())
                elif current_mode == 4:
                    line1 = custom_text.get('line_1', '')
                    line2 = custom_text.get('line_2', '')
                    ser.write(f"L1:{line1}\n".encode())
                    ser.write(f"L2:{line2}\n".encode())
            time.sleep(1) 
        except: break

# --- CONNECTION & TRAY ---
def connection_manager():
    logging.info("Connection Manager started.")
    while running:
        current_conf = load_config()
        settings = current_conf.get('settings', {})
        port = settings.get('port', 'COM5')
        baud = settings.get('baud', 9600)
        
        try:
            with serial.Serial(port, baud, timeout=1) as ser:
                logging.info(f"Connected to {port}")
                t1 = threading.Thread(target=arduino_listener, args=(ser,), daemon=True)
                t2 = threading.Thread(target=send_telemetry, args=(ser,), daemon=True)
                t1.start()
                t2.start()
                while running and t1.is_alive() and t2.is_alive():
                    time.sleep(1)
        except Exception as e:
            logging.error(f"Serial Error on {port}: {e}. Retrying in 10s...")
            time.sleep(10)

def create_image():
    image = Image.new('RGB', (64, 64), color=(30, 144, 255))
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 16, 48, 48), fill=(255, 255, 255))
    return image

def quit_window(icon, item):
    global running
    running = False
    icon.stop()
    logging.info("Application shutting down.")
    os._exit(0)

def main():
    threading.Thread(target=connection_manager, daemon=True).start()
    current_conf = load_config()
    hub_name = current_conf.get('settings', {}).get('grid_name', 'Gridflow')
    icon = pystray.Icon("Gridflow", create_image(), hub_name, 
                        menu=pystray.Menu(pystray.MenuItem("Exit", quit_window)))
    icon.run()

if __name__ == "__main__":
    main()