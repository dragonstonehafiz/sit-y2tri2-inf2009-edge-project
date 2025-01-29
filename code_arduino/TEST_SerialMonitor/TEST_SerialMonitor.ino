// Testing controls using python serial messaging

const uint8_t laser1_pin = 2;
bool laser1_state = false;
const uint8_t laser2_pin = 4;
bool laser2_state = false;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(laser1_pin, OUTPUT);
  digitalWrite(laser1_pin, laser1_state); 
  pinMode(laser2_pin, OUTPUT);
  digitalWrite(laser2_pin, laser2_state); 
}

void loop() {
  // If there is data at the serial port
  if (Serial.available() > 0) {
    String msg = Serial.readString();

    if (msg == "laser1") {
      laser1_state = !laser1_state;
      digitalWrite(laser1_pin, laser1_state);
    }
    else if (msg == "laser2") {
      laser2_state = !laser2_state;
      digitalWrite(laser2_pin, laser2_state);
    }
  }
}
