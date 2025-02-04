"""
Interface for the Arduino UNO board using the pyfirmata2 library.
"""
import pyfirmata2
import time
            
class ArduinoUNO:
    class ServoData:
        _pin: pyfirmata2.pyfirmata2.Pin
        _value: int
        def __init__(self, pin: pyfirmata2.pyfirmata2.Pin):
            self._pin = pin
            self._value = 0
            
        def zero(self):
            self._pin.write(0)
            self._value = 0
            
        def write(self, value: int):
            self._pin.write(value)
            self._value = value

    _initialized: bool
    _board: pyfirmata2.Arduino
    _servoX: ServoData
    _servoY: ServoData
    _laser1Pin: pyfirmata2.pyfirmata2.Pin
    _laser2Pin: pyfirmata2.pyfirmata2.Pin
    
    def __init__(self, port: str):
        # Attempt connection. If fail, stop initialization.
        try:
            print(f"Connecting to serial port: {port}.")
            self._board = pyfirmata2.Arduino(port)
        except Exception as e:
            print("Failed to connect to board.")
            print(e)
            self._initialized = False
            return
        print("Connected to board.")
        self._initialized = True
        
        # Set up internal variables tracking each pin
        self._servoX = ArduinoUNO.ServoData(self._board.get_pin('d:6:s'))
        self._servoY = ArduinoUNO.ServoData(self._board.get_pin('d:8:s'))
        # Set servo turn amount to 0 degrees
        self._servoX.zero()
        self._servoY.zero()
        time.sleep(1)
        # Set up laser pins
        self._laser1Pin = self._board.get_pin('d:2:o')
        self._laser2Pin = self._board.get_pin('d:4:o')
        
        print("Board Initialized.")

    def exit(self):
        self.write_servo_x(0)
        time.sleep(0.5)
        self.write_servo_y(0)
        time.sleep(0.5)
        self.write_laser1(False)
        self.write_laser2(False)
        self._board.exit()

    def is_initialized(self) -> bool:
        return self._initialized
    
    def write_servo_x(self, value: int):
        self._servoX.write(value)
        
    def write_servo_y(self, value: int):
        self._servoY.write(value)
        
    def write_laser1(self, value: bool):
        self._laser1Pin.write(value)
        
    def write_laser2(self, value: bool):
        self._laser2Pin.write(value)