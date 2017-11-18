# Multi Pong

## Jeu de pong sur android jusqu'à 10 joueurs

### Licence

~~~text
Copyright (C) Labomedia November 2017

Multi Pong is licensed under the
    Creative Commons Attribution-ShareAlike 3.0 Unported License.

To view a copy of this license, visit
    [creativecommons.org](http://creativecommons.org/licenses/by-sa/3.0/)

or send a letter to
    Creative Commons
    444 Castro Street
    Suite 900, Mountain View
    California, 94041
    USA
~~~

### Kivy, buildozer, python 3.5

Construit sur Debian Stretch 9.2

Voir [Kivy Buildozer pour créer une application Android avec un script python](https://wiki.labomedia.org/index.php/Kivy_Buildozer_pour_cr%C3%A9er_une_application_Android_avec_un_script_python)

pour l'installation de buildozer et son utilisation.

### Installation du serveur sur un PC

#### Pricipe du serveur
Le script sh lance un script python et un blend avec le blenderplayer.

Le serveur envoie en multi-cast en permanence à tous les joueurs et blender toutes les datas nécessaires avec en plus l'IP du serveur pour que les joueurs envoient en TCP.

Le Blender Game Engine sert de moteur physique et de visualisation du jeu sur grand écran.

#### Installation de twisted

* [Installation de Twisted pour python 3.x](https://wiki.labomedia.org/index.php/Installation_de_Twisted_pour_python_3.x)

#### Installation de kivy

* [Installation de Kivy](https://wiki.labomedia.org/index.php/2_Kivy:_Installation)

#### Installation de Blender

~~~text
sudo apt-get install blender
~~~

#### Installation de mylabotools

mylabotools comprend mes scripts pour mes tâches courantes.

Voir  [mylabotools](https://github.com/sergeLabo/mylabotools)

### Installation sur android
Récupérer le apk sur votre téléphone, l'installer après avoir autorisé les sources inconnues puisque la source est connue !!

### Réception sur Android en Multicast

Dans buildozer.spec, définir:

~~~text
android.permissions = INTERNET,CHANGE_WIFI_MULTICAST_STATE,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE
~~~


### Merci à La Labomedia
