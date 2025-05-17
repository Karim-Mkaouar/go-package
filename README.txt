myPlayer.py
-----------
Ce fichier contient toute l’IA du binôme pour le tournoi de Go.

- Heuristique avancée (evaluate) :
    - Calcule le score du plateau en prenant en compte du Différence de pions,Libertés des groupes, Groupes faibles/forts, Atari et Contrôle des coins.
    - En début de partie, l’IA privilégie la prise de coins pour contrôler la zone.
    - Si l’IA a le double du score adverse, elle considère la partie gagnée et arrête la recherche.
    - Si un groupe n’a plus de liberté, il est considéré comme perdu.
    - Si l’adversaire n’a plus de liberté, l’IA considère la victoire acquise.

- Gestion de la fin de partie:
    - L’IA ne joue jamais de coup illégal après la fin (vérification stricte dans getPlayerMove).
    - Retourne "PASS" si la partie est finie, si deux PASS consécutifs sont joués, ou si la seule action légale est PASS.

- Recherche de coup (Minimax/IDS/alphabeta) :
    - Utilise l’algorithme "iterative deepening search" (IDS) pour explorer les coups possibles jusqu’à une profondeur maximale, en respectant une limite de temps par coup.
    - IDS utilise l’algorithme Minimax avec élagage Alpha-Bêta pour accélérer la recherche et éviter les branches inutiles.
    - Le choix du coup se fait toujours parmi les coups légaux, en évitant tout coup illégal ou non pertinent.
-----------

-----------
Binome: 
    - Karim Mkaouar
    - Hassen Akrout
-----------





Goban.py 
---------

Fichier contenant les règles du jeu de GO avec les fonctions et méthodes pour parcourir (relativement) efficacement
l'arbre de jeu, à l'aide de legal_moves() et push()/pop() comme vu en cours.

Ce fichier sera utilisé comme arbitre dans le tournoi. Vous avez maintenant les fonctions de score implantés dedans.
Sauf problème, ce sera la methode result() qui donnera la vainqueur quand is_game_over() sera Vrai.

Vous avez un décompte plus précis de la victoire dans final_go_score()

Pour vous aider à parcourir le plateau de jeu, si b est un Board(), vous pouvez avoir accès à la couleur de la pierre
posée en (x,y) en utilisant b[Board.flatten((x,y))]


GnuGo.py
--------

Fichier contenant un ensemble de fonctions pour communiquer avec gnugo. Attention, il faut installer correctement (et
à part gnugo sur votre machine).  Je l'ai testé sur Linux uniquement mais cela doit fonctionner avec tous les autres
systèmes (même s'ils sont moins bons :)).


starter-go.py
-------------

Exemples de deux développements aléatoires (utilisant legal_moves et push/pop). Le premier utilise legal_moves et le
second weak_legal_moves, qui ne garanti plus que le coup aléatoire soit vraiment légal (à cause des Ko).

La première chose à faire est probablement de 


localGame.py
------------

Permet de lancer un match de myPlayer contre lui même, en vérifiant les coups avec une instanciation de Goban.py comme
arbitre. Vous ne devez pas modifier ce fichier pour qu'il fonctionne, sans quoi je risque d'avoir des problèmes pour
faire entrer votre IA dans le tournoi.


playerInterface.py
------------------

Classe abstraite, décrite dans le sujet, permettant à votre joueur d'implanter correctement les fonctions pour être
utilisé dans localGame et donc, dans le tournoi. Attention, il faut bien faire attention aux coups internes dans Goban
(appelés "flat") et qui sont utilisés dans legal_moves/weak_legal_moves et push/pop des coups externes qui sont
utilisés dans l'interface (les named moves). En interne, un coup est un indice dans un tableau 1 dimension
-1, 0.._BOARDSIZE^2 et en externe (dans cette interface) les coups sont des chaines de caractères dans "A1", ..., "J9",
"PASS". Il ne faut pas se mélanger les pinceaux.


myPlayer.py
-----------

Fichier que vous devrez modifier pour y mettre votre IA pour le tournoi. En l'état actuel, il contient la copie du
joueur randomPlayer.py


randomPlayer.py
---------------

Un joueur aléatoire que vous pourrez conserver tel quel


gnugoPlayer.py
--------------

Un joueur basé sur gnugo. Vous permet de vous mesurer à lui simplement.


namedGame.py
------------

Permet de lancer deux joueurs différents l'un contre l'autre.
Il attent en argument les deux modules des deux joueurs à importer.


EXEMPLES DE LIGNES DE COMMANDES:
================================

python3 localGame.py
--> Va lancer un match myPlayer.py contre myPlayer.py

python3 namedGame.py myPlayer randomPlayer
--> Va lancer un match entre votre joueur (NOIRS) et le randomPlayer
 (BLANC)

 python3 namedGame gnugoPlayer myPlayer
 --> gnugo (level 0) contre votre joueur (très dur à battre)

# README – IA de Go (Karim Mkouar & Hassen Akrout)




