import serial.tools.list_ports

def get_available_ports() -> list:
    """
    Gets a list of available serial ports.
    """
    ports = serial.tools.list_ports.comports()
    return ports

def print_available_ports() -> None:
    """
    Prints all available serial ports.
    """
    ports = get_available_ports()
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No serial ports found.")
    else:
        for port in ports:
            print(f"  {port.device} - {port.description}")
            
def is_port_available(port: str) -> bool:
    """Checks if the provided serial port is available to be used.

    Args:
        port (str): The port to check.

    Returns:
        bool: Boolean for if the port is available.
    """
    ports = get_available_ports()
    for p in ports:
        if p.device == port:
            return True
    return False