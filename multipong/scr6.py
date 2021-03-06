#! /usr/bin/env python3
# -*- coding: utf-8 -*-


# #####################################################################
# Copyright (C) Labomedia November 2017
#
# This file is part of multipong.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# #####################################################################


import kivy
kivy.require('1.10.0')

from kivy.app import App
from kivy.properties import ListProperty
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from terrain import Terrain
from touch_improve import projection

# Points pour kivy
NUM = 6
TERRAIN = Terrain(NUM)
LINE = TERRAIN.line
NET = TERRAIN.net_line
PATH = TERRAIN.path_line


# Pass variable between python script http://bit.ly/2n0ksWh
from __main__ import *


class Screen6(Screen):
    """Ecran pour 6 joueurs en position 0 1 2 3 4 5"""

    points = ListProperty(LINE)
    net = ListProperty(NET)
    ball = ObjectProperty()

    paddle_0 = ObjectProperty()
    paddle_1 = ObjectProperty()
    paddle_2 = ObjectProperty()
    paddle_3 = ObjectProperty()
    paddle_4 = ObjectProperty()
    paddle_5 = ObjectProperty()

    score_0 = ObjectProperty()
    score_1 = ObjectProperty()
    score_2 = ObjectProperty()
    score_3 = ObjectProperty()
    score_4 = ObjectProperty()
    score_5 = ObjectProperty()

    titre = ObjectProperty()
    classement = ObjectProperty()

    def __init__(self, **kwargs):

        super(Screen6, self).__init__(**kwargs)

        self.coef = COEF

        # mon numéro
        self.my_num = 0

        # Dict des paddles
        self.paddle_d = {   0: self.paddle_0,
                            1: self.paddle_1,
                            2: self.paddle_2,
                            3: self.paddle_3,
                            4: self.paddle_4,
                            5: self.paddle_5}

        self.paddle_d[0].source = './images/g_m60.png'
        self.paddle_d[1].source = './images/g_v.png'
        self.paddle_d[2].source = './images/g_m30.png'
        self.paddle_d[3].source = './images/g_m60.png'
        self.paddle_d[4].source = './images/g_v.png'
        self.paddle_d[5].source = './images/g_m30.png'

        # Ma paddle position
        self.my_pad_pos = [0, 0]

        # Dict des scores
        self.score_d = {    0: self.score_0,
                            1: self.score_1,
                            2: self.score_2,
                            3: self.score_3,
                            4: self.score_4,
                            5: self.score_5}

        # height = 100 --> bidouille
        h = 720 * self.coef
        # 1/2 Taille de la balle
        self.BALL = h/(33*2)
        # 1/2 Taille de paddle
        self.PADDLE = h/(10.8*2)

    def apply_paddle_red_color(self):
        """J'applique le rouge à ma paddle"""

        if self.my_num == 0:
            self.paddle_d[0].source = './images/r_m60.png'
            self.paddle_d[1].source = './images/g_v.png'
            self.paddle_d[2].source = './images/g_m30.png'
            self.paddle_d[3].source = './images/g_m60.png'
            self.paddle_d[4].source = './images/g_v.png'
            self.paddle_d[5].source = './images/g_m30.png'
        if self.my_num == 1:
            self.paddle_d[0].source = './images/g_m60.png'
            self.paddle_d[1].source = './images/r_v.png'
            self.paddle_d[2].source = './images/g_m30.png'
            self.paddle_d[3].source = './images/g_m60.png'
            self.paddle_d[4].source = './images/g_v.png'
            self.paddle_d[5].source = './images/g_m30.png'
        if self.my_num == 2:
            self.paddle_d[0].source = './images/g_m60.png'
            self.paddle_d[1].source = './images/g_v.png'
            self.paddle_d[2].source = './images/r_m30.png'
            self.paddle_d[3].source = './images/g_m60.png'
            self.paddle_d[4].source = './images/g_v.png'
            self.paddle_d[5].source = './images/g_m30.png'
        if self.my_num == 3:
            self.paddle_d[0].source = './images/g_m60.png'
            self.paddle_d[1].source = './images/g_v.png'
            self.paddle_d[2].source = './images/g_m30.png'
            self.paddle_d[3].source = './images/r_m60.png'
            self.paddle_d[4].source = './images/g_v.png'
            self.paddle_d[5].source = './images/g_m30.png'
        if self.my_num == 4:
            self.paddle_d[0].source = './images/g_m60.png'
            self.paddle_d[1].source = './images/g_v.png'
            self.paddle_d[2].source = './images/g_m30.png'
            self.paddle_d[3].source = './images/g_m60.png'
            self.paddle_d[4].source = './images/r_v.png'
            self.paddle_d[5].source = './images/g_m30.png'
        if self.my_num == 5:
            self.paddle_d[0].source = './images/g_m60.png'
            self.paddle_d[1].source = './images/g_v.png'
            self.paddle_d[2].source = './images/g_m30.png'
            self.paddle_d[3].source = './images/g_m60.png'
            self.paddle_d[4].source = './images/g_v.png'
            self.paddle_d[5].source = './images/r_m30.png'

    def apply_my_num(self, my_num):
        """Appelé par main Game apply_my_num"""

        self.my_num = my_num

    def apply_score(self, score):
        """Set les scores
        apply_score(score)
        score = [4, 2, 5, 8, 7, 9]
        """

        n = min(len(score), NUM)
        for i in range(n):
            self.score_d[i].text = str(score[i])

    def apply_ball_pos(self, ball_pos):
        """Positionne la balle avec position du serveur."""

        if ball_pos:
            x, y = TERRAIN.get_kivy_coord(ball_pos)

            # Correction de Window size
            x *= self.coef
            y *= self.coef

            # Ajout du décalage de centre de ball, pas de coef
            s = self.BALL
            x -= s
            y -= s

            X = int(x)
            Y = int(y)

            self.ball.pos = [X, Y]

    def apply_other_paddles_pos(self, paddle_pos):
        """  Toutes les paddles sauf la mienne
             moi         l'autre
        [[-9.5, 0.0], [9.5, -1.81], [0, 0], [0, 0], ....]
        au reset len(paddle_pos) = 10
        """

        n = min(len(paddle_pos), NUM)
        for pp in range(n):
            if pp != self.my_num and paddle_pos[pp]!= [0, 0]:
                x, y = TERRAIN.get_kivy_coord(paddle_pos[pp])

                # Correction de Window size
                x *= self.coef
                y *= self.coef

                # Ajout du décalage de centre de paddle
                s = self.PADDLE
                x -= s
                y -= s

                X = int(x)
                Y = int(y)

                self.paddle_d[pp].pos = [X, Y]

    def apply_classement(self, classement):
        """Applique le classement
        classement = {'pierre': 1, 'AI': 2}
        str = 'pierre': 1, 'AI': 2
        """

        text = "\n"
        if classement:
            for i in range(len(classement)):
                for name, rank in classement.items():
                    if rank == i + 1:
                        if name != "Isac  Asimov":
                            name = name[:-8]
                        text += ". " + str(i+1) + "  " + name + "\n\n"

            self.classement.text = text
            self.titre.text = "Classement"
        else:
            self.titre.text = ""
            self.classement.text = ""

    def on_touch_move(self, touch):
        """Capture de la position de touch"""

        x = touch.x/self.coef
        y = touch.y/self.coef

        if self.my_num is not None:
            self.apply_touch(x, y)

    def apply_touch(self, x, y):
        """Calcul du déplacement de ma paddle."""

        if self.my_num == 0:
            x1, y1, x2, y2 = (PATH[0], PATH[1], PATH[2], PATH[3])

        # Vertical y = y
        if self.my_num == 1:
            x = PATH[2] # x du 2ème points

        if self.my_num == 2:
            x1, y1, x2, y2 = (PATH[4], PATH[5], PATH[6], PATH[7])

        if self.my_num == 3:
            x1, y1, x2, y2 = (PATH[6], PATH[7], PATH[8], PATH[9])

        # Vertical y = y
        if self.my_num == 4:
            x = PATH[10] # x du 5ème points

        if self.my_num == 5:
            x1, y1, x2, y2 = (PATH[10], PATH[11], PATH[0], PATH[1])

        # Les non verticales
        if self.my_num in [0, 2, 3, 5]:
            # Correction pour saisie zone noire à droite
            if self.my_num == 0:
                x -= 580
            if self.my_num == 2:
                x -= 500
            if self.my_num == 3:
                x -= 580
            if self.my_num == 5:
                x -= 500
            x, y = projection(x1, y1, x2, y2, x, y)
            x, y = projection(x1, y1, x2, y2, x, y)

        # Position centée de ma paddle pour blender
        self.my_pad_pos = [x, y]
        # Pour kivy ici
        self.apply_my_paddle_pos(x, y)

    def apply_my_paddle_pos(self, x, y):
        """Avec la capture de position sur l'écran"""

        # Correction de Window size
        x *= self.coef
        y *= self.coef

        # Ajout du décalage de centre de ball, pas de coef
        s = self.PADDLE
        x -= s
        y -= s

        X = int(x)
        Y = int(y)

        if self.my_num is not None:
            # Ma position
            self.paddle_d[self.my_num].pos = [X, Y]

    def get_my_blender_paddle_pos(self):
        """Retourne la position de ma paddle, pour envoyer au serveur
        """

        [x, y] = TERRAIN.get_blender_coord(self.my_pad_pos)

        return [x, y]
