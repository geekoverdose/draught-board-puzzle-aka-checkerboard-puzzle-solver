from numpy import array, rot90, fliplr, array_equal
from checkerboardpuzzle_stone import Rotation

def generate_rotated_nparrays(nparray):
    """generate rotated and mirrored versions of given nparray."""
    r1 = rot90(nparray)
    r2 = rot90(r1)
    r3 = rot90(r2)
    f1 = fliplr(nparray)
    f2 = fliplr(r1)
    f3 = fliplr(r2)
    f4 = fliplr(r3)
    all_rot = [nparray,r1,r2,r3,f1,f2,f3,f4]
    return all_rot

def generate_rotations(fields):
    """generate all rotations of that stone."""
    #r1 = rot90(fields)
    #r2 = rot90(r1)
    #r3 = rot90(r2)
    #f1 = fliplr(fields)
    #f2 = fliplr(r1)
    #f3 = fliplr(r2)
    #f4 = fliplr(r3)
    #all_rot = [r1,r2,r3,f1,f2,f3,f4]
    all_rot = generate_rotated_nparrays(fields)
    # check if rotations are equal
    rotations = [] # [Rotation(fields)]
    for r_new in all_rot:
        l = len(filter(lambda r_old:array_equal(r_old.nparray,r_new), rotations))
        if l > 1:
            raise Exception('Rotations doubled? That should be impossible!')
        elif l == 0:
            # not in rotations yet, add
            rotations = rotations + [Rotation(r_new)]
    return rotations

def unique_nparrays(nparrays):
    """return unique list of nparrays."""
    unique = []
    for a in nparrays:
        for u in unique:
            if (a == u).all():
                break
        else:
            unique = unique + [a]
    return unique

def append_to_file(filepath, text):
    """append text to given file."""
    with open(filepath, 'a') as myfile:
        myfile.write(text)
        myfile.close()