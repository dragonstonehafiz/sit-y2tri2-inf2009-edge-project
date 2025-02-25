from helper.RaspberryPiZero2 import RaspberryPiZero2
import time

def help():
    help_message = """
Turret Scan Test
Commands:

    mode:<mode> - Set the mode of the turret 
        0: stationary
        1: scanning x
        2: scanning y
        3: scanning xy
        
        To leave this mode, press CTRL+C
        
    debug:<boolean> - Turn debug mode on or off (1 or 0)
    
    quit - Exit the program
    
    help - Display this message
"""
    print(help_message)
    
def turnX(board: RaspberryPiZero2, turnAmount=1, xTurningDir=True):
    if xTurningDir == True:
        board.turnServoX(turnAmount)
        if board.getServoXAngle() >= 180:
            xTurningDir = False
    else:
        board.turnServoX(-turnAmount)
        if board.getServoXAngle() <= 0:
            xTurningDir = True
    return xTurningDir

def turnY(board: RaspberryPiZero2, turnAmount=1, yTurningDir=True):
    print(board.getServoYAngle())
    if yTurningDir == True:
        board.turnServoY(turnAmount)
        if board.getServoYAngle() >= 135:
            yTurningDir = False
    else:
        board.turnServoY(-turnAmount)
        if board.getServoYAngle() <= 45:
            yTurningDir = True
    return yTurningDir

if __name__ == "__main__":
    board = RaspberryPiZero2()
    help()
    
    # Set the initial turning direction
    # True = +, False = -
    xTurningDir = True
    yTurningDir = True
    turnAmount = 10
    
    while True:
        action = input("Command: ")
        action = action.lower()
        
        if action == "help":
            help()
        elif action == "quit":
            break
        elif ":" in action:
            split_text = action.split(":")
            
            # Check if command is valid
            command = split_text[0]
            if command not in ["mode", "debug"]:
                print("Command invalid")
                continue
            
            # Make sure second part of command is a number
            try:
                mode = int(split_text[1])
            except Exception as e:
                print(f"error {e}")
                continue
            else:
                if mode in [0, 1, 2, 3] and command == "mode":
                    print("Press CTRL+C to exit mode")
                    while True:
                        time.sleep(0.25)
                        try:
                            if mode == 0:
                                pass
                            elif mode == 1:
                                xTurningDir = turnX(board, turnAmount=turnAmount, xTurningDir=xTurningDir)
                            elif mode == 2:
                                yTurningDir = turnY(board, turnAmount=turnAmount, yTurningDir=yTurningDir)
                            elif mode == 3:
                                xTurningDir = turnX(board, turnAmount=turnAmount, xTurningDir=xTurningDir)
                                yTurningDir = turnY(board, turnAmount=turnAmount, yTurningDir=yTurningDir)
                        except KeyboardInterrupt as e:
                            print("Leaving Scanning Mode")
                            break
                elif command == "debug":
                    board.setDebug(bool(mode))
                else:
                    print("Invalid Mode")
                

    board.cleanup()
