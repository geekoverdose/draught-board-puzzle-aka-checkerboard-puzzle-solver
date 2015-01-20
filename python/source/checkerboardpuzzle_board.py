from numpy import array, array_equal, ones
import itertools
import operator
import copy
from checkerboardpuzzle_statics import B, W, _, filled, colors, filled_factor, B_filled, W_filled, field_valid, field_invalid, colors
from checkerboardpuzzle_stone import Rotation, Stone
from checkerboardpuzzle_utils import generate_rotated_nparrays, unique_nparrays

class Board:
    def __init__(self, w, h, stones_free):
        self.parent = None # remembering search path
        self.w = w
        self.h = h
        self.stones_free = stones_free
        self.board = None
        self.stones_possible_placements = None
        self.fields_possible_fillings = None
        self.stones_placed = None

    def __copy__(self):
        other = Board(self.w, self.h, self.stones_free.copy())
        other.parent = self.parent
        other.board = self.board.copy()
        other.stones_possible_placements = copy.copy(self.stones_possible_placements)
        other.fields_possible_fillings = copy.copy(self.fields_possible_fillings)
        other.stones_placed = self.stones_placed.copy()
        return other       
           
    def __str__(self):
        top = '===' + ''.join(['===' for _ in range(len(self.board[0]))])
        s = '\n' + top + '\n'
        for row in self.board:
            s = s + '| ' + ' '.join(map(lambda x:'b ' if x == B 
                                        else 'w ' if x == W 
                                        else 'BX' if x == B_filled 
                                        else 'WX' if x == W_filled
                                        else '_ ', row)) + ' |\n'
        s = s + top + '\n'
        return s
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        # placed stones represent board: rotation, y, x
        if len(self.stones_placed) != len(other.stones_placed):
            return False
        for s in self.stones_placed:
            if not s in other.stones_placed:
                return False
        return True
    
    def __ne__(self, other):
        return not self.__eq__(other)
            
    def str_stones_individual(self):
        """str to represent individual stones instead of filling an b/w fields."""
        # generate board that represents stone numbers
        b = ones([len(self.board), len(self.board[0])]) * -1
        for p in self.stones_placed:
            for y in range(p[2], p[2] + len(p[1].nparray)):
                for x in range(p[3], p[3] + len(p[1].nparray[0])):
                    if p[1].nparray[y-p[2],x-p[3]] in colors:
                        if b[y,x] != -1:
                            raise Exception('not filled board found while printing solution:' + str(self))
                        b[y,x] = self.stones_placed[p]
        # generate string representation of that board
        top = '===' + ''.join(['====' for _ in range(len(self.board[0]))])
        s = '\n' + top + '\n'
        for r1,r2 in zip(b, self.board):
            row = zip(r1,r2)
            s = s + '| ' + ' '.join(map(lambda x:'{:2.0f}'.format(x[0]) + ('B' if x[1] == B_filled else 'W'), row)) + ' |\n'
        s = s + top + '\n'
        return s
    
    def initialize_empty_board(self):
        """initialized the first board = first node in the search tree. only call on that specific board."""
        self.generate_initial_board()
        self.stones_possible_placements = self.generate_initial_stone_placements() # 
        self.stones_placed = {} # map<(stone, rotation, y, x), nr>
        self.fields_possible_fillings = self.generate_initial_field_fillings()
                
    def generate_initial_board(self):
        """generate inital board. to be called on first node in search tree only."""
        self.board = array([[B if abs(x-y) % 2 == 0 else W for x in range(self.w)] for y in range(self.h)])
    
    def generate_initial_stone_placements(self):
        """generates all possible positions of stone rotations on the gameboard. to be called on first node in search tree only."""
        placements = []
        for stone in self.stones_free:
            for rotation in stone.rotations:
                #print self
                #print 'generating placement possibilities for rotation', rotation
                for y in range(self.h - len(rotation.nparray) + 1):
                    for x in range(self.w - len(rotation.nparray[0]) + 1):
                        #print 'generating pos y=' + str(y) + ', x=' + str(x)
                        if self.is_stone_placement_possible(rotation, y, x):
                            #print 'rotation and pos is possible.'
                            placements = placements + [(stone, rotation, y, x)]
        # print amount of possible placements per stone
        print 'generated', len(placements), 'possible stone placements in total.'
        return placements
    
    def generate_initial_field_fillings(self):
        """generate stats about which stones could fill which fields."""
        fields_possible_fillings = []
        for fieldY in range(len(self.board)):
            for fieldX in range(len(self.board[0])):
                for p in self.stones_possible_placements:
                    if self.is_field_fillable(fieldY, fieldX, *p):
                        fields_possible_fillings = fields_possible_fillings + [(fieldY, fieldX, p[0], p[1], p[2], p[3])]
        return fields_possible_fillings
    
    def is_field_fillable(self, fieldY, fieldX, stone, rotation, rotationY, rotationX):
        """check if this field can still be filled from self.stones_possible_placements."""
        if fieldY >= rotationY and fieldY < (rotationY + len(rotation.nparray)) and fieldX >= rotationX and fieldX < (rotationX + len(rotation.nparray[0])):
            # we're inside the stones possible placement rectangle
            # check if rotation would fill that field if placed on given y, x pos
            if rotation.nparray[fieldY-rotationY,fieldX-rotationX] in colors:
                return True
        return False
    
    def stone_placement_possibility_frequencies(self, index):
        """possible stone placements on board. index 0 is for stones, 1 is for rotations."""
        freq = {}
        for k in self.stones_possible_placements:
            if not k[index] in freq:
                freq[k[index]] = 1
            else:
                freq[k[index]] = freq[k[index]] + 1
        return freq
   
    def board_subset(self, y, x, h, w):
        """return subset of board with write access to board."""
        # TODO eventually do caching for speedup here
        return self.board[y:(y + h),
                          x:(x + w)]
    
    def is_stone_placement_possible(self, rotation, y, x):
        """check if placement of stone in given rotation is possible with this board."""
        board_subset = self.board_subset(y, x, len(rotation.nparray), len(rotation.nparray[0]))
        placement = board_subset + rotation.nparray
        #print placement
        for invalid in field_invalid:
            if invalid in placement:
                # leave and don't trigger else
                break
        else:
            # not invalid = valid
            return True
        return False
        
    def place_stone_on_board(self, stone, rotation, y, x):
        """place a stone in the given rotation on the board. removes it from the free stones, adds it to the placed stones. changes the board and the stone placment possibilities."""
        # decrease free stone count
        # check that stone placement possibilitiy exists
        # add to placed stones
        # modify board
        # check all stone placement possibilities and remove invalid ones
        #print 'placing stone', stone, '\nin rotation', rotation, '\nat y/x', y, '/', x
        key = (stone, rotation, y, x)
        # sanity check: possibility exists?
        if not key in self.stones_possible_placements:
            raise Exception('Trying to illplace a stone: combination not in stones_possible_placements.')
        # sanity check: stone in free stones?
        if not stone in self.stones_free:
            raise Exception('Stone is not in free stones.')
        # remove/decrease free stones count
        cnt = self.stones_free[stone]
        # sanity check: stone count is too low
        if cnt < 1:
            raise Exception('Empty stone placment possibility.')
        # remove stone placement possibility
        if cnt == 1:
            del self.stones_free[stone]
        else:
            self.stones_free[stone] = self.stones_free[stone] - 1
        # add to placed stones
        self.stones_placed[key] = len(self.stones_placed.keys())
        # sanity check: stone placement still possible?
        if not self.is_stone_placement_possible(rotation, y, x):
            raise Exception('Trying to place a rotation in a way that is no longer possible.')
        # modify board
        board_subset = self.board_subset(y, x, len(rotation.nparray), len(rotation.nparray[0]))
        for iy in range(len(rotation.nparray)):
            for ix in range(len(rotation.nparray[0])):
                if rotation.nparray[iy,ix] in colors:
                    # sanity check: this field must be free
                    if not board_subset[iy,ix] in colors:
                        raise Exception('Trying to fill position on board that is already filled.')
                    board_subset[iy,ix] = board_subset[iy,ix] * filled_factor
                    
        # update stone placement possibilities
        if cnt == 1:
            # remove all possibilities that corresponded to that stone
            self.stones_possible_placements = filter(lambda p:not p[0] == stone, self.stones_possible_placements)
        # remove placements not possible anymore due to now added stone
        self.stones_possible_placements = filter(lambda p:self.is_stone_placement_possible(*p[1:4]), self.stones_possible_placements)
        
        # update fields possible fillings
        self.fields_possible_fillings = self.generate_initial_field_fillings()
        #self.fields_possible_fillings = filter(lambda f:not f[2:] in placements_not_possible_anymore, self.fields_possible_fillings)
        # is that part even necessary?
        #self.fields_possible_fillings = filter(lambda f:self.is_field_fillable(*f), self.fields_possible_fillings)
        
    def fields_possible_fillings_freq(self):
        """return possible field filling frequency. O(n) runtime instead of O(n^2/2)."""
        freq = {}
        for f in self.fields_possible_fillings:
            k = f[0:2]
            if not k in freq:
                freq[k] = 1
            else:
                freq[k] = freq[k] + 1
        #print freq
        return freq
        
    def is_valid(self):
        """check if this board is valid = can yield valid solutions."""
        # check that each free stone can still be placed
        placements_stones = map(lambda p:p[0], self.stones_possible_placements)
        for stone in self.stones_free:
            if not stone in placements_stones:
                #print self, 'stone', stone, 'cannot be placed anymore.'
                return False
        # check that each free field can still be filled
        field_freq = self.fields_possible_fillings_freq()
        for y in range(len(self.board)):
            for x in range(len(self.board[0])):
                pos = (y,x)
                if not self.board[y,x] in filled:
                    if not pos in field_freq.keys():
                        #print self, 'field', pos, 'cannot be filled anymore.'
                        return False
        return True
    
    def is_solved(self):
        """check if this board is solved."""
        if len(self.stones_free) != 0:
            return False
        if 0 in self.board:
            raise Exception('No stones left to place, but still fields free on board: ' + str(self))
        return True

    def successors(self):
        """generate all useful successors from this board."""
        # find stone with least placement possibilities
        # choose biggest stone amongst those with least placement possibilities
        # if first stone: remove generated mirrored and rotated gameboards
        placement_freq = self.stone_placement_possibility_frequencies(0)
        # TODO if stones have equal amount of placement possibilities, choose bigger stone
        stone_min_placement_possibilities = min(placement_freq, key=placement_freq.get)
        print 'placing stone', stone_min_placement_possibilities
        #print stone_min_placement_possibilities
        keys = filter(lambda tup: tup[0] == stone_min_placement_possibilities, self.stones_possible_placements)
        successors = []
        all_rotations = [] # gets filled only if this is the first stone to be placed. is used to prevent mirrored/rotated start-boards from being generated.
        for key in keys:
            suc = copy.copy(self)
            suc.parent = self
            # place stone on board
            suc.place_stone_on_board(*key)
            if suc.is_valid():
                if not len(self.stones_placed) == 0:
                    # not first stone to be placed - just add
                    successors = successors + [suc]
                else:
                    # first stone to be placed: only generate subset of successors: no mirrored, not all quarters of board
                    print 'looking at suc nr', len(successors), 'rotationsize is', len(all_rotations), '...'
                    for r in all_rotations:
                        if (r == suc.board).all():
                            # is already in rotations, skip
                            print('already exists in rotations.')
                            break
                    else:
                        # is not yet in rotations, add all new rotations
                        rotated1 = unique_nparrays(generate_rotated_nparrays(suc.board))
                        rotated2 = []
                        for r1 in rotated1:
                            rotated2 = rotated2 + unique_nparrays(generate_rotated_nparrays(r1))
                        rotated2 = unique_nparrays(rotated2)
                        all_rotations = all_rotations + rotated2
                        # add successor too
                        successors = successors + [suc]
        return successors, len(keys)