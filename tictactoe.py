# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 12:09:43 2015

@author: odyssey
"""


import random
import copy

import pdb;
class Player:    
    def __init__(self,sign,randomness=0.1):
        self.V=dict()
        self.sign=sign
        self.opponentSign=(self.sign==1 and 2 or 1)
        self.randomMoveProbability=randomness
        self.wincombn=[[6, 7, 8], [3, 4, 5], [0, 1, 2], [0, 3, 6], [1, 4, 7], [2, 5, 8],[0, 4, 8], [2, 4, 6]]
        self.alpha=0.1
    def getValueForState(self,board):
        win,loose=self.winLoose(board)
        if win:
            return 1
        if loose:
            return 0
        score=self.V.get(board)    
        if (score is None):            
            self.V[board]=0.5
            return 0.5
        else:
            return score
        
    def winLoose(self,board):
        checks=[[board.state[i] for i in sqn] for sqn in self.wincombn]
        win=(3 in [check.count(self.sign) for check in checks])        
        loose=(3 in [check.count(self.opponentSign) for check in checks])
        return win,loose
            
            
    def randomMove(self,game,empty):                
        rnd=random.randrange(0,len(empty))        
        newBoard=game.board.newBoard(empty[rnd],self.sign)
        game.board=newBoard
    
    def updateValueForState(self,state,newval):
        self.V[state]=newval
        
    def greedyMove(self,game,empty): 
        # greedy move                
        possibleMovesAndScores=dict()
        for cell in empty:
            candidate=game.board.newBoard(cell,self.sign)
            score=self.getValueForState(candidate)
            possibleMovesAndScores[candidate]=score
        
        vals=possibleMovesAndScores.values()
        maxScore=max(vals)
        bestMoves=[k for k,v in possibleMovesAndScores.items() if v==maxScore]
        chooseOne=random.randrange(0,len(bestMoves))
        oneBestMove=bestMoves[chooseOne]
        
        
        if len(game.history)>2:                    
            oldval=self.getValueForState(game.history[-2])
            newval=oldval+self.alpha*(self.getValueForState(oneBestMove)-oldval)
            self.updateValueForState(game.history[-2],newval)
        game.board=oneBestMove
        
    def makeMove(self,game):
        empty=game.board.emptyCells()
        if (random.random()<self.randomMoveProbability):
            return self.randomMove(game,empty)            
        return self.greedyMove(game,empty)

class HumanPlayer(Player):
    def __init__(self,sign):
        Player.__init__(self,sign)
    def makeMove(self,game):
        move=raw_input("your move:")
        # check valid move
        newBoard=game.board.newBoard(int(move),self.sign)
        game.board=newBoard

class LearningFromExplorationPlayer(Player):
    def randomMove(self,game,empty):                
        rnd=random.randrange(0,len(empty))        
        newBoard=game.board.newBoard(empty[rnd],self.sign)
        oldval=self.getValueForState(game.history[-2])
        newval=oldval+self.alpha*(self.getValueForState(newBoard)-oldval)
        self.updateValueForState(game.history[-2],newval)
        game.board=newBoard

class SymmetryPlayer(Player):
    def __init__(self,sign,randomness=0.1):
        Player.__init__(self,sign,randomness)
    def updateValueForState(self,state,newval):        
        self.V[state]=newval 
        for i in range(0,2):
            state=state.rotate()
            self.V[state]=newval 
            
        reflected=state.reflectHorizontal()
        self.V[reflected]=newval 
        for i in range(0,2):
            reflected=reflected.rotate()
            self.V[reflected]=newval 
        
class Game:
    def __init__(self,playerOne,playerTwo):
        self.playerOneWin=False
        self.playerOneLoose=False
        self.tie=False
        self.playerOne=playerOne
        self.playerTwo=playerTwo
        self.board=Board()
        self.history=[]                               
        self.addBoardToHistory()
        
    def addBoardToHistory(self):        
        self.history.append(copy.deepcopy(self.board))
    def play(self):        
        if isinstance(self.playerOne,HumanPlayer):
            print self.board
        while(True):
            self.playerOne.makeMove(self)            
            if isinstance(self.playerOne,HumanPlayer) or isinstance(self.playerTwo,HumanPlayer):
                print self.board
            self.addBoardToHistory()
            if self.finished(): break
            
            self.playerTwo.makeMove(self)
            if isinstance(self.playerOne,HumanPlayer) or isinstance(self.playerTwo,HumanPlayer):
                print self.board
            self.addBoardToHistory()
            if self.finished(): break
                    
    def finished(self):
        win,loose=self.playerOne.winLoose(self.board)
        self.win=win
        self.loose=loose
        if not(win or loose):
            empty=self.board.emptyCells()
            if len(empty)==0:
                self.tie=True
        if (self.win or self.loose or self.tie):
            return True
        return False
        
        

            
class Board:     
    def display(self):
        form = '''
            \t| %s | %s | %s |
            \t-------------
            \t| %s | %s | %s |
            \t-------------
            \t| %s | %s | %s |
            '''
        disp=[]
        for i in self.state:
            if i==0:
                disp.append('-')
            elif i==1:
                disp.append('X')    
            elif i==2:
                disp.append('O')
        return (form % tuple(disp))
            
    def __init__(self,state=None):
        if (state is None):        
            self.state=[0]*9
        else:
            self.state=state
    def __repr__(self):
        return self.display()
    def emptyCells(self):
        return [idx for idx,val in enumerate(self.state) if val==0]
    def newBoard(self,location,sign):
        mycopy=copy.deepcopy(self)
        mycopy.state[location]=sign
        return mycopy
    def __hash__(self):
        return hash(tuple(self.state))
    def __eq__(self,other):
        return tuple(self.state)==tuple(other.state)
    def rotate(self):
        mycopy=copy.deepcopy(self)
        #0>6,1>3,2>0
        #3>7,4>4,5>1
        #6>8,7>5,8>2
        mycopy.state[6]=self.state[0]
        mycopy.state[8]=self.state[6]
        mycopy.state[2]=self.state[8]
        mycopy.state[0]=self.state[2]
        
        mycopy.state[3]=self.state[1]
        mycopy.state[7]=self.state[3]
        mycopy.state[5]=self.state[7]
        mycopy.state[1]=self.state[5]
        return mycopy
#         mycopy.state[4]=self.state[4]
    def reflectHorizontal(self):
        mycopy=copy.deepcopy(self)
        mycopy.state[6]=self.state[0]
        mycopy.state[7]=self.state[1]
        mycopy.state[8]=self.state[2]
        
        mycopy.state[0]=self.state[6]
        mycopy.state[1]=self.state[7]
        mycopy.state[2]=self.state[8]
        return mycopy

class GameLoop:
    def __init__(self,playerOne,playerTwo):
        self.wintimes=0
        self.loosetimes=0
        self.tietimes=0
    
    
        self.playerOne=playerOne
        self.playerTwo=playerTwo
        self.games=[]
        
    def run(self,numrounds=10000):
        for i in range(0,numrounds):
            g=Game(self.playerOne,self.playerTwo)
            g.play()
            if (g.win):
                self.wintimes=self.wintimes+1
            if (g.loose):
                self.loosetimes=self.loosetimes+1
            if (g.tie):
                self.tietimes=self.tietimes+1
            self.games.append(g)    


