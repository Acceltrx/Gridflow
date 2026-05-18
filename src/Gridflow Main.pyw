import os
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Shared directories & files (AppData/Roaming/GridDash)
SHARED_DIR = os.path.join(os.environ['APPDATA'], 'GridFlow')
os.makedirs(SHARED_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(SHARED_DIR, 'gridflow_config.json')
SHARED_STATUS = os.path.join(SHARED_DIR, 'gridflow_status.json')

LOG_FILE = os.path.join(SHARED_DIR, 'debug_log.txt')

import logging
import re  
import webbrowser 

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.info("--- Script Startup ---")

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

# Default configuration dictionary
DEFAULT_CONFIG = {
  "settings": {
    "port": "COM5",
    "baud": 9600,
    "idle_timeout_seconds": 300,
    "grid_name": "Gridflow",
    "display_mode": 0
  },
  "custom_text": {
    "line_1": "Welcome to",
    "line_2": "Gridflow!"
  },
  "work_flow": {
    "mode_1": {
      "name": "Personal",
      "path1": "C:/Users/{YOUR_USER}/AppData/Local/Programs/Notion/Notion.exe",
      "url1": "https://mail.google.com/mail/u/1/#inbox",
      "url2": "https://www.youtube.com",
      "hotkey1": "Click(920, 1060)"
    },
    "mode_2": {
      "name": "Work",
      "path1": "C:/Users/{YOUR_USER}/AppData/Local/Programs/Opera GX/opera.exe",
      "url1": "https://github.com/",
      "combo1": ["win", "e"],
      "path2": "C:/Users/{YOUR_USER}/AppData/Local/Programs/Microsoft VS Code/Code.exe"
    },
    "mode_3": {
      "name": "School",
      "path1": "C:/Users/{YOUR_USER}/AppData/Roaming/Spotify/Spotify.exe",
      "url1": "https://classroom.google.com/"
    }
  },
  "keys": {
    "1": { "type": "app", "path": "C:/Path/To/Your/App.exe" },
    "2": { "none": {} },
    "3": { "none": {} },
    "4": { "none": {} },
    "5": { "none": {} },
    "6": { "none": {} },
    "7": { "type": "internal", "action": "work_flow", "mode": "mode_1" },
    "8": { "type": "internal", "action": "work_flow", "mode": "mode_2" },
    "9": { "type": "internal", "action": "work_flow", "mode": "mode_3" },
    "0": { "type": "combo", "keys": ["win", "d"] },
    "*": { "type": "internal", "action": "change_mode" },
    "#": { "type": "internal", "action": "send_message", "trigger": "t", "content": "Ready!" }
  }
}

last_config_mtime = 0
config = {}

def load_config():
    global last_config_mtime, config
    
    # Auto-generate if it doesn't exist
    if not os.path.exists(CONFIG_FILE):
        logging.warning(f"Config file not found. Generating default at: {CONFIG_FILE}")
        try:
            os.makedirs(SHARED_DIR, exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            config = DEFAULT_CONFIG
            last_config_mtime = os.path.getmtime(CONFIG_FILE)
            logging.info("Default config generated successfully.")
            return config
        except Exception as e:
            logging.error(f"Error creating default config: {e}")
            return DEFAULT_CONFIG

    # Load normally if it does exist
    try:
        current_mtime = os.path.getmtime(CONFIG_FILE)
        if current_mtime > last_config_mtime:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                new_data = json.load(f)
                if isinstance(new_data, dict):
                    config = new_data
                    last_config_mtime = current_mtime
                    logging.info("Config (re)loaded successfully.")
    except json.JSONDecodeError:
        # Happens if we try to read the file the exact millisecond the user is saving it
        pass
    except Exception as e:
        logging.error(f"Error loading config (using last valid version): {e}")
    
    return config if config else DEFAULT_CONFIG

config = load_config()

current_mode = config.get('settings', {}).get('display_mode', 0)
modes = ["TIME/DATE", "SYSTEM STATS", "STORAGE/NET", "MEDIA MODE", "CUSTOM TEXT"]
running = True
is_afk = False

# --- Shared status writer ---
def write_shared_status(connected=True, port=""):
    try:
        os.makedirs(SHARED_DIR, exist_ok=True)
        # Force utf-8 encoding and avoid special characters
        with open(SHARED_STATUS, 'w', encoding='utf-8') as f:
            json.dump({
                "connected": connected,
                "port": port,
                "display_mode": current_mode
            }, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to write shared status: {e}")

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

def get_idle_duration():
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
    millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
    return millis / 1000.0

def send_message(trigger_key, message_text):
    try:
        pyautogui.press(trigger_key) 
        time.sleep(0.1)              
        pyautogui.typewrite(message_text)
        pyautogui.press('enter')     
    except Exception as e:
        logging.error(f"Error in send_message: {e}")   

try:
    pynvml.nvmlInit()
    nvml_available = True
except:
    nvml_available = False

def execute_command(key_code, ser):
    current_conf = load_config() 
    key_configs = current_conf.get('keys', {})
    
    if key_code not in key_configs:
        try:
            ser.write(b"KT:none\n")
            ser.flush()
        except: pass
        return

    cmd = key_configs[key_code]
    cmd_type = cmd.get('type', 'unknown')
    
    try:
        ser.write(f"KT:{cmd_type}\n".encode())
        ser.flush()
    except Exception as e:
        logging.error(f"Failed to send KT feedback: {e}")

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

                # Save to Gridflow's own config
                try:
                    current_conf['settings']['display_mode'] = current_mode
                    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                        json.dump(current_conf, f, indent=2)
                    logging.info(f"Mode changed to: {modes[current_mode]}")
                except Exception as e:
                    logging.error(f"Failed to save display_mode: {e}")

                # Update shared status
                write_shared_status(connected=True, port=current_conf.get('settings', {}).get('port', 'COM5'))

            elif cmd['action'] == "send_message":
                trigger = cmd.get('trigger', 't')
                content = cmd.get('content', '')
                send_message(trigger, content)
            
            elif cmd['action'] == "work_flow":
                mode_id = cmd.get('mode') 
                workflow = current_conf.get('work_flow', {}).get(mode_id, {})
                logging.info(f"Triggering Workflow: {workflow.get('name', mode_id)}")
                
                for item_key, value in workflow.items():
                    if not value or item_key == "name":
                        continue
                    try:
                        if item_key.startswith("path"):
                            subprocess.Popen(value)
                        elif item_key.startswith("url"):
                            webbrowser.open(value)
                        elif item_key.startswith("combo"):
                            if isinstance(value, list):
                                pyautogui.hotkey(*value)
                            else:
                                logging.error(f"Combo error: {item_key} must be a list in config.json")
                        elif item_key.startswith("hotkey"):
                            if "Click" in value:
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
            logging.error(f"Listener loop error (Likely Disconnected): {e}")
            break # Thread will exit, triggering reconnect loop logic
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
        except Exception as e:
            logging.error(f"Telemetry error (Likely Disconnected): {e}")
            break # Thread will exit, triggering reconnect loop logic

def connection_manager():
    logging.info("Connection Manager started.")
    while running:
        current_conf = load_config()
        port = current_conf.get('settings', {}).get('port', 'COM5')
        baud = current_conf.get('settings', {}).get('baud', 9600)
        
        try:
            with serial.Serial(port, baud, timeout=1) as ser:
                logging.info(f"Connected to {port}")
                write_shared_status(connected=True, port=port)
                
                t1 = threading.Thread(target=arduino_listener, args=(ser,), daemon=True)
                t2 = threading.Thread(target=send_telemetry, args=(ser,), daemon=True)
                t1.start()
                t2.start()
                
                while running and t1.is_alive() and t2.is_alive():
                    # Watch for LIVE changes to the port in gridflow_config.json
                    dynamic_conf = load_config()
                    new_port = dynamic_conf.get('settings', {}).get('port', port)
                    
                    if new_port != port:
                        logging.info(f"Port changed in config from {port} to {new_port}. Reconnecting...")
                        break  # Breaks inner loop to close current serial and open the new one
                        
                    time.sleep(1)
                
                # If we leave the inner loop (e.g. threads crashed due to unplugging, or port changed)
                logging.warning("Connection loop exited naturally. Updating status.")
                write_shared_status(connected=False, port="")
                
        except serial.SerialException as e:
            # Reaches here if port e.g., 'COM2' isn't valid or is busy
            logging.warning(f"Could not connect to {port}. Retrying in 5s... ({e})")
            write_shared_status(connected=False, port="")
            # Small ticks so app exits fast if needed
            for _ in range(5):
                if not running: break
                time.sleep(1)
        except Exception as e:
            logging.error(f"Unexpected Serial Error: {e}")
            write_shared_status(connected=False, port="")
            time.sleep(5)

def get_tray_icon():
    if getattr(sys, 'frozen', False):
        base = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        icon_path = os.path.join(base, 'assets', 'Gridflow.ico')
    else:
        script_dir   = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        icon_path    = os.path.join(project_root, 'assets', 'Gridflow.ico')
    
    return Image.open(icon_path)

def quit_window(icon, item):
    global running
    running = False
    write_shared_status(connected=False, port="")  # clean up on exit
    icon.stop()
    logging.info("Application shutting down.")
    os._exit(0)

def main():
    threading.Thread(target=connection_manager, daemon=True).start()
    current_conf = load_config()
    hub_name = current_conf.get('settings', {}).get('grid_name', 'Gridflow')
    icon = pystray.Icon("Gridflow", get_tray_icon(), hub_name,
                        menu=pystray.Menu(pystray.MenuItem("Exit", quit_window)))
    icon.run()

if __name__ == "__main__":
    main()