# Checkerboard puzzle solver implementation using depth first search, branch cutting and intelligent successor generation. Does not perfectly eliminate rotated and flipped solutions yet, bust most of them.
# Rainhard Findling
# 2015/01
#
import os
from checkerboardpuzzle_stone_loader import read_stones_from_file, stone_frequency
from checkerboardpuzzle_board import Board
from checkerboardpuzzle_utils import append_to_file

def main():
    solve('8x8_1.txt', [8,8])
      

def solve(stones_file, board_dim):
    # generate solution file, extend stone file path
    if not os.path.exists('../solutions/'):
        os.makedirs('../solutions/')
    solution_file = '../solutions/' + stones_file + '_solutions.txt'
    if os.path.isfile(solution_file):
        os.remove(solution_file)
    stones_file = '../stones/' + stones_file

    # generate board
    stones = read_stones_from_file(stones_file)
    freq = stone_frequency(stones)
    print freq
    board = Board(*board_dim, stones_free = freq)
    board.initialize_empty_board()
    print board
    print board.stone_placement_possibility_frequencies(0)

    # solve the board
    depth_first_search(board, solution_file)


def depth_first_search(board, solution_file):
    list_open = [board]
    list_closed = []
    solutions = []
    branchings_possible = []
    branchings_real = []
    while len(list_open) > 0:
        cur = list_open.pop()
        list_closed = list_closed + [cur]
        print 'looking at', cur, 'list_open', len(list_open), 'list_closed', len(list_closed)
        sucs, branching = cur.successors()
        branchings_possible = branchings_possible + [branching]
        branchings_real = branchings_real + [len(sucs)]
        print 'branching_possible', sum(branchings_possible)/float(len(branchings_possible)), 'branching_real', sum(branchings_real)/float(len(branchings_real))
        if len(sucs) == 0:
            print 'all suc. invalid, aborting.'
        for suc in sucs:
            if not suc in list_open and not suc in list_closed:
                if suc.is_solved():
                    print 'solution:\n', suc.str_stones_individual()
                    solutions = solutions + [suc]
                    list_closed = list_closed + [suc]
                    append_to_file(solution_file, suc.str_stones_individual())
                else:
                    list_open = list_open + [suc]
    print 'done. solutions:'
    for s in solutions:
        print s.str_stones_individual()
    print 'in total:', len(solutions)


if __name__ == '__main__':
    main()