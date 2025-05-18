# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''

import time
import Goban 
from random import choice
from playerInterface import *
from utils import getGroupLiberties, getMyGroup, getOppoGroup, neighbors

class myPlayer(PlayerInterface):
    ''' Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and 
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy!

    '''

    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None
        self.corners = [0, 7, 56, 63] 
        self.time_left = 30 * 0.95 # # 95% du temps total pour prendre en compte les pertes de temps et les imprÃ©cisions

    def getPlayerName(self):
        return "M_BEN_AYED-Y_MAHJOUB"

    def getPlayerMove(self):
        if self.time_left <= 0:
            return "PASS"
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS"
        # rÃ©partir le temps restant sur les coups possibles
        # on fixe une borne infÃ©rieure de 0.2s et supÃ©rieure de 45s par coup
        start_move = time.time()
        nb_moves = max(len(self._board.generate_legal_moves()), 1)
        per_move = self.time_left / nb_moves
        move_time = min(max(per_move, 1), 45.0)
        
        move = self.NextMove(self._board, move_time) 
        self._board.push(move)
        
        elapsed = time.time() - start_move
        self.time_left = self.time_left - elapsed
        # New here: allows to consider internal representations of moves
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        self._board.prettyPrint()
        # move is an internal representation. To communicate with the interface I need to change if to a string
        return Goban.Board.flat_to_name(move) 

    def playOpponentMove(self, move):
        print("Opponent played ", move) # New here
        #Â the board needs an internal represetation to push the move.  Not a string
        self._board.push(Goban.Board.name_to_flat(move)) 

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")


    def alphaBeta(self, board, depth, alpha, beta, startingTime, deadline):
        """
            ImplÃ©mentation de l'algorithme alpha-bÃªta pour explorer l'arbre des coups.

            - board : Ã©tat actuel du plateau.
            - depth : profondeur maximale Ã  atteindre.
            - alpha, beta : bornes de l'Ã©lagage alpha-bÃªta.
            - startingTime : temps de dÃ©part de l'itÃ©ration.
            - deadline : temps maximum autorisÃ©.

            Retourne une Ã©valuation numÃ©rique de l'Ã©tat du jeu.
        """

        legalMoves = board.generate_legal_moves()
        myNextMove = board._nextPlayer != self._mycolor
        currentTime = time.time()
        if currentTime - startingTime >= deadline:
            return self.evaluate(board)
        if depth == 0 or board.is_game_over() or len(legalMoves) == 0:
            return self.evaluate(board)

        if myNextMove:
            value = float("-inf")
            for m in legalMoves:
                if time.time() - startingTime >= deadline:  # VÃ©rifiez le temps restant
                    break
                board.push(m)
                value = max(value, self.alphaBeta(board, depth - 1, alpha, beta, startingTime, deadline))
                board.pop()
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = float("inf")
            for m in legalMoves:
                if time.time() - startingTime >= deadline:  # VÃ©rifiez le temps restant
                    break
                board.push(m)
                value = min(value, self.alphaBeta(board, depth - 1, alpha, beta, startingTime, deadline))
                board.pop()
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value

    def iterativeDepending(self, board, deadline):
        begin = time.time()
        finishTime = begin + deadline
        depth = 1
        result = 0
        while True:
            now = time.time()
            if now >= finishTime:  # on arrÃªte lÃ©gÃ¨rement avant la limite
                break
            result = self.alphaBeta(board, depth, float("-inf"), float("inf"), now, finishTime - now)
            depth += 1
        return result

    def NextMove(self, board, deadline):
        """
            Calcule le meilleur coup Ã  jouer en utilisant l'algorithme alpha-bÃªta
            avec recherche itÃ©rative en profondeur.

            Retourne le coup choisi (en reprÃ©sentation interne).
        """
        if self.time_left <= 0:
            return -1
        myChoiceMove = None
        maximum = float("-inf")
        beginTime = time.time()
        legalMoves = board.generate_legal_moves()
        if -1 in legalMoves:
            legalMoves.remove(-1)  # enlever le coup PASS
        if len(legalMoves) == 0:
            return -1  # passer si aucun coup possible
        
        limitSearchTime = deadline / max(len(legalMoves),1)   
        for m in legalMoves:
            if time.time() - beginTime >= deadline:
                break
            board.push(m)
            gain = self.iterativeDepending(board, limitSearchTime)
            board.pop()
            if gain > maximum:
                maximum = gain
                myChoiceMove = m
            if time.time() - beginTime >= deadline:
                break

        print("score =", maximum)
        return myChoiceMove

    def evaluate(self, board):
        """
            Ã‰value l'Ã©tat actuel du plateau.

            - Prend en compte les scores des deux joueurs.
            - Analyse les groupes de pierres et leurs libertÃ©s.
            - PÃ©nalise les groupes faibles avec peu de libertÃ©s.

            Retourne un score numÃ©rique reprÃ©sentant l'avantage du joueur courant.
        """

        b = list(board)
        empty = b.count(0)
        black_score, white_score = board.compute_score()
        if self._mycolor == 1:
            my_score, oppo_score = black_score, white_score
        else:
            my_score, oppo_score = white_score, black_score
        
        #bonus pour les coins
        corner_bonus = sum(1 for c in self.corners if b[c] == self._mycolor) * 5
        #bonus pour les bords
        bords_bonus = sum(1 for i in range(len(b)) if b[i] == self._mycolor and (i % 8 == 0 or i % 8 == 7 or i < 8 or i >= 56)) * 2

        my_group = getMyGroup(board, self._mycolor)
        oppo_group = getOppoGroup(board, self._opponent)
        #on retourne les listes contenant le nombre de dergÃ© de libertÃ© pour chaque groupe.
        my_group_liberties = [getGroupLiberties(b, my_group, self._board.flip(self._mycolor)) for group in my_group]
        oppo_group_liberties = [getGroupLiberties(b, oppo_group, self._mycolor) for group in oppo_group]

        score = my_score - oppo_score + corner_bonus + bords_bonus  # base : diffÃ©rence de score

        #pÃ©naliser les groupes faibles (peu de libertÃ©s)
        for lib in my_group_liberties:
            if lib <= 1:
                score -= 10
        for lib in oppo_group_liberties:
            if lib <= 1:
                score += 10
        #favoriser des libertÃ©s dans le GO
        for g, lib in zip(my_group, my_group_liberties):
            score += len(g) + lib
        for g, lib in zip(oppo_group, oppo_group_liberties):
            score -= len(g) + lib
        #bonus pour les menaces de capture
        for lib in oppo_group_liberties:
            if lib == 1:
                score += 20  #menace immÃ©diate
            elif lib == 2:
                score += 10  #menace proche

        #l'Ã©valuation du territoire
        territory_score = 0
        for i in range(len(b)):
            if b[i] == 0:  # Case vide
                neighs = neighbors(i, b)
                my_count = sum(1 for n in neighs if b[n] == self._mycolor)
                oppo_count = sum(1 for n in neighs if b[n] == self._opponent)
                if my_count > oppo_count:
                    territory_score += 1
                elif oppo_count > my_count:
                    territory_score -= 1
        score += territory_score

        #bonus pour les connexions entre groupes
        for group in my_group:
            shared_liberties = set()
            for pos in group:
                shared_liberties.update(neighbors(pos, b))
            if any(b[n] == self._mycolor for n in shared_liberties):
                score += 5
        
        return score

