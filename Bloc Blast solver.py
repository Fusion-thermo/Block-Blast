from PIL import Image, ImageGrab
from time import sleep,time
import pyautogui #for absolutely no apparent reason removing this breaks the program, the positioning doesn't go where it is supposed to go.
from pynput.mouse import Button, Controller
from itertools import permutations
from Classes import *

mouse = Controller()


def lecture():
    x_min=1025
    y_min=1240
    x_max=1710
    y_max=1468
    im = ImageGrab.grab(bbox =(x_min,y_min,x_max,y_max))
    #im.show()
    px=im.load()
    decalage=41
    x0=30
    x=0
    ref_fond=(48,74,139)
    grille=np.zeros(((y_max-y_min)//41+2,(x_max-x_min)//41+2))
    while (x+1)*decalage + x0 < (x_max-x_min)-1:
        print("x",x)
        x+=1
        y=0
        fond=True
        while (y+1)*decalage<(y_max-y_min)-1:
            print(y,y*decalage,y_max-y_min)
            y+=1
            check_couleur=bonne_couleur(px[x*decalage + x0,y*decalage],ref_fond,0.1)
            if fond and not check_couleur:#sur le fond mais pas la couleur du fond = pas sur le fond
                fond=False
                grille[y,x]=1
            elif not check_couleur: #pas sur le fond et pas la couleur du fond = toujours pas sur le fond
                grille[y,x]=1
            elif not fond: #pas sur le fond mais couleur du fond = on est de nouveau sur le fond
                break
    return grille

# sleep(1)
# grille=lecture()
# print(grille)
# mouse.position = (10,10)

ex_grille=np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.],
 [0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0.],
 [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0.],
 [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.]])


def creer_formes(grille):
    formes=[]
    for ligne in range(grille.shape[0]):
        for colonne in range(grille.shape[1]):
            if grille[ligne,colonne] == 1:
                #récupérer les coordonnées de chaque 1 de la forme
                grille[ligne,colonne] = 0
                origine=Carre(ligne,colonne)
                frontiere=[origine]
                forme=Forme([origine])
                formes.append(forme)
                while len(frontiere)>0:
                    nouveau=[]
                    for carre in frontiere:
                        if carre.l+1<grille.shape[0] and (grille[carre.l+1,carre.c] == 1).all():
                            grille[carre.l+1,carre.c] = 0
                            forme.carres.append(Carre(carre.l+1,carre.c))
                            nouveau.append(Carre(carre.l + 1,carre.c))
                        if carre.c+1<grille.shape[1] and (grille[carre.l,carre.c + 1] == 1).all():
                            grille[carre.l,carre.c+1] = 0
                            forme.carres.append(Carre(carre.l,carre.c+1))
                            nouveau.append(Carre(carre.l,carre.c + 1))
                        if carre.l-1>0 and (grille[carre.l - 1,carre.c] == 1).all():
                            grille[carre.l-1,carre.c] = 0
                            forme.carres.append(Carre(carre.l-1,carre.c))
                            nouveau.append(carre(Carre.l - 1,carre.c))
                        if carre.c-1>0 and (grille[carre.l,carre.c - 1] == 1).all():
                            grille[carre.l,carre.c-1] = 0
                            forme.carres.append(Carre(carre.l,carre.c-1))
                            nouveau.append(Carre(carre.l,carre.c - 1))
                    frontiere=nouveau[:]
                forme.initialiser()
    return formes


def positionner(plateau,formes):
    score_positions=[]
    #le score d'un ordre de formes augmente avec le nombre de l ou c supprimés (donc remplis)
    #actuellement on cherche la position avec le plus de voisins puis on regarde si des l ou c sont pleins
    #on pourrait aussi choisir la position d'une forme selon si elle remplit ou non une l ou c
    #mais aussi selon les trous créés
    plateau_original=np.copy(plateau)
    tours=[]
    for ordre in permutations(range(3)):
        tour_actuel=Tour_de_jeu(ordre)
        print(ordre)
        score_ordre=0
        plateau=np.copy(plateau_original)
        for numero in ordre:
            forme=formes[numero]
            scores=[]
            for l in range(plateau.shape[0] - forme.hauteur):
                for c in range(plateau.shape[1] - forme.largeur):
                    #vérifie si la place est prise
                    continuer=False
                    for carre in forme.carres:
                        if plateau[l+carre.l,c+carre.c] == 1:
                            continuer=True
                            break
                    if continuer:
                        continue
                    #calcule le score en fonction des voisins
                    score=0
                    for carre in forme.bords:
                        if l+carre.l == -1 or l+carre.l == plateau.shape[0] or c+carre.c == -1 or c+carre.c == plateau.shape[1]:
                            score+=1
                        else:
                            score+=plateau[l+carre.l,c+carre.c]
                    scores.append(Carre(l,c,score))
            #choisit la meilleure position
            scores.sort(key=trier_positions,reverse=True)
            best=scores[0]
            tour_actuel.positions.append(best)
            #place la pièce
            for carre in forme.carres:
                plateau[best.l+carre.l,best.c+carre.c] = 1
            #print(plateau)
            #supprimer les colonnes pleines
            for c in range(plateau.shape[1]):
                if sum(plateau[l,c] for l in range(plateau.shape[0])) == plateau.shape[1]:
                    score_ordre+=1
                    for l in range(plateau.shape[0]):
                        plateau[l,c]=0
            #supprimer les lignes pleines
            for l in range(plateau.shape[0]):
                if sum(plateau[l,c] for c in range(plateau.shape[1])) == plateau.shape[0]:
                    score_ordre+=1
                    for c in range(plateau.shape[1]):
                        plateau[l,c]=0
        #print(plateau)
        tour_actuel.score=score_ordre
        tour_actuel.plateau=plateau
        tours.append(tour_actuel)
        #score_positions.append((score_ordre,np.copy(plateau)))
    #sélectionne le plateau avec le meilleur score
    #score_positions.sort(reverse=True,key=trier_score_positions)
    tours.sort(reverse=True,key=trier_tours)
    #plateau=np.copy(score_positions[0][1])
    #print(score_positions)
    return tours[0]


def bouger_formes(tour,formes):
    #calculer où lâcher la forme
    decalage=89
    x0, y0=1015,435
    for numero in tour.ordre:
        forme=formes[numero]
        forme.relache_x = (x0 + tour.positions[numero].c * decalage) + forme.largeur*decalage//2
        forme.relache_y = (y0 + tour.positions[numero].l * decalage) + forme.hauteur*decalage//2
        mouse.position = (forme.x_clic,forme.y_clic)
        sleep(0.3)
        mouse.press(Button.left)
        sleep(0.5)
        mouse.position = (forme.relache_x,forme.relache_y)
        sleep(0.6)
        mouse.release(Button.left)





# formes=creer_formes(ex_grille)
# # for i in formes:
# #     i.affichage()

# plateau=np.zeros((8,8))
# tour=positionner(plateau,formes)
# print(tour.ordre,tour.plateau)
# bouger_formes(tour,formes)

# #main
fini=False
sleep(1)
plateau=np.zeros((8,8))
while not fini:
    grille=lecture()
    formes=creer_formes(grille)
    tour=positionner(plateau,formes)
    plateau=np.copy(tour.plateau)
    bouger_formes(tour,formes)
    sleep(2)
