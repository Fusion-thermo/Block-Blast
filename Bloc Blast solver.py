from PIL import Image, ImageGrab
from time import sleep,time
import pyautogui #for absolutely no apparent reason removing this breaks the program, the positioning doesn't go where it is supposed to go.
from pynput.mouse import Button, Controller
from itertools import permutations
from Classes import *

mouse = Controller()

def lecture_plateau():
    x_min=1015
    y_min=434
    x_max=1722
    y_max=1142
    im = ImageGrab.grab(bbox =(x_min,y_min,x_max,y_max))
    #im.show()
    px=im.load()
    decalage=89
    l0=45
    c0=45
    ref_fond=(35,45,85)
    plateau=np.zeros((8,8))
    for l in range(8):
        for c in range(8):
        #print("x",x, x*decalage+x0+x_min)
            if not bonne_couleur(px[l*decalage + l0,c*decalage+c0],ref_fond,0.1):
                plateau[c,l]=1
    return plateau

def lecture_grille():
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
# grille=lecture_grille()
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
                            if carre.l+dl<grille.shape[0] and carre.c+dc<grille.shape[1] and carre.l+dl>=0 and carre.c+dc>=0 and (grille[carre.l + dl,carre.c + dc] == 1):
                                grille[carre.l+dl,carre.c+dc] = 0
                                forme.carres.append(Carre(carre.l+dl,carre.c+dc))
                                nouveau.append(Carre(carre.l+dl,carre.c+dc))
                    frontiere=nouveau[:]
                #forme.affichage()
                forme.initialiser()
    return formes


def positionner(plateau,formes):
    plateau_original=np.copy(plateau)
    tours=[]
    for ordre in permutations(range(3)):
        tour_actuel=Tour_de_jeu(ordre)
        print(ordre)
        score_ordre=0
        #plateau=np.copy(plateau_original)
        plateau_ordre=np.copy(plateau_original)
        possible=True
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
                    bonus=50
                    for col in range(plateau.shape[1]):
                        if sum(plateau_test_de_case[line,col] for line in range(plateau.shape[0])) == plateau.shape[0]:
                            print("colonne pleine")
                            score+=bonus
                            for line in range(plateau.shape[0]):
                                plateau_test_de_case[line,col]=0
                    #supprime les lignes pleines
                    for line in range(plateau.shape[0]):
                        if sum(plateau_test_de_case[line,col] for col in range(plateau.shape[1])) == plateau.shape[1]:
                            print("ligne pleine")
                            score+=bonus
                            for col in range(plateau.shape[1]):
                                plateau_test_de_case[line,col]=0
                    #favorise le remplissage de l et c
                    coeff=2
                    for col in range(plateau.shape[1]):
                        score+=sum(plateau[line,col] for line in range(plateau.shape[0])) * coeff
                    for line in range(plateau.shape[0]):
                        score+=sum(plateau[line,col] for col in range(plateau.shape[1])) * coeff
                    #pénaliser la création de 0 avec 4 voisins
                    coeff=6
                    carres_possibles=[(-1,0),(0,1),(1,0),(0,-1)]
                    for line in range(plateau.shape[0]):
                        for col in range(plateau.shape[1]):
                            if plateau_test_de_case[line,col]==0:
                                voisins=0
                                for carre in carres_possibles:
                                    if carre[0]+line>=plateau.shape[0] or carre[1]+col>=plateau.shape[1] or carre[0]+line<0 or carre[1]+col<0 or (plateau_test_de_case[carre[0]+line,carre[1]+col] == 1):
                                        voisins+=1
                                if voisins>3:
                                    score-=voisins*coeff

                    scores.append(Carre(l,c,score,plateau_test_de_case))
            if len(scores)==0:
                #pas possible de placer ce bloc
                print("impossible")
                possible=False
                break
            #choisit la meilleure position
            scores.sort(key=trier_positions,reverse=True)
            best=scores[0]
            print(best.score)
            tour_actuel.positions[numero] = best
            plateau_ordre=np.copy(best.plateau)
            score_ordre+=best.score
        #print(plateau)
        if possible:
            tour_actuel.score=score_ordre
            tour_actuel.plateau=plateau_ordre
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
        forme.relache_x = (x0 + tour.positions[numero].c * decalage) + forme.largeur*decalage//2 + 35
        forme.relache_y = (y0 + tour.positions[numero].l * decalage) + forme.hauteur*decalage//2 + ecart_vertical +10
        mouse.position = (forme.x_clic,forme.y_clic)
        sleep(0.3)
        mouse.press(Button.left)
        sleep(0.5)
        #mouse.position = (forme.relache_x,forme.relache_y)
        #mouse.move(forme.relache_x - forme.x_clic,forme.relache_y - forme.y_clic)
        a=(forme.relache_y - forme.y_clic) / (forme.relache_x - forme.x_clic)
        b=forme.y_clic - a*forme.x_clic
        dx=(forme.relache_x - forme.x_clic) / abs(forme.relache_x - forme.x_clic) * min(1,abs(1/a)) * 8
        x,y=forme.x_clic,forme.y_clic
        while y>forme.relache_y:
            #print(a,b,x,y)
            x+=dx
            y=a*x+b
            mouse.position=(x,y)
            sleep(0.00001)
        #print(forme.relache_x - forme.x_clic,forme.relache_y - forme.y_clic)
        sleep(0.9)
        mouse.release(Button.left)
        mouse.position = (955,1226)



#sleep(1)
#grille=lecture_grille()
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
#plateau=np.zeros((8,8))
plateau=lecture_plateau()
print(plateau)
while not fini:
    grille=lecture_grille()
    print(grille)
    formes=creer_formes(grille)
    if len(formes)!=3:
        raise Exception("Pas 3 formes")
    for i in formes:
        i.affichage()
    tour=positionner(plateau,formes)
    if isinstance(tour,str):
        print('Aucune solution possible')
        fini=True
    else:
        print("ordre choisi",tour.ordre)
        plateau=np.copy(tour.plateau)
        print("plateau\n",plateau)
        bouger_formes(tour,formes)
        sleep(2)
