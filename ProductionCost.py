# coding=utf-8
import time
start_time = time.time()

# networkx package pour le graphe
import networkx as nx
from networkx import *
import sys
import os
import pickle

# matplotlib package et pyplot pour la visualisation
import matplotlib.pyplot as plt

phraseEntree = "phrasesEntrée.txt"
resultat = "Resultat.txt"
fichierDistances = "ArcsEtDistances.csv"

msgAide = "Usage: python ProductionCost.py [-in inputFileName] [-out outputFileName] [-dist arcsAndDistancesFileName]"

grid_files_path = 'grid_files/'

if len(sys.argv) == 3:
    if sys.argv[1] == "-in":
        phraseEntree = sys.argv[2]
    elif sys.argv[1] == "-out":
        resultat = sys.argv[2]
    else:
        print(msgAide)
        sys.exit(2)

elif len(sys.argv) == 5:
    if sys.argv[1] == sys.argv[3]:
        print(msgAide)
        sys.exit(2)

    if sys.argv[1] == "-in":
        phraseEntree = sys.argv[2]        
    elif sys.argv[1] == "-out":
        resultat = sys.argv[2]
    elif sys.argv[1] == "-dist":
        fichierDistances = sys.argv[2]
    else:
        print(msgAide)
        sys.exit(2)

    if sys.argv[3] == "-in":
        phraseEntree = sys.argv[4]
    elif sys.argv[3] == "-out":
        resultat = sys.argv[4]
    elif sys.argv[3] == "-dist":
        fichierDistances = sys.argv[4]
    else:
        print(msgAide)
        sys.exit(2)

elif len(sys.argv) == 7:
    if (sys.argv[1] == sys.argv[3]) or (sys.argv[1] == sys.argv[5] or (sys.argv[3] == sys.argv[5])):
        print(msgAide)
        sys.exit(2)
    if sys.argv[1] == "-in":
        phraseEntree = sys.argv[2]        
    elif sys.argv[1] == "-out":
        resultat = sys.argv[2]
    elif sys.argv[1] == "-dist":
        fichierDistances = sys.argv[2]
    else:
        print(msgAide)
        sys.exit(2)

    if sys.argv[3] == "-in":
        phraseEntree = sys.argv[4]
    elif sys.argv[3] == "-out":
        resultat = sys.argv[4]
    elif sys.argv[3] == "-dist":
        fichierDistances = sys.argv[4]
    else:
        print(msgAide)
        sys.exit(2)
    
    if sys.argv[5] == "-in":
        phraseEntree = sys.argv[6]
    elif sys.argv[5] == "-out":
        resultat = sys.argv[6]
    elif sys.argv[5] == "-dist":
        fichierDistances = sys.argv[6]
    else:
        print(msgAide)
        sys.exit(2)

elif len(sys.argv) != 1:
    print(msgAide)
    sys.exit(2)

print("arc_distances file is " + fichierDistances)
print("input file is " + phraseEntree)
print("output file is " + resultat)

text = open(phraseEntree, "r")
end = open(resultat, "w")


class WeightedPath:

    def __init__(self):
        self.path = []
        self.weight = 0


# Fonction qui établit le noeud à partir duquel il faut commencer à calculer un arc
'''
text = texte d'entrée
nodeList = liste de tous les noeuds du graphe
edgeList = tableau associatif de tous les arcs avec en clé le noeud tête et en valeurs le noeud pointé et le poids de l'arc
'''


def initialNode(text, nodeList, edgeList):
    path = []
    startNode = "accueil"
    stock = []
    totalWeight = 0
    # On parcours le fichier texte
    for line in text:
        line = line.lower()
        line = line.strip()
        # On évite les lignes vides
        if line != "":
            # On récupère le plus court chemin
            words = shortestPath(startNode, line, nodeList, edgeList)
            path = words.path
            # On récupère le dernier élément de la liste
            startNode = path[-1]
            # On ajoute le poids
            totalWeight += words.weight

        finalPath = []
        # On ajoute le premier élément de la liste au chemin final
        finalPath.append(path[0])
        # On parcours le chemin
        for i in range(1, len(path)):
            # Si on toruve deux mots qui se suivent différents
            if path[i - 1] != path[i]:
                # on ajoute l'elt au chemin final
                finalPath.append(path[i])
        # On stocke dans une liste le chemin et le poids total
        stock.append(str(finalPath) + " " + str(totalWeight))

    return stock


# Fonction qui prend en entrée un mot de la phrase et en fait une liste de noeuds possibles
'''
nodeList = liste de tous les noeuds du graphe
word = chaque word de la phrase d'entrée 
'''


def textToNodes(word, nodeList):
    candidatesNode = []
    # on parcours la liste des noeuds
    for i in range(0, len(nodeList)):
        # on découpe au '@' pour récupérer le mot d'origine au lieu de l'identifiant complet
        wordNode = nodeList[i].split("@")
        # Si le mot d'origine est égal au word de la phrase
        if wordNode[0] == word:
            # on l'ajoute à la liste des noeuds canidats potentiels
            candidatesNode.append(nodeList[i])
    return candidatesNode


# Fonction de calcul du plus court path
'''
initialNode = point de départ de la recherche dans le graphe
sentance = phrase d'entrée pour laquelle il faut calculer le cout de production
nodeList = liste de tous les noeuds du graphe
edgeList = tableau associatif de tous les arcs avec en clé le noeud tête et en valeurs le noeud pointé et le weight de l'arc
'''


def shortestPath(initialNode, sentance, nodeList, edgeList):
    initialNodes = []
    words = sentance.split(" ")
    shortestPath = []
    # Initialisation du poids total
    totalWeight = 0
    initialNodes.append(initialNode)

    # On créé la variable du chemin final
    finalPath = []
    pathList = []

    # On céé un nouveau graphe avec la liste des candidats
    coupleGraphe = nx.DiGraph()
    coupleGraphe.add_node("end")

    index = 0
    # On parcours la phrase
    for word in words:
        minWeight = 10000
        # On stocke dans une variable les mots "candidats" pour créer le plus court chemin        
        candidates = textToNodes(word, nodeList)

        # Pour chaque candidat
        for candidate in candidates:
            # On ajoute les candidats comme noeuds du sous graphe
            coupleGraphe.add_node(candidate)

            # Quand on arrive à l fin d ela phrase
            if index == len(words) - 1:
                # On créé un arc "end" de poids 0
                coupleGraphe.add_edge(candidate, "end", weight=0)
            elif index == 0:
                # On créé un arc "end" de poids 0
                coupleGraphe.add_edge("accueil", candidate, weight=0)

            # On parcours la liste des noeuds initiaux
            for firstNode in initialNodes:
                # On extrait le plus court chemin entre le premier noeud et le candidat avec la fonctionn "shortest_path "fonction Networkx
                try:
                    path = nx.shortest_path(G, source=firstNode, target=candidate)
                except nx.NetworkXNoPath:
                    print ("No path between %s and %s." % (firstNode, candidate))

                # On initialise le poids
                weight = 0
                # On parcours le chemin
                for i in range(1, len(path)):
                    edgePrevNode = edgeList[path[i - 1]]
                    for edge in edgePrevNode:
                        # On vérifie que le premier elt de la variable arc = shortest path de i
                        if edge[0] == path[i]:
                            weight += edge[1]                                                        

                # Si le poids est inférieur au poids minimum
                if weight < minWeight:
                    # Le poids min prend la valeur du poids
                    minWeight = weight

                pathList.append(path)

                coupleGraphe.add_edge(path[0], path[-1], weight=weight)
        # On modifie le point de départ de la fonction
        initialNodes = candidates
        index = index + 1

        # On calcule la somme des poids entre les arcs
        totalWeight += minWeight

    # On applique à nouveau une recherche du plus court chemin dans le sous graphe
    try:
        shortestpath = nx.shortest_path(coupleGraphe, source="accueil", target="end")
    except nx.NetworkXNoPath:
        print ("No path between %s and %s. Please check the input phrase" % ("accueil", "end"))
        sys.exit()
    # On céé le chemin final
    wordIndex = 0
    # On parcours la liste des chemins
    for path in pathList:
        if (shortestpath[wordIndex] == path[0]) and (shortestpath[wordIndex + 1] == path[-1]):
            for words in path:
                finalPath.append(words)
            wordIndex = wordIndex + 1
    print(finalPath, f'Cost : {totalWeight}')
    # On créé un objet
    weightedPath = WeightedPath()
    weightedPath.path = finalPath
    weightedPath.weight = totalWeight

    return weightedPath

# Fonction qui stocke un objet dans un fichier .pkl
'''
obj = lobjet à stocker
name = nom du fichier créé
'''
def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

# Fonction qui récupere un objet contenu dans un fichier .pkl
'''
name = nom du fichier cible
'''
def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

# stocker la taille actuelle et l'heure de la dernière modification du fichier fichierDistances
sizeCsv = os.stat(fichierDistances).st_size
modTimeCsv = os.stat(fichierDistances).st_mtime
fileStats = str(sizeCsv) + '-' + str(modTimeCsv)

# vérifier l'existence du fichier 'stat.txt'
if (not os.path.exists('stat.txt')):
    # create empty file
    open("stat.txt", "a").close()

# vérifier l'existence du fichier 'grap.txt'
if (not os.path.exists('graph.txt')):
    # create empty file
    open("graph.txt", "a").close()

# vérifier si les valeurs actuelles de sizeCsv et de modTimeCsv sont égales à celles du fichier stat.txt
with open("stat.txt", "r") as file: 
    #Si distanceCalculation.csv a été modifié, on crée à nouveau le graphe, la liste de noeuds et la table de liens. 
    if (file.read() != fileStats):
        
        # # On créé le graph G
        G = nx.DiGraph()

        # # On ouvre le fichier contenant la liste des pictogrammes
        f = open(fichierDistances, "r")

        edgeList = {}

        # # On parcours le fichier pour déterminer les noeuds, les arcs et les poids
        for line in f:
            line = line.strip()
            col = line.split('\t')

            # Addition du noeud au graphe
            G.add_node(col[1])

            # Création des arcs avec leurs poids
            G.add_edge(col[1], col[2], weight=col[3])

            # Création d'un tableau associatif qui comprendra les noeuds et les poids
            if col[1] in edgeList.keys():
                edgeList[col[1]].append((col[2], float(col[3])))
            else:
                edgeList[col[1]] = [(col[2], float(col[3]))]

        # # création de la liste des noeuds
        nodeList = list(G.nodes())

        nx.write_gpickle(G, "graph.txt")
        save_obj(edgeList, 'edges')
        save_obj(nodeList, 'nodes')
    
# métre-a-jour fichier stat.txt
with open("stat.txt", "w") as file: 
    file.writelines([fileStats])

# Lire le graphe, la liste de noeuds et la table de liens stockés en mémoire  
G = nx.read_gpickle("graph.txt")
nodeList = load_obj('nodes')
edgeList = load_obj('edges')

result = initialNode(text, nodeList, edgeList)

# Ecriture du résultat dans un fichier
for elt in result:
    end.write(elt + "\n")

# On choisi le type d'algorithme qui gère la disposition des noeuds dans l'espace
# pos = nx.spring_layout(G)

# f.close()
text.close()

print("--- %s seconds ---" % '{:5.5}'.format(time.time() - start_time))