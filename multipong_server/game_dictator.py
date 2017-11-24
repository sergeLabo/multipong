#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

## game_dictator.py

#############################################################################
# Copyright (C) Labomedia November 2017
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franproplin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#############################################################################

"""
serveur
    Reçu de Blender:
        {'reset': 0, 'paddle': [[-9.5, 0.0], [9.5, -4.008979797363281], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]], 'ball': [8.999176025390625, -5.898959159851074]}

    Reçu de pierre:
        {'paddle': [6, 5], 'name': 'pierre'}


"""


from collections import OrderedDict
from time import time, sleep
import threading
import json


class GameManagement():
    """Gestion du jeu avec les datas envoyés par tous les joueurs."""

    def __init__(self, conf):

        # Config du jeu
        self.conf = conf

        t = time()

        # Dict avec dernière valeur reçue de chaque joueur
        self.players = OrderedDict()

        # Gestion du jeu
        self.winner = ""
        self.ranked = []
        self.scene = "play"
        self.rank_end = 0
        self.t_rank = 0 # actualisé avec winner
        self.classement = {}
        self.level = 0
        self.t_reset = 0
        self.transit = 0 # pour bloquage des jeux si level change
        self.t_transit = t
        self.tempo_transit = 2
        self.ball = [2, 2]
        self.paddle = []
        self.paddle_1_pos = []
        self.reset = 0

        # Suivi fréquence
        self.t_count = t  # Affichage fréquence régulier
        self.count = 0

    def add_data_in_players(self, user, data):
        """Ajoute les datas reçues d'un user dans le raw dict."""

        self.players[user] = data

        # Affichage de la fréquence d'appel de cette méthode
        self.frequency()

    def update_game_management(self):
        """Appelé par create_msg_for_all_players, tourne donc à 60 fps."""

        self.update_level()
        self.update_paddle()
        self.update_transit()
        self.update_classement()
        self.update_rank()

    def update_paddle(self):
        """Set les positions des paddles des joueurs dans self.paddle"""

        self.paddle = []
        # Tous niveaux
        if len(self.players) >= 1:
            for k, v in self.players.items():
                if "paddle" in v:
                    self.paddle.append(v["paddle"])

        # niveau 1, paddle auto en plus de la 0
        if len(self.players) == 1:
            self.paddle.append(self.paddle_1_pos)

    def frequency(self):
        self.count += 1
        t = time()
        if t - self.t_count > 5:
            print("Fréquence d'accès par les clients", int(self.count/5))
            self.count = 0
            self.t_count = t

    def update_transit(self):
        """Si transit:
        - bloquage des scores à 10
        - bloquage balle à 1, 1
        - pas de bloquage des paddles
        - question ? ajout d'une scène black en overlay ?
        """

        if self.transit:
            if time() - self.t_transit > self.tempo_transit:
                self.transit = 0

    def update_level(self):
        """Mise à jour du level."""

        level_old = self.level
        l = len(self.players)

        if l == 0:
            l = 1

        if level_old != l:
            self.transit = 1
            self.t_transit = time()

        # Maxi 10 joueurs
        if l > 10:
            l=10
            print("Nombre de joueurs supérieur à 10 soit", l)

        self.level = l

    def update_rank(self):
        """Gère le temps d'affichge de rank."""

        if self.scene == "rank":
            if time() - self.t_rank > 2:
                self.rank_end = 1
            if time() - self.t_rank > 2.1: # 5 ou 6 envoi
                self.rank_end = 1
                self.reset_data()

    def update_classement(self):
        """TODO: Fonction trop longue donc pas clair"""

        self.ranked = []

        # Je récupère ceux qui sont déjà classés
        for k, v in self.players.items():
            if "classement" in v:
                if v["classement"] != 0:
                    self.ranked.append(v["classement"])
        self.ranked.sort()

        # Je récupère ceux qui viennent de perdre
        # mais le nb de classés doit être inf au nb de joueurs, pas de 1:
        if len(self.ranked) < self.level:
            for k, v in self.players.items():
                if "classement" in v and "my_score" in v:
                    # Ceux qui viennent de perdre et ne ne sont pas encore classés
                    if v["classement"] == 0 and v["my_score"] == 0:
                        if len(self.ranked) == 0:
                            cl = len(self.players)
                        else:
                            cl = self.ranked[0] - 1
                        if cl != 1: # le gagnant est gérer ci-dessous
                            v["classement"] = cl
                            self.ranked.append(cl)
                            self.ranked.sort()

        # Si il y a un 2ème, c'est fini, le restant est le 1er
        # le score du dernier ne va pas à 0, et si il y va, il a gagné
        if 2 in self.ranked:
            # Qui a un classement = 0 ?
            for k, v in self.players.items():
                if "classement" in v and "name" in v:
                    if v["classement"] == 0:
                        v["classement"] = 1
                        self.winner = v["name"]
                        self.scene = "rank"
                        self.t_rank = time()
                        print("The winner is {}".format(self.winner))

        # Maj du dict du classement final, car un joueur est 1
        # mais 1 seul 1, parfois plus car le jeu continue à tourner
        verif = 0
        for i in self.ranked:
            if i == 1:
                verif += 1
        if 1 in self.ranked and verif == 1:
            clst = {}
            for k, v in self.players.items():
                if "classement" in v and "name" in v:
                    clst[v["name"]] = v["classement"]
            self.classement = clst
        else:
            self.classement = {}

    def update_blend(self, blend):
        """Maj de la position de la balle et du reset
        avec valeurs reçues de blender
         blend = {"ball": (1,1), "reset": 0}
        """

        self.ball = blend["ball"]
        self.paddle_1_pos = blend["paddle_1_pos"]
        self.reset = blend["reset"]

    def get_score(self):
        """Retourne les scores de tous les joueurs, dans une liste.
        Le dict est ordonné, j'ajoute les scores dans l'ordre.
        """

        score = []  # liste
        for k, v in self.players.items():
            if "my_score" in v:
                score.append(v["my_score"])

        if self.transit: # sert à rien fait dans le jeu
            score = [10] * self.level

        return score

    def get_who(self):
        """Retourne le numéro de tous les joueurs dans un dict
        {"toto":0, "tata":1}
        """

        who = {}
        a = 0
        for k, v in self.players.items():
            if "name" in v:
                who[v["name"]] = a
                a += 1
        return who

    def create_msg_for_all_players(self):
        """Appelé à 60 fps par le serveur dans MyTcpServerFactory.
        Commence par demander une mise à jour du jeu.
        Message à créer:
            {   "level": 2,
                "scene" : 'play',
                "classement": {},
                "ball": [7.19, 7.19],
                "score": [9, 7],
                "paddle": [[-9.4, 2.5], [-9.4, 0.40]],
                "who_are_you": {'moi': 0, 'toi': 1},
                "rank_end":  0,
                "reset": 0,
                "transit": 0 }
        """

        # Maj
        self.update_game_management()

        # Je regroupe tout
        msg = { "level": self.level,
                "scene" : self.scene,
                "classement": self.classement,
                "ball": self.ball,
                "score": self.get_score(),
                "paddle": self.paddle,
                "who_are_you": self.get_who(),
                "rank_end":   self.rank_end,
                "reset": self.reset,
                "transit": self.transit  }

        return msg

    def reset_data(self):
        """Reset si demandé par un joueur avec R
        ou à la fin de rank
        """

        print("Reset in Game Dictator")
        self.players = OrderedDict()
        self.ranked = []
        self.scene = "play"
        self.winner = ""
        self.rank_end = 0
        self.t_rank = 0
        self.classement = {}
        self.level = 0
        self.players = {}

    def delete_disconnected_players(self, user):
        """Appelé depuis MyTcpServer si conection lost."""

        try:
            del self.players[user]
            print("{} supprimé dans players".format(user))
        except:
            a = "Le joueur {} n'est plus dans le dictionnaire"
            print(a.format(user))

        for key, val in self.players.items():
            try:
                if val["user"] == user:
                    del self.players[key]
                    break
                print("{} supprimé dans players".format(key))
            except:
                print("{} n'est pas dans players".format(key))
