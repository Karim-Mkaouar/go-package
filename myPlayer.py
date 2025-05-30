# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''

import time
import Goban 
from random import choice
from playerInterface import *
import random

TIME_LIMIT = 1.0  # secondes par coup
MAX_IDS_DEPTH = 6  # Limite de profondeur maximale pour l'IDS
class myPlayer(PlayerInterface):
    """Joueur de Go IA de base : greedy (score immédiat). À améliorer !"""

    def __init__(self, depth=1, max_moves=10):
        self._board = Goban.Board()
        self._mycolor = None
        self._opponent = None
        self._depth = depth
        self._max_moves = max_moves

    def getPlayerName(self):
        return "Karim & Hassen"

    def _move_priority(self, move):
        # Priorité : coins > bords > centre > 1ère ligne hors coins
        size = self._board._BOARDSIZE
        x, y = move % size, move // size
        corners = [(0,0), (0,size-1), (size-1,0), (size-1,size-1)]
        if (x, y) in corners:
            return 0  # Coin
        if x == 0 or x == size-1 or y == 0 or y == size-1:
            return 1  # Bord
        if x == 1 or x == size-2 or y == 1 or y == size-2:
            return 2  # 2e ligne
        return 3  # Centre

    def evaluate(self, fast=False):
        if self._board.is_game_over():
            score = self._board.final_go_score()
            if isinstance(score, tuple) and len(score) == 2:
                try:
                    black, white = float(score[0]), float(score[1])
                except Exception:
                    black, white = 0, 0
            elif isinstance(score, str):
                if score.startswith('B+'):
                    black = float(score[2:])
                    white = 0
                elif score.startswith('W+'):
                    black = 0
                    white = float(score[2:])
                elif '-' in score:
                    parts = score.split('-')
                    try:
                        black, white = float(parts[0]), float(parts[1])
                    except Exception:
                        black, white = 0, 0
                else:
                    black, white = 0, 0
            else:
                black, white = 0, 0
            if self._mycolor == Goban.Board._BLACK:
                return black - white
            else:
                return white - black
        # Heuristique rapide si fast=True : différence de pions uniquement
        blacks = sum(1 for i in range(self._board._BOARDSIZE**2) if self._board._board[i] == Goban.Board._BLACK)
        whites = sum(1 for i in range(self._board._BOARDSIZE**2) if self._board._board[i] == Goban.Board._WHITE)
        if fast:
            if self._mycolor == Goban.Board._BLACK:
                return blacks - whites
            else:
                return whites - blacks
        # Nouvelle heuristique avancée sans dépendre de myPackage.py
        size = self._board._BOARDSIZE
        board = self._board._board
        my_color = self._mycolor
        oppo_color = Goban.Board.flip(my_color)
        visited = set()
        my_groups = []
        oppo_groups = []
        my_groups_liberties = []
        oppo_groups_liberties = []
        # Groupes et libertés (sans import externe)
        def neighbors(idx):
            x, y = idx % size, idx // size
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < size and 0 <= ny < size:
                    yield ny*size+nx
        def group_liberties(idx, color, group_set):
            group = set()
            libs = set()
            stack = [idx]
            while stack:
                i = stack.pop()
                if i in group:
                    continue
                group.add(i)
                for n in neighbors(i):
                    if board[n] == 0:
                        libs.add(n)
                    elif board[n] == color and n not in group:
                        stack.append(n)
            group_set.update(group)
            return libs, group
        for i in range(size*size):
            if i in visited:
                continue
            if board[i] == my_color:
                group_set = set()
                libs, group = group_liberties(i, my_color, group_set)
                my_groups.append(list(group))
                my_groups_liberties.append(len(libs))
                visited.update(group)
            elif board[i] == oppo_color:
                group_set = set()
                libs, group = group_liberties(i, oppo_color, group_set)
                oppo_groups.append(list(group))
                oppo_groups_liberties.append(len(libs))
                visited.update(group)
        # Bonus pour capture imminente
        capture_bonus = 0
        for g in oppo_groups_liberties:
            if g == 1:
                capture_bonus += 30
            if g == 0:
                capture_bonus += 100
        # Malus pour groupes faibles
        weak_penalty = 0
        for g in my_groups_liberties:
            if g == 1:
                weak_penalty -= 40
        # Bonus pour taille de groupe et libertés
        group_score = 0
        for i, group in enumerate(my_groups):
            group_score += len(group) * my_groups_liberties[i] + my_groups_liberties[i] * 5
        for i, group in enumerate(oppo_groups):
            group_score -= len(group) * oppo_groups_liberties[i]
        # Score de base (territoire)
        blacks = sum(1 for i in range(size*size) if board[i] == Goban.Board._BLACK)
        whites = sum(1 for i in range(size*size) if board[i] == Goban.Board._WHITE)
        base_score = (blacks - whites) if my_color == Goban.Board._BLACK else (whites - blacks)
        # Pondération finale
        score = (
            base_score +
            0.2 * (sum(my_groups_liberties) - sum(oppo_groups_liberties)) +
            capture_bonus +
            weak_penalty +
            0.5 * group_score
        )
        return score

    def minimax(self, depth, maximizingPlayer, consecutive_passes=0):
        if depth == 0 or self._board.is_game_over() or consecutive_passes >= 2:
            return self.evaluate(fast=True), None
        moves = self._board.legal_moves()
        non_pass_moves = [move for move in moves if self._board.flat_to_name(move) != "PASS"]
        # Correction : on n'applique plus de limitation arbitraire sur le nombre de coups explorés
        # non_pass_moves = non_pass_moves[:self._max_moves]  # SUPPRIMÉ
        if not non_pass_moves:
            self._board.push(Goban.Board.name_to_flat("PASS"))
            value, _ = self.minimax(depth-1, not maximizingPlayer, consecutive_passes+1)
            self._board.pop()
            return value, None
        if maximizingPlayer:
            maxEval = float('-inf')
            best_move = None
            for move in non_pass_moves:
                self._board.push(move)
                eval, _ = self.minimax(depth-1, False, 0)
                self._board.pop()
                if eval > maxEval:
                    maxEval = eval
                    best_move = move
            return maxEval, best_move
        else:
            minEval = float('inf')
            best_move = None
            for move in non_pass_moves:
                self._board.push(move)
                eval, _ = self.minimax(depth-1, True, 0)
                self._board.pop()
                if eval < minEval:
                    minEval = eval
                    best_move = move
            return minEval, best_move

    def alphabeta(self, depth, alpha, beta, maximizingPlayer, consecutive_passes=0):
        if depth == 0 or self._board.is_game_over() or consecutive_passes >= 2:
            return self.evaluate(fast=True), None
        moves = self._board.legal_moves()
        non_pass_moves = [move for move in moves if self._board.flat_to_name(move) != "PASS"]
        # Trie les coups pour explorer d'abord coins/bords
        non_pass_moves.sort(key=self._move_priority)
        if not non_pass_moves:
            # Simulate a PASS
            self._board.push(Goban.Board.name_to_flat("PASS"))
            value, _ = self.alphabeta(depth-1, alpha, beta, not maximizingPlayer, consecutive_passes+1)
            self._board.pop()
            return value, None
        if maximizingPlayer:
            maxEval = float('-inf')
            best_move = None
            for move in non_pass_moves:
                self._board.push(move)
                try:
                    eval, _ = self.alphabeta(depth-1, alpha, beta, False, 0)
                finally:
                    self._board.pop()
                if eval > maxEval:
                    maxEval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return maxEval, best_move
        else:
            minEval = float('inf')
            best_move = None
            for move in non_pass_moves:
                self._board.push(move)
                try:
                    eval, _ = self.alphabeta(depth-1, alpha, beta, True, 0)
                finally:
                    self._board.pop()
                if eval < minEval:
                    minEval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return minEval, best_move

    def getPlayerMove(self):
        # 1. Vérification stricte : ne jamais jouer si la partie est finie
        if self._board.is_game_over():
            return "PASS"
        moves = self._board.legal_moves()
        # 2. Si la seule action légale est PASS, on retourne PASS immédiatement
        if len(moves) == 1 and self._board.flat_to_name(moves[0]) == "PASS":
            return "PASS"
        # 3. Vérification stricte de la fin (deux PASS consécutifs dans l'historique)
        history = getattr(self._board, '_history', [])
        if len(history) >= 2:
            last1 = self._board.flat_to_name(history[-1]) if isinstance(history[-1], int) else None
            last2 = self._board.flat_to_name(history[-2]) if isinstance(history[-2], int) else None
            if last1 == "PASS" and last2 == "PASS":
                return "PASS"
        # 4. Si aucun coup non-PASS n'est possible, on passe
        non_pass_moves = [move for move in moves if self._board.flat_to_name(move) != "PASS"]
        if len(non_pass_moves) == 0:
            return "PASS"
        # 5. Si le nombre de pierres sur le plateau est très faible en fin de partie, on passe (sécurité)
        blacks = sum(1 for i in range(self._board._BOARDSIZE**2) if self._board._board[i] == Goban.Board._BLACK)
        whites = sum(1 for i in range(self._board._BOARDSIZE**2) if self._board._board[i] == Goban.Board._WHITE)
        if blacks + whites < 5 and len(history) > 100:
            return "PASS"
        maximizing = (self._board._nextPlayer == self._mycolor)
        fast_score = self.evaluate(fast=True)
        # Nouvelle règle : si aucun coup ne permet d'améliorer le score rapide, on passe
        can_improve = False
        for move in non_pass_moves:
            self._board.push(move)
            score_after = self.evaluate(fast=True)
            self._board.pop()
            if (self._mycolor == Goban.Board._BLACK and score_after > fast_score) or (self._mycolor == Goban.Board._WHITE and score_after > fast_score):
                can_improve = True
                break
        if not can_improve:
            return "PASS"
        # Stratégie : passage automatique seulement si l'adversaire a passé ET qu'il reste moins de 10 coups
        total_moves = len(self._board._history) if hasattr(self._board, '_history') else 0
        max_moves_possible = self._board._BOARDSIZE * self._board._BOARDSIZE
        last_opponent_pass = False
        if total_moves >= 1:
            last_move = self._board._history[-1]
            if isinstance(last_move, int):
                last_opponent_pass = (self._board.flat_to_name(last_move) == "PASS")
        moves_left = max_moves_possible - total_moves
        allow_auto_pass = (last_opponent_pass and moves_left < 10)
        if allow_auto_pass:
            pass_score_limit = -10
            if (self._mycolor == Goban.Board._BLACK and fast_score < pass_score_limit) or (self._mycolor == Goban.Board._WHITE and fast_score < pass_score_limit):
                return "PASS"
        # Si je suis largement gagnant ET que tous les coups n'améliorent pas mon score, je passe aussi
        if (self._mycolor == Goban.Board._BLACK and fast_score > 20) or (self._mycolor == Goban.Board._WHITE and fast_score > 20):
            best_score = fast_score
            can_improve = False
            for move in non_pass_moves:
                self._board.push(move)
                score_after = self.evaluate(fast=True)
                self._board.pop()
                if (self._mycolor == Goban.Board._BLACK and score_after > best_score) or (self._mycolor == Goban.Board._WHITE and score_after > best_score):
                    can_improve = True
                    break
            if not can_improve:
                return "PASS"
        # Gestion du temps pour optimiser la profondeur de recherche
  
        start_time = time.time()
        best_move = None
        best_value = float('-inf') if maximizing else float('inf')
        depth = 1
        while depth <= MAX_IDS_DEPTH:
            elapsed = time.time() - start_time
            if elapsed > TIME_LIMIT:
                break
            try:
                if maximizing:
                    value, move = self.alphabeta(depth, float('-inf'), float('inf'), maximizing, 0)
                    if move is not None:
                        best_move = move
                        best_value = value
                else:
                    value, move = self.alphabeta(depth, float('-inf'), float('inf'), maximizing, 0)
                    if move is not None:
                        best_move = move
                        best_value = value
            except Exception as e:
                print(f"Erreur à la profondeur {depth} : {e}")
                break
            depth += 1
            if time.time() - start_time > TIME_LIMIT * 0.9:
                break
        if best_move is None:
            return "PASS"
        self._board.push(best_move)
        return Goban.Board.flat_to_name(best_move)

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



