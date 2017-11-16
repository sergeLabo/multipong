#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = '0.024'

"""
pas d'accent dans les fichiers !!!!!!!!!!!!!!!
ne pas oublier de commenter le Window.size

version
0.024 avec class Game
0.023 test user id
0.022 fullscreen tout construit correct
0.021 landscape
"""


import kivy
kivy.require('1.10.0')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import ListProperty
from kivy.properties import ReferenceListProperty
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.config import Config
from kivy.lang import Builder
from kivy.vector import Vector
from kivy.clock import Clock

import os
from time import time
import json
import ast
from threading import Thread

# Les fichiers de ces modules sont dans le dossier courrant
# Reception en multicast
from labmulticast import Multicast
# Envoi en TCP
from labtcpclient import LabTcpClient

Window.size = (1280, 720)

"""
1 joueur carre
2 joueur carre
3 joueur triangle
4 joueur carre
5 joueur penta
6 joueur hexa
7 joueur hepta
8 joueur octa
9 joueur ennea
10 joueur deca
"""

# Variables globales

# Points des polygones = coordonnees blender
# et correction [offset_x, offset_y, size]

carre = [-9.93542,  9.935437,
          9.93543,  9.93543,
          9.93543, -9.93543,
         -9.93543, -9.93543]

carre_correction = [360, 360, 36]

triangle = [0, 12.12306,
            -14.22068, -12.50787,
            14.22068, -12.50787]

triangle_correction = [418, 366, 29]

penta = [   0,        9.34335,
            9.74,     2.26683,
            6.01965, -9.18323,
           -6.01965, -9.18323,
           -9.74,     2.26683]

penta_correction = [380, 358, 38.6]

hexa = []
hepta = []
octa = []
ennea = []
deca = []

def lines_points(poly, poly_correction):
    """Retourne la liste des points pour dessiner le polygone.
    poly=liste des points avec coordonnees blender
    poly_correction=[offset_x, offset_y, size_x, size_y]
    """

    pc = poly_correction
    points_list = []

    for i in range(len(poly)):
        # size
        pt =  poly[i] * poly_correction[2]

        # Offset
        if i % 2 == 0:
            pt += poly_correction[0]
        if i % 2 != 0:
            pt += poly_correction[1]

        points_list.append(int(pt))

    return points_list

def datagram_to_dict(data):
    """Decode le message.
    Retourne un dict ou None
    """

    try:
        dec = data.decode("utf-8")
    except:
        print("Decodage UTF-8 impossible")
        dec = data

    try:
        msg = ast.literal_eval(dec)
    except:
        print("ast.literal_eval impossible")
        msg = dec

    if isinstance(msg, dict):
        return msg
    else:
        print("Message reçu: None")
        return None

def get_user_id():
    """u0_a73"""

    try:
        user = os.getlogin()
        print("User login:", user)
    except:
        user = "j" + str(int(time()[-8:]))
        print("User:", user)
    return  user


class Screen5(Screen):
    """Ecran pour 5 joueurs"""

    p = lines_points(penta, penta_correction)
    points = ListProperty(p)

    def __init__(self, **kwargs):

        super(Screen5, self).__init__(**kwargs)


class Screen4(Screen):
    """Ecran pour 4 joueurs"""

    p = lines_points(carre, carre_correction)
    points = ListProperty(p)

    def __init__(self, **kwargs):

        super(Screen4, self).__init__(**kwargs)


class Screen3(Screen):
    """Ecran pour 3 joueurs"""

    p = lines_points(triangle, triangle_correction)
    points = ListProperty(p)

    def __init__(self, **kwargs):

        super(Screen3, self).__init__(**kwargs)


class Screen2(Screen):
    """Ecran pour 2 joueurs"""

    p = lines_points(carre, carre_correction)
    points = ListProperty(p)

    def __init__(self, **kwargs):

        super(Screen2, self).__init__(**kwargs)


class Screen1(Screen):
    """Le joueur sera 'Joueur 1'"""

    # Ce sont des attibuts de classe
    # Accessible avec root.points dans kv
    ball = ObjectProperty(None)
    points = ListProperty(lines_points(carre, carre_correction))
    paddle = ListProperty((15, 320, 700, 320))

    def __init__(self, **kwargs):
        super(Screen1, self).__init__(**kwargs)

    def apply_ball_position(self, ball_pos):
        """Positionne la balle avec position du serveur
        TODO: serait mieux avec center
        """

        cc = carre_correction

        self.ball.pos[0] = int((ball_pos[0]*cc[2]) + cc[0] - 6)
        self.ball.pos[1] = int((ball_pos[1]*cc[2]) + cc[1] - 6)

    def on_touch_move(self, touch):
        ##Screen1.paddle[1] = touch.y
        pass


class PongBall(Widget):
    center_x = NumericProperty(0)
    center_y = NumericProperty(0)
    center = ReferenceListProperty(center_x, center_y)

    def move(self):
        pass


class MainScreen(Screen):
    """Ecran principal"""

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        # Construit le reseau, tourne tout le temps
        scr_manager = self.get_screen_manager()
        #self.network = Network(scr_manager)
        self.game = Game(scr_manager)

    def get_screen_manager(self):
        return MultiPongApp.get_running_app().screen_manager


class Network:
    """Les Screen accede a Network avec
    MultiPongApp.get_running_app()
    """

    def __init__(self, screen_manager):

        # config, obtenu avec des dir()
        config = MultiPongApp.get_running_app().config

        # Multi
        self.multi_ip, self.multi_port = self.get_multicast_addr(config)
        self.my_multi = Multicast(  self.multi_ip,
                                    self.multi_port,
                                    1024)
        self.server_msg = None

        # Serveur data
        self.dictat = None

        # TCP
        self.tcp_ip = None
        self.tcp_port = self.get_tcp_port(config)
        self.tcp_clt = None
        self.tcp_msg = {}

    def network_update(self):
        """Maj de reception, maj des datas, envoi"""

        # Recup du message su serveur en multicast
        svr_msg = self.get_multicast_msg()
        self.dictat = self.get_svr_data(svr_msg)

        # Recup ip serveur si pas deffinie
        self.set_server_addr()

        # Creation du socket TCP si None
        self.create_tcp_socket()

    def get_svr_data(self, svr_msg):
        """Retourne dictat"""

        try:
            sm = svr_msg["svr_msg"]
            dictat = sm["dictat"]
        except:
            dictat = None

        return dictat

    def get_multicast_addr(self, config):
        """Retourne l'adresse multicast"""

        multi_ip = config.get('network', 'multi_ip')
        multi_port = int(config.get('network', 'multi_port'))

        return multi_ip, multi_port

    def get_multicast_msg(self):
        """{svr_msg = 'svr_msg':
                    {'ip': '192.168.1.12',
                    'dictat': {
                        'level': 1,
                        'ball': [9.556015014648438, 9.324382781982422],
                        'transit': 0,
                        'who_are_you': {},
                        'rank_end': 0,
                        'paddle': {},
                        'score': [],
                        'scene': 'play',
                        'classement': {},
                        'reset': 0}}}
        """

        try:
            data = self.my_multi.receive()
            svr_msg = datagram_to_dict(data)
        except:
            print("Pas de reception multicast")
            svr_msg = None
        return svr_msg

    def get_tcp_port(self, config):
        """Retourne le port TCP"""

        return int(config.get('network', 'tcp_port'))

    def set_server_addr(self):
        """Recupere l'ip du serveur, et defini l'adresse serveur."""

        if self.dictat and "ip" in self.dictat and not self.tcp_ip:
            self.tcp_ip = self.svr_data["svr_msg"]["ip"]

    def create_tcp_socket(self):
        if self.tcp_ip and not self.tcp_clt:
            try:
                self.tcp_clt = LabTcpClient(self.tcp_ip,
                                            self.tcp_port)
            except:
                self.tcp_clt = None
                print("Pas d'ip dans le message du serveur")

    def send_tcp_msg(self):
        env = json.dumps(self.tcp_msg).encode("utf-8")
        if self.tcp_clt:
            self.tcp_clt.send(env)


class Game(Network):

    def __init__(self, screen_manager, **kwargs):

        super(Game, self).__init__(screen_manager, **kwargs)

        self.scr_manager = screen_manager
        self.cur_screen = self.get_current_screen()

        # Rafraichissement du jeu
        tempo = 0.03 #self.get_tempo()
        self.event = Clock.schedule_interval(self.game_update, tempo)

        # Verif freq
        self.t = time()
        self.v_freq = 0

        self.my_name = get_user_id()

    def get_tempo(self):
        """Retourne la tempo de la boucle de Clock."""

        config = MultiPongApp.get_running_app().config
        freq = int(config.get('network', 'freq'))

        if freq > 60:
            freq = 60
        if freq < 1:
            freq = 1
        print("Frequence d'envoi en TCP =", freq)
        return 1/freq

    def game_update(self, dt):
        """self.dictat = {"level":  2,
                        "scene" : 'play',
                        "classement": {},
                        "ball":   [7.19, 7.19],
                        "score":  [9, 7],
                        "paddle": {0: [-9.4, 0.0], 1: [-9.4, 0.40]},
                        "who_are_you": {'moi': 0, 'toi': 1},
                        "rank_end": 0,
                        "reset":   0,
                        "transit": 0 }, "ip": etc ...}}
        """

        self.verif_freq()
        self.network_update()

        # Maj du screen courant
        self.get_current_screen()

        # Apply
        self.apply_ball_pos()
        self.apply_paddle_pos()

        # Envoi au serveur
        self.create_msg()
        self.send_tcp_msg()

    def apply_ball_pos(self):
        try:
            ball_pos = self.dictat["ball"]
        except:
            ball_pos = None

        if ball_pos:
            if self.cur_screen.name != "Main":
                # Les screen de 1 a 10 doivent avoir apply_ball_position
                self.cur_screen.apply_ball_position(ball_pos)

    def apply_paddle_pos(self):
        pass

    def create_msg(self):
        if "Main" not in self.cur_screen.name:
            self.tcp_msg = {"joueur": {"name":   self.my_name,
                                       "paddle": self.get_paddle()}}

    def verif_freq(self):
        self.v_freq += 1
        a = time()
        if a - self.t > 1:
            print("FPS:", self.v_freq)
            self.v_freq = 0
            self.t = a

    def get_current_screen(self):
        """Set le screen en cours"""

        self.cur_screen = self.scr_manager.current_screen

    def get_paddle(self):
        """retourne pos de ma paddle"""
        return [6, 5]

    def get_my_name():
        if "Main" not in self.cur_screen.name:
            return "Joueur" + self.cur_screen
        else:
            return None



SCREENS = { 0: (MainScreen, "Main"),
            1: (Screen1,    "1"),
            2: (Screen2,    "2"),
            3: (Screen3,    "3"),
            4: (Screen4,    "4"),
            5: (Screen5,    "5")}


class MultiPongApp(App):
    """Construction de l'application. Execute par __main__,
    app est le parent de cette classe dans kv.
    """

    def build(self):
        """Execute en premier apres run()"""

        # Creation des ecrans
        self.screen_manager = ScreenManager()
        for i in range(len(SCREENS)):
            self.screen_manager.add_widget(SCREENS[i][0](name=SCREENS[i][1]))
        return self.screen_manager

    def on_start(self):
        """Execute apres build()"""
        pass

    def build_config(self, config):
        """Si le fichier *.ini n'existe pas,
        il est cree avec ces valeurs par defaut.
        Si il manque seulement des lignes, il ne fait rien !
        """

        config.setdefaults('network',
                            { 'multi_ip': '228.0.0.5',
                              'multi_port': '18888',
                              'tcp_port': '8000',
                              'freq': '60'})

        config.setdefaults('kivy',
                            { 'log_level': 'debug',
                              'log_name': 'multipong_%y-%m-%d_%_.txt',
                              'log_dir': '/sdcard',
                              'log_enable': '1'})

        config.setdefaults('postproc',
                            { 'double_tap_time': 250,
                              'double_tap_distance': 20})

    def build_settings(self, settings):
        """Construit l'interface de l'ecran Options,
        pour multipong seul,
        Kivy est par defaut,
        appele par app.open_settings() dans .kv
        """

        data = """[{"type": "title", "title": "Configuration du reseau"},

                      {"type": "numeric",
                      "title": "Frequence d'envoi",
                      "desc": "Frequence entre 1 et 60 Hz",
                      "section": "network", "key": "freq"}
                   ]"""

        # self.config est le config de build_config
        settings.add_json_panel('MultiPong', self.config, data=data)

    def on_config_change(self, config, section, key, value):
        """Si modification des options, fonction appelee automatiquement."""

        freq = int(self.config.get('network', 'freq'))
        menu = self.screen_manager.get_screen("Main")

        if config is self.config:
            token = (section, key)

            # If frequency change
            if token == ('network', 'freq'):
                # Restart the server with new address
                #self.screen_manager.get_screen("Main").restart_server()
                print("Nouvelle frequence", freq)

    def go_mainscreen(self):
        """Retour au menu principal depuis les autres ecrans."""

        #if touch.is_double_tap:
        self.screen_manager.current = ("Main")

    def do_quit(self):
        """Quitter proprement."""

        print("Quitter proprement")

        # Stop propre de Clock
        menu = self.screen_manager.get_screen("Main")
        menu.game.event.cancel()

        # Kivy
        MultiPongApp.get_running_app().stop()

        # Extinction de tout
        os._exit(0)


if __name__ == '__main__':
    MultiPongApp().run()
