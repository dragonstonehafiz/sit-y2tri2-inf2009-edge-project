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
        time.sleep(2)
        print("Connected to board:", board)

        while True:
            board.digital[2].write(True)
            board.digital[4].write(True)
            time.sleep(0.5)
            board.digital[2].write(False)
            board.digital[4].write(False)
            time.sleep(0.5)

        board.exit()

if __name__ == "__main__":
    main()