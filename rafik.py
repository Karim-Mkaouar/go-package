# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.
'''
from time import time
import Goban
from numpy.random import normal
from playerInterface import *
import math

pruneScore = 20000

def getNeighbors(stone) :
    neigh=[]
    position = divmod(stone, 9)
    neighbors = ((position[0]-1, position[1]), (position[0], position[1]-1),(position[0], position[1]+1),(position[0]+1, position[1]))
    for i in neighbors :
        if i[0] >= 0 and i[0] < 9 and i[1] >= 0 and i[1] < 9:
            neigh.append(9 * i[0] + i[1])
    return(neigh)

def getConnectedStones(board,stone,myColor,done,listStone):

    neighbors = getNeighbors(stone)
    neighbors = list(set(neighbors) - set(done))
    listStone.append(stone)

    for neighbor in neighbors :
        done = list(dict.fromkeys(done))
        if board[neighbor]==myColor  :
            done.append(neighbor)
            getConnectedStones(board,neighbor,myColor,done,listStone)
        else : 
            done.append(neighbor)
    listStone = list(dict.fromkeys(listStone))
    return (listStone)

def getAllConnections(board,myColor,opColor):
    myGroup=[]
    opGroup=[]
    
    for i in range(81) :
        if board[i]==myColor :
            done=False
            for g in myGroup :
                if i in g :
                    done=True
                    break
            if done==False :
                v=getConnectedStones(board,i,myColor,[i],[])
                myGroup.append(v)
        elif board[i]==opColor :
            done=False
            for g in opGroup :
                if i in g :
                    done=True
                    break
            if done==False :
                v=getConnectedStones(board,i,opColor,[i],[])
                opGroup.append(v)
    return(myGroup,opGroup)

    
def getGroupLiberties (board,group) :
    groupList=[]
    for st in group :
        v=getNeighbors(st)
        v=list(set(v) - set(group))
        #groupList.append(v)
        groupList=groupList+v
    groupList = list(dict.fromkeys(groupList))
    liberties_degree=0
    for st in groupList :
        if board[st]==0 :
            liberties_degree+=1
    return (liberties_degree)

def getAllGroupsLiberties(board,groups) :
    listGroup=[]
    for group in groups :
        listGroup.append(getGroupLiberties(board,group))
    return listGroup

class myPlayer(PlayerInterface):
    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None
        self.corners= [20,24,40,56,60]

    def evaluate(self,board) :
        b = list(board)
        empty = b.count(0)
        win_score = 100-empty
        for i in self.corners:
            if b[i]==self._mycolor :
                self.corners.remove(i)
                return(pruneScore)
        black_score, white_score = self._board.compute_score()
        if (self._mycolor==1):
            my_score, oppo_score = black_score, white_score
        else :
            oppo_score,my_score  = black_score, white_score
        if ((my_score)>=(oppo_score*2) and oppo_score >4):
            return(pruneScore)
        oppo_color=self._board.flip(self._mycolor)
        my_groups,oppo_groups=getAllConnections(b,self._mycolor,oppo_color)
        my_groups_liberties=getAllGroupsLiberties(b,my_groups)
        oppo_groups_librties=getAllGroupsLiberties(b,oppo_groups)
        for g in my_groups_liberties :
            if g<=1 : 
                return((win_score-10000) / 2) 
        pt=0
        for g in oppo_groups_librties :
            if g==1 : 
                win_score+=50
            if g==0 :
                pt+=1
                if (pt==2) :
                    return(pruneScore)
                else :
                    win_score+=100
        for me in range(len(my_groups)) :
            if len(my_groups[me])>=2 :
                win_score+=len(my_groups[me])*my_groups_liberties[me]+my_groups_liberties[me]*5+20
        for op in range(len(oppo_groups)) :
            win_score-=len(oppo_groups[op])*oppo_groups_librties[op] 
        # Calculate scores for groups 
        my_groups_2liberties = my_groups_liberties.count(2)
        oppo_groups_2liberties = oppo_groups_librties.count(2)
        groups_score = oppo_groups_2liberties- my_groups_2liberties
        # calcule liberties's score
        liberties_group = sum(my_groups_liberties)-sum(oppo_groups_librties)
        x=normal(1, 0.1)
        return win_score + groups_score * x + liberties_group * x

    def alphaBeta(self,board,depth,alpha,beta,startingTime,deadline) :
        legalMoves = board.generate_legal_moves()
        myNextMove = False if board._nextPlayer == self._mycolor else True
        
        result = self.evaluate(board)
        currentTime = time()
        elapsedTime = (currentTime - startingTime)

        if (elapsedTime >= deadline or board.is_game_over() or (depth == 0) or (len(legalMoves) == 0) or (result >= pruneScore) or (result <= -pruneScore)) :
            return result
        
        if (myNextMove):
            for m in legalMoves :
                board.push(m)
                alpha = max([alpha, self.alphaBeta(board, depth - 1, alpha, beta, startingTime, deadline)])
                board.pop()
                if (beta <= alpha) :
                    break
            return alpha
        else :
            for m in legalMoves :
                board.push(m)
                beta = min([beta, self.alphaBeta(board, depth - 1, alpha, beta, startingTime, deadline)])
                board.pop()
                if (beta <= alpha) :
                    break
            return beta

    def iterativeDepthSearch(self,board,deadline):
        begin = time()
        finish = begin + deadline
        depth = 1
        result = 0
        while True:
            now =time()
            if (now >= finish) :
                break
            resultSh = self.alphaBeta(board, depth, -math.inf, math.inf, now, finish - now)
            if (resultSh >= pruneScore) :
                return resultSh
            result = resultSh
            depth+=1  
        return result

    def nextMove(self):
        myChoiceMove = None
        maximum = -math.inf
        beginTime = time()
        legalMoves = self._board.generate_legal_moves()
        #remove PASS
        legalMoves.remove(-1)
        if (len(legalMoves)<81) :
            black_score, white_score = self._board.compute_score()
            if (self._mycolor==1) :
                if self._board._lastPlayerHasPassed and black_score > white_score :
                    return -1
            if (self._mycolor==2) :
                if self._board._lastPlayerHasPassed and black_score < white_score :
                    return -1
            if len(legalMoves)==0 :
                return -1
        if len(legalMoves)>0 :
            for m in legalMoves :
                self._board.push(m)
                limitSearchTime = ((0.5) / len(legalMoves))
                gain = self.iterativeDepthSearch(self._board, limitSearchTime)
                self._board.pop()
                pruneScore = 20000
                if (gain >= pruneScore) :
                    return (m)
                if (gain > maximum) :
                    maximum = gain
                    myChoiceMove = m
        else :
            myChoiceMove = -1

        return myChoiceMove

    def getPlayerName(self):
        return "Team mbahloul001 rrekhis"
    
    def getPlayerMove(self):
        global pruneScore 
        pruneScore = 20000
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS"
        move = self.nextMove()
        
        self._board.push(move)
        
        # New here: allows to consider internal representations of legalMoves
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        self._board.prettyPrint()
        # move is an internal representation. To communicate with the interface I need to change if to a string
        return Goban.Board.flat_to_name(move) 

    def playOpponentMove(self, move):
        print("Opponent played ", move) # New here
        # the board needs an internal represetation to push the move.  Not a string
        self._board.push(Goban.Board.name_to_flat(move)) 

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")