from helper.RaspberryPiZero2 import RaspberryPiZero2
import time

def help():
    help_message = """
Turret Scan Test
Commands:

    mode:<mode> - Set the mode of the turret (0: stationary, 1: scanning x, 2: scanning y, 3: scanning xy)
    
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
        board.turnServoX(-turnAmount)
        if board.getServoXAngle() <= 0:
            yTurningDir = True
    return yTurningDir

if __name__ == "__main__":
    board = RaspberryPiZero2()
    help()
    
    # Set the initial turning direction
    # True = +, False = -
    xTurningDir = True
    yTurningDir = True
    
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
                if mode == 0:
                    continue
                elif mode == 1:
                    xTurningDir = turnX(board, turnAmount=1, xTurningDir=xTurningDir)
                elif mode == 2:
                    yTurningDir = turnY(board, turnAmount=1, yTurningDir=yTurningDir)
                elif mode == 3:
                    xTurningDir = turnX(board, turnAmount=1, xTurningDir=xTurningDir)
                    yTurningDir = turnY(board, turnAmount=1, yTurningDir=yTurningDir)
                time.sleep(0.5)

   
    board.cleanup()
