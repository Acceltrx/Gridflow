***

# ⚙️ Gridflow

<img width="862" height="367" alt="image" src="https://github.com/user-attachments/assets/72a75d77-29e8-4366-ab05-54793686f962" />

<br>

**Gridflow** is a high-performance, open-source productivity ecosystem that bridges physical tactile control with advanced Windows automation. Inspired by professional macro pads like the *Stream Deck*, Gridflow transforms a standard 4x4 matrix keypad and an I2C LCD into a context-aware command center for your desktop.

## 🚀 Key Features
- **Workflow Orchestration:** Trigger complex sequences — opening multiple apps, URLs, and multi-key combos — with a single press.
- **Real-Time Telemetry:** Monitor your CPU, RAM, GPU, Disk, and Network speeds directly on a 16x2 I2C LCD.
- **Zero-UI Background Logic:** Runs efficiently in your system tray with minimal resource impact (<1% CPU, <60MB RAM).
- **Hot-Reloading:** Modify your `gridflow_config.json` and see changes take effect instantly — no restarts required.
- **AFK Awareness:** Automatically manages LCD backlighting based on user activity.
- **Ecosystem Ready:** Continuously syncs live telemetry and connection status with the **GridDash** HUD companion app.

---

## ⌨️ Hardware Requirements
- **Controller:** Arduino Uno R3
- **Input:** 4x4 Matrix Keypad (Pins D2–D9)
- **Output:** 16x2 I2C LCD Display (SDA → A4, SCL → A5)
- **Optional:** 5V Passive Buzzer ([-] to D10)

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

## ⚙️ Configuration & References

Gridflow is designed for zero-friction setup.

1. **Initialize:** Launch Gridflow. On first run, it automatically generates your default config at `%APPDATA%\GridFlow\gridflow_config.json`.
2. **Personalize:** Open that file in any text editor.
   - **Settings:** Set `"port"` (e.g. `COM5`) to match your Arduino's serial port.
   - **Paths:** Replace all `{YOUR_USER}` placeholders with your actual Windows username.
   - **Customization:** Define your own apps, URLs, and workflows within the JSON structure.

### Key Mappings (`"keys"`)
The `keys` object maps physical keypad inputs to actions:

- **App:** `{ "type": "app", "path": "C:/Path/To/App.exe" }`
- **URL:** `{ "type": "url", "path": "https://google.com" }`
- **Hotkey:** `{ "type": "hotkey", "action": "volumeup" }` — supports standard `pyautogui` key names.
- **Combo:** `{ "type": "combo", "keys": ["win", "shift", "s"] }`
- **Internal:**
  - **Change Mode:** `{ "type": "internal", "action": "change_mode" }` — cycles through 5 display modes: Clock, PC Stats, Disk/Net, Media, Custom Text.
  - **Send Text:** `{ "type": "internal", "action": "send_message", "trigger": "t", "content": "Hello from Gridflow!" }`
  - **Trigger Workflow:** `{ "type": "internal", "action": "work_flow", "mode": "mode_1" }` — add as many workflow modes as needed.

### Workflow Orchestration (`"work_flow"`)
Workflows let you execute multiple tasks from a single keypress. Inside each mode, use these key prefixes:

- `path[n]` — launches an application.
- `url[n]` — opens a URL in your default browser.
- `combo[n]` — executes a key combination (must be a list, e.g. `["win", "e"]`).
- `hotkey[n]` — a standard key name, or `Click(X, Y)` for mouse automation.

**Example:**
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

Requires Python 3.x.

```bash
# Clone the repository
git clone https://github.com/YourUsername/Gridflow.git
cd Gridflow

# Install dependencies
pip install -r requirements.txt

# Run the application
python "src/Gridflow Main.pyw"
```

---

## 🛠️ Deployment

### Compiling to a Standalone Executable

1. Install the compiler: `pip install auto-py-to-exe`
2. Launch it by running `auto-py-to-exe` in your terminal.
3. **Script Location:** Select `src/Gridflow Main.pyw`.
4. **Output:** Choose *Window Based (hide the console)*.
5. **Icon:** Select `assets/Gridflow.ico`.
6. **Additional Files:** Add the `assets` folder and map it to `assets` so the bundled executable can locate the icon at runtime.
7. **Version Info (Optional):** Link your `version_info.txt` for professional file properties.
8. Click **Convert .py to .exe**. The executable will appear in the `output` folder.

> **Note:** No config file needs to be bundled — Gridflow auto-generates it in `%APPDATA%` on first launch.

### Launch on Startup

1. Press `Win + R`, type `shell:startup`, and press **Enter**.
2. Create a shortcut to your compiled `Gridflow Main.exe`.
3. Move the shortcut into the Startup folder. Gridflow will now launch silently in your system tray on boot.

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

> GPU usage stats require an NVIDIA graphics card (pynvml). Ensure your NVIDIA drivers are up to date.

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