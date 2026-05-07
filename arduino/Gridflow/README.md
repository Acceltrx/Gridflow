\*\*\*



\# 🔌 Gridflow Arduino Firmware



This folder contains the firmware for the Arduino hardware interface used in the \*\*Gridflow\*\* ecosystem.



\## 🛠 Hardware Wiring

Ensure your components are connected to the following pins on your Arduino Uno R3:



| Component | Arduino Pin |

| :--- | :--- |

| \*\*Keypad Rows\*\* | Pins 9, 8, 7, 6 |

| \*\*Keypad Columns\*\* | Pins 5, 4, 3, 2 |

| \*\*LCD (SDA)\*\* | A4 |

| \*\*LCD (SCL)\*\* | A5 |

| \*\*Buzzer\*\* | Pin 10 |



\## 🚀 Setup Instructions

1\. \*\*Library Installation:\*\*

&nbsp;  - Open your Arduino IDE.

&nbsp;  - Go to \*\*Sketch\*\* -> \*\*Include Library\*\* -> \*\*Manage Libraries...\*\*

&nbsp;  - Search for and install:

&nbsp;    - `LiquidCrystal I2C` (by Frank de Brabander)

&nbsp;    - `Keypad` (by Mark Stanley, Alexander Brevig)

2\. \*\*Upload:\*\*

&nbsp;  - Open `Gridflow.ino` in the Arduino IDE.

&nbsp;  - Select your board (\*\*Arduino Uno\*\*) and your \*\*COM Port\*\*.

&nbsp;  - Click \*\*Upload\*\*.

3\. \*\*Verification:\*\*

&nbsp;  - Once uploaded, open the Serial Monitor (set to 9600 Baud). 

&nbsp;  - You should see the startup tone and the LCD display "System: Online."



\*\*\*

