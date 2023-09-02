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
    x0=10
    x=-1
    ref_fond=(48,74,139)
    grille=np.zeros(((y_max-y_min)//41+2,(x_max-x_min)//41+2))
    while (x+1)*decalage + x0 < (x_max-x_min)-1:
        #print("x",x, x*decalage+x0+x_min)
        x+=1
        y=0
        fond=True
        while (y+1)*decalage<(y_max-y_min)-1:
            #print(y,y*decalage+y_min)
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

ex_grille=np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0],
 [0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0],
 [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])


def creer_formes(grille):
    formes=[]
    carres_possibles=[(-1,-1),(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1)]
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
                        for c_poss in carres_possibles:
                            dl,dc=c_poss[0],c_poss[1]
                            if carre.l+dl<grille.shape[0] and carre.c+dc<grille.shape[1] and carre.l+dl>=0 and carre.c+dc>=0 and (grille[carre.l + dl,carre.c + dc] == 1).all():
                                grille[carre.l+dl,carre.c+dc] = 0
                                forme.carres.append(Carre(carre.l+dl,carre.c+dc))
                                nouveau.append(Carre(carre.l+dl,carre.c+dc))
                    frontiere=nouveau[:]
                #forme.affichage()
                forme.initialiser()
    return formes


def positionner(plateau,formes):
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
        plateau_ordre=np.copy(plateau_original)
        for numero in ordre:
            forme=formes[numero]
            scores=[]
            for l in range(plateau.shape[0] - forme.hauteur+1):
                for c in range(plateau.shape[1] - forme.largeur+1):
                    plateau_test_de_case=np.copy(plateau_ordre)
                    #vérifie si la place est prise
                    continuer=False
                    for carre in forme.carres:
                        if plateau_test_de_case[l+carre.l,c+carre.c] == 1:
                            continuer=True
                            print("place prise")
                            break
                    if continuer:
                        continue
                    #calcule le score en fonction des voisins puis en fonction des lignes ou colonnes remplies
                    score=0
                    for carre in forme.bords:
                        if l+carre.l == -1 or l+carre.l == plateau.shape[0] or c+carre.c == -1 or c+carre.c == plateau.shape[1]:
                            score+=1
                        else:
                            score+=plateau_test_de_case[l+carre.l,c+carre.c]
                    #place la pièce
                    for carre in forme.carres:
                        plateau_test_de_case[l+carre.l,c+carre.c] = 1
                    #supprime les colonnes pleines
                    for c in range(plateau.shape[1]):
                        if sum(plateau_test_de_case[l,c] for l in range(plateau.shape[0])) == plateau.shape[0]:
                            print("colonne pleine")
                            score+=20
                            for l in range(plateau.shape[0]):
                                plateau_test_de_case[l,c]=0
                    #supprime les lignes pleines
                    for l in range(plateau.shape[0]):
                        if sum(plateau_test_de_case[l,c] for c in range(plateau.shape[1])) == plateau.shape[1]:
                            print("ligne pleine")
                            score+=20
                            for c in range(plateau.shape[1]):
                                plateau_test_de_case[l,c]=0
            
                    scores.append(Carre(l,c,score,plateau_test_de_case))
            if len(scores)==0:
                #pas possible de placer ce bloc
                print("impossible")
                score_ordre=-1
                break
            #choisit la meilleure position
            scores.sort(key=trier_positions,reverse=True)
            best=scores[0]
            print(best.score)
            tour_actuel.positions[numero] = best
            plateau_ordre=np.copy(best.plateau)
        #print(plateau)
        if score_ordre >= 0:
            tour_actuel.score=score_ordre
            tour_actuel.plateau=plateau
            tours.append(tour_actuel)
    #sélectionne le plateau avec le meilleur score
    tours.sort(reverse=True,key=trier_tours)
    if len(tours) > 0:
        return tours[0]
    else:
        return "Perdu"


def bouger_formes(tour,formes):
    #calculer où lâcher la forme
    decalage=89
    x0, y0=1015,435
    ecart_vertical=210
    for numero in tour.ordre:
        forme=formes[numero]
        forme.relache_x = (x0 + tour.positions[numero].c * decalage) + forme.largeur*decalage//2 + 30
        forme.relache_y = (y0 + tour.positions[numero].l * decalage) + forme.hauteur*decalage//2 + ecart_vertical +10
        mouse.position = (forme.x_clic,forme.y_clic)
        sleep(0.3)
        mouse.press(Button.left)
        sleep(0.5)
        #mouse.position = (forme.relache_x,forme.relache_y)
        #mouse.move(forme.relache_x - forme.x_clic,forme.relache_y - forme.y_clic)
        a=(forme.relache_y - forme.y_clic) / (forme.relache_x - forme.x_clic)
        b=forme.y_clic - a*forme.x_clic
        dx=(forme.relache_x - forme.x_clic) / abs(forme.relache_x - forme.x_clic) * min(1,abs(1/a)) * 10
        x,y=forme.x_clic,forme.y_clic
        while y>forme.relache_y:
            #print(a,b,x,y)
            x+=dx
            y=a*x+b
            mouse.position=(x,y)
            sleep(0.00001)
        #print(forme.relache_x - forme.x_clic,forme.relache_y - forme.y_clic)
        sleep(0.7)
        mouse.release(Button.left)
        mouse.position = (955,1226)



#sleep(1)
#grille=lecture()
#print(ex_grille)
#mouse.move(100,100)
#formes=creer_formes(ex_grille)
#for i in formes:
#    i.affichage()

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
    print(grille)
    formes=creer_formes(grille)
    if len(formes)!=3:
        raise "Pas 3 formes"
    for i in formes:
        i.affichage()
    tour=positionner(plateau,formes)
    if isinstance(tour,str):
        fini=True
    else:
        print("ordre choisi",tour.ordre)
        plateau=np.copy(tour.plateau)
        print("plateau",plateau)
        bouger_formes(tour,formes)
        sleep(2)
