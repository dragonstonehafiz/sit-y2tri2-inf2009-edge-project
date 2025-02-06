import argparse
from helper.serial_helper import print_available_ports, is_port_available
from helper.arduino import ArduinoUNO

def help():
    help_message = """
Servo Calibration Tool
Commands:

    <servo>:<angle> - Set the angle of the servo
    <servo> - x or y
    <angle> - 0 to 180
    Example - x:180
    
    quit - Exit the program
    
    help - Display this message
"""
    print(help_message)
    
def main(serial_port: str):
    if not is_port_available(serial_port):
        print(f"Serial port {serial_port} is not available. Aborting.")
        return
    board = ArduinoUNO(serial_port)
    
    help()
    
    while True:
        action = input("Command: ")
        action = action.lower()
        
        if action == "help":
            help()
        elif action == "quit":
            break
        elif ":" in action:
            split_text = action.split(":")
            
            # Check if servo is valid
            servo = split_text[0]
            if servo not in ["x", "y", "laser1", "laser2"]:
                print("Invalid servo")
                continue
            
            # Compute angle part
            try:
                angle = int(split_text[1])
            except Exception as e:
                print(f"error {e}")
                continue
            else:
                if angle > 180:
                    angle = 180
                elif angle < 0:
                    angle = 0
                    
                # Turn Servo
                if servo == "x":
                    board.write_servo_x(angle)
                elif servo == "y":
                    board.write_servo_y(angle)
                elif servo == "laser1":
                    board.write_laser1(angle)
                elif servo == "laser2":
                    board.write_laser2(angle)
                          
    
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