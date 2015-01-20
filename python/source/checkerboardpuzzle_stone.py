from numpy import sum
from checkerboardpuzzle_rotation import Rotation
from checkerboardpuzzle_utils import generate_rotations

class Stone:
    """A stone which knows all it's possible rotations."""
    
    def __init__(self, nparray):
        rotations = generate_rotations(nparray)
        self.rotations = rotations
        
    def __str__(self):
        return self.rotations[0].__str__()
    
    def __repr__(self):
        return self.__str__()
    
    def area(self):
        """amount of fields covered."""
        return sum(nparray != 0)