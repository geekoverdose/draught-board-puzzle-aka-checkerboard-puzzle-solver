from numpy import array, rot90, fliplr, array_equal
from checkerboardpuzzle_statics import B, W, _, B_filled, W_filled

class Rotation:
    """A specific rotation of a stone."""
    # TODO eventually derive from numpy.array instead of wrapping it (speedup)
    
    def __init__(self, nparray):
        self.nparray = nparray # a numpy.array
        
    def __str__(self):
        #return self.fields.__str__()
        top = '===' + ''.join(['==' for _ in range(len(self.nparray[0]))])
        s = '\n' + top + '\n'
        #s = s + '-----------\n'
        for row in self.nparray:
            s = s + '| ' + ' '.join(map(lambda x:'B' if x == B else 'W' if x == W else '_', row)) + ' |\n'
        s = s + top
        return s
    
    def __repr__(self):
        return self.__str__()