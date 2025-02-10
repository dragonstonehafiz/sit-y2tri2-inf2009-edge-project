from helper.RaspberryPiZero2 import RaspberryPiZero2

def help():
    help_message = """
Servo Calibration Tool
Commands:

    setx:<angle> - Set the x servo to the specified angle (+)
    turnx:<angle> - Turn the x servo by the specified angle (+-)
    sety:<angle> - Set the y servo to the specified angle (+)
    turny:<angle> - Turn the y servo by the specified angle (+-)
    laser:<boolean> - Turn the laser on or off (1 or 0)
    debug:<boolean> - Turn debug mode on or off (1 or 0)
    
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
            if servo not in ["setx", "turnx", "turny", "sety", "laser"]:
                print("Invalid Pin")
                continue
            
            # Compute angle part
            try:
                angle = int(split_text[1])
            except Exception as e:
                print(f"error {e}")
                continue
            else:
                # Turn Servo
                if servo == "setx":
                    board.setServoX(angle)
                elif servo == "turnx":
                    board.turnServoX(angle)
                elif servo == "sety":
                    board.setServoY(angle)
                elif servo == "turny":
                    board.turnServoY(angle)
                elif servo == "laser":
                    board.setLaser(bool(angle))
                elif servo == "debug":
                    board.setDebug(bool(angle))
   
    board.cleanup()
