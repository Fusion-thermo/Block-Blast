# Block Blast

How to use :
1) Connect your phone to the computer with scrpy : https://github.com/Genymobile/scrcpy
2) Open the app on your phone
3) Launch the script on your computer, it will see and click on the window of scrpy which is the same as playing on the phone.

Objectifs :

- Essayer de survivre le plus longtemps possible
- Y a-t-il une stratégie qui permet de ne jamais perdre ?
- Le jeu nous fait-il perdre volontairement ?

Ma stratégie finale :
- Tester toutes les places possibles pour une pièce en attribuant un score à chaque place
- Favorise les voisins et les bords
- Favorise le remplissage d'une ligne ou colonne
- Favorise la complétion d'une ligne ou colonne
- Pénalise la création de bloc isolé
- Pénalise la création de trous
- Toutes les combinaisons possibles d'ordre des 3 pièces sont testées
