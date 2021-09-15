#!python -m pip install networkx
#!python -m pip install matplotlib==2.2.3
#!python -m pip install ipywidgets
#!python -m pip install graphviz
#!python -m pip install pandas
#!python -m pip install pudb
#!python -m pip install nbconvert
#!python -m pip install nbconvert -U
#coding=utf-8


# %matplotlib
import matplotlib.pyplot as plt
import random
import copy
import math
import numpy as np
import sys
from graphviz import Digraph

# import time
import networkx as nx
from networkx import *
import pickle
from argparse import ArgumentParser
import pathlib

# ALGORITHME GÉNÉTIQUE
from deap import base
from deap import creator
from deap import tools


class Slot():
    '''Représente l'element le plus basique d'une grille.
    
    Il peut contenir un pictogramme ou être vide (None).

    :word: mot lié au pictpgramme
    :type word: chaîne de caractères
    :is_core: boolean qui indique si le mot associé fait partie du vocabulaire de base.
    :type is_core: boolean
    :page_destination: Eventuelle page de destination liée au pictogramme. Peut être nulle.
    :type page_destination: class: `Page`
    '''

    def __init__(self, word, is_core, page_destination):        
        '''Constructeur        
        '''        

        self.__word = copy.copy(word)
        self.__is_core = copy.copy(is_core)
        self.__page_destination = copy.copy(page_destination)

    def get_word(self):
        '''Accesseur
        
        :return: Renvoi le mot lié au slot
        :rtype: châine de charactères        
        '''

        return self.__word

    def get_is_core(self):
        '''Accesseur

        :return: Renvoi le boolean `is_core` du slot
        :rtype: boolean        
        '''

        return self.__is_core

    def get_page_destination(self):
        '''Accesseur
        
        :return: Renvoi la page de destination du slot
        :rtype: class: `Page`        
        '''

        return self.__page_destination

    def set_word(self, word):
        '''Setter. Mettre en place le mot du slot
        
        :word: mot à metre en place
        :type word: chaîne de caractères        
        '''

        self.__word = word

    def set_page_destination(self, page):
        '''Setter. Mettre en place la page de destination du slot
        
        :page: page à mettre en place
        :type page: class: `Page`        
        '''

        self.__page_destination = page

    def __str__(self):
        '''Méthode de affichage du slot
        
        :return: Renvoi l'information du slot
        :rtype: chaîne de charactères
        '''

        dest = self.__page_destination
        if dest:
            dest = self.__page_destination.get_name()

        return f'{self.__word}({dest})'


class Page():
    '''Une page est un arrangement 2D de slots avec une taille fixe

    :param name: le nom de la page
    :type name: chaîne de caractères
    :param row_size: La hauteur de la table (nombre de lignes)
    :type row_size: entier
    :param col_size: La largueur de la table (nombre de colonnes)
    :type col_size: entier
    '''

    def __init__(self, name, row_size, col_size):
        '''Constructeur'''  

        self.__name = name
        self.__row_size = row_size
        self.__col_size = col_size
        self.__full = False
        self.__slots = []
        self.__fill()
        self.__last_R = 0
        self.__last_C = 0


    def __fill(self):
      '''Initialise chacun des slots à None'''

      self.__slots = []
      for i in range(0, self.__row_size) :
        self.__slots.append([None])
        for j in range(0, self.__col_size) :
          self.__slots[i].append(None)


    def set_slot(self, slot, num_row, num_col):
      '''Setter. Ajoute le Slot `slot` en position `num_row`, `num_col` dans la page

      :param slot: slot à mettre en place 
      :type slot: class `Slot`
      :param num_row: nombre de la ligne 
      :type num_row: entier
      :param num_col: nombre de la colonne
      :type num_col: entier
      :raises Exception: exception de dépassement des indices.
      :return: renvoie l'ancienne valeur du slot
      :rtype: class `Slot`
      '''

      if (num_row >= self.__row_size) or (num_col >= self.__col_size):
        print(f'row={num_row}, col={num_col}')
        print(f'row_size={self.__row_size}, col_size={self.__col_size}')
                
        raise Exception('Error: slot row or col out of bounds') 

      old_value = self.__slots[num_row][num_col]
      self.__slots[num_row][num_col] = slot

      return old_value


    def set_name(self, name):
      '''Setter. Mettre en place le nom de la page

      :param name: nom à mettre en place
      :type name: chaîne de charactères
      :return: renvoie le nom affecté
      :rtype: chaîne de charactères
      '''
      self.__name = name

      return name

    
    def get_name(self):
      '''Accesseur. 

      :return: renvoie le nom actuel de la page
      :rtype: chaîne de charactères
      '''

      return self.__name


    def get_row_size(self):
      '''Accesseur. 

      :return: renvoie la hauteur de la page
      :rtype: entier
      '''

      return self.__row_size


    def get_col_size(self):
      '''Accesseur. 

      :return: renvoie la longueur de la page
      :rtype: entier
      '''

      return self.__col_size


    def get_slot(self, num_row, num_col):
      '''Accesseur. 

      :return: renvoie le slot affecté à la position `(num_row, num_col)` 
      :rtype: class: `Slot`
      '''

      return self.__slots[num_row][num_col]


    def get_slot_list(self):
      '''Accesseur

      :return: renvoie la liste de slots de la page
      :rtype: Liste de Slots
      '''

      return self.__slots
    

    def get_pictograms(self):
      '''Obtiens les informations des pictogrammes dans la page

      Produit un tableau d'attributes contenant toutes les informations (nom, ligne, colonne, nom de page, page de destination) de chaque pictogramme de la page courante.

      :return: renvoie un tableau d'attributes 
      :rtype: Dict
      '''

      current_page_name = self.get_name()
      attributes = {}
      for row in range(0, self.__row_size):
        for col in range (0, self.__col_size):
          slot = self.__slots[row][col]
          if slot:
            word = slot.get_word()
            dest = slot.get_page_destination()
            if dest:
              dest_page_name = dest.get_name()
            else:
              dest_page_name = None

            id = f'{word}@{current_page_name}'
            while id in attributes:
              id = f'{id}*'

            attributes[id] = [word, row, col, current_page_name, dest_page_name]  

      return attributes


    def is_free(self, num_row, num_col):
      '''Retourne vrai si le slot à la position (`num_row`, `num_col`) est libre, faux sinon.

      :param num_row: nombre de la ligne
      :type num_row: entier
      :param num_col: nombre de la colonne
      :type num_col: entier
      :return: renvoie un bolean
      :rtype: bolean
      '''
      return self.__slots[num_row][num_col] == None


    def is_full(self):
      '''Retourne vrai si la table est pleine (aucun slot vide), faux sinon

      :return: renvoie un bolean 
      :rtype: bolean
      '''

      if (self.__full):
        return True
      for row in range(0, self.__row_size):
        for col in range (0, self.__col_size):
          if self.__slots[row][col] == None:
            return False
      self.__full = True
      return True


    def add_word(self, word, core=False, dest=None) :
      '''Crée et ajoute un slot(pictogramme) dans le prochain emplacement disponible de la page 
      
      Fonction récursive.

      :param word: nom du mot du pictogramme
      :type word: chaîne de charactères
      :param core: indique si le mot est du voc de base, defaults to False
      :type core: boolean, optional
      :param dest: page de destination du pictogramme, defaults to None
      :type dest: classe: `Page`, optional
      :return: renvoie le nom du mot si affectation possible, null sinon 
      :rtype: chaîne de charactères
      '''

      if(self.__last_C == self.__col_size) : 
        self.__last_C = 0
        self.__last_R += 1

      if(self.__last_R == self.__row_size) :
        self.__full = True
        print("Failed to add word <", word, ">. The table is full.")

        return None

      if(self.__slots[self.__last_R][self.__last_C] == None) :
        s = Slot(word, core, dest)
        self.__slots[self.__last_R][self.__last_C] = s
        self.__last_R
        self.__last_C += 1

        return word
      
      self.__last_R
      self.__last_C += 1

      return self.add_word(word, dest=dest)

    #  (à revoir ? Efficacité chaînes de caractères)
    def __str__(self):
      '''Méthode d'affichage d'une page

      :return: renvoie la structure de la page dans un format lisible
      :rtype: chaîne de charactères
      '''

      s = "Page: " + self.__name + "\n("
      for i in range(0, self.__row_size) : 
        for j in range(0, self.__col_size) :
          s+=str(self.__slots[i][j])
          s+=", "
        s+='\n'

      return s+')'

    
class Grid():
  '''Meta-classe représentant la structure complète d'un système de grilles de pictogrammes 

  :param input_file: fichier `.csv` en format `Augcom` ou tableau d'attributes décrivant chaque pictogramme avec le format: {`id_picto` : [`nom`, `ligne`, `colonne`, `page`, `destination`]}
  :type input_file: fichier / Dict
  :param row_size: hauteur fixe de chaque page de la grille
  :type row_size: entier
  :param col_size: longueur fixe de chaque page de la grille
  :type col_size: entier
  :raises Exception: exception d'entrée incompatible  
  '''

  def __init__(self, input_file, row_size, col_size):
    '''Constructeur'''

    self.__row_size = row_size
    self.__col_size = col_size
    self.__core_voc = {}
    self.__pages = {}
    self.__pageCounter = 0     
    self.__fusion_id = 0
    self.__create_grid(input_file)


  def get_root_page(self):
    '''Obtient la page racine, qui est par défaut la page nommé `accueil`

    :return: renvoi la page d'accueil 
    :rtype: classe: `Page`
    '''

    return self.__pages.get('accueil')

  
  def get_nb_pages(self):
    '''Renvoie le nombre de pages contenues dans la grille

    :return: nombre total de pages
    :rtype: entier
    '''

    return self.__pageCounter
  

  def get_page_names(self):
    '''Renvoie la liste de noms de pages contenues dans la grille

    :return: liste de noms
    :rtype: Liste
    '''

    return self.__pages.keys()


  def get_page(self, name):
    '''Renvoie la page avec le nom `name` 

    :param name: nom de la page à chercher
    :type name: chaîne de charactères
    :return: la page concernée
    :rtype: classe: `Page`
    '''

    return self.__pages.get(name) 


  def get_page_dict(self):
    '''Renvoie le tableau de pages de la grille

    :return: tableau de pages
    :rtype: Dict (format: {`page_name`: chaine de charactères : `page`: classe `Page`})
    '''

    return self.__pages


  def get_core_voc(self):
    '''Renvoie le tableau d'attributes décrivant tous les pictogrammes

    :return: tableau d'attributes
    :rtype: Dict (format: {`id_picto`:[`nom`,`ligne`,`colonne`,`page`, `page_dest`]})
    '''

    return self.__core_voc


  def get_row_size(self):
    '''Renvoie la hauteur de la grille

    :return: nombre de lignes
    :rtype: entier
    '''

    return self.__row_size


  def get_col_size(self):
    '''Renvoie la longueur de la grille

    :return: nombre de colonnes
    :rtype: entier
    '''

    return self.__col_size

  
  def add_word_in_root(self, word, dest=None):
    '''Ajoute un nouveau pictogramme à la page d'accueil dans la première position disponible

    :param word: nom du pictogramme
    :type word: chaîne de charactères
    :param dest: page de destination du pictogramme, defaults to None
    :type dest: classe `Page`, optional
    '''

    accueil_page = self.__pages.get('accueil')
    if accueil_page.is_full() :

      print('accueil complète, désolé')
      return

    accueil_page.add_word(word, dest=dest)

    return


  def add_new_page(self, name):
    '''Fonction d'encapsulation 

    Ajoute une nouvelle page à la grille

    :param name: le nom de la nouvelle page
    :type name: chaîne de charactères
    :return: la page ajoutée
    :rtype: classe: `Page`
    '''

    return self.__add_page(name)


  def __add_page(self, name_page):
    '''Ajoute une nouvelle page à la grille

    :param name_page: le nom de la nouvelle page
    :type name_page: chaîne de charactères
    :return: la page ajoutée
    :rtype: classe: `Page`
    '''

    page = Page(name_page, self.__row_size, self.__col_size)    
    self.__pages[name_page] = page
    self.__pageCounter += 1 

    return page


    ''''''
  def update_leaf_picto(self, extra_page):
    '''Affecte la page `extra_page` à un pictogramme disponible

    Recherche le premier pictogramme qui n'a pas de page de destination et mettre en place `extra_page` 
    comme destination. 

    :param extra_page: la page à affecter
    :type extra_page: classe: `Page`
    :return: Renvoie la page contenant le pictogramme trouvé.
    :rtype: classe: `Page`
    '''    

    core_voc_dict = self.get_core_voc()

    # Valider que la première page de la grille soit l'accueil, sinon la remettre à la tête du tableau
    pages_dict = self.get_page_dict()
    first_page_name = list(pages_dict.keys())[0]
    if first_page_name != 'accueil':
      # 1. convertir le tableau d'attribs à une liste de tuples 
      tuples = list(pages_dict.items())
      # 2. trouver l'indice de l'accueil dans le tableau d'attribs
      counter = 0
      for page_name in pages_dict:
        if page_name == 'accueil':
          break
        counter+=1
      # 3. placer la page d'accueil comme premier element de la liste de tuples
      tuples[0], tuples[counter] = tuples[counter], tuples[0]
      # 4. reconvertir la liste de tuples en tableau
      pages_dict = dict(tuples)

    # Parcourir tous les slots de chaque page et affecter la page destination au 1er slot sans destination.
    for page in pages_dict.values():
      if page.get_name() != extra_page.get_name():
        for row in range(1, page.get_row_size()):
          for col in range(1, page.get_col_size()):
            slot = page.get_slot(row, col)
            if slot:
              if not slot.get_page_destination():
                # slot.set_page_destination(extra_page)  ****
                new_slot = Slot(slot.get_word(), False, extra_page)
                page.set_slot(new_slot, row, col)

                #m-à-j le tableau d'attributes
                for key, picto in core_voc_dict.items():
                  if picto[0] == slot.get_word() and picto[1] == row and picto[2] == col and picto[3] == page.get_name():
                    
                    picto[4] = extra_page.get_name()
                                  
                # print([(k,p) for k,p in core_voc_dict.items() if p[3] == 'accueil'])
                return page


    '''  '''
  def __create_grid(self, input_file):
    '''Crée une grille à partir d'un fichier texte ou d'un tableau d'attributes

    :param input_file: fichier/tableau source contenant toute l'information d'une grille 
    :type input_file: fichier `.csv` en format `Augcom` (voir le repo du projet pour plus d'information), 
    ou tableau d'attributes décrivant chaque pictogramme (format: {`id_picto`:[`nom`,`ligne`,`colonne`,`page`, `page_dest`]})    
    :raises Exception: exception d'entrée incompatible
    '''

    #référence pour le calcul de row_size, col_size et destination
    last_id = None

    # si l'entrée est un dictionaire de pictogrammes
    if isinstance(input_file, dict):
      # print("Grille créée à partir d'un dictionaire de pictogrammes")
      
      self.__core_voc = dict(input_file)

    # si l'entrée est un fichier .csv en format Augcom
    elif input_file.endswith('.csv'):
      # print("Grille créée à partir du fichier " + input_file)
    
      # Fichier brut à traiter
      with open(input_file, "r") as rawFile:

        #Traitement du fichier source
        for lines in rawFile:
          lines = lines.lower()
          sentence = lines.strip()
          col = sentence.split("\t")		

          # On gére le problème des lignes semi-vides créées par les liens entre les répertoires
          if len(col) > 4:
            
            word = col[0]
            row = int(col[1])
            column = int(col[2])
            page = col[3]			
            id = col[4]

            # enregistrer le mot, les coordonnées, la page actuelle et la destination de chaque pictogramme
            self.__core_voc[id] = [word, row, column, page, None]
            
            last_id = id

          # Nous récupérons les liens entre les répertoires
          elif len(col) > 1:            
            pointed_link = col[1]            			
            self.__core_voc.get(last_id)[4] = pointed_link

    else:
      raise Exception('Entrée incompatible. Seul tableaux d attributes (dict) ou fichiers .csv (format AUGCOM) sont acceptés')

    self.__add_core_voc()


  def __add_core_voc(self):
    '''Mettre en place la structure de la grille à partir de son tableau d'attributes
    
    Crée des pages et des slots et les affecte en suivant le tableau d'attributes'''
    
    #parcourir le tableau d'attributes and extraire l'information
    for picto in self.__core_voc.values():
      word = picto[0]
      row = picto[1]
      col = picto[2]
      page_name = picto[3]
      dest_name = picto[4]

      # créer la page contenant le picto s'il n'existe pas
      if page_name in self.__pages:
        page = self.__pages.get(page_name)
      else:		  
        page = self.__add_page(page_name)

      # créer la page de destination s'il n'existe pas    
      if dest_name:
        if dest_name in self.__pages:
          destination = self.__pages.get(dest_name)
        else:			
          destination = self.__add_page(dest_name)          
      else:
        destination = None

      # créer un slot et l'ajouter dans la bonne page et position
      slot = Slot(word, True, destination)    
      page.set_slot(slot, row, col)


  def cross_pages(self, page1, page2, parent=None):
    '''Croise deux pages et toutes les sous-pages analogues reliées entre elles 

    :param page1: première page à croiser
    :type page1: classe: `Page`
    :param page2: deuxième page à croiser
    :type page2: classe: `Page`
    :param parent: page de référence pour mettre en place les pictogrammes de retour. Cette page fait un appel récursive, defaults to None
    :type parent: classe: `Page`, optional
    :return: renvoie 3 choses: Un tableau contenant les attributes des pictos dans la page résultante,
     la page résultante et un tableau contenant les pictos non affectés à la page résultante lors du croissement
    :rtype: [type]
    '''

    # obtenir la taille des pages    
    row_size = self.get_row_size()
    col_size = self.get_col_size()
    
    # sufixe pour rendre unique le nom de chaque page (pas implémenté)
    new_page_name_suffix = random.randint(0,10000)

    # tableau de tous les attributs des pictogrammes de la page résultante
    attributes = {}

    # tableau des pictogrammes non affectés lors de la fusion
    unallocated_pictos = {}

    # tableau pour stocker les pictos non affectés dans les appels récursives
    unalloc = {}

    # CAS 1: Aucune page n'existe
    # ============================
    if (not page1) and (not page2):
      # print('Rien a croiser, fin de la fonction')
      
      return {}, None, unalloc
    
    # CAS 2: seul page1 existe
    # ============================
    if page1 and (not page2):
      result_page = copy.deepcopy(page1)
      picto_dict = result_page.get_pictograms()

      # m-à-j du picto_dict
      for id, picto1 in picto_dict.items():
            # réviser les duplicatas
            while id in attributes:
              id = f'{id}*'
            
            attributes[id] = picto1

      for picto in picto_dict.values():
        # chercher et m-à-j le picto de retour.
        if (picto[0] == 'retour_r') and (picto[1] == row_size - 1) and (picto[2] == col_size - 1):
          if parent:
            picto_dict[f'retour_r@{result_page.get_name()}'][4] = parent.get_name()
            
        else:
          slot = result_page.get_slot(picto[1], picto[2])
          dest = slot.get_page_destination()

          #déterminer (recursivement) les pictos liés à la destination de chaque slot
          attribs, selected_dest_page, unalloc = self.cross_pages(dest, None, result_page)

          # m-à-j de attributes
          for pict_id, picto2 in attribs.items():
            # réviser les duplicatas
            while pict_id in attributes:
              pict_id = f'{pict_id}*'
            
            attributes[pict_id] = picto2  
      
      return attributes, result_page, {}      
    
    # CAS 3: seul page2 existe
    # ============================
    if page2 and (not page1):        
      result_page = copy.deepcopy(page2) 
      picto_dict = result_page.get_pictograms()

      # m-à-j du picto_dict
      for id, picto1 in picto_dict.items():
            # réviser les duplicatas
            while id in attributes:
              id = f'{id}*'
            
            attributes[id] = picto1

      for picto in picto_dict.values():
        # chercher et m-à-j le picto de retour.
        if (picto[0] == 'retour_r') and (picto[1] == row_size - 1) and (picto[2] == col_size - 1):
          if parent:
            picto_dict[f'retour_r@{result_page.get_name()}'][4] = parent.get_name()

        else:
          slot = result_page.get_slot(picto[1], picto[2])
          dest = slot.get_page_destination()

          #déterminer (recursivement) les pictos liés à la destination de chaque slot
          attribs, selected_dest_page, unalloc = self.cross_pages(None, dest, result_page)

          # m-à-j de attributes
          for pict_id, picto2 in attribs.items():
            # réviser les duplicatas
            while pict_id in attributes:
              pict_id = f'{pict_id}*'
            
            attributes[pict_id] = picto2  
      
      return attributes, result_page, {}

    # CAS 4: les deux pages existent
    # ============================
    if page1 and page2:

      # décider le nom du page à retenir
      if random.randint(0,1):
        new_page_name = page1.get_name()
      else:
        new_page_name = page2.get_name()

      # TO-DO: Vérifier si new_page_name existe déjà dans les pages selectionées. Deux solutions:  
      # - ajouter suffixe au nom de la page pour la differencier des pages de base
      # new_page_name += f'_{new_page_name_suffix}'
      # où
      # - Enregistrer les noms crées au fur et à mesure du croissement dans une liste, puis modifier légerement le nom si déjà dans la liste
      # # ?? 

      #page résultante
      result_page = Page(new_page_name, row_size, col_size)

      #sélectionner les pictos qui vont populer la page résultante
      for row in range(row_size):
        for col in range(col_size):
          slot_page1 = copy.deepcopy(page1.get_slot(row, col))
          slot_page2 = copy.deepcopy(page2.get_slot(row, col))
          random_selector = random.randint(0,1)

          # les deux pictogrammes existent
          if (slot_page1) and (slot_page2):
            dest_1 = slot_page1.get_page_destination()
            dest_2 = slot_page2.get_page_destination()

            if random_selector:
              selected_slot = slot_page1
              not_selected_slot = slot_page2
              page_name = page1.get_name()
              page_name_not_selected = page2.get_name()
              
            else:
              selected_slot = slot_page2
              not_selected_slot = slot_page1
              page_name = page2.get_name()
              page_name_not_selected = page1.get_name()
    
            #déterminer (recursivement) la destination du slot selectionné
            if (selected_slot.get_word() != 'retour_r'):              
              attribs, selected_dest_page, unalloc = self.cross_pages(dest_1, dest_2, result_page)
			      # picto de retour trouvé
            elif (row == row_size - 1) and (col == col_size - 1):
              attribs, selected_dest_page, unalloc = {}, parent, {}

            #garder les pictos non affectés --------------------------------------
            word_not_selected = not_selected_slot.get_word()
            if word_not_selected != 'retour_r':
              id_not_selected = f'{word_not_selected}@{page_name_not_selected}'

              #si deux pictos non affectés ont le même id, modifier légerement l'id de l'un des deux
              while id_not_selected in unallocated_pictos or id_not_selected in attributes:
                # '*' à la fin d'une id indiquera l'existence de 2 pictos differents avec la même mot et même nom de page 
                id_not_selected = f'{id_not_selected}*'            
                        
              unallocated_pictos[id_not_selected] = word_not_selected

          # seul le premier pictogramme existe
          elif slot_page1:
            selected_slot = slot_page1
            page_name = page1.get_name()

            if selected_slot.get_word() != 'retour_r':
              dest_1 = slot_page1.get_page_destination()
              attribs, selected_dest_page, unalloc = self.cross_pages(dest_1, None, result_page)            
            else:
              if parent:
                attribs, selected_dest_page, unalloc = {}, parent, {}              

          # seul le deuxième pictogramme existe
          elif slot_page2:
            selected_slot = slot_page2
            page_name = page2.get_name()

            if selected_slot.get_word() != 'retour_r':
              dest_2 = slot_page2.get_page_destination()
              attribs, selected_dest_page, unalloc = self.cross_pages(dest_2, None, result_page)            
            else:
              if parent:
                attribs, selected_dest_page, unalloc = {}, parent, {}
            
          # aucun des pictos n'existe pas
          else: 
            selected_slot = None            

          # --------------------------------------------------------------------------------------
          #m-à-j des attributes du pictogramme selectionné dans la page résultante
          if selected_slot:
            word = selected_slot.get_word()
            selected_slot = Slot(word, False, selected_dest_page)
            result_page.set_slot(selected_slot, row, col)

            #ajouter les pictos des pages de destination au tableau d'attributes
            attributes.update(attribs)

            #m-à-j le dict de pictos non affectés avec ceux des appels récursives
            unallocated_pictos.update(unalloc)

            if selected_dest_page:                
                dest_page_name = selected_dest_page.get_name()
            else:
              dest_page_name = None

            # id du picto selectionné
            id_selected = f'{word}@{page_name}'

            #si deux pictos ont le même id, modifier légerement l'id de l'un d'eux
            while id_selected in attributes or id_selected in unallocated_pictos:
              id_selected = f'{id_selected}*'
            
            attributes[id_selected] = [word, row, col, new_page_name, dest_page_name]

          # mettre en place le picto selectionné dans la page résultante 
          result_page.set_slot(selected_slot, row, col)     
    
    return attributes, result_page, unallocated_pictos


  def fusion_with(self, grid):
    '''Fusione aléatoirement les strutures analogues (pages) de deux grilles

    Fonction récursive. En partant des deux accueils, on compare chaque slot d'une page avec son analogue 
    dans l'autre page et choisit aléatoirement l'un d'entre eux.
    Par exemple, les slots situés à la position (2,3) dans les pages d'accueil de la première et la deuxième 
    grille sont utilisés pour définir le slot situé à (2,3) dans la page d'accueil de la grille résultante.
    Ainsi, pour chaque position il y a toujours un slot selectionné (ce qui va dans les pages de base de la 
    grille résultante) et un autre non-selectionné qui va dans des pages spécialement concues à ce propos (extra_pages).

    La grille résultante est une structure unique et indépéndante. Elle contient les pictogrammes des deux grilles
    originales.

    :param grid: la deuxième grille avec laquelle la grille actuelle va se fusioner
    :type grid: classe: `Grid`
    :return: une nouvelle grille avec une nouvelle structure 
    :rtype: classe: `Grid`
    '''

    # tableau d'attributes de la grille résultante contenant uniquement les pictos selectionnés
    attributes_dict = {}

    # tableau contentant tous les pictogrammes non selectionnés lors de la fusion
    unalloc_dict = {}

    # extraire la taille des grilles
    row_size = self.get_row_size()
    col_size = self.get_col_size()

    # extraire les pages d'accueil de chacune des grilles
    current_accueil = self.get_root_page() 
    foreing_accueil = grid.get_root_page()  

    # Fusioner les deux grilles à travers leurs pages d'accueil.   
    attributes_dict, result_page, unalloc_dict = self.cross_pages(current_accueil, foreing_accueil)    

    # Créer la structure de base de la grille résultante
    new_grid = Grid(attributes_dict, row_size, col_size)

    # remplir slots vides (pas de slot) avec les pictos non affectées
    for page in new_grid.get_page_dict().values():
      for row in range(1, row_size):
        for col in range(1, col_size):
          slot = page.get_slot(row, col)
          if not slot:            
            try:
              # renvoyer l'id du pictgramme non affecté suivant
              id_next_unalloc_picto = next(iter(unalloc_dict))

              #vérifier si l'id du picto non alloué existe déjà dans le tableau d'attributes de la grille (re-check)
              if id_next_unalloc_picto in new_grid.get_core_voc():
                new_id = f'{id_next_unalloc_picto}*'
                # ajouter des '*' jusqu'à ce que l'id soit unique
                while new_id in new_grid.get_core_voc():
                  new_id = f'{new_id}*'

                unalloc_dict[new_id] = unalloc_dict.pop(id_next_unalloc_picto)
                id_next_unalloc_picto = new_id

              unalloc_picto = unalloc_dict.pop(id_next_unalloc_picto)
              word = unalloc_picto
              slot = Slot(word, False, None)
              page.set_slot(slot, row, col)

              #m-à-j du dict d'attriburtes de la nouvelle grille
              new_grid.get_core_voc()[id_next_unalloc_picto] = [word, row, col, page.get_name(), None]     

            # unalloc_dict est vide         
            except:
              print('** fusion complète 1 **')
              return new_grid
    
    # gérer le cas où il y a plus de pictos non alloués que de slots vides.
    while len(unalloc_dict):
            
      # créer et ajouter une page extra pour les allouer
      extra_page_name = f'extra_{random.randint(0,10000)}'    
      extra_page = new_grid.add_new_page(extra_page_name)

      # choisir le picto connecté à la page extra. On parcours les pages en partant de l'accueil.
      origin_page = new_grid.update_leaf_picto(extra_page)    

      # mettre en place le picto de retour
      if origin_page:
        picto_retour = Slot('retour_r', False, origin_page)
        extra_page.set_slot(picto_retour, row_size - 1, col_size - 1)
        new_grid.get_core_voc()[f'retour_r@{extra_page_name}'] = ['retour_r', row_size - 1, col_size - 1, extra_page_name, origin_page.get_name()]
      
      # remplir slots vides de la PAGE EXTRA avec des pictos non affectées
      for row in range(1, row_size):
          for col in range(1, col_size):
            slot = extra_page.get_slot(row, col)
            # si le slot est vide
            if not slot:
              try:
                # renvoyer l'id du pictgramme non affecté suivant
                id_next_unalloc_picto = next(iter(unalloc_dict))

                #vérifier si l'id du picto non alloué existe dans le dict d'attributes de la grille
                # sinon, ajouter '*' à la fin de l'id répété pour en créér un id unique  
                if id_next_unalloc_picto in new_grid.get_core_voc():
                  new_id = f'{id_next_unalloc_picto}*'

                  while new_id in new_grid.get_core_voc():
                    new_id = f'{new_id}*'

                  unalloc_dict[new_id] = unalloc_dict.pop(id_next_unalloc_picto)
                  id_next_unalloc_picto = new_id

                unalloc_picto = unalloc_dict.pop(id_next_unalloc_picto)
                word = unalloc_picto
                slot = Slot(word, False, None)
                extra_page.set_slot(slot, row, col)

                #m-à-j du dict d'attriburtes de la nouvelle grille
                new_grid.get_core_voc()[id_next_unalloc_picto] = [word, row, col, extra_page.get_name(), None]              
              except:
                print('** fusion complète 2 **')                
                return new_grid
                
    return new_grid


  # TO-DO: ne fonctionne pas, à déboger 
  def shuffle(self):
    '''Mélange les pictogrammes à l'intérieure de chaque page de la grille

    Change uniquement la distribution spaciale des pictogrammes d'une page. 

    :raises Exception: capacité de la page dépassé
    :return: nouvelle grille 
    :rtype: classe: `Grid`
    '''

    # copier le tableau d'attributes de la grille originale
    core_voc_copy = copy.deepcopy(self.get_core_voc())

    # new_grid_core_voc = new_grid.get_core_voc()
    row_size = self.get_row_size()
    col_size = self.get_col_size()

    #créer liste de coordoneées de slots
    all_coords = [(i,j) for i in range(1, row_size) for j in range(1, col_size)]
    
    #omettre le picto dans le coin en bas à droite (retour, plus, etc) 
    all_coords.pop()

    for page_name in self.get_page_dict():
      # liste de toutes les coordonnées sauf (row_size-1, col_size-1)
      coords_list = list(all_coords) 
      # 
      info = []

      #mélange la liste
      random.shuffle(coords_list)
      
      for id, picto in self.get_core_voc().items():
        
        # choisir pictos dans la même page. Ne tenir pas compte des pictos en ligne/col = 0. 
        if (picto[3] == page_name) and (picto[1] != 0) and (picto[2] != 0):
          info.append((id, picto))
          if (picto[1] != row_size-1) or (picto[2] != col_size-1):     
            
            try:          
              row, col = coords_list.pop()
            except:              
              raise Exception('Le nombre de pictogrammes dépasse la capacité de la page. Valider tableau d attributes')
            
            #affecter les nouvelles coordonnées aux pictos de la pag courante
            core_voc_copy[id][1] = row
            core_voc_copy[id][2] = col
    
    return Grid(core_voc_copy, row_size, col_size)


  def to_graph(self):
    '''Génére un graphe décrivant la structure de la grille

    :return: un graphe dirigé
    :rtype: classe: `networkx.DiGraph`
    '''

    nodes = set([])
    edges = set([])
    for key,page in self.__pages.items():
      nodes.add(key)
      slots = page.get_slot_list()
      for items in slots:
        for slot in items:
          if slot != None:
            dest = slot.get_page_destination()
            if dest != None:
              dest = dest.get_name()
              edges.add((key, dest))
    
    G=nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    nx.draw(G,with_labels=True)
    # plt.savefig("grid_graph.png") # save as png
    plt.show() # display

    return G


  def to_text(self, output_name='grid_text.csv'):
    '''Crée un fichier texte (.csv) décrivant la grille en format AUGCOM.

    Voir le repo du projet pour plus d'information sur le format Augcom.

    :param output_name: le nom du fichier résultant, defaults to 'grid_text.csv'
    :type output_name: chaîne de charactères, optional
    '''

    print("output file is " + output_name)
    print()
    sorted_attrib_dict = {}

    # trier le dict d'attributes par nom de page
    for page_name in self.get_page_dict():     
      for picto_id, attributes in self.get_core_voc().items():
        if attributes[3] == page_name:
          sorted_attrib_dict[picto_id] = self.get_core_voc().get(picto_id)       

    # Fichier résultant
    with open(output_name, "w") as text_file:
      for picto_id, attributes in sorted_attrib_dict.items():
        print(f'{attributes[0].upper()}\t{attributes[1]}\t{attributes[2]}\t{attributes[3]}\t{picto_id}', file=text_file) 
        if attributes[4]:
          print(f'\t\t\t{picto_id}\t{attributes[4]}', file=text_file)


  def __str__(self):
    '''Méthode d'affichage 1

    :return: renvoie une représentation lisible de la structure de la grille
    :rtype: chaîne de charactères
    '''

    s = 'grid : {\n'
    for page in self.__pages.values():
      s+= str(page) + '\n'
    s += '}\n'
    return s

     
  def display(self, name='default'):
    '''Méthode d'affichage 2

    Génére une image detaillé et intuitive de la structure de la grille. Il utilise Graphviz et le language DOT.
    Il export automatiquement l'image en format png au répértoire actuel 

    :param name: le nom du fichier image produit, defaults to 'default'
    :type name: chaîne de charactères, optional
    :return: renvoie un graphe dirigé
    :rtype: classe: `networkx.DiGraph`
    '''

    graph = Digraph(comment='Test', node_attr={'shape': 'record'}) #, 'fixedsize': 'true', 'width':'4', 'height':'2'})
    row_size = self.get_row_size()
    col_size = self.get_col_size()
    slot_index = 0

    for page_name,page in self.get_page_dict().items():
      
      attribute_string = '{ '
      separator_1 = ''
      for row in range(0, row_size):
        separator_2 = ''
        attribute_string += f'{separator_1}' + ' { '
        for col in range(0, col_size):
          slot_index  = row * col_size + col
          slot = page.get_slot(row, col)

          if slot:
            word = slot.get_word()
            dest = slot.get_page_destination()

            #ajouter lien entre picto directoire et la page correspondante 
            if dest:              
              graph.edge(f'{page_name}:{slot_index}', f'{dest.get_name()}')
          elif row == 0 and col == 0:
            word = page_name.upper()
          else:
            word = ''

          attribute_string += f'{separator_2}<{slot_index}>{word} '
          separator_2 = '|'

        separator_1 = '|'
        attribute_string += '} '
      attribute_string += ' }'

      #créer noeud 
      graph.node(f'{page_name}', f'{attribute_string}')

    # rendre l'image et l'export au format png  
    graph.render(filename=name,format='png')

    return graph

#=========================================================================================================================

def compute_distances(grid, movement_factor=1, selection_factor=1):
  '''Calcule la distance entre chaque paire de pictogrammes à l'intérieure de chaque page d'une grille

  Prend en compte la difficulté du mouvement (movement_factor) et la difficulté de la sélection (selection_factor)

  :param grid: grille à traiter
  :type grid: classe: `Grid`
  :param movement_factor: facteur de difficulté du mouvement, defaults to 1
  :type movement_factor: entier, optional
  :param selection_factor: facteur de difficulté de la sélection, defaults to 1
  :type selection_factor: entier, optional
  :return: déscription textuelle des distances entre chaque pictogramme 
  :rtype: chaîne de charactères
  '''

  # Dictionaire des distances
  disTab = grid.get_core_voc()
  # Copie du dict à utiliser dans la boucle interne
  distTab_copy = copy.deepcopy(disTab) 
  # Final distances
  distances = ''

  # Définition du poids du mouvement
  m = movement_factor
  # Définition du poids du temps de sélection
  n = selection_factor

  for key1,picto1 in disTab.items():
    # ID de référence
    refID = key1
    # On crée une variable qui prend comme valeur le nom de la page actuelle
    currentPage = picto1[3]
    # On récupere les coordonnées
    x1 = picto1[1]
    y1 = picto1[2]
    # On enleve picto1 du deuxième dict
    distTab_copy.pop(key1)
    
    for key2,picto2 in distTab_copy.items():
      # ID de deuxième picto en question
      ID = key2

      # On vérifie que l'on est toujours sur la bonne page
      currentPage2 = picto2[3]
      x2 = picto2[1]
      y2 = picto2[2]

      if currentPage2 == currentPage:
        # Si les deux IDs sont différents on récupère les coordonnées x et y de chacun
        if refID != ID:
          # Calcul des distances Euclidiennes
          squaredDistance = (x1 - x2) ** 2 + (y1 - y2) ** 2
          pictoDistance = math.sqrt(squaredDistance)

          #Si le mot de d'arrivée de l'arc est un répertoire: C=(P1,P2)m
          if "_r@" in ID :
            #On écrit la fomule sans le n
            distances += "Mot à Répertoire" + "\t" + refID + "\t" + ID + "\t" + str(pictoDistance * m) + "\n"

          #Si le pictogarmme départ et celui d'arrivée sont des mots: C=(P1,P2)m+n            
          else :
            distances += "Mot à Mot" + "\t" + refID + "\t" + ID + "\t" + str(pictoDistance * m + n) + "\n"
            distances += "Mot à Mot" + "\t" + ID + "\t" + refID + "\t" + str(pictoDistance * m + n) + "\n"

    # On écrit le lien entre un pictogramme directeur (plus, retour, pagination, flèche retour et répertoires) et la page
    if picto1[4]:
      # Formule correspondnat uniquement à l'action de sélection: C=n
      distances += "Picto directeur à Page" + "\t" + refID + "\t" + picto1[4] + "\t" + str(n) + "\n"

    # On écrit le lien entre la page et le pictogramme 
    # On calcule la distance entre le lien de la page et des pictogrammes à partir du pictogramme en haut à gauche avec x=1 et y=1
    squaredDistance3 = (1 - x1) ** 2 + (1 - y1) ** 2
    pageToPicto = math.sqrt(squaredDistance3)

    #Si le pictogramme d'arrivée de l'arc est un répetoire: C=(P(1,1)P2)m
    if "_r@" in picto1[0] :
      #On calcule sans le n
      distances += "Page à Répertoire" + "\t" + currentPage + "\t" + picto1[0] + "\t" + str(pageToPicto* m) + "\n"
    # Si le pictogramme d'arrivée est un mot: C=(P(1,1)P2)m+n
    else :
      distances += "Page à Mot" + "\t" + currentPage + "\t" + refID + "\t" + str(pageToPicto * m + n) + "\n"

  return distances

#=========================================================================================================================

# FONCTIONS AUXILIAIRES POUR LE CALCUL DU COÛT DE PRODUCTION
#--------------------------------------------------------------

class WeightedPath:
    '''Classe auxiliaire pour stocker le chemin et le coût lors du calcul du chemin optimale'''

    def __init__(self):
        '''Constructeur'''

        self.path = []
        self.weight = 0


def initialNode(text, nodeList, edgeList, G):
    '''Fonction qui établit le noeud à partir duquel il faut commencer à calculer un arc

    :param text: texte d'entrée
    :type text: chaîne de charactères
    :param nodeList: liste de tous les noeuds du graphe
    :type nodeList: liste
    :param edgeList: tableau associatif de tous les arcs avec en clé le noeud tête et en valeurs le noeud pointé et le poids de l'arc
    :type edgeList: Dict
    :param G: graphe initial 
    :type G: classe: `networkx.DiGraph`
    :return: liste avec le chemin et le poids total
    :rtype: liste
    '''

    path = []
    stock = []
    totalWeight = 0
    startNode = "accueil"

    # On parcours le fichier texte
    for line in text.splitlines():
        line = line.lower()
        line = line.strip()
        # On évite les lignes vides
        if line != "":
            # On récupère le plus court chemin
            words = shortestPath(startNode, line, nodeList, edgeList, G)
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
        stock.append((finalPath, totalWeight))

    return stock


def textToNodes(word, nodeList):
    '''Fonction qui prend en entrée un mot de la phrase et en fait une liste de noeuds possibles

    :param word: chaque word de la phrase d'entrée
    :type word: chaîne de charactères
    :param nodeList: liste de tous les noeuds du graphe
    :type nodeList: liste
    :return: liste des noeuds canidats potentiels
    :rtype: liste
    '''
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


def shortestPath(initialNode, sentance, nodeList, edgeList, G):
    '''Fonction de calcul du plus court path

    :param initialNode: point de départ de la recherche dans le graphe
    :type initialNode: Node
    :param sentance: phrase d'entrée pour laquelle il faut calculer le cout de production
    :type sentance: chaîne de charactères
    :param nodeList: liste de tous les noeuds du graphe
    :type nodeList: liste
    :param edgeList: tableau associatif de tous les arcs avec en clé le noeud tête et en valeurs le noeud pointé et le weight de l'arc
    :type edgeList: Dict
    :param G: graphe en question
    :type G: classe: networkx.DiGraph
    :return: objet contenant le chemin final et le coût final
    :rtype: classe: `WeightedPath`
    '''

    initialNodes = []
    words = sentance.split(" ")
    shortestPath = []

    # Initialisation du poids total
    totalWeight = 0
    initialNodes.append(initialNode)
    
    # On créé la variable du chemin final
    finalPath = []
    pathList = []

    # On créé un nouveau graphe avec la liste des candidats
    coupleGraphe = nx.DiGraph()

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
                # On créé un arc "accueil" de poids 0
                coupleGraphe.add_edge("accueil", candidate, weight=0)

            # On parcours la liste des noeuds initiaux
            for firstNode in initialNodes:
                # On extrait le plus court chemin entre le premier noeud et le candidat avec la fonctionn "shortest_path "fonction Networkx
                try:
                    # graph = Digraph(filename='GGGG',format='png',comment='TEST_1')
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
        
    # On créé le chemin final
    wordIndex = 0

    # On parcours la liste des chemins
    for path in pathList:
        if (shortestpath[wordIndex] == path[0]) and (shortestpath[wordIndex + 1] == path[-1]):
            for words in path:
                finalPath.append(words)
            wordIndex = wordIndex + 1
    
    # On créé un objet
    weightedPath = WeightedPath()
    weightedPath.path = finalPath
    weightedPath.weight = totalWeight

    return weightedPath


def save_obj(obj, name ):
    '''Fonction qui stocke un objet dans un fichier .pkl

    :param obj: l'objet à stocker
    :type obj: any
    :param name: nom du fichier créé
    :type name: chaîne de charactères
    '''
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    '''Fonction qui récupere un objet contenu dans un fichier .pkl

    :param name: nom du fichier cible
    :type name: chaîne de charactères
    :return: renvoie le fichier avec nom `name`
    :rtype: any
    '''
    with open(name + '.pkl', 'rb') as f:

        return pickle.load(f)


def compute_cost(input_sentence, distances):
  '''Calcule le coût associé à la phrase d'entrée utilisant les distances données en entrée 

  :param input_sentence: phrase d'entrée
  :type input_sentence: chaîne de charactères
  :param distances: contient les distances entre chaque pictogramme 
  :type distances: chaîne de charactères
  :return: le meilleur chemin et le coût final
  :rtype: liste
  '''
  # start_time = time.time()

  # variable qui garde le meilleur chemin et le coût final
  result = []
      
  # # On créé le graph G
  graph = nx.DiGraph()

  # tableau associatif (dict) qui comprendra les noeuds et les poids
  edgeList = {}

  # # On parcours les distances pour déterminer les noeuds, les arcs et les poids
  for line in distances.splitlines():
      line = line.strip()
      col = line.split('\t')
      
      # Addition du noeud au graphe
      graph.add_node(col[1])

      # Création des arcs avec leurs poids
      graph.add_edge(col[1], col[2], weight=col[3])

      # Création du tableau associatif 
      if col[1] in edgeList.keys():
          edgeList[col[1]].append((col[2], float(col[3])))
      else:
          edgeList[col[1]] = [(col[2], float(col[3]))]

  # création de la liste des noeuds
  nodeList = list(graph.nodes())

  output = initialNode(input_sentence, nodeList, edgeList, graph)

  # Sauvegarde des résultats
  for elt in output:
      result.append(elt)      

  # print("--- %s seconds ---" % '{:5.5}'.format(time.time() - start_time))

  return result

#=========================================================================================================================
# ALGORITHME GÉNÉTIQUE
# Ici on utilise le framework de la librairie < Algorithmes évolutionnaires distribués en Python (DEAP) >

# CX_PROB  est la probabilité avec laquelle deux individus se croissent
# MUT_PROB est la probabilité de mutation d'un individu
CX_PROB, MUT_PROB = 0.5, 0.5    

# SCORE_THRESHOLD est le coût ciblé.
# MAX_ITER est le nombre maximale d'itérations
SCORE_THRESHOLD, MAX_ITER = 7.0, 10

# Dimensions des grilles
ROW_SIZE = 4
COL_SIZE = 4

# NB_SELECTED_IND est le nombre d'individus qu'on va séléctioner dans chaque génération
NB_SELECTED_IND = 5


def main(files, sentence, row_sz, col_sz, score_threshold, max_iter):
  '''Fonction principale qui implémente la boucle itérative de l'algorithme génétique

  :param files: liste de noms de fichiers source
  :type files: liste
  '''

  def init_grid(container, source_file):
    '''Initialise la grille dans le cadre de DEAP

    :param container: structure qui encapsule les données dentrée
    :type container: un conteneur
    :param source_file: fichier/tableau source
    :type source_file: fichier texte ou tableau d'attributes
    :return: un conteneur avec les parametres d'entrée
    :rtype: conteneur
    '''
    
    return container(source_file, row_sz, col_sz)


  def init_population(container, func, source_file_list):
    '''Initialise une population dans le cadre de DEAP

    :param container: structure qui encapsule les données dentrée
    :type container: un conteneur
    :param func: une fonction qui va être utilisé sur le fichier source
    :type func: fonction
    :param source_file_list: liste de noms de fichiers source
    :type source_file_list: liste
    :return: un conteneur avec quelques parametres d'entrée
    :rtype: conteneur
    '''

    return container(func(file) for file in source_file_list)


  #Créer le container pour la fonction de coût et les individus
  creator.create("FitnessMax", base.Fitness, weights=(1.0,))      ##todo: arrange weights quand plusieurs fitnesses (sentences) 
  creator.create("Individual", Grid, fitness=creator.FitnessMax, best_path=[])

  # Initialisateurs
  toolbox = base.Toolbox()
  toolbox.register("individual", init_grid, creator.Individual)
  toolbox.register("population", init_population, list, toolbox.individual)


  def evalProdCost(phrase, individual):
    '''Fonction d'évaluation du coût de production dans le cadre de DEAP

    :param phrase: phrase d'entrée
    :type phrase: chaîne de charactères
    :param individual: représentation d'une grille dans le cadre de DEAP
    :type individual: classe: `toolbox.individual`
    :return: renvoie le coût associé à `sentance` sur la grille `individual`  
    :rtype: [type]
    '''
    distances = compute_distances(individual)
    cost = compute_cost(phrase, distances)
    # path = result[0][0]
    # cost = result[0][1]
    
    individual.best_path = cost[0][0]
            
    return cost[0][1],    ##todo: plusieurs phrases


  def external_fusion(individual1, individual2): 
    '''Fonction de fusion externe (DEAP)

    :param individual1: première grille 
    :type individual1: classe: `toolbox.individual`
    :param individual2: deuxième grille
    :type individual2: classe: `toolbox.individual`
    :return: la grille résultante
    :rtype: classe: `toolbox.individual`
    '''
    new_grid = individual1.fusion_with(individual2)  

    return toolbox.individual(new_grid.get_core_voc())


  def internal_fusion(individual):
    '''Fonction de fusion interne (DEAP)

    :param individual: la grille concernée
    :type individual: classe: `toolbox.individual`
    :return: renvoie la grille résultante
    :rtype: classe: `toolbox.individual`
    '''

    new_grid = individual.shuffle()

    return toolbox.individual(new_grid.get_core_voc())


  # Operateurs génétiques
  toolbox.register("evaluate", evalProdCost, sentence)
  toolbox.register("mate", external_fusion)
  toolbox.register("mutate", internal_fusion)
  toolbox.register("select", tools.selBest)


#=========================================================================================================================
#PIPEPLINE DE L'ALGORITHME GÉNÉTIQUE

  #Création de la population
  pop = toolbox.population(files)

  # Évaluer l'ensemble de la population
  fitnesses = list(map(toolbox.evaluate, pop))
  for ind, fit in zip(pop, fitnesses):
    ind.fitness.values = fit

  # Effectuer l'évolution

  # Extraction de toutes les fitnesses
  fits = [ind.fitness.values[0] for ind in pop]

  # Variable permettant de suivre le nombre de générations
  g = 0

  # Commencez l'évolution ***
  
  # évoluer jusqu'à ce qu'un individu atteigne `score_threshold` ou que le nombre de générations atteigne `max_iter`
  while max(fits) > score_threshold and g < max_iter:
    # A new generation
    g = g + 1
    print("-- Generation %i --" % g)

    # Sélectionnez les individus de la génération suivante
    offspring = toolbox.select(pop, NB_SELECTED_IND)

    # Appliquer le crossover et la mutation sur la progéniture ***

    # CROSSOVER (FUSION)
    new_cx_individuals = []
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
      if random.random() < CX_PROB:
        n_ind = toolbox.mate(child1, child2)
        toolbox.evaluate(n_ind)        
        
        new_cx_individuals.append(n_ind)

    # m-à-j offspring    
    offspring.extend(new_cx_individuals)

    # *****************************************************************************
    # MUTATION (REORGANISATION INTERNE)     TO-DO: Déboguer
    # new_mut_individuals = []
    # for mutant in offspring:
    #   if random.random() < MUT_PROB:
    #     n_ind = toolbox.mutate(mutant)
    #     new_mut_individuals.append(n_ind)

    #     # del mutant.fitness.values

    # m-à-j offspring 
    # offspring.extend(new_mut_individuals)
    # *****************************************************************************

    # Evaluer les individus sans fitness calculée (fitness invalide) ***
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses = map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
      ind.fitness.values = fit

    # remplacer l'ancienne population par la descendance
    pop = offspring

  # Rassemblez tous les fitness dans une liste et imprimez les statistiques
  fits = [ind.fitness.values[0] for ind in pop]
            
  length = len(pop)
  mean = sum(fits) / length
  sum2 = sum(x*x for x in fits)
  std = abs(sum2 / length - mean**2)**0.5

  # indice de l'individu avec la fitness la plus optimale
  index_min = np.argmin(fits)

  # indice de l'individu avec la pire fitness
  index_max = np.argmax(fits)

  c = 0
  print()
  print('Chemins optimales de la population finale: \n')
  for ind in pop:
    print(f'Path_{c}: {ind.best_path}')
    # ind.display(f'img/ind_{c}')

  #   with open(f'{abs_path}data/ind_{c}.csv', 'w') as f:
  #     # print(f'Path_{c}: {ind.best_path}', file=f)
  #     # print(file=f)
  #     for k,i in ind.get_core_voc().items():
  #       print(k, i, file=f)
    c+=1

  print()
  print(f'Coûts de production de la population finale: \n')
  print(fits)
  print()

  print('Statistiques de la population finale;')
  print("  Min %s" % min(fits))
  print("  Max %s" % max(fits))
  print("  Avg %s" % mean)
  print("  Std %s" % std)

#=========================================================================================================================

if __name__ == '__main__':  

  # créer un parser pour obtenir l'information nécessaire de l'utilisateur
  parser = ArgumentParser()

  # ajouter des arguments
  parser.add_argument("-f", "--filelist", default='liste_sources.csv', 
                      help="écrire le nom du fichier contenant les noms de fichiers source liés aux grilles de départ.")
  parser.add_argument("-s", "--sentence", default='phrase.txt',
                      help="écrire le nom du fichier contenant la phrase d'entrée")
  parser.add_argument("-nl", "--nblignes", default=ROW_SIZE, type=int,
                      help="écrire le nombre de lignes d'une page de la grille. Défaut=4")
  parser.add_argument("-nc", "--nbcolonnes", default=COL_SIZE, type=int,
                      help="écrire le nombre de colonnes d'une page de la grille. Défaut=4")
  parser.add_argument("-th", "--threshold", default=SCORE_THRESHOLD, type=float,
                      help="écrire le seuil de coût qu'arrête l'algorithme quant est atteint")
  parser.add_argument("-mi", "--maxiter", default=MAX_ITER, type=int,
                      help="écrire le seuil d'itérations qu'arrête l'algorithme quant est atteint")

  # extraire les valeurs des arguments
  args = parser.parse_args()

  # validation des fichiers texte
  if not (args.filelist.endswith('.csv') or args.filelist.endswith('.txt')):
    print(f'Extention du fichier source << {args.filelist} >> non compatible. Utilise .csv ou .txt')
    sys.exit(0)
  
  if not (args.sentence.endswith('.csv') or args.sentence.endswith('.txt')):
    print(f'Extension du fichier de la phrase d entrée << {args.sentence} >> non compatible. Utilise .csv ou .txt')
    sys.exit(0)
  
  # Paramètres d'entrée 
  grids_source_list = []
  sentence = ''
  row_size = args.nblignes
  col_size = args.nbcolonnes
  threshold = args.threshold
  maxiter = args.maxiter

  # extraire la liste de fichiers source
  with open(f'{args.filelist}') as file1:
    for line in file1:
      l = line.split(',')
      for item in l:
        fichier = item.strip()
        grids_source_list.append(fichier)

  # extraire la phrase d'entrée
  with open(args.sentence) as file2:
    for line in file2:
      l = line.split(',')
      for item in l:
        phrase = item.strip()
        sentence += f'{phrase}\n'

  # executer le programme principale
  main(grids_source_list, sentence, row_size, col_size, threshold, maxiter)
