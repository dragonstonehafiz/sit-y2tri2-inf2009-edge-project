"""
For this file to work, you need to push the stabdard firmata sketch to the Arduino Uno board before running this code.
"""

import pyfirmata2
import argparse
import serial.tools.list_ports
import time

def list_serial_ports():
    """Lists available serial ports."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No serial ports found.")
    else:
        print("Available serial ports:")
        for port in ports:
            print(f"  {port.device} - {port.description}")
        

def main():
    parser = argparse.ArgumentParser(description="Serial Port Listing Example with PyFirmata")
    parser.add_argument('-ls', action='store_true', help="List available serial ports")
    parser.add_argument('-p', '--port', help="Serial port to connect to", required=True)

    args = parser.parse_args()

    if args.ls:
        list_serial_ports()
    else:
        print(f"Connecting to serial port: {args.port}.")
        board = pyfirmata2.Arduino(args.port)
        print("Connected to board:", board)
        
        servo1 = board.get_pin('d:6:s')
        servo2 = board.get_pin('d:8:s')
        servoVal = 0
        servoDir = True
        print("Zeroing servos")
        servo1.write(servoVal)
        servo2.write(servoVal)
        time.sleep(2)
        
        while True:
            board.digital[2].write(True)
            board.digital[4].write(True)
            time.sleep(0.5)
            board.digital[2].write(False)
            board.digital[4].write(False)
            time.sleep(0.5)
            
            if servoDir:
                servoVal += 20
            else:
                servoVal -= 20
            if (servoVal >= 180):
                servoVal = 180
                servoDir = not servoDir
            elif (servoVal <= 0):
                servoVal = 0
                servoDir = not servoDir
                
            print(servoVal)
            servo1.write(servoVal)
            servo2.write(servoVal)

        board.exit()

if __name__ == "__main__":
    main()