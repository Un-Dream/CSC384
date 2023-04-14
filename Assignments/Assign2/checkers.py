import argparse
import copy
import sys
import time

MAX_DEPTH = 8
INF = 10000000000
state_time = time.time()

cache = {} # you can use this to implement state caching!

solutions = []
#solution = list of potential solution states

class State:
    # This class is used to represent a state.
    # board : a list of lists that represents the 8*8 board
    def __init__(self, board, turn, jump = False, parent = None, last_move = None, pieces = {'r': [], 'b': [], 'R': [], 'B': []}):

        self.board = board
        self.turn = turn
        self.width = 8
        self.height = 8
        self.jump = jump
        self.parent = parent
        self.last_move = last_move
        self.pieces = pieces
        self.eval = eval_heuristic(self)

    def display(self):
        for i in self.board:
            for j in i:
                print(j, end="")
            print("")
        print("")


    def display_string(self):
        """
        Return the current board as a string.
        """
        s = ''
        for i, line in enumerate(self.board):
            for ch in line:
                s += ch
            s += '\n'

        return s[:-1]

    def goal_max(self):
        #return true if the state is a goal state for the max player
        #return false otherwise


        for i in range(self.height):
            for j in range(self.width):
                p = self.board[i][j]
                if p == 'b' or p == 'B':
                    if can_move(self, p, i, j):
                        
                        return False

        solutions.append(self)
        return True

    def goal_min(self):
        #return true if the state is a goal state for the min player
        #return false otherwise
        for i in range(self.height):
            for j in range(self.width):
                p = self.board[i][j]
                if p == 'r' or p == 'R':
                    if can_move(self, p, i, j):
                        
                        return False
        return True



def can_be_capture(state, i,j):
    #determine if the piece at (i,j) can be captured
    #return true if the piece can be captured
    #return false otherwise
    piece = state.board[i][j]
    opp = get_opp_char(piece)
    if i+1 < state.height and j+1 < state.width and state.board[i+1][j+1] in opp:
        if i-1 >= 0 and j-1 >= 0 and state.board[i-1][j-1] == '.':
            return True
    if i+1 < state.height and j-1 >= 0 and state.board[i+1][j-1] in opp:
        if i-1 >= 0 and j+1 < state.width and state.board[i-1][j+1] == '.':
            return True
    if i-1 >= 0 and j+1 < state.width and state.board[i-1][j+1] in opp:
        if i+1 < state.height and j-1 >= 0 and state.board[i+1][j-1] == '.':
            return True
    if i-1 >= 0 and j-1 >= 0 and state.board[i-1][j-1] in opp:
        if i+1 < state.height and j+1 < state.width and state.board[i+1][j+1] == '.':
            return True
    return False


def eval_heuristic(state):
        #return the heuristic value for the given state
        #the heuristic value should be an integer
        #the heuristic value should be positive if the state is good for the max player
        #the heuristic value should be negative if the state is good for the min player
        #the heuristic value should be 0 if the state is a tie
        #the heuristic value should be the difference between the number of pieces for the max player and the number of pieces for the min player
        #you can use the following function to count the number of pieces for each player
        #num_pieces = count_pieces(state)
        #num_pieces[0] is the number of pieces for the max player
        #num_pieces[1] is the number of pieces for the min player

        if state.turn == 'r':
            if state.goal_max():
                return INF
            elif state.goal_min():
                return -INF
        else:
            if state.goal_min():
                return -INF
            elif state.goal_max():
                return INF

        count = 0
        num_pieces = count_pieces(state)
        count = 3*num_pieces[0] - 3*num_pieces[1] + 5* num_pieces[2] - 5* num_pieces[3] 


        closer = 0

        edges = 0
        half = 0
        centre = 0
        for i in range(state.height):
            l = state.board[i][0]
            r = state.board[i][state.width-1]
            if l == 'r':
                edges += 1
            elif l == 'R':
                edges += 2
            elif l == 'b':
                edges -= 1
            elif l == 'B':
                edges -= 2

            if r == 'r':
                edges += 1
            elif r == 'R':
                edges += 2
            elif r == 'b':
                edges -= 1
            elif r == 'B':
                edges -= 2

            for j in range(state.width):
                p = state.board[i][j]
                if p == 'r':
                    closer += 7-i
                elif p == 'b':
                    closer -= i

                if p == 'R':
                    centre += state.width/2 - j + state.height/2 - i
                elif p == 'B':
                    centre -= state.width/2 - j + state.height/2 - i
            
            # if i >= state.height/4 and i <= state.height*3/4:
            #     for j in range(state.width):
            #         p = state.board[i][j]
            #         if p == 'r' or p == 'R':
            #             edges += 1
            #         elif p == 'b' or p == 'B':
            #             edges -= 1
        # count =0


        amount_left = 0
        # amount_left = num_pieces[0] - num_pieces[1] + num_pieces[2] - num_pieces[3]
        if num_pieces[0] + num_pieces[2] > num_pieces[1] + num_pieces[3]:
            amount_left = 9 - num_pieces[1] - num_pieces[3]
        elif num_pieces[0] + num_pieces[2] < num_pieces[1] + num_pieces[3]:
            amount_left = -9 + num_pieces[0] + num_pieces[2]
        else:
            amount_left = 0
        return int(1000000*count + 10000*closer + 100*amount_left + (edges+centre))


        





def count_pieces(state:State):
    #return a list of the number of pieces for the max player and the min player
    #the first element of the list is the number of pieces for the max player
    #the second element of the list is the number of pieces for the min player
    #the third element of the list is the number of kings for the max player
    #the fourth element of the list is the number of kings for the min player
    num_pieces = [0, 0, 0, 0]
    for i in range(state.height):
        for j in range(state.width):
            p = state.board[i][j]
            if p == 'r':
                num_pieces[0] += 1
            elif p == 'b':
                num_pieces[1] += 1
            elif p == 'R':
                num_pieces[2] += 1
            elif p == 'B':
                num_pieces[3] += 1
    return num_pieces


def can_move(state:State, piece, i, j):
    #determine if the piece can move
    #return true if the piece can move
    #return false otherwise
    opp = get_opp_char(piece)
    if piece == 'r':
        #move
        if i-1 >= 0 and j+1 < state.width and state.board[i-1][j+1] == '.':
            return True
        if i-1 >= 0 and j-1 >= 0 and state.board[i-1][j-1] == '.':
            return True

        #jump
        if i-2 >= 0 and j+2 < state.width and state.board[i-2][j+2] == '.' and state.board[i-1][j+1] in opp:
            return True
        if i-2 >= 0 and j-2 >= 0 and state.board[i-2][j-2] == '.' and state.board[i-1][j-1] in opp:
            return True

    elif piece == 'b':
        #move
        if i+1 < state.height and j+1 < state.width and state.board[i+1][j+1] == '.':
            return True
        if i+1 < state.height and j-1 >= 0 and state.board[i+1][j-1] == '.':
            return True
        #jump
        if i+2 < state.height and j+2 < state.width and state.board[i+2][j+2] == '.' and state.board[i+1][j+1] in opp:
            return True
        if i+2 < state.height and j-2 >= 0 and state.board[i+2][j-2] == '.' and state.board[i+1][j-1] in opp:
            return True


    elif piece == 'R' or piece == 'B':
        #move
        if i-1 >= 0 and j+1 < state.width and state.board[i-1][j+1] == '.':
            return True
        if i-1 >= 0 and j-1 >= 0 and state.board[i-1][j-1] == '.':
            return True
        if i+1 < state.height and j+1 < state.width and state.board[i+1][j+1] == '.':
            return True
        if i+1 < state.height and j-1 >= 0 and state.board[i+1][j-1] == '.':
            return True
        #jump
        if i-2 >= 0 and j+2 < state.width and state.board[i-2][j+2] == '.' and state.board[i-1][j+1] in opp:
            return True
        if i-2 >= 0 and j-2 >= 0 and state.board[i-2][j-2] == '.' and state.board[i-1][j-1] in opp:
            return True
        if i+2 < state.height and j+2 < state.width and state.board[i+2][j+2] == '.' and state.board[i+1][j+1] in opp:
            return True
        if i+2 < state.height and j-2 >= 0 and state.board[i+2][j-2] == '.' and state.board[i+1][j-1] in opp:
            return True
    
    return False



def gen_successors(state:State):
    #return a list of successors for the given state
    #each successor is a State object
    successors_move = []
    successors_jump = []
    if state.turn == 'r':
        for i in range(state.height):
            for j in range(state.width):
                suc_move = []
                suc_jump = []

                if state.board[i][j] == 'r':
                    
                    suc_jump = jump(state, i, j, 'r', first = True)
                    if suc_jump == [] and successors_jump == []:
                        suc_move = move(state, i, j, 'r')
                elif state.board[i][j] == 'R':
                    # print('++++++')
                    # print('R')
                    # state.display()
                    
                    suc_jump = jump(state, i, j, 'R', first = True)
                    if suc_jump == [] and successors_jump == []:
                        suc_move = move(state, i, j, 'R')
                successors_move.extend(suc_move)
                successors_jump.extend(suc_jump)

                
    elif state.turn == 'b':
        for i in range(state.height):
            for j in range(state.width):
                suc_move = []
                suc_jump = []
                if state.board[i][j] == 'b':
                    
                    suc_jump = jump(state, i, j, 'b', first = True)
                    if suc_jump == [] and successors_jump == []:
                        suc_move = move(state, i, j, 'b')   
                elif state.board[i][j] == 'B':
                    suc_jump = jump(state, i, j, 'B', first = True)
                    if suc_jump == [] and successors_jump == []:
                        suc_move = move(state, i, j, 'B')
                successors_move.extend(suc_move)
                successors_jump.extend(suc_jump)
    # s = input("press enter to continue")
    # print("successors_move")


    if successors_jump:
        if state.turn == 'r':
            successors_jump.sort(key = lambda x: x.eval, reverse = True)
        else:
            successors_jump.sort(key = lambda x: x.eval)
        return successors_jump
    else:
        if state.turn == 'r':
            successors_move.sort(key = lambda x: x.eval, reverse = True)
        else:
            successors_move.sort(key = lambda x: x.eval)
        return successors_move
                

def move(state:State, i, j, piece):
    #return a list of successors for the given piece
    move = []

    opp = get_opp_char(piece)
    if piece  == 'r':

        #move up right
        if i-1 >= 0 and j+1 < state.width and state.board[i-1][j+1] == '.':
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i-1][j+1] = 'r'
            if i-1 == 0:
                new_state.board[i-1][j+1] = 'R'
            new_state.turn = 'b'
            new_state.parent = state
            new_state.last_move = (i-1, j+1)
            new_state.eval = eval_heuristic(new_state)
            move.append(new_state)
        
        #move up left
        if i-1 >= 0 and j-1 >= 0 and state.board[i-1][j-1] == '.':
            # print("enter r")
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i-1][j-1] = 'r'
            if i-1 == 0:
                new_state.board[i-1][j-1] = 'R'
            new_state.turn = 'b'
            new_state.parent = state
            new_state.last_move = (i-1, j-1)
            
            new_state.eval = eval_heuristic(new_state)
            move.append(new_state)


    elif piece == 'b':
        #move down right
        if i+1 < state.height and j+1 < state.width and state.board[i+1][j+1] == '.':
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i+1][j+1] = 'b'
            if i+1 == state.height-1:
                new_state.board[i+1][j+1] = 'B'
            new_state.turn = 'r'
            new_state.parent = state
            new_state.last_move = (i+1, j+1)
            
            new_state.eval = eval_heuristic(new_state)
            move.append(new_state)
        #move down left
        if i+1 < state.height and j-1 >= 0 and state.board[i+1][j-1] == '.':
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i+1][j-1] = 'b'
            if i+1 == state.height-1:
                new_state.board[i+1][j-1] = 'B'
            new_state.turn = 'r'
            new_state.parent = state
            new_state.last_move = (i+1, j-1)
            
            new_state.eval = eval_heuristic(new_state)
            move.append(new_state)


    elif piece == 'R':
        #move down right
        if i+1 < state.height and j+1 < state.width and state.board[i+1][j+1] == '.':
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i+1][j+1] = 'R'
            new_state.turn = 'b'
            new_state.parent = state
            new_state.last_move = (i+1, j+1)
            
            new_state.eval = eval_heuristic(new_state)
            move.append(new_state)
        #move down left
        if i+1 < state.height and j-1 >= 0 and state.board[i+1][j-1] == '.':
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i+1][j-1] = 'R'
            new_state.turn = 'b'
            new_state.parent = state
            new_state.last_move = (i+1, j-1)
            
            new_state.eval = eval_heuristic(new_state)
            move.append(new_state)
        #move up right
        if i-1 >= 0 and j+1 < state.width and state.board[i-1][j+1] == '.':
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i-1][j+1] = 'R'
            new_state.turn = 'b'
            new_state.parent = state
            new_state.last_move = (i-1, j+1)
            
            new_state.eval = eval_heuristic(new_state)
            move.append(new_state)
        #move up left
        if i-1 >= 0 and j-1 >= 0 and state.board[i-1][j-1] == '.':
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i-1][j-1] = 'R'
            new_state.turn = 'b'
            new_state.parent = state
            new_state.last_move = (i-1, j-1)
            
            new_state.eval = eval_heuristic(new_state)
            move.append(new_state)


    elif piece == 'B':
        #move down right
        if i+1 < state.height and j+1 < state.width and state.board[i+1][j+1] == '.':
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i+1][j+1] = 'B'
            new_state.turn = 'r'
            new_state.parent = state
            new_state.last_move = (i+1, j+1)
            
            new_state.eval = eval_heuristic(new_state)
            move.append(new_state)
        #move down left
        if i+1 < state.height and j-1 >= 0 and state.board[i+1][j-1] == '.':
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i+1][j-1] = 'B'
            new_state.turn = 'r'
            new_state.parent = state
            new_state.last_move = (i+1, j-1)
            
            new_state.eval = eval_heuristic(new_state)
            move.append(new_state)
        #move up right
        if i-1 >= 0 and j+1 < state.width and state.board[i-1][j+1] == '.':
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i-1][j+1] = 'B'
            new_state.turn = 'r'
            new_state.parent = state
            new_state.last_move = (i-1, j+1)
            
            new_state.eval = eval_heuristic(new_state)
            move.append(new_state)
        #move up left
        if i-1 >= 0 and j-1 >= 0 and state.board[i-1][j-1] == '.':
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i-1][j-1] = 'B'
            new_state.turn = 'r'
            new_state.parent = state
            new_state.last_move = (i-1, j-1)
            
            new_state.eval = eval_heuristic(new_state)
            move.append(new_state)

    return move


def jump(state:State, i, j, piece, first = False, promoted = False):
    #return a list of successors for the given piece
    jump_list = []
    last = True
    opp = get_opp_char(piece)

    prom = False

    if promoted:
        return [state]


    if piece  == 'r':
        #jumping up right
        if i-1 >= 0 and j+1 < state.width and state.board[i-1][j+1] in opp\
            and i-2 >= 0 and j+2 < state.width and state.board[i-2][j+2] == '.':
            last = False
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i-1][j+1] = '.'
            new_state.board[i-2][j+2] = 'r'
            p = 'r'
            prom = False
            if i-2 == 0:
                new_state.board[i-2][j+2] = 'R'
                p = 'R'
                prom = True
            new_state.turn = 'b'
            new_state.parent = state
            new_state.last_move = (i-2, j+2)
            
            new_state.eval = eval_heuristic(new_state)
            jump_list.extend(jump(new_state, i-2, j+2, p, promoted=prom))
        
        #jumping up left
        if i-1 >= 0 and j-1 >= 0 and state.board[i-1][j-1] in opp\
            and i-2 >= 0 and j-2 >= 0 and state.board[i-2][j-2] == '.':
            last = False
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i-1][j-1] = '.'
            new_state.board[i-2][j-2] = 'r'
            p = 'r'
            prom = False
            if i-2 == 0:
                new_state.board[i-2][j-2] = 'R'
                p = 'R'
                prom = True
            new_state.turn = 'b'
            new_state.parent = state
            new_state.last_move = (i-2, j-2)
            
            new_state.eval = eval_heuristic(new_state)
            jump_list.extend(jump(new_state, i-2, j-2, p, promoted=prom))


    elif piece == 'R':
        #jumping down right
        if i+1 < state.height and j+1 < state.width and state.board[i+1][j+1] in opp\
             and i+2 < state.height and j+2 < state.width and state.board[i+2][j+2] == '.':
            last = False
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i+1][j+1] = '.'
            new_state.board[i+2][j+2] = 'R'
            new_state.turn = 'b'
            new_state.parent = state
            new_state.last_move = (i+2, j+2)
            
            new_state.eval = eval_heuristic(new_state)
            jump_list.extend(jump(new_state, i+2, j+2, 'R'))

        #jumping down left
        if i+1 < state.height and j-1 >= 0 and state.board[i+1][j-1] in opp\
             and i+2 < state.height and j-2 >= 0 and state.board[i+2][j-2] == '.':
            last = False
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i+1][j-1] = '.'
            new_state.board[i+2][j-2] = 'R'
            new_state.turn = 'b'
            new_state.parent = state
            new_state.last_move = (i+2, j-2)
            
            new_state.eval = eval_heuristic(new_state)
            jump_list.extend(jump(new_state, i+2, j-2, 'R'))



        #jumping up right
        if i-1 >= 0 and j+1 < state.width and state.board[i-1][j+1] in opp\
            and i-2 >= 0 and j+2 < state.width and state.board[i-2][j+2] == '.':

            # print("broken\n")
            # state.display()
            # print("-------------------\n")
            last = False
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i-1][j+1] = '.'
            new_state.board[i-2][j+2] = 'R'
            new_state.turn = 'b'
            new_state.parent = state
            new_state.last_move = (i-2, j+2)
            jump_list.extend(jump(new_state, i-2, j+2, 'R'))

        #jumping up left
        if i-1 >= 0 and j-1 >= 0 and state.board[i-1][j-1] in opp\
            and i-2 >= 0 and j-2 >= 0 and state.board[i-2][j-2] == '.':
            last = False            
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i-1][j-1] = '.'
            new_state.board[i-2][j-2] = 'R'
            new_state.turn = 'b'
            new_state.parent = state
            new_state.last_move = (i-2, j-2)
            
            new_state.eval = eval_heuristic(new_state)
            # print('jumping up left')
            jump_list.extend(jump(new_state, i-2, j-2, 'R'))
    




    elif piece == 'b':
        #jumping down right
        if i+1 < state.height and j+1 < state.width and state.board[i+1][j+1] in opp\
            and i+2 < state.height and j+2 < state.width and state.board[i+2][j+2] == '.':
            last = False
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i+1][j+1] = '.'
            new_state.board[i+2][j+2] = 'b'
            p = 'b'
            prom = False
            if i+2 == state.height-1:
                new_state.board[i+2][j+2] = 'B'
                p = 'B'
                prom = True
            new_state.turn = 'r'
            new_state.parent = state
            new_state.last_move = (i+2, j+2)
            
            new_state.eval = eval_heuristic(new_state)
            jump_list.extend(jump(new_state, i+2, j+2, p, promoted=prom))


        #jumping down left
        if i+1 < state.height and j-1 >= 0 and state.board[i+1][j-1] in opp\
            and i+2 < state.height and j-2 >= 0 and state.board[i+2][j-2] == '.':
            last = False
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i+1][j-1] = '.'
            new_state.board[i+2][j-2] = 'b'
            p = 'b'
            prom = False
            if i+2 == state.height-1:
                new_state.board[i+2][j-2] = 'B'
                p = 'B'
                prom = True
            new_state.turn = 'r'
            new_state.parent = state
            new_state.last_move = (i+2, j-2)
            
            new_state.eval = eval_heuristic(new_state)
            jump_list.extend(jump(new_state, i+2, j-2, p, promoted=prom))

    
    elif piece == 'B':
        #jumping down right
        if i+1 < state.height and j+1 < state.width and state.board[i+1][j+1] in opp\
            and i+2 < state.height and j+2 < state.width and state.board[i+2][j+2] == '.':
            last = False
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i+1][j+1] = '.'
            new_state.board[i+2][j+2] = 'B'
            new_state.turn = 'r'
            new_state.parent = state
            new_state.last_move = (i+2, j+2)
            
            new_state.eval = eval_heuristic(new_state)
            jump_list.extend(jump(new_state, i+2, j+2, 'B'))

        #jumping down left
        if i+1 < state.height and j-1 >= 0 and state.board[i+1][j-1] in opp\
            and i+2 < state.height and j-2 >= 0 and state.board[i+2][j-2] == '.':
            last = False
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i+1][j-1] = '.'
            new_state.board[i+2][j-2] = 'B'
            new_state.turn = 'r'
            new_state.parent = state
            new_state.last_move = (i+2, j-2)
            
            new_state.eval = eval_heuristic(new_state)
            jump_list.extend(jump(new_state, i+2, j-2, 'B'))


        #jumping up right
        if i-1 >= 0 and j+1 < state.width and state.board[i-1][j+1] in opp\
            and i-2 >= 0 and j+2 < state.width and state.board[i-2][j+2] == '.':
            last = False
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i-1][j+1] = '.'
            new_state.board[i-2][j+2] = 'B'
            new_state.turn = 'r'
            new_state.parent = state
            new_state.last_move = (i-2, j+2)
            
            new_state.eval = eval_heuristic(new_state)
            jump_list.extend(jump(new_state, i-2, j+2, 'B'))
        
        #jumping up left
        if i-1 >= 0 and j-1 >= 0 and state.board[i-1][j-1] in opp\
            and i-2 >= 0 and j-2 >= 0 and state.board[i-2][j-2] == '.':
            last = False
            new_state = copy.deepcopy(state)
            new_state.board[i][j] = '.'
            new_state.board[i-1][j-1] = '.'
            new_state.board[i-2][j-2] = 'B'
            new_state.turn = 'r'
            new_state.parent = state
            new_state.last_move = (i-2, j-2)
            
            new_state.eval = eval_heuristic(new_state)
            jump_list.extend(jump(new_state, i-2, j-2, 'B'))
            
    if last and not first:
        return [state]
    return jump_list

    



def a_b_max(state, cache, alpha, beta, depth):
    #return the best value for the max player
    #return the best state for the max player

    # print(depth)
    # print("\n")

    if depth == MAX_DEPTH or state.eval == INF or state.eval == -INF:
        return state.eval, state

    best_value = -INF
    best_state = None

    successors = gen_successors(state)
    for s in reversed(successors):
        value, _ = a_b_min(s, cache, alpha, beta, depth+1)
        if value >= best_value:
            best_value = value
            best_state = s
        if best_value >= beta:
            return best_value, best_state
        alpha = max(alpha, best_value)

    return best_value, best_state

def a_b_min(state, cache, alpha, beta, depth):
    # print("min " + str(depth) + "\n")
    #return the best value for the min player
    #return the best state for the min player
    if depth == MAX_DEPTH or state.eval == INF or state.eval == -INF:
        return state.eval, state
    best_value = INF
    best_state = None

    # if state:
    #     state.display()
    successors = gen_successors(state)
    for s in successors:
        value, _ = a_b_max(s, cache, alpha, beta, depth+1)
        if value <= best_value:
            best_value = value
            best_state = s
        if best_value <= alpha:
            return best_value, best_state
        beta = min(beta, best_value)

    return best_value, best_state



def start(state, turn, cache, depth):

    count  = 0
    split_time = time.time()
    prev_time = time.time()

    while(state.eval != INF and state.eval != -INF):
        

        
        curr_time = time.time()

        # print(curr_time - state_time)
        # print(state.eval)
        if curr_time - state_time < 120 and curr_time - state_time > 110 and solutions:
            # print("Time's up! You lose! -2")
            return solutions[-1]

        if curr_time - state_time < 120 and (split_time - prev_time+ curr_time - state_time) > 120 and solutions:
            # print("Time's up! You lose! -1")
            return solutions[-1]
        
        if curr_time - state_time < 4*60 and (split_time - prev_time + curr_time - state_time) > 4*60 and solutions:
            # print("Time's up! You lose! - 3")
            return solutions[-1]

        prev_time = curr_time
        # print(state.eval)
        # state.display()
        # print("Turn: " + state.turn)
        

        # input("Press Enter to continue...")
        if state.turn == 'r':
            _, state = a_b_max(state, cache, -INF, INF, 0)
        else:
            # print("Computer's turn")
            _, state = a_b_min(state, cache, -INF, INF, 0)
            # print("Computer's turn done")
        # state.display()
        # print('\n')
        count +=1

        split_time = time.time()
        
    return state

def get_opp_char(player):
    if player in ['b', 'B']:
        return ['r', 'R']
    else:
        return ['b', 'B']

def get_next_turn(curr_turn):
    if curr_turn == 'r':
        return 'b'
    else:
        return 'r'

def read_from_file(filename):

    f = open(filename)
    lines = f.readlines()
    board = [[str(x) for x in l.rstrip()] for l in lines]
    f.close()

    return board




def get_solution(state, start):
    """
    Get the solution path from the given state.

    :param state: The given state.
    :type state: State
    :return: A list of states from the initial state to the given state.
    :rtype: list
    """
    solution = []
    t =  '.'
    while state.parent != None:
        solution.append(state)
        t = state.turn
        while state.parent and state.parent.turn == t:
            state = state.parent
            t = state.turn
        state = state.parent
    solution.append(start)
    solution.reverse()
    return solution

def find_loc(state:State):
    loc = {'r': [], 'b': [], 'R': [], 'B': []}
    for i in range(state.height):
        for j in range(state.width):
            if state.board[i][j] in ['r', 'b', 'R', 'B']:
                loc[state.board[i][j]].append((i, j))
    return loc


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
        # state.display()
        output_file.write(state.display_string())
        output_file.write("\n")
        output_file.write("\n")

    
    output_file.close()



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzles."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    args = parser.parse_args()



    initial_board = read_from_file(args.inputfile)
    state = State(initial_board, 'r')
    turn = 'r'
    ctr = 0
    # print('-----------------')
    # print('Initial State')
    # state.display()
    # print('-----------------')
    # a = gen_successors(state)
    # for i in a:
    #     i.display()
    #     print('-----------------')


    # print(state.goal_max())
    # print(state.goal_min())
    final = start(state, 'r', {}, 0)
    # final.display()
    # print(time.time() - state_time)

    output_to_file(args.outputfile, get_solution(final, state))
    # sys.stdout = open(args.outputfile, 'w')
    # sys.stdout = sys.__stdout__

