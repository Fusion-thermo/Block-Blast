import numpy as np

def bonne_couleur(mesure, reference, ecart_admissible):
    correct=True
    for i in range(3):
        if abs(mesure[i]-reference[i]) > ecart_admissible*255:
            correct=False
    return correct

class Mouvement():
    def __init__(self,l,c,score,plateau):
        self.l=l
        self.c=c
        self.score=score
        self.plateau=plateau

class Carre():
    def __init__(self,l,c,score=0):
        self.l=l
        self.c=c
        self.score=score

class Forme:
    def __init__(self,carres):
        self.carres=carres
        self.largeur=0
        self.hauteur=0
        self.bords=[]
        self.x_clic=0
        self.y_clic=0
        self.x_relache=0
        self.y_relache=0
    def initialiser(self):
        #définit le pixel où cliquer pour déplacer la forme
        #en colonnes : le milieu de la forme
        #lorsqu'on clique sur une forme, le centre (à la fois l et c) se déplace de la ligne centrale invisible des 3 formes à la bordure basse de l'écran
        #ligne invisible en y=1355, la bordure du bas (qui correspond au centre de la pièce) et est en 1145
        #donc lorsqu'on clique au centre de la forme le centre de la nouvelle pièce se situe 210 pixels plus haut
        x_min=1025
        y_min=1240
        decalage=41
        x0=30

        min_l=100
        max_l=0
        min_c=100
        max_c=0
        for carre in self.carres:
            if carre.l<min_l:
                min_l=carre.l
            if carre.l>max_l:
                max_l=carre.l
            if carre.c<min_c:
                min_c=carre.c
            if carre.c>max_c:
                max_c=carre.c
        self.largeur=max_c-min_c+1
        self.hauteur=max_l-min_l+1
        self.x_clic=x_min + (min_c * decalage + x0) + self.largeur*decalage//2 #début bbox + pixel de la forme le plus à gauche + moitié de la largeur
        self.y_clic=y_min + (min_l * decalage) + self.hauteur*decalage//2 #début bbox + pixel de la forme le plus en haut + moitié de la largeur
        #pour avoir des coordonnées qui partent de 0,0 dans le coin en haut à gauche de la forme
        for carre in self.carres:
            carre.l-=min_l
            carre.c-=min_c
        #définir les carrés au bord
        coos=[(carre.l,carre.c) for carre in self.carres]
        for carre in self.carres:
            if (carre.l+1,carre.c) not in coos:
                self.bords.append(Carre(carre.l+1,carre.c))
                coos.append((carre.l+1,carre.c))
            if (carre.l-1,carre.c) not in coos:
                self.bords.append(Carre(carre.l-1,carre.c))
                coos.append((carre.l-1,carre.c))
            if (carre.l,carre.c+1) not in coos:
                self.bords.append(Carre(carre.l,carre.c+1))
                coos.append((carre.l,carre.c+1))
            if (carre.l,carre.c-1) not in coos:
                self.bords.append(Carre(carre.l,carre.c-1))
                coos.append((carre.l,carre.c-1))
        self.carres.sort(key=trier_carres)
        self.bords.sort(key=trier_carres)
    def affichage(self):
        print("Carres",[(carre.l,carre.c) for carre in self.carres])
        print("bords",[(carre.l,carre.c) for carre in self.bords])

def trier_carres(carre):
    return (carre.l,carre.c)
def trier_positions(carre):
    return carre.score
def trier_score_positions(score):
    return score[0]
def trier_tours(tour):
    return tour.score

class Tour_de_jeu():
    def __init__(self,ordre,score=0,plateau=np.zeros((8,8))):
        self.ordre=ordre
        self.positions=[0,0,0]
        self.score=score
        self.plateau=plateau
    def affichage(self):
        print(self.ordre,[(carre.l,carre.c,carre.score) for carre in self.positions],self.score)