import argparse
from helper.serial_helper import print_available_ports, is_port_available
from helper.arduino import ArduinoUNO

def main(serial_port: str):
    if not is_port_available(serial_port):
        print(f"Serial port {serial_port} is not available. Aborting.")
        return
    board = ArduinoUNO(serial_port)
    
    board.exit()

if __name__ == "__main__":
    # Command line arguments to decide which serial port to use
    parser = argparse.ArgumentParser(description="Serial Port Listing Example with PyFirmata")
    parser.add_argument('-ls', action='store_true', help="List available serial ports")
    parser.add_argument('-p', '--port', help="Serial port to connect to", required=True)
    args = parser.parse_args()
    if args.ls:
        print_available_ports()
        quit()
    else:
        main(args.port)