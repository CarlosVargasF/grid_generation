#!/usr/bin/env python
# -*-coding:utf-8-*-

'''
Code qui calcule la distance entre les pictogrammes d'une application de CAA
Prend en compte la difficulté du mouvement et la difficulté de la sélection
'''

# Importation du module mathématique
import math
import sys

inputFile = "ProloquoBrut.csv"
outputFile = "ArcsEtDistances.csv"
msgAide = "Usage: python distanceCalculation.py [-in inputFileName] [-out outputFileName]"

if len(sys.argv) == 3:
    if sys.argv[1] == "-in":
        inputFile = sys.argv[2]
    elif sys.argv[1] == "-out":
        outputFile = sys.argv[2]
    else:
        print(msgAide)
        sys.exit(2)

elif len(sys.argv) == 5:
    if sys.argv[1] == sys.argv[3]:
        print(msgAide)
        sys.exit(2)

    if sys.argv[1] == "-in":
        inputFile = sys.argv[2]        
    elif sys.argv[1] == "-out":
        outputFile = sys.argv[2]    
    else:
        print(msgAide)
        sys.exit(2)

    if sys.argv[3] == "-in":
        inputFile = sys.argv[4]
    elif sys.argv[3] == "-out":
        outputFile = sys.argv[4]    
    else:
        print(msgAide)
        sys.exit(2)

print("input file is " + inputFile)
print("output file is " + outputFile)

# Fichier brut à traiter
rawFile = open(inputFile, "r")

# Fichier d'écriture des arcs
# bowsFile = open(f'distances_{inputFile}.csv', "w")
bowsFile = open(outputFile, "w")

# Création de la liste des distances
disTab = []

# Création de la liste des liens entre les répertoires
linksList = []
linkCount = 0

# Définition du poids du mouvement
m = 1
# Définition du poids du temps de sélection
n = 1


# Traitement du fichier source
for lines in rawFile:
	lines = lines.lower()
	sentence = lines.strip()
	col = sentence.split("\t")

	# On gère le problème des lines semi vides créées par les liens entre les répertoires
	if len(col) > 4:
		# Décraration des variables
		words = col[0]
		column = col[2]
		line = col[1]
		page = col[3]
		iden = col[4]

		# Récupération des coordonnées x,y
		x = int(line)
		y = int(column)

		# On stocke les coordonnées l'ID et x,y dans une liste
		disTab.append([iden, x, y, words, page])

	# On récupère les liens entre les répertoires
	elif len(col) > 1:
		headLink = col[0]
		pointedLink = col[1]

		# On stocke les liens entre les répertoires
		linksList.append([headLink, pointedLink])

# On parcours la liste créé plus haut
for i in range(0, len(disTab)):
	# On crée une variable qui prend comme valeur l'ID du mot d'indice i
	refID = disTab[i][0]
	# On crée une variable qui prend comme valeur le nom de la page actuelle
	currentPage = disTab[i][4]
	# On créé une variable qui prend comme valeur le mot d'indice i
	mot = disTab[i][3]
	x1 = disTab[i][1]
	y1 = disTab[i][2]

	for j in range(i, len(disTab)):
		# On créé une nouvelle variable qui prend comme valeur l'ID du mot d'indice j
		ID = disTab[j][0]

		# On vérifie que l'on est toujours sur la bonne page
		currentPage2 = disTab[j][4]
		x2 = disTab[j][1]
		y2 = disTab[j][2]

		if currentPage2 == currentPage:
			# Si les deux IDs sont différents on récupère les coordonnées x et y de chacun
			if refID != ID:
				mot2 = disTab[j][3]

				# Calcul des distances Euclidiennes
				squaredDistance = (x1 - x2) ** 2 + (y1 - y2) ** 2
				pictoDistance = math.sqrt(squaredDistance)

				#Si le mot de d'arrivée de l'arc est un répertoire C=(P1,P2)m
				if "_r@" in ID :
					#On écrit la fomule sans le n
					bowsFile.write("Mot à Répertoire" + "\t" + refID + "\t" + ID + "\t" + str(pictoDistance * m) + "\n")
				else :
					#Si le pictogarmme départ et celui d'arrivée sont des mots C=(P1,P2)m+n
					# On écrit la formule normale
					bowsFile.write("Mot à Mot" + "\t" + refID + "\t" + ID + "\t" + str(pictoDistance * m + n) + "\n")
					bowsFile.write("Mot à Mot" + "\t" + ID + "\t" + refID + "\t" + str(pictoDistance * m + n) + "\n")

	# On écrit le lien entre un pictogramme directeur (plus, retour, pagination, flèche retour et répertoires) et la page
	if linkCount < len(linksList):
		# Formule correspondnat uniquement à l'action de sélection donc C=n
		bowsFile.write("Picto directeur à Page" + "\t" + linksList[linkCount][0] + "\t" + linksList[linkCount][1] + "\t" + str(n) + "\n")
		linkCount += 1

	# On écrit le lien entre la page et le pictogramme 
	# On calcule la disantce entre le lien de la page et des pictogrammes à partir du pictogramme en haut à gauche avec x=1 et y=1
	squaredDistance3 = (1 - x1) ** 2 + (1 - y1) ** 2
	pageToPicto = math.sqrt(squaredDistance3)

	#Si le pictogramme d'arrivée de l'arc est un répetoire C=(P(1,1)P2)m
	if "_r@" in disTab[i][0] :
		#On calcule sans le n
		bowsFile.write("Page à Répertoire" + "\t" + currentPage + "\t" + disTab[i][0] + "\t" + str(pageToPicto* m) + "\n")
	else :
		# Si le pictogramme de départ est une page et celui d'arrivée un mot C=(P(1,1)P2)m+n
		bowsFile.write("Page à Mot" + "\t" + currentPage + "\t" + disTab[i][0] + "\t" + str(pageToPicto * m + n) + "\n")


bowsFile.close()
rawFile.close()
