from copy import deepcopy
from heapq import heappush, heappop
import time
import argparse
import sys

#====================================================================================

char_goal = '1'
char_single = '2'

class Piece:
    """
    This represents a piece on the Hua Rong Dao puzzle.
    """

    def __init__(self, is_goal, is_single, coord_x, coord_y, orientation):
        """
        :param is_goal: True if the piece is the goal piece and False otherwise.
        :type is_goal: bool
        :param is_single: True if this piece is a 1x1 piece and False otherwise.
        :type is_single: bool
        :param coord_x: The x coordinate of the top left corner of the piece.
        :type coord_x: int
        :param coord_y: The y coordinate of the top left corner of the piece.
        :type coord_y: int
        :param orientation: The orientation of the piece (one of 'h' or 'v') 
            if the piece is a 1x2 piece. Otherwise, this is None
        :type orientation: str
        """

        self.is_goal = is_goal
        self.is_single = is_single
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.orientation = orientation


    def __repr__(self):
        return '{} {} {} {} {}'.format(self.is_goal, self.is_single, \
            self.coord_x, self.coord_y, self.orientation)
    

    def move(self, direction):
        """
        Move the piece one step in the direction of the orientation.
        """
            
        if direction == 'up':
            self.coord_y -= 1
        elif direction == 'down':
            self.coord_y += 1
        elif direction == 'left':
            self.coord_x -= 1
        elif direction == 'right':
            self.coord_x += 1




class Board:
    """
    Board class for setting up the playing board.
    """

    def __init__(self, pieces):
        """
        :param pieces: The list of Pieces
        :type pieces: List[Piece]
        """

        self.width = 4
        self.height = 5

        self.pieces = pieces

        # self.grid is a 2-d (size * size) array automatically generated
        # using the information on the pieces when a board is being created.
        # A grid contains the symbol for representing the pieces on the board.
        self.grid = []
        self.__construct_grid()


    def __construct_grid(self):
        """
        Called in __init__ to set up a 2-d grid based on the piece location information.

        """

        for i in range(self.height):
            line = []
            for j in range(self.width):
                line.append('.')
            self.grid.append(line)


        # print(self.pieces)
        # print('\n')
        for piece in self.pieces:
            if piece.is_goal:
                self.grid[piece.coord_y][piece.coord_x] = char_goal
                self.grid[piece.coord_y][piece.coord_x + 1] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x + 1] = char_goal
            elif piece.is_single:
                self.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                if piece.orientation == 'h':
                    self.grid[piece.coord_y][piece.coord_x] = '<'
                    self.grid[piece.coord_y][piece.coord_x + 1] = '>'
                elif piece.orientation == 'v':
                    self.grid[piece.coord_y][piece.coord_x] = '^'
                    self.grid[piece.coord_y + 1][piece.coord_x] = 'v'

    def display(self):
        """
        Print out the current board.

        """
        for i, line in enumerate(self.grid):
            for ch in line:
                print(ch, end='')
            print()

    def display_string(self):
        """
        Return the current board as a string.
        """
        s = ''
        for i, line in enumerate(self.grid):
            for ch in line:
                s += ch
            s += '\n'

        return s[:-1]




    def findempty(self):
        """
        Find the empty space on the board.

        :return: A tuple of the x and y coordinate of the empty space.
        :rtype: list(Tuple[int, int])
        """

        l = []
        for i, line in enumerate(self.grid):
            for j, ch in enumerate(line):
                if ch == '.':
                    l.append((j, i))
        return l

    def goal_check(self):
        """
        Check if the current board is the goal board.

        :return: True if the current board is the goal board and False otherwise.
        :rtype: bool
        """

        if self.grid[3][1] == char_goal and self.grid[3][2] == char_goal \
            and self.grid[4][1] == char_goal and self.grid[4][2] == char_goal:
            return True
        return False


    def manhattan(self):
        """
        Calculate the manhattan distance of the current board.

        :return: The manhattan distance of the current board.
        :rtype: int
        """

        dist = 0
        for i in self.pieces:
            if i.is_goal:
                dist += abs(i.coord_x - 1) + abs(i.coord_y - 3)
        return dist
            


class State:
    """
    State class wrapping a Board with some extra current state information.
    Note that State and Board are different. Board has the locations of the pieces. 
    State has a Board and some extra information that is relevant to the search: 
    heuristic function, f value, current depth and parent.
    """

    def __init__(self, board, f, depth, parent=None):
        """
        :param board: The board of the state.
        :type board: Board
        :param f: The f value of current state.
        :type f: int
        :param depth: The depth of current state in the search tree.
        :type depth: int
        :param parent: The parent of current state.
        :type parent: Optional[State]
        """
        self.board = board
        self.f = f
        self.depth = depth
        self.parent = parent
        self.id = hash(board)  # The id for breaking ties.
    
    # def expand(self):
    #     """
    #     Expand the current state and return a list of new states.
    #     """

    


    def available_moves(self):
        """
        Find the available moves for the current state.

        :return: A list of available moves.
        :rtype: List[states]
        """

        empty = self.board.findempty()
        new_states = []

        
        
        p = self.board.pieces
        for ind, i in enumerate(p):
            # print("inside\n\n")
            # self.board.display()
            # print("again\n\n")
            
            # print(copy)
            # print(i)
            # print('\n')
            
            #check if piece can move on board into empty space
            if i.is_goal == True:
                #up
                if i.coord_y - 1 >= 0:
                    if self.board.grid[i.coord_y - 1][i.coord_x] == '.' and \
                            self.board.grid[i.coord_y - 1][i.coord_x + 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('up')
                        new_states.append(State(Board(copy_list), self.f, self.depth + 1, self))
                #down
                if i.coord_y + 2 <= 4:
                    if self.board.grid[i.coord_y + 2][i.coord_x] == '.' and \
                            self.board.grid[i.coord_y + 2][i.coord_x + 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('down')
                        new_states.append(State(Board(copy_list), self.f, self.depth + 1, self))

                #left
                if i.coord_x - 1 >= 0:
                    if self.board.grid[i.coord_y][i.coord_x - 1] == '.' and \
                            self.board.grid[i.coord_y + 1][i.coord_x - 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('left')
                        new_states.append(State(Board(copy_list), self.f, self.depth + 1, self))

                #right
                if i.coord_x + 2 <= 3:
                    if self.board.grid[i.coord_y][i.coord_x + 2] == '.' and \
                            self.board.grid[i.coord_y + 1][i.coord_x + 2] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('right')
                        new_states.append(State(Board(copy_list), self.f, self.depth + 1, self))
            


            if i.is_single:
                #up
                if i.coord_y - 1 >= 0:
                    if self.board.grid[i.coord_y - 1][i.coord_x] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('up')
                        new_states.append(State(Board(copy_list), self.f, self.depth + 1, self))
                #down
                if i.coord_y + 1 <= 4:
                    if self.board.grid[i.coord_y + 1][i.coord_x] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('down')
                        new_states.append(State(Board(copy_list), self.f, self.depth + 1, self))

                #left
                if i.coord_x - 1 >= 0:
                    if self.board.grid[i.coord_y][i.coord_x - 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('left')
                        new_states.append(State(Board(copy_list), self.f, self.depth + 1, self))

                #right
                if i.coord_x + 1 <= 3:
                    if self.board.grid[i.coord_y][i.coord_x + 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('right')
                        new_states.append(State(Board(copy_list), self.f, self.depth + 1, self))
                



            if i.orientation == 'h':
                #up
                if i.coord_y - 1 >= 0:
                    if self.board.grid[i.coord_y - 1][i.coord_x] == '.' and \
                            self.board.grid[i.coord_y - 1][i.coord_x + 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('up')
                        new_states.append(State(Board(copy_list), self.f, self.depth + 1, self))

                #down
                if i.coord_y + 1 <= 4:
                    if self.board.grid[i.coord_y + 1][i.coord_x] == '.' and \
                            self.board.grid[i.coord_y + 1][i.coord_x + 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('down')
                        new_states.append(State(Board(copy_list), self.f, self.depth + 1, self))
                #left
                if i.coord_x - 1 >= 0:
                    if self.board.grid[i.coord_y][i.coord_x - 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('left')
                        new_states.append(State(Board(copy_list), self.f, self.depth + 1, self))
                #right
                if i.coord_x + 2 <= 3:
                    if self.board.grid[i.coord_y][i.coord_x + 2] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('right')
                        new_states.append(State(Board(copy_list), self.f, self.depth + 1, self))
            


            if i.orientation == 'v':
                #up
                if i.coord_y - 1 >= 0:
                    if self.board.grid[i.coord_y - 1][i.coord_x] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('up')
                        new_states.append(State(Board(copy_list), self.f, self.depth + 1, self))
                #down
                if i.coord_y + 2 <= 4:
                    if self.board.grid[i.coord_y + 2][i.coord_x] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('down')
                        new_states.append(State(Board(copy_list), self.f, self.depth + 1, self))
                #left
                if i.coord_x - 1 >= 0:
                    if self.board.grid[i.coord_y][i.coord_x - 1] == '.' and \
                            self.board.grid[i.coord_y + 1][i.coord_x - 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('left')
                        new_states.append(State(Board(copy_list), self.f, self.depth + 1, self))
                #right
                if i.coord_x + 1 <= 3:
                    if self.board.grid[i.coord_y][i.coord_x + 1] == '.' and \
                            self.board.grid[i.coord_y + 1][i.coord_x + 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('right')
                        new_states.append(State(Board(copy_list), self.f, self.depth + 1, self))


        # print('\nnewstates\n')
        # print(new_states)
        return new_states

    

    def available_moves_manhattan(self):
        """
        Find the available moves for the current state.

        :return: A list of available moves.
        :rtype: List[states]
        """

        empty = self.board.findempty()
        new_states = []

        
        
        
        p = self.board.pieces
        for ind, i in enumerate(p):

            #check if piece can move on board into empty space
            if i.is_goal == True:
                #up
                if i.coord_y - 1 >= 0:
                    if self.board.grid[i.coord_y - 1][i.coord_x] == '.' and \
                            self.board.grid[i.coord_y - 1][i.coord_x + 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('up')
                        new_board = Board(copy_list)
                        new_states.append(State(new_board, self.depth + new_board.manhattan() , self.depth + 1, self))
                #down
                if i.coord_y + 2 <= 4:
                    if self.board.grid[i.coord_y + 2][i.coord_x] == '.' and \
                            self.board.grid[i.coord_y + 2][i.coord_x + 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('down')
                        new_board = Board(copy_list)
                        new_states.append(State(new_board, self.depth + new_board.manhattan() , self.depth + 1, self))

                #left
                if i.coord_x - 1 >= 0:
                    if self.board.grid[i.coord_y][i.coord_x - 1] == '.' and \
                            self.board.grid[i.coord_y + 1][i.coord_x - 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('left')
                        new_board = Board(copy_list)
                        new_states.append(State(new_board, self.depth + new_board.manhattan() , self.depth + 1, self))

                #right
                if i.coord_x + 2 <= 3:
                    if self.board.grid[i.coord_y][i.coord_x + 2] == '.' and \
                            self.board.grid[i.coord_y + 1][i.coord_x + 2] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('right')
                        new_board = Board(copy_list)
                        new_states.append(State(new_board, self.depth + new_board.manhattan() , self.depth + 1, self))
            


            if i.is_single:
                #up
                if i.coord_y - 1 >= 0:
                    if self.board.grid[i.coord_y - 1][i.coord_x] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('up')
                        new_board = Board(copy_list)
                        new_states.append(State(new_board, self.depth + new_board.manhattan() , self.depth + 1, self))
                #down
                if i.coord_y + 1 <= 4:
                    if self.board.grid[i.coord_y + 1][i.coord_x] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('down')
                        new_board = Board(copy_list)
                        new_states.append(State(new_board, self.depth + new_board.manhattan() , self.depth + 1, self))

                #left
                if i.coord_x - 1 >= 0:
                    if self.board.grid[i.coord_y][i.coord_x - 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('left')
                        new_board = Board(copy_list)
                        new_states.append(State(new_board, self.depth + new_board.manhattan() , self.depth + 1, self))

                #right
                if i.coord_x + 1 <= 3:
                    if self.board.grid[i.coord_y][i.coord_x + 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('right')
                        new_board = Board(copy_list)
                        new_states.append(State(new_board, self.depth + new_board.manhattan() , self.depth + 1, self))
                



            if i.orientation == 'h':
                #up
                if i.coord_y - 1 >= 0:
                    if self.board.grid[i.coord_y - 1][i.coord_x] == '.' and \
                            self.board.grid[i.coord_y - 1][i.coord_x + 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('up')
                        new_board = Board(copy_list)
                        new_states.append(State(new_board, self.depth + new_board.manhattan() , self.depth + 1, self))

                #down
                if i.coord_y + 1 <= 4:
                    if self.board.grid[i.coord_y + 1][i.coord_x] == '.' and \
                            self.board.grid[i.coord_y + 1][i.coord_x + 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('down')
                        new_board = Board(copy_list)
                        new_states.append(State(new_board, self.depth + new_board.manhattan() , self.depth + 1, self))
                #left
                if i.coord_x - 1 >= 0:
                    if self.board.grid[i.coord_y][i.coord_x - 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('left')
                        new_board = Board(copy_list)
                        new_states.append(State(new_board, self.depth + new_board.manhattan() , self.depth + 1, self))
                #right
                if i.coord_x + 2 <= 3:
                    if self.board.grid[i.coord_y][i.coord_x + 2] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('right')
                        new_board = Board(copy_list)
                        new_states.append(State(new_board, self.depth + new_board.manhattan() , self.depth + 1, self))
            


            if i.orientation == 'v':
                #up
                if i.coord_y - 1 >= 0:
                    if self.board.grid[i.coord_y - 1][i.coord_x] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('up')
                        new_board = Board(copy_list)
                        new_states.append(State(new_board, self.depth + new_board.manhattan() , self.depth + 1, self))
                #down
                if i.coord_y + 2 <= 4:
                    if self.board.grid[i.coord_y + 2][i.coord_x] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('down')
                        new_board = Board(copy_list)
                        new_states.append(State(new_board, self.depth + new_board.manhattan() , self.depth + 1, self))
                #left
                if i.coord_x - 1 >= 0:
                    if self.board.grid[i.coord_y][i.coord_x - 1] == '.' and \
                            self.board.grid[i.coord_y + 1][i.coord_x - 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('left')
                        new_board = Board(copy_list)
                        new_states.append(State(new_board, self.depth + new_board.manhattan() , self.depth + 1, self))
                #right
                if i.coord_x + 1 <= 3:
                    if self.board.grid[i.coord_y][i.coord_x + 1] == '.' and \
                            self.board.grid[i.coord_y + 1][i.coord_x + 1] == '.':
                        copy_list = deepcopy(p)
                        copy_list[ind].move('right')
                        new_board = Board(copy_list)
                        new_states.append(State(new_board, self.depth + new_board.manhattan() , self.depth + 1, self))


        # print('\nnewstates\n')
        # print(new_states)
        return new_states



        


def read_from_file(filename):
    """
    Load initial board from a given file.

    :param filename: The name of the given file.
    :type filename: str
    :return: A loaded board
    :rtype: Board
    """

    puzzle_file = open(filename, "r")

    line_index = 0
    pieces = []
    g_found = False

    for line in puzzle_file:

        for x, ch in enumerate(line):

            if ch == '^': # found vertical piece
                pieces.append(Piece(False, False, x, line_index, 'v'))
            elif ch == '<': # found horizontal piece
                pieces.append(Piece(False, False, x, line_index, 'h'))
            elif ch == char_single:
                pieces.append(Piece(False, True, x, line_index, None))
            elif ch == char_goal:
                if g_found == False:
                    pieces.append(Piece(True, False, x, line_index, None))
                    g_found = True
        line_index += 1

    puzzle_file.close()

    board = Board(pieces)
    
    return board


def get_solution(state):
    """
    Get the solution path from the given state.

    :param state: The given state.
    :type state: State
    :return: A list of states from the initial state to the given state.
    :rtype: list
    """
    solution = [state]
    while state.parent != None:
        state = state.parent
        solution.append(state)
    solution.reverse()
    return solution



def DFS(state):
    """
    Depth-first search algorithm recursively.

    :param state: The initial state.
    :type state: State
    :return: A solution state.
    :rtype: State
    """
    frontier = [state]
    explored = []
    # state.board.display()
    # print("\n")
    while frontier:
        # print(frontier)
        state = frontier.pop()
        # print('current depth: ', state.depth)
        # state.board.display()
        # print(state.board.display_string())
        # input()
        if state.board.display_string() not in explored:
            

            # print(state.board.display())
            # state.board.display()
            # print('------\n')
            # input()
            explored.append(state.board.display_string())
            # print('explored: ', explored)

            if state.board.goal_check():
                # print("\n\nhihi\n")
                return state



            for child in state.available_moves():
                # print("\n\nhihi\n")
                # child.board.display()
                # print('\n')
                # print(child)
                # print('child id: ', child.id)
                if child.board.display_string() not in explored:
                    frontier.append(child)
                    # print('frontier: ', frontier)
            # print('end------\n')
        


def As_Man(state):
    """
    A* algorithm with Manhattan distance as heuristic.
    """
    frontier = [state]
    explored = []
    while frontier:
        state = frontier.pop(0)
        if state.board.display_string() not in explored:
            explored.append(state.board.display_string())
            if state.board.goal_check():
                return state
            for child in state.available_moves_manhattan():
                if child.board.display_string() not in explored:
                    frontier.append(child)
            frontier.sort(key=lambda x: x.f)
    return None



def output_to_file(filename, solution):
    """
    Output the solution to a given file.

    :param filename: The name of the given file.
    :type filename: str
    :param solution: The solution path.
    :type solution: list
    """
    output_file = open(filename, "w")
    for state in solution:
        output_file.write(state.board.display_string())
        output_file.write("\n")
    output_file.close()



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzle."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    parser.add_argument(
        "--algo",
        type=str,
        required=True,
        choices=['astar', 'dfs'],
        help="The searching algorithm."
    )
    args = parser.parse_args()

    # read the board from the file
    board = read_from_file(args.inputfile)

    # solve the puzzle
    if args.algo == 'astar':
        output_to_file(args.outputfile, get_solution(As_Man(State(board, 0, 0, None))))
    elif args.algo == 'dfs':
        output_to_file(args.outputfile, get_solution(DFS(State(board, 0, 0, None))))

    #board.display()

    # a = As_Man(State(board, 0, 0, None))
    # # print(a.board.display())
    # p = get_solution(a)
    # for i in p:
    #     print('\n')
    #     i.board.display()

    # print(i.depth)