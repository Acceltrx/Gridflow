***

# ⚙️ Gridflow

<img width="862" height="367" alt="image" src="https://github.com/user-attachments/assets/72a75d77-29e8-4366-ab05-54793686f962" />

<br>

**Gridflow** is a high-performance, open-source productivity ecosystem that bridges physical tactile control with advanced Windows automation. Inspired by professional macro pads like the *Stream Deck*, Gridflow transforms a standard 4x4 matrix keypad and an I2C LCD into a context-aware command center for your desktop.

## 🚀 Key Features
*   **Workflow Orchestration:** Trigger complex sequences (opening multiple apps, URLs, and multi-key combos) with a single press.
*   **Real-Time Telemetry:** Monitor your CPU, RAM, GPU, Disk, and Network speeds directly on a 16x2 I2C LCD.
*   **Zero-UI Background Logic:** Runs efficiently in your System Tray with minimal resource impact (<1% CPU, <60MB RAM).
*   **Hot-Reloading:** Modify your `config.json` and see changes take effect instantly—no restarts required.
*   **AFK Awareness:** Automatically manages LCD backlighting based on user activity.

---

## ⌨️ Hardware Requirements
*   **Controller:** Arduino Uno R3
*   **Input:** 4x4 Matrix Keypad (Pins D2-D9)
*   **Output:** 16x2 I2C LCD Display (SDA to A4, SCL to A5)
*   **Optional:** 5V Passive Buzzer ([-] to D10)

| Component | Pin (Arduino) |
| :--- | :--- |
| Keypad Row 1 | 9 |
| Keypad Row 2 | 8 |
| Keypad Row 3 | 7 |
| Keypad Row 4 | 6 |
| Keypad Col 1 | 5 |
| Keypad Col 2 | 4 |
| Keypad Col 3 | 3 |
| Keypad Col 4 | 2 |
| LCD SDA | A4 |
| LCD SCL | A5 |

---

## ⚙️ Configuration Setup & References

1. **Initialize:** Copy `config.example.json` and rename it to `config.json`.
2. **Personalize:** Open `config.json` in your favorite editor.
    *   **Settings:** Update the `"port"` (e.g., `COM5`) to match your Arduino's serial port.
    *   **Paths:** Replace all `{YOUR_USER}` placeholders with your actual Windows username.
    *   **Customization:** Define your own Apps, URLs, and Workflows within the JSON structure.
3. **Launch:** Run `Gridflow Main.exe` (or `src/Gridflow Main.pyw` if using Python directly).

### Key Mappings (`"keys"`)
The `keys` object maps your physical keypad inputs to specific actions:
*   **App:** `{ "type": "app", "path": "C:/Path/To/App.exe" }`
*   **URL:** `{ "type": "url", "path": "https://google.com" }`
*   **Hotkey:** `{ "type": "hotkey", "action": "volumeup" }` (Supports standard `pyautogui` key names).
*   **Combo:** `{ "type": "combo", "keys": ["win", "shift", "s"] }`
*   **Internal:** 
    *   **Change Mode:** `{ "type": "internal", "action": "change_mode" }` (5 idle screen display modes: Clock, PC stats, disk/net monitor, media, custom text)
    *   **Send Text:** `{ "type": "internal", "action": "send_message", "trigger": "t", "content": "Hello from Gridflow!" }`
    *   **Trigger Workflow:** `{ "type": "internal", "action": "work_flow", "mode": "mode_1" }` (You can create more workflows as you go)

### Workflow Orchestration (`"work_flow"`)
Workflows allow you to execute multiple tasks with one trigger. Inside a mode (e.g., `mode_1`), use these prefixes:
*   `path[n]`: Launches an application.
*   `url[n]`: Opens a website.
*   `combo[n]`: Executes a key combination (must be a **list**, e.g., `["win", "e"]`).
*   `hotkey[n]`: Can be a standard key or `Click(X, Y)` for mouse automation.

**Example Structure:**
```json
"mode_1": {
  "name": "My Workflow",
  "path1": "C:/App/Example.exe",
  "url1": "https://github.com",
  "combo1": ["win", "d"],
  "hotkey1": "Click(500, 500)"
}
```

---

## 📋 Installation (Development)
If you are running from source, ensure you have Python 3.x installed:

```bash
# Clone the repository
git clone https://github.com/YourUsername/Gridflow.git

# Install dependencies
pip install -r requirements.txt

# Move config.json to src
# Run the application
python "src/Gridflow Main.pyw"
```

---

## 🛠 Deployment & Automation

### Compiling to Executable
If you prefer not to run the Python script manually, you can compile Gridflow into a standalone `.exe`:
1. Install `auto-py-to-exe`: `pip install auto-py-to-exe`
2. Run it by typing `auto-py-to-exe` in your terminal.
3. Select `src/Gridflow Main.pyw` as the script location.
4. **Icon:** In the "Icon" tab, select `assets/Gridflow_logo.ico`.
5. **Data:** In the "Additional Files" tab, link your `config.json`.
6. **Advanced:** Link your `version_info.txt` file for professional file properties.
7. Convert the project. Your executable will appear in the `output` folder.

### Launch on Startup
To have Gridflow launch automatically when you sign into Windows:
1. Press `Win + R`, type `shell:startup`, and hit **Enter**.
2. Create a **Shortcut** of your `Gridflow Main.exe`.
3. Drag and drop that shortcut into the Startup folder. Gridflow will now launch automatically on boot!

---

## 📸 Snapshots

_[Top View]_
<img width="901" height="407" alt="image" src="https://github.com/user-attachments/assets/32c22bb3-2b87-4a1a-ac88-c60c3ac402e8" />

---

_[Telemetry: Clock]_
<img width="600" height="581" alt="image" src="https://github.com/user-attachments/assets/80da6e41-b9fc-4027-9515-0f4137e98422" />

---

_[Telemetry: PC Stats]_
<img width="594" height="551" alt="image" src="https://github.com/user-attachments/assets/cc074e9f-09b9-490e-9d5e-44a9da1279cc" />
_[Limitation: GPU usage stats are only compatible to Nvidia graphics cards (Since the code uses pynvml)]_ <br>
_[Reminder: Update Nvidia graphics card to latest drivers to ensure function]_

---

_[Telemetry: Disk/Net Monitor]_
<img width="597" height="516" alt="image" src="https://github.com/user-attachments/assets/d84ed3b8-b31c-4061-8d55-218acb9ea243" />

---

_[Telemetry: Media]_
<img width="597" height="517" alt="image" src="https://github.com/user-attachments/assets/ad0abafd-e61f-457c-9fbe-496217fddc15" />

---

_[Telemetry: Custom Text]_
<img width="596" height="497" alt="image" src="https://github.com/user-attachments/assets/461a5b3b-2ad2-4020-8ab6-3254a5050332" />

---