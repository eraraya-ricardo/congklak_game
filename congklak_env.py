# congklak game environment
# version 1.0.0

import numpy as np
import random

class congklak_board:
    def __init__(self):
        # array to save the score, also function as the big holes' stone counter
        self.score = np.full(shape=2, fill_value=0, dtype=np.int)
        
        # array to save the state of the board (small holes' stone counter)
        self.state = None
        
        # board size
        self.N = None
        
        # starting hole
        self.starting_hole = None
        
        # turn player marker (0 or 1, the player who goes first is 0 and the other one is 1)
        self.turn = None
        
        # the state of the game (if the game is finished, done = True)
        self.done = False
        
        # the ruleset being used for the game
        self.ruleset = None

        # logging variables
        self.turns_count = None
        self.games_count = None
        self.log = None
        
    def setup(self, board_size, max_iter, rule='original'):
        # set up the board state and the marker for turn player
        self.ruleset = rule
        self.N = board_size
        self.state = np.full(shape=int(2*self.N), fill_value=self.N, dtype=np.int)
        self.turn = 0
        self.turns_count = 0
        self.games_count = 0
        self.log = None
        self.max_iter = max_iter
        
    def reset(self):
        # reset the board
        if self.N == None:
            return print("Setup the board first.")
        else:
            self.state = np.full(shape=int(2*self.N), fill_value=self.N, dtype=np.int)
            self.score = np.full(shape=2, fill_value=0, dtype=np.int)
            self.done = False
            self.turn = 0
            self.turns_count = 0

    def observation_space(self):
        if self.N == None:
            return print("Setup the board first.")
        else:
            return (2*self.N)**2

    def action_space(self):
        if self.N == None:
            return print("Setup the board first.")
        else:
            return self.N
        
    def step(self, action):
        # update the state of the board and score
        
        if self.N == None:
            return print("Setup the board first.")
        else:
            # check if the action is legal
            if self.is_legal(action):
                # do the rotation
                last_hole, scoring = self.rotation()
                # if the last hole is the turn player's big hole, scoring = True --> wait for the new selection of the starting hole
                # but if the last hole is not big hole, scoring = False --> then...
                if scoring == False:
                    # if the last hole's stones = 1 --> 2 scenarios
                    if self.state[last_hole] == 1:
                        # if the last hole is the turn player's hole --> shooting --> end turn
                        if int(last_hole/self.N) == self.turn:
                            # the shooting function here is already modified.
                            # if the hole across of the last hole is NOT empty --> do the shooting
                            # else --> do nothing
                            self.shooting(last_hole)
                            self.end_turn()
                        # if the last hole is the opponent's hole --> end turn
                        else:
                            self.end_turn()
                    # if the last hole's stones > 1
                    else:
                        # if the ruleset being used is the original ruleset
                        if self.ruleset == 'original':
                            # action's range is [0,N-1], last hole's range is [0, 2N-1], self.state's range is [0, 2N-1].
                            # Action needs to be increased by self.turn*self.N to match the self.state's range.
                            # The last hole needs to be reduced by self.turn*self.N to match the action's range.
                            # repeat the rotation with starting_hole = last_hole
                            self.step(last_hole - self.turn*self.N)
                        # if the ruleset being used is the ruleset suggested by Kasim
                        elif self.ruleset == 'kasim2016':
                            # if the last hole is the turn player's hole --> same as in the original ruleset
                            # repeat the rotation with starting_hole = last_hole
                            if int(last_hole/self.N) == self.turn:
                                self.step(last_hole - self.turn*self.N)
                            # if the last hole is the opponent's hole --> end turn (rule revision by Kasim)
                            else:
                                self.end_turn()
            else:
                #return print("The move is illegal.")
                pass
    
    def rotation(self):
        scoring = False
        hole = int(self.starting_hole + self.turn*self.N)
        stones = self.state[hole]
        self.state[hole] = 0
        while stones > 0:
            hole += 1
            if int(hole - self.turn*self.N) == self.N:
                self.score[self.turn] += 1
                scoring = True
                stones -= 1
            if stones > 0:
                hole = hole%(2*self.N)
                self.state[hole] += 1
                scoring = False
                stones -= 1
        return hole, scoring
    
    def shooting(self, last_hole):
        d = abs(last_hole - ((self.N-1) + self.turn))
        hole_across = (self.N-1) + int(not(self.turn)) - d*(2*self.turn - 1)
        # if the hole across of the last hole is empty --> do nothing
        if self.state[hole_across] == 0:
            pass
        # if the hole across of the last hole is NOT empty --> do the shooting
        else:
            self.score[self.turn] += self.state[last_hole] + self.state[hole_across]
            self.state[last_hole] = 0
            self.state[hole_across] = 0
        #print(N-1, int(not(self.turn)), d*(2*self.turn - 1))
        
    def end_turn(self):
        # check for the winner, if there is a winner --> done = True (end the game)
        if self.score[self.turn] > self.N**2:
            self.done = True
            self.games_count += 1
        # if both player's score is equal to N**2 --> draw --> done = True (end the game)
        elif self.score[self.turn] == self.score[int(not(self.turn))] and self.score[self.turn] == self.N**2:
            self.done = True
            self.games_count += 1
        # else --> continue the game, pass the turn to the opponent
        else:
            self.turn = int(not(self.turn))
            self.turns_count += 1
        
    def is_legal(self, action):
        # check whether the move is legal/valid or not
        self.starting_hole = action
        hole = int(self.starting_hole + self.turn*self.N)
        if self.state[hole] == 0:
            return False
        else:
            return True

    def whose_turn(self):
        # check whose turn now
        if self.N == None:
            return print("Setup the board first.")
        else:
            return self.turn
        
    def possible_action(self):
        # take a random sample of possible/valid action
        pa = np.array([], dtype=np.int)
        for i in range (len(self.state[(0+self.turn*self.N):(self.N+self.turn*self.N)])):
            if self.state[(0+self.turn*self.N):(self.N+self.turn*self.N)][i] != 0:
                pa = np.append(pa, i)
        return pa

    def one_hot_state(self):
        # convert board state to one-hot-encoded board state
        input_units = np.zeros(((2*self.N)**2,))

        for i in range (len(self.state)):
            if self.state[i] > (2*self.N-1):
                input_units[i*2*self.N + 2*self.N-1] = self.state[i] - (2*self.N-1)
            else:
                input_units[i*2*self.N + self.state[i]] = 1

        return input_units

    def logging(self, score):
        # log the score
        new_log = np.concatenate((score, 0.0, 0.0, self.turns_count), axis=None).reshape(1,-1)
        if self.log is None:
            self.log = new_log
        else:
            self.log = np.append(self.log, new_log, axis=0)
        if len(self.log) >= self.max_iter*0.2:
              self.log[-1, 2] = np.average(self.log[int(len(self.log)-0.2*self.max_iter):len(self.log), 0])
              self.log[-1, 3] = np.average(self.log[int(len(self.log)-0.2*self.max_iter):len(self.log), 1])

    def log_to_txt(self, fdir):
        # saving the log to txt file
        np.savetxt(fdir + ".txt", self.log)
        print("Log score to text file")
