import serial.tools.list_ports

if __name__ == "__main__":
    try:
        # Load Serial Instance
        serialInst = serial.Serial(port='COM4', baudrate=115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
        print(f"Serial Port is open: {serialInst.is_open}")
        
        while 1:
            command = input("Message to send (or quit): ")
            if (command == "quit"):
                break
            
            serialInst.write(command.encode("utf-8"))
    except Exception as e:
        print(f"Error: {e}")
        exit()
    
    