# Block Blast


WARNING : 

This script worked in August 2023, since then there has been updates on the mobile app wich renders this code obsolete.
The two mains changes that should be taken into account are : 
1) There can be less than three shapes proposed
2) The distance between the pointer and the position of the moving piece is not always identical anymore (distance increases with vertical position)


How to use and set up :

1) Connect your phone to the computer with scrpy : https://github.com/Genymobile/scrcpy

2) Set the scrpy window at full screen

3) Open the app Block Blast on your phone and select Classic mode

4) Change pixels coordinates and maybe pixels rgb values in the code if your computer screen is not 2736x1824 like mine.
Maybe try to change them proportionnaly to your dimensions, if it doesn't work try tweaking it manually using the file Ecran annoté.png
(arrows do not point to the exact pixel but close enough).
It may be difficult because there are a lot of lines where the pixel dimensions where fine tuned to my screen, 
if you have to also tweak it you will probably have to go through trial and error to find the correct ones.
You can take a full screenshot and paste it on paint.net or other to get the exact coordinates on the screenshot.

5) Launch the script on your computer and change your window to the full screen scrpy window, if the delay of 1 second is too brief you can change it too.

6) Watch as it plays automatically.

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
