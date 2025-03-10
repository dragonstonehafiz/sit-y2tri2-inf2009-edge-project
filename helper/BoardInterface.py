from abc import ABC, abstractmethod

class BoardInterface(ABC):
    @abstractmethod
    def get_servo_x(self):
        pass

    @abstractmethod
    def get_servo_y(self):
        pass

    @abstractmethod
    def set_servo_x(self, angle):
        pass

    @abstractmethod
    def turn_servo_x(self, angle):
        pass
        
    @abstractmethod
    def set_servo_y(self, angle):
        pass
        
    @abstractmethod
    def turn_servo_y(self, angle):
        pass
        
    @abstractmethod
    def set_laser(self, value):
        pass
        
    @abstractmethod
    def close(self):
        pass
