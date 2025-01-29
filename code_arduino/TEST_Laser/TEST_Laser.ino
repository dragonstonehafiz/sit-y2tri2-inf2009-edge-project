// A simple program that alternates between two lasers every 0.5s

uint8_t laser1_pin = 2;
uint8_t laser2_pin = 4;

void setup() {
  pinMode(laser1_pin, OUTPUT);
  pinMode(laser2_pin, OUTPUT);
}

void loop() {
  digitalWrite(laser1_pin, HIGH);
  digitalWrite(laser2_pin, LOW);
  delay(500);
  
  digitalWrite(laser1_pin, LOW);
  digitalWrite(laser2_pin, HIGH);
  delay(500);
}