
import sys
from time import time, sleep
from json import load
import numpy as np


GESTURES  = {   2: (7, 5),
                3: (4, 2),
                0: (13, 10),
                1: (10, 13),
                2: (7, 5),
                3: (4, 2),
                4: (4, 3),
                5: (7, 6),
                6: (1, 8) }

K_NOTE = 0.3  # hystérésis des keypoints
K_ABSURDE = 1  # points trop éloignés par rapport à la frame précédente
K_FAR_AWAY = 3  # points trop éloignés du centre
LISSAGE = 3  # moyenne des LISSAGE dernières valeurs


class Gestures:
    """Reconnaissance de gestes avec points COCO
    et envoi de note en OSC.
    """
    def __init__(self, client):
        """ COCO: points3D = [18* [1,2,3]]"""

        self.client = client

        self.depth = 0.5
        self.mini = 1.5
        self.maxi = 6
        self.step = 1  # int de 1 à 5

        # 36 notes possibles
        self.encours = [0] * 36

        self.nb_points = 18
        self.points = None
        self.points_old = None
        self.center = [0,0,0]

        # Lissage: 18 x 3 x LISSAGE
        self.liss = []
        for i in range(18):
            self.liss.append([])
            for j in range(3):
                self.liss[i].append([])
        for i in range(18):
            for j in range(3):
                self.liss[i][j] = [0] * LISSAGE

    def add_points(self, points):
        """points = liste de 18 items, soit [1,2,3] soit None

        Filtres:
            Les points ne sont pas supprimés mais remplacés par None

        """

        self.points = points

        # Suppression des points trop éloignés par rapport à la frame précédente
        self.delete_absurde()

        # Suppression des points trop éloignés du centre
        self.delete_far_away()

        # Lissage avec moyenne des LISSAGE dernières valeurs
        self.get_lisse_points()

        # Centre, step, application pour notes
        self.get_center()
        self.get_step()
        self.gestures()

    def get_lisse_points(self):
        """Pour chaque coordonnées (18*3),
                moyenne des LISSAGE dernières valeurs"""
        points = self.points
        if points:
            for i in range(18):
                if points[i]:
                    for j in range(3):
                        self.liss[i][j].append(points[i][j])
                        # Si liss rempli, je détruits le 1er
                        if len(self.liss[i][j]) == LISSAGE + 1:
                            del self.liss[i][j][0]
                # si pas de point, je ne rajoute rien dans la pile

        smoothed_points = []
        for i in range(18):
            smoothed_points.append([0, 0, 0])

        for i in range(18):
            for j in range(3):
                # Moyenne des LISSAGE de [18][3]
                moy = 0
                for k in range(LISSAGE):
                    moy += self.liss[i][j][k]
                smoothed_points[i][j] = moy / LISSAGE

        self.points = smoothed_points

    def delete_absurde(self):
        """Suppression des points trop éloignés par rapport à la position
        de la frame précédente.
        """
        if not self.points_old:
            self.points_old = self.points
        points_correct = []
        for i in range(len(self.points)):
            if self.points[i] and self.points_old[i]:
                a = np.asarray(self.points[i])
                b = np.asarray(self.points_old[i])
                norme = np.sqrt(np.sum(a - b)**2)
                if norme < K_ABSURDE:
                    points_correct.append(self.points[i])
                else:
                    points_correct.append(None)
            else:
                points_correct.append(None)

        # Mise en mémoire des dernières valeurs
        self.points_old = self.points
        # Mise à jour avec nouvelles valeurs
        self.points = points_correct

    def delete_far_away(self):
        """Suppression des points trop éloigné du centre"""
        points_good = []
        for point in self.points:
            if point:
                u = np.asarray(point)
                v = np.asarray(self.center)
                norme = np.sqrt(np.sum(u - v)**2)
                if norme < K_FAR_AWAY:
                    points_good.append(point)
                else:
                    points_good.append(None)
            else:
                points_good.append(None)

        self.points = points_good

    def get_center(self):
        """Moyenne de tous les z"""
        x_sum, y_sum, z_sum = [], [], []
        for point in self.points:
            if point:
                # point[0] != 1000 suffit, x et y seront aussi != 1000
                if point[0] != 1000:
                    x_sum.append(point[0])
                    y_sum.append(point[1])
                    z_sum.append(point[2])

        if x_sum:
            x_average = np.average(np.array(x_sum))
            self.center[0] = x_average
        if y_sum:
            y_average = np.average(np.array(y_sum))
            self.center[1] = y_average
            self.depth = y_average
        if z_sum:
            z_average = np.average(np.array(z_sum))
            self.center[2] = z_average

    def get_step(self):
        """Division en 5 step de la profondeur
        step = int de 1 à 5, maxi = 2, mini = 0.5
        pas = (maxi - mini)/5
        si maxi = 2,5 mini = 0,5 pas = 0.4
        si depth = 2
        step = (2 - 0.5)/0.4 = 3.75 --> int(3.75) --> 3
        """
        if self.maxi - self.mini != 0:
            pas = (self.maxi - self.mini)/5
            if self.depth is not None:
                self.step = (self.depth - self.mini)/pas

    def gestures(self):
        """ step 1 --> 0 1 2 3 ... 6
            step 2 --> 7 8 9 10 ... 12
        """
        pts = self.points
        if pts:
            for key, val in GESTURES.items():
                p2 = val[0]
                p1 = val[1]
                if pts[p1] and pts[p2]:
                    note = int(key + self.step*5)
                    if note < 0: note = 0
                    if note > 35: note = 35
                    # z plus haut
                    if pts[p2][2] > pts[p1][2] + K_NOTE:
                        if not self.encours[note]:
                            # #print(round(pts[p2][2], 2), round(pts[p1][2], 2))
                            # #print("Envoi de:", note)
                            self.client.send_msg(b'/note', note)
                            self.encours[note] = 1
                    # z plus bas
                    if pts[p2][2] < pts[p1][2] - K_NOTE:
                        self.encours[note] = 0


def read_json(fichier):
    """Tous les messages dans une liste dans un json"""
    try:
        with open(fichier) as f:
            data = load(f)
        f.close()
    except FileNotFoundError as e:
        print(e)
        sys.exit()
    return data


def get_points_blender(data):
    """ Récupération des points:
            frame_data = list(coordonnées des points empilés d'une frame
            soit 3*18 items avec:
            mutipliées par 1000
            les None sont remplacés par (-1000000, -1000000, -1000000)
            le numéro du body (dernier de la liste) doit être enlevé
        Conversion:
            Conversion de cubemos en blender
            Les coords sont multipliées par 1000 avant envoi en OSC
            Permutation de y et z, z est la profondeur pour RS et OpenCV
            et inversion de l'axe des y en z

    """

    # Réception de 54=3*18 ou 45=3*15
    if len(data) == 54 or len(data) == 45:
        nombre = int(len(data)/3)
        points = []
        for i in range(nombre):
            # Reconstruction par 3
            val = [ data[(3*i)],
                    data[(3*i)+1],
                    data[(3*i)+2]]
            if val == [-1000000, -1000000, -1000000]:
                points.append(None)
            else:
                # Conversion
                points.append([val[0]/1000, val[2]/1000, -val[1]/1000])
    else:
        points = None

    return points


if __name__ == "__main__":
    """Lecture d'un json avec les messages envoyés d'une capture,
    filtre, nettoyage, et reenvoi comme si capture en temps réel.
    """

    from osc_client import OscClt

    t0 = time()
    n = 0
    clt = OscClt(b'localhost', 8003)
    gest = Gestures(clt)

    fichier = "./json/cap_2021_04_25_14_30.json"
    data = read_json(fichier)
    print("Nombre de data:", len(data))

    depths = []
    centersx = []
    centersy = []
    centersz = []
    xs = []
    x = 0
    for i in range(0, len(data), 1):

        # Les points dans les json sont au format cubemos*1000
        # avec y et z interverti et y inversé
        points_blender = get_points_blender(data[i][0][:-1])

        gest.add_points(points_blender)

        # get_points convertit les points cubemos en point blender
        # points = [None, [-1.535, 5.456, 0.569], None, None, None,
        # [-1.466, 5.388, 0.511], ... 18 points]
        # send_global_message(self, points3D, bodyId=110): au format de cubemos
        # avec y et z intervertit et y positif vers le bas
        # je reconverti:
        points_cubemos = []
        for point in gest.points:
            if not point:
                points_cubemos.append(None)
            else:
                # les z deviennent y vers le bas
                points_cubemos.append([ point[0], -point[2], point[1]])
        # #print("points_cubemos", points_cubemos, "\n")
        # Multiplication par 1000 et sérialisation fait par osc
        clt.send_global_message(points_cubemos)

        # Ajout dans les listes pour enregistrement
        depths.append(gest.depth)
        centersx.append(gest.center[0])
        centersy.append(gest.center[1])
        centersz.append(gest.center[2])
        xs.append(x)
        x += 1

        # #sleep(0.065)
        n += 1
        t = time()
        if t - t0 > 10:
            print(  "FPS =", round(n/10, 1),
                    "depth :", gest.depth,
                    "center :", gest.center)
            t0 = t
            n = 0

    np.save('./json/depths.npy', np.asarray(depths))
    np.save('./json/centersx.npy', np.asarray(centersx))
    np.save('./json/centersy.npy', np.asarray(centersy))
    np.save('./json/centersz.npy', np.asarray(centersz))
    np.save('./json/xs.npy', np.asarray(xs))
