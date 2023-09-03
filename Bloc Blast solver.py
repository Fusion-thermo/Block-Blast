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
    px=im.load()
    decalage=89
    l0=45
    c0=45
    ref_fond=(35,45,85)
    plateau=np.zeros((8,8))
    for l in range(8):
        for c in range(8):
            if not bonne_couleur(px[l*decalage + l0,c*decalage+c0],ref_fond,0.1):
                plateau[c,l]=1
    return plateau

def lecture_grille():
    x_min=1025
    y_min=1240
    x_max=1710
    y_max=1468
    im = ImageGrab.grab(bbox =(x_min,y_min,x_max,y_max))
    px=im.load()
    decalage=41
    x0=10
    x=-1
    ref_fond=(48,74,139)
    grille=np.zeros(((y_max-y_min)//41+2,(x_max-x_min)//41+2))
    while (x+1)*decalage + x0 < (x_max-x_min)-1:
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

def compte_trous(plateau):
    trous=[]
    carres_possibles=[(-1,0),(0,1),(1,0),(0,-1)]
    for ligne in range(8):
        for colonne in range(8):
            if plateau[ligne,colonne] == 0:
                plateau[ligne,colonne] = 1
                frontiere=[Carre(ligne,colonne)]
                nombre=1
                while len(frontiere)>0:
                    nouveau=[]
                    for carre in frontiere:
                        for c_poss in carres_possibles:
                            dl,dc=c_poss[0],c_poss[1]
                            if carre.l+dl<8 and carre.c+dc<8 and carre.l+dl>=0 and carre.c+dc>=0 and (plateau[carre.l + dl,carre.c + dc] == 0):
                                plateau[carre.l+dl,carre.c+dc] = 1
                                nouveau.append(Carre(carre.l+dl,carre.c+dc))
                                nombre+=1
                    frontiere=nouveau[:]
                trous.append(nombre)
    return trous

def positionner(plateau,formes):
    #pour chaque ordre possible, on parcourt les 3 numéros, et pour chauqe numéro on teste toutes les placements possibles
    #venant du précédent numéro. Ce qui permet de tester toutes les possibilités de placement des 3 formes
    plateau_original=np.copy(plateau)
    tours=[] #tous les placements possibles des 3 formes pour tous les ordres possibles
    #lorsque 2 formes sont identiques on peut diviser par 2 le nombre de possibilités
    deja_vu=[]
    remplissage=np.count_nonzero(plateau)
    for ordre in permutations(range(3)):
        vu=False
        for permut in deja_vu:
            compte=0
            for i in range(3):
                if [(carre.l,carre.c) for carre in formes[permut[i]].carres] == [(carre.l,carre.c) for carre in formes[ordre[i]].carres]:
                    compte+=1
            if compte==3:
                print("Ordre identique (2 formes identiques)")
                vu=True
                break
        if vu:
            continue
        deja_vu.append(ordre)
        #print(ordre)
        tour_actuel=Tour_de_jeu(ordre)
        tour_actuel.plateau=np.copy(plateau_original)
        possible=True
        tours_ordre=[tour_actuel]
        for numero in ordre:
            tours_numero=[]
            forme=formes[numero]
            for tour in tours_ordre:
                tours_case=[]
                for l in range(8 - forme.hauteur+1):
                    for c in range(8 - forme.largeur+1):
                        #vérifie si la place est prise
                        continuer=False
                        for carre in forme.carres:
                            if tour.plateau[l+carre.l,c+carre.c] == 1:
                                continuer=True
                                break
                        if continuer:
                            continue
                        plateau_test_de_case=np.copy(tour.plateau)
                        #calcule le score en fonction des voisins
                        score=0
                        for carre in forme.bords:
                            if l+carre.l == -1 or l+carre.l == 8 or c+carre.c == -1 or c+carre.c == 8:
                                score+=1
                            else:
                                score+=plateau_test_de_case[l+carre.l,c+carre.c]
                        #place la pièce
                        for carre in forme.carres:
                            plateau_test_de_case[l+carre.l,c+carre.c] = 1
                        #supprime les colonnes pleines et augmente le score
                        bonus=30
                        lignes,colonnes=[],[]
                        for col in range(8):
                            if sum(plateau_test_de_case[line,col] for line in range(8)) == 8:
                                #print("colonne pleine")
                                score+=bonus
                                colonnes.append(col)
                        #supprime les lignes pleines et augmente le score
                        for line in range(8):
                            if sum(plateau_test_de_case[line,col] for col in range(8)) == 8:
                                #print("ligne pleine")
                                score+=bonus
                                lignes.append(line)
                        for col in colonnes:
                            for line in range(8):
                                plateau_test_de_case[line,col]=0
                        for line in lignes:
                            for col in range(8):
                                plateau_test_de_case[line,col]=0
                        #favorise le remplissage de l et c
                        coeff=2 #le coeff doit être plus grand que 1 pour avoir un effet multiplicatif sur la complétion d'une l ou c
                        for col in range(8):
                            score+=sum(plateau[line,col] for line in range(8)) * coeff
                            score+=sum(plateau[col,line] for line in range(8)) * coeff
                        #pénalise la création de blocs de 1 carré
                        coeff=6
                        carres_possibles=[(-1,0),(0,1),(1,0),(0,-1)]
                        for line in range(8):
                            for col in range(8):
                                if plateau_test_de_case[line,col]==1:
                                    voisins=0
                                    for carre in carres_possibles:
                                        if carre[0]+line>=8 or carre[1]+col>=8 or carre[0]+line<0 or carre[1]+col<0 or (plateau_test_de_case[carre[0]+line,carre[1]+col] == 0):
                                            voisins+=1
                                    if voisins>3:
                                        score-=voisins*coeff

                        #pénalise les trous
                        coeff=2
                        trous=compte_trous(np.copy(plateau_test_de_case))
                        for trou in trous:
                            score -= (len(trous)-1) * 1/trou * coeff

                        tour_test_de_case=Tour_de_jeu(ordre,score+tour.score,np.copy(plateau_test_de_case))
                        tour_test_de_case.positions=tour.positions[:]
                        tour_test_de_case.positions[numero] = Carre(l,c,score)
                        tours_case.append(tour_test_de_case)
                if len(tours_case)==0:
                    #pas possible de placer ce bloc
                    continue
                plateau_vu=[]
                score_vu=[]
                for tour_case in tours_case:
                    #pour réduire le nombre de situations à tenter on supprime les opérations qui donnent le même résultat
                    #il ne faut pas le faire au score car 2 plateaux différents peuvent avoir le même score
                    
                    #faire toutes les possibilités est trop lent et inutile s'il y a peu de cases
                    if remplissage>15:
                        #visiblement cela ne sert à rien
                        # passer=False
                        # for vu in plateau_vu:
                        #     if (tour_case.plateau == vu).all():
                        #         passer=True
                        #         break
                        # if not passer:
                        #     tours_numero.append(tour_case)
                        #     plateau_vu.append(np.copy(tour_case.plateau))
                        # else:
                        #     print("égalité")
                        tours_numero.append(tour_case)
                    else:
                        #ici on le fait au score car lorsqu'il y a peu de cases c'est trop long de tester toutes les possibilités
                        passer=False
                        for vu in score_vu:
                            if vu==tour_case.score:
                                passer=True
                                break
                        if not passer:
                            tours_numero.append(tour_case)
                            score_vu.append(tour_case.score)

            if len(tours_numero)==0:
                print("impossible")
                possible=False
                break
            tours_ordre=tours_numero[:]
        if possible:
            for tour in tours_ordre:
                tours.append(tour)
    #sélectionne le plateau avec le meilleur score
    if len(tours) > 0:
        tours.sort(reverse=True,key=trier_tours)
        print("{} plateaux possibles".format(len(tours)))
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
        sleep(0.4)
        mouse.press(Button.left)
        sleep(0.5)
        a=(forme.relache_y - forme.y_clic) / (forme.relache_x - forme.x_clic)
        b=forme.y_clic - a*forme.x_clic
        dx=(forme.relache_x - forme.x_clic) / abs(forme.relache_x - forme.x_clic) * min(1,abs(1/a)) * 12
        x,y=forme.x_clic,forme.y_clic
        while y>forme.relache_y:
            x+=dx
            y=a*x+b
            mouse.position=(x,y)
            sleep(0.00001)
        sleep(0.5)
        mouse.release(Button.left)
        mouse.position = (955,1226)

# #main
fini=False
sleep(1)
#plateau=np.zeros((8,8))
plateau=lecture_plateau()
#print(plateau)
while not fini:
    grille=lecture_grille()
    #print(grille)
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
        #print("ordre choisi",tour.ordre)
        plateau=np.copy(tour.plateau)
        print(plateau)
        bouger_formes(tour,formes)
        sleep(1)
