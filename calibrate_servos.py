import argparse
from helper.RaspberryPiZero2 import RaspberryPiZero2

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
    

if __name__ == "__main__":
    board = RaspberryPiZero2()
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
                    board.setServoX(angle)
                elif servo == "y":
                    board.setServoY(angle)
                # elif servo == "laser1":
                #     board.write_laser1(angle)
                # elif servo == "laser2":
                #     board.write_laser2(angle)
   
    board.cleanup()
