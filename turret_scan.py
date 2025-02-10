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
    if yTurningDir == True:
        board.turnServoY(turnAmount)
        if board.getServoYAngle() >= 180:
            yTurningDir = False
    else:
        board.turnServoY(-turnAmount)
        if board.getServoYAngle() <= 0:
            yTurningDir = True
    return yTurningDir

if __name__ == "__main__":
    board = RaspberryPiZero2(debug=True)
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
            if command != "mode":
                print("Command invalid")
                continue
            
            # Make sure second part of command is a number
            try:
                mode = int(split_text[1])
            except Exception as e:
                print(f"error {e}")
                continue
            else:
                if mode in [0, 1, 2, 3]:
                    print("Press CTRL+C to exit mode")
                    while True:
                        try:
                            if mode == 0:
                                continue
                            elif mode == 1:
                                xTurningDir = turnX(board, turnAmount=turnAmount, xTurningDir=xTurningDir)
                            elif mode == 2:
                                yTurningDir = turnY(board, turnAmount=turnAmount, yTurningDir=yTurningDir)
                            elif mode == 3:
                                xTurningDir = turnX(board, turnAmount=turnAmount, xTurningDir=xTurningDir)
                                yTurningDir = turnY(board, turnAmount=turnAmount, yTurningDir=yTurningDir)
                            time.sleep(0.1)
                        except KeyboardInterrupt as e:
                            "Leaving Scanning Mode"
                            break
                else:
                    print("Invalid Mode")
                

    board.cleanup()
