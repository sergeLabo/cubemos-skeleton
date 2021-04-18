
from time import sleep
from json import load
import numpy as np

GESTURES_UP  = {0: (13, 10),
                1: (10, 13),
                2: (7, 5),
                3: (4, 2),
                4: (4, 3),
                5: (7, 6),
                6: (1, 8)}


class Gestures:
    """Reconnaissance de gestes avec points COCO
    et envoi de note en OSC.
    """

    def __init__(self, client):
        """ COCO: points3D = [18* [1,2,3]]"""

        self.client = client

        self.depth = 1
        self.mini = 50
        self.maxi = -50
        self.step = 1  # int de 1 à 5
        # 36 notes possibles
        self.encours = [0] * 36

        self.nb_points = 18
        self.points = None

    def add_points(self, points):
        """points = liste de 18 items, soit [1,2,3] soit None"""
        self.points = points
        self.get_depth_mini_maxi_current()
        self.gestures()

    def get_depth_mini_maxi_current(self):
        """Moyenne de tous les z"""
        zs = []
        for point in self.points:
            if point:
                if point[2] != 1000:
                    zs.append(point[2])
        if zs:
            # Profondeur courrante
            depth = np.average(np.array(zs))
        else:
            depth = 1
        # mini maxi
        if depth < self.mini:
            self.mini = depth
        if depth > self.maxi:
            self.maxi = depth

        self.depth = depth
        self.get_step()

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
                if pas != 0:
                    self.step = int((self.depth - self.mini)/pas)
                else:
                    self.step = 1

    def gestures(self):
        """ step 1 --> 0 1 2 3 ... 6
            step 2 --> 7 8 9 10 ... 12
        """
        pts = self.points
        for key, val in GESTURES_UP.items():
            p2 = val[0]
            p1 = val[1]
            if pts[p1] and pts[p2]:
                note = key + self.step*5
                if pts[p2][1] > pts[p1][1] + 0.1:
                    if not self.encours[note]:
                        print("Envoi de:", note)
                        self.client.send_msg(b'/note', note)
                        self.encours[note] = 1
                if pts[p2][1] < pts[p1][1] - 0.1:
                    self.encours[note] = 0


def read_json(fichier):
    try:
        with open(fichier) as f:
            data = load(f)
        f.close()
    except:
        data = None
        print("Fichier inexistant ou impossible à lire.")
    return data


def get_points(data):
    """frame_data = list(coordonnées des points empilés d'une frame
        soit 3*18 items avec:
            mutipliées par 1000
            les None sont remplacés par (-1000000, -1000000, -1000000)
            le numéro du body (dernier de la liste) doit être enlevé
    """
    # Réception de 54=3*18 ou 45=3*15
    points = None
    if len(data) == 54 or len(data) == 45:
        nombre = int(len(data)/3)
        points = []
        for i in range(nombre):
            # data[de 0 à 54] n'est jamais None car vient de l'OSC
            val = [ data[(3*i)],
                    data[(3*i)+1],
                    data[(3*i)+2]]
            if val == [-1000000, -1000000, -1000000]:
                points.append(None)
            else:
                # Less coords sont multipliées par 1000 avant envoi en OSC
                # Permutation de y et z, z est la profondeur pour RS et OpenCV
                # et inversion de l'axe des y en z
                points.append([val[0]/1000, val[2]/1000, -val[1]/1000])

    return points


if __name__ == "__main__":

    from osc_client import OscClt

    clt = OscClt(b'localhost', 8003)

    gest = Gestures(clt)

    fichier = "./json/cap_2021_04_17_13_56.json"
    data = read_json(fichier)

    for i in range(len(data)):
        points = get_points(data[i][:-1])
        gest.add_points(points)
        sleep(0.06)
