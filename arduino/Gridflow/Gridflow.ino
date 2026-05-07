#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
#include <Keypad.h>

#define buzzerPin 10
#define NOTE_E6  1319
#define NOTE_G6  1568
#define NOTE_C7  2093
#define NOTE_C6  1047
#define NOTE_G5  784
#define NOTE_E5  659

LiquidCrystal_I2C lcd(0x27, 16, 2);

const byte ROWS = 4; 
const byte COLS = 4; 
char keys[ROWS][COLS] = {
  {'A','B','C','D'},
  {'3','6','9','#'},
  {'2','5','8','0'},
  {'1','4','7','*'}
};
byte rowPins[ROWS] = {9, 8, 7, 6}; 
byte colPins[COLS] = {5, 4, 3, 2}; 

Keypad keypad = Keypad( makeKeymap(keys), rowPins, colPins, ROWS, COLS );

unsigned long lastKeyPressTime = 0;
const unsigned long displayDuration = 2000; 
bool showingKey = false;
char currentKey = ' '; 

void setup() {
  pinMode(buzzerPin, OUTPUT);
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  
  lcd.setCursor(0, 0);
  lcd.print("Gridflow");
  lcd.setCursor(0, 1);
  lcd.print("System: Online");
  playStartupSound();
  delay(1500);
  lcd.clear();
}

void playStartupSound() {
  tone(buzzerPin, NOTE_E6, 80);
  delay(100);
  tone(buzzerPin, NOTE_G6, 80);
  delay(100);
  tone(buzzerPin, NOTE_C7, 150);
}

void playShutdownSound() {
  tone(buzzerPin, NOTE_C6, 100);
  delay(120);
  tone(buzzerPin, NOTE_G5, 100);
  delay(120);
  tone(buzzerPin, NOTE_E5, 200);
}

void loop() {
  char key = keypad.getKey();

  if (key) {
    lcd.backlight(); 
    currentKey = key; 
    
    if (key == '*') {
      Serial.println(key);
    } else {
      showingKey = true;
      lastKeyPressTime = millis();
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Key Pressed:");
      lcd.setCursor(0, 1);
      lcd.print("> ");
      lcd.print(key); 
      Serial.println(key);
    }
    tone(buzzerPin, 3000, 25);
  }

  if (showingKey && (millis() - lastKeyPressTime > displayDuration)) {
    showingKey = false;
    lcd.clear();
  }

  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    data.trim();
    
    if (data == "BL:0") {
      lcd.noBacklight();
      lcd.clear();
      playShutdownSound();
    } else if (data == "BL:1") {
      lcd.backlight();
      playStartupSound();
    } 
    
    else if (data.startsWith("KT:")) {
      if (showingKey) {
        String type = data.substring(3);
        lcd.setCursor(0, 1);
        lcd.print("> ");
        lcd.print(currentKey);
        lcd.print(" [");
        lcd.print(type);
        lcd.print("]    "); 
      }
    }
    else if (!showingKey) {
      if (data.startsWith("L1:")) {
        lcd.setCursor(0, 0);
        lcd.print(data.substring(3) + "                ");
      } else if (data.startsWith("L2:")) {
        lcd.setCursor(0, 1);
        lcd.print(data.substring(3) + "                ");
      }
    }
  }
}