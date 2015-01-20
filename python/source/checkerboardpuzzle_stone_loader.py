from numpy import array, array_equal
from checkerboardpuzzle_statics import B, W, _, B_filled, W_filled
from checkerboardpuzzle_stone import Rotation, Stone

def read_stones_from_file(filepath):
    """reades stones from a textfile."""
    f = open(filepath, 'r')
    stones = []
    stoneid = 0 # stoneid 
    w = -1 # width must be the same per stone
    h = -1 # start height = -1
    rows = []
    for line in f.read().splitlines():
        if '=' in line:
            #print 'separator line, creating stone', stoneid
            fields = array(rows)
            #print fields
            #print 'dimensions: x=' + str(len(fields[0])) + ', y=' + str(len(fields))
            stone = Stone(fields)
            stones = stones + [stone]
            # reset stuff
            rows = []
            h = -1
            w = -1
            stoneid = stoneid + 1
        else:
            h = h + 1
            #print 'working on stone', stoneid, 'line', h, 'now.'
            values = line.split(',')
            if w == -1:
                w = len(values)
            elif w != len(values):
                raise Exception('nr. of columns differ amongst rows for at least one stone .')
            values = map(lambda x:B if x == 'B' else W if x == 'W' else _, values)
            rows = rows = rows + [values]
    f.close()
    return stones
    
def stone_frequency(stones):
    """Create map of stones and their frequency - to find out doubled stones."""
    freq = {}
    for s_new in stones:
        for s_old in freq:
            for r_new in s_new.rotations:
                for r_old in s_old.rotations:
                    #print 'comparing', r_new, 'and', r_old
                    if array_equal(r_new.nparray, r_old.nparray):
                        freq[s_old] = freq[s_old] + 1
                        break
                else:
                    continue
                break
            else:
                continue
            break
        else:
            # no match!
            freq[s_new] = 1
    return freq