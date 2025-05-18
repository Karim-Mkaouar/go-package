import numpy
#renvoie les voisins d'une case
def neighbors(st, b) :
    size=int(numpy.sqrt(len(b)))
    pos = divmod(st, size)
    neighbors = ((pos[0]+1, pos[1]), (pos[0]-1, pos[1]), (pos[0], pos[1]+1), (pos[0], pos[1]-1))
    n=[]
    for i in neighbors :
        if 0 <= i[0] < size and 0<= i[1] < size :
            n.append(size * i[0] + i[1])
    return(n)

def getStoneGroup(b,st,color,done,v):
    v.append(st)
    neighs = neighbors(st,b)
    neighs = list(set(neighs) - set(done))
    for case in neighs :
        done = list(dict.fromkeys(done))
        if b[case]==color  :
            done.append(case)
            getStoneGroup(b,case,color,done,v)
        else : 
            done.append(case)
    v = list(dict.fromkeys(v))
    return v

def getMyGroup(b, my_color):
    my_group = []
    for i in range(len(b)):
        if b[i] == my_color:
            #print("i", i)
            if not any(i in h for h in my_group):
                v = getStoneGroup(b, i, my_color, [i], [])
                my_group.append(v)
    return my_group

def getOppoGroup(b, oppo_color):
    oppo_group = []
    for i in range(len(b)):
        if b[i] == oppo_color:
            if not any(i in h for h in oppo_group):
                v = getStoneGroup(b, i, oppo_color, [i], [])
                oppo_group.append(v)
    return oppo_group

"""
    ici on chereche Ã  calculer le nombre de libertÃ©s pour chaque groupe donnÃ©.
"""
def getGroupLiberties(b, gr, oppo):
    """
    Calcule le nombre de libertÃ©s pour un groupe donnÃ©.
    """
    k = []
    for group in gr:  # Parcourt chaque groupe
        for i in group:  # Parcourt chaque position dans le groupe
            v = neighbors(i, b)
            v = list(set(v) - set(group))
            k += v
    k = list(dict.fromkeys(k))
    liberties_degree = 0
    opp_neighbor = 0
    for i in k:
        if b[i] == oppo:
            opp_neighbor += 1
        elif b[i] == 0:
            liberties_degree += 1
    return liberties_degree

