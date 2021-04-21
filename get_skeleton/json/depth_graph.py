
import json
import numpy as np
import matplotlib.pyplot as plt

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


def plot_depht(depths, tops_liss):
    t = np.asarray(tops_liss)
    s = np.asarray(depths)

    fig, ax = plt.subplots()
    ax.plot(t, s)

    ax.set(xlabel='Temps', ylabel='Profondeur',
           title='Profondeur lissée')
    ax.grid()

    fig.savefig("depth.png")
    plt.show()

def get_depth(points):
    """Moyenne de tous les z"""
    zs = []
    for point in points:
        if point:
            if point[2] != 1000:
                zs.append(point[2])

    # Profondeur courrante
    depth = float(np.average(np.array(zs)))

    return depth


if __name__ == '__main__':

    fichier = "cap_2021_04_21_18_27.json"
    data = read_json(fichier)
    depths = []
    tops = []
    for i in range(len(data)):
        # [:-1] pour oter le numéro du body en fin de liste
        points = get_points(data[i][0][:-1])
        top = data[i][1]
        depth = get_depth(points)
        if depth:
            depths.append(depth)
        tops.append(top)
    print("Nombre de valeurs", len(depths))
    fps = 15
    duree = int(len(depths)/fps)  # sec
    print("Durée de l'enregistrement:", duree)

    # Lissage
    depths_liss = []
    tops_liss = []
    for k in range(int((len(depths)/5) - 1)):
        moy = 0
        for i in range(5):
            moy += depths[k*5 + i]
        depths_liss.append(moy/5)
        tops_liss.append(tops[k*5])

    plot_depht(depths_liss, tops_liss)
