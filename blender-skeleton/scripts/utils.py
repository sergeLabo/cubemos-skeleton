
import json
# #import numpy as np

from bge import logic as gl


def read_json(fichier):
    try:
        with open(fichier) as f:
            data = json.load(f)
        f.close()
    except:
        data = Nonefiltre
        print("Fichier inexistant ou impossible à lire:")
    return data


def get_all_scenes():
    """Récupération des scènes"""
    # Liste des objets scènes
    activeScenes = gl.getSceneList()

    # Liste des noms de scènes
    scene_name = []
    for scn in activeScenes:
        scene_name.append(scn.name)

    return activeScenes, scene_name


def get_scene_with_name(scn):
    """Récupération de la scène avec le nom"""

    activeScenes, scene_name = get_all_scenes()
    if scn in scene_name:
        return activeScenes[scene_name.index(scn)]
    else:
        print(scn, "pas dans la liste")
        return None


def get_all_objects():
    """
    Trouve tous les objets des scènes actives
    Retourne un dict {nom de l'objet: blender object}
    """
    activeScenes, scene_name = get_all_scenes()

    all_obj = {}
    for scn_name in scene_name:
        scn = get_scene_with_name(scn_name)
        for blender_obj in scn.objects:
            blender_objet_name = blender_obj.name
            all_obj[blender_objet_name] = blender_obj

    return all_obj


def add_object(obj, position, life):
    """
    Ajoute obj à la place de Empty
    position liste de 3

    addObject(object, reference, time=0)
    Adds an object to the scene like the Add Object Actuator would.
    Parameters:
        object (KX_GameObject or string) – The (name of the) object to add.
        reference (KX_GameObject or string) – The (name of the) object which
        position, orientation, and scale to copy (optional), if the object
        to add is a light and there is not reference the light’s layer will be
        the same that the active layer in the blender scene.
        time (integer) – The lifetime of the added object, in frames. A time
        of 0 means the object will last forever (optional).

    Returns: The newly added object.
    Return type: KX_GameObject
    """

    gl.empty.worldPosition = position
    game_scn = get_scene_with_name("Scene")
    return game_scn.addObject(obj, gl.empty, life)

# Ne sert qu'à lister les keys !
JOINTS = {  "00": "head",
            "01": "cou",
            "02": "epaule.r",
            "03": "coude.r",
            "04": "poignet.r",
            "05": "epaule.l",
            "06": "coude.l",
            "07": "poignet.l",
            "08": "hanche.r",
            "09": "genou.r",
            "10": "cheville.r",
            "11": "hanche.l",
            "12": "genou.l",
            "13": "cheville.l",
            "14": "oeuil.r",
            "15": "oeuil.l",
            "16": "oreille.r",
            "17": "oreille.l",
            "18": "centre.bassin",
            "19": "head"}

# Définition des points origine, direction des cubes de matérialisation des os
PAIRS_COCO = {  "upper_arm.L": [5, 6],
                "forearm.L": [6, 7],
                "upper_arm.R": [2, 3],
                "forearm.R": [3, 4],
                "thigh.L": [11, 12],
                "shin.L": [12, 13],
                "thigh.R": [8, 9],
                "shin.R": [9, 10],
                "shoulder.L": [1, 5],
                "shoulder.R": [1, 2],
                "tronc.L": [5, 11],
                "tronc.R": [2, 8],
                "bassin": [8, 11],
                "cou": [1, 0]}
                # #"yeux": [15, 16],
                # #"oreille.R": [15, 14],
                # #"oreille.L": [16, 17],
                # #"head": [0, 19]}

PAIRS_MPI = {  "upper_arm.L": [5, 6],
                "forearm.L": [6, 7],
                "upper_arm.R": [2, 3],
                "forearm.R": [3, 4],
                "thigh.L": [11, 12],
                "shin.L": [12, 13],
                "thigh.R": [8, 9],
                "shin.R": [9, 10],
                "shoulder.L": [1, 5],
                "shoulder.R": [1, 2],
                "tronc.L": [5, 11],
                "tronc.R": [2, 8],
                "bassin": [8, 11],
                "head": [1, 0]}


# Liste des os du squelette
""" [spine, spine.001, spine.002, spine.003, spine.004, spine.005, spine.006,
    shoulder.L, upper_arm.L, forearm.L, hand.L, shoulder.R, upper_arm.R,
    forearm.R, hand.R, pelvis.L, pelvis.R, thigh.L, shin.L, thigh.R, shin.R]
"""
