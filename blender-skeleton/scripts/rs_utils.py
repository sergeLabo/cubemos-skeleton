from time import time, sleep
import json
from collections import deque

try:
    from scipy.signal import savgol_filter
    SCIPY = True
except:
    print("Vous devez installer scipy !")
    SCIPY = False

class Filtre:
    """Filtre les points reçus du RealSense
    piles[17][2] = deque([1.937, -0.495, 0.144, 3.24], maxlen=4)
    """

    def __init__(self, nb_points=18, pile_size=20):

        self.pile_size = pile_size
        self.nb_points = nb_points
        self.points = None

        self.piles = []
        for i in range(self.nb_points):
            self.piles.append([])
            for j in range(3):
                self.piles[i].append(deque(maxlen=pile_size))

        # Filtre
        self.window_length = self.get_window_length()
        self.order = 2

    def add(self, points):
        """points = liste de 15 items, soit [1,2,3] soit None"""
        # Si pas de points, on passe
        self.points = points
        if points:
            for i in range(self.nb_points):
                if points[i]:
                    for j in range(3):  # 3
                        self.piles[i][j].append(points[i][j])

    def get_smooth_points(self):
        """Calcul de 15 points lissés, même structure que self.points
        Si la pile n'est pas remplie, retourne None pour ce point.
        Ne tiens pas compte de self.points
        """
        smooth_points = [0]*self.nb_points
        for i in range(self.nb_points):
            smooth_points[i] = []
            for j in range(3):
                if len(self.piles[i][j]) == self.pile_size:
                    three_points_smooth = savgol_filter(list(self.piles[i][j]),
                                                        self.window_length,
                                                        self.order)
                    pt = round(three_points_smooth[-1], 3)
                    smooth_points[i].append(pt)
        return smooth_points

    def get_window_length(self):
        """window_length=impair le plus grand dans la pile"""

        if self.pile_size % 2 == 0:
            window_length = self.pile_size - 1
        else:
            window_length = self.pile_size
        return window_length


def read_json(fichier):
    try:
        with open(fichier) as f:
            data = json.load(f)
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
    else:
        points = None

    return points


if __name__ == '__main__':

    filtre = Filtre(15, 20)
    fichier = "./json/cap_2021_04_11_14_32.json"
    data = read_json(fichier)

    for i in range(len(data)):
        # [:-1] pour oter le numéro du body en fin de liste
        points = get_points(data[i][:-1])
        print("\n\n", points[0])
        filtre.add(points)
        sleep(0.01)
        smooth_points = filtre.get_smooth_points()
        print("smooth points:")
        print(smooth_points[0])
