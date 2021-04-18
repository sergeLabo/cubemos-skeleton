import math
from time import time
# #import numpy as np

from bge import logic as gl
from bge import events
from mathutils import Vector, Quaternion, Matrix

from scripts.utils import get_all_objects, JOINTS
from scripts.rs_utils import get_points


def apply_objet_position_orientation(objet_point_1, objet_point_2, objet):
    """Valable pour un objet seulement.
    objet_point_1, objet_point_2 sont 2 objets Blender:
        ils définissent un vecteur.
    L'objet objet est orienté suivant ce vecteur,
        si objet_point_2 n'est pas None
    et positionné en objet_point_1.
    """

    if objet_point_2:
        try:
            a = objet_point_1.worldPosition
            b = objet_point_2.worldPosition

            direction  = (b - a).normalized()
            axis_align = Vector((1.0, 0.0, 0.0))

            angle = axis_align.angle(direction)
            axis  = axis_align.cross(direction)

            quat = Quaternion(axis, angle)
            objet.localOrientation = quat.to_euler('XYZ')

            sc = (b-a).length
            # Les coefficients correspondent à la taille des objects cube
            # qui représentent les os
            objet.localScale = [sc*5*gl.scale, 0.2*gl.scale, 0.2*gl.scale]
        except:
            pass

    # Apply position
    objet.worldPosition = objet_point_1.worldPosition


def set_sphere_position_scale():
    if gl.points:
        for i in range(14):  # gl.nombre):
            if gl.points[i]:
                v = Vector(gl.points[i])*gl.scale
                gl.spheres[i].worldPosition = [ v[0] + gl.left_right,
                                                v[1] + gl.av_ar,
                                                v[2] + gl.up_down]
                gl.spheres[i].worldScale = [1.5*gl.scale,
                                            1.5*gl.scale,
                                            1.5*gl.scale]


def set_body_position_orientation():
    """ Le point '18' est au centre de [8, 11] soit au centre du bassin.
    Il ne vient pas de COCO !
    Le bone spine suit les rotation de 18 sur Z
    """
    # Position 8 à droite 11 à gauche
    if gl.points[8] and gl.points[11]:

        x = (gl.spheres[8].worldPosition[0] + gl.spheres[11].worldPosition[0])/2
        y = (gl.spheres[8].worldPosition[1] + gl.spheres[11].worldPosition[1])/2
        z = (gl.spheres[8].worldPosition[2] + gl.spheres[11].worldPosition[2])/2

        gl.spheres[18].worldPosition = [x, y, z]
        gl.spheres[18].worldScale  = [1.5*gl.scale, 1.5*gl.scale, 1.5*gl.scale]

    # Rotation: direction = de 11 à 8
    if gl.points[8] and gl.points[11]:
        try:
            a = gl.spheres[8].worldPosition
            b = gl.spheres[11].worldPosition
            direction  = (b - a).normalized()
            axis_align = Vector((1.0, 0.0, 0.0))
            angle = axis_align.angle(direction)
            axis  = axis_align.cross(direction)
            quat = Quaternion(axis, angle)
            gl.spheres[18].localOrientation = quat.to_euler('XYZ')
        except:
            pass


def set_head_location():
    """ Le point '19' est au centre de [14, 15] soit au centre des yeux.
    Il ne vient pas de COCO !
    """
    if gl.points[14] and gl.points[15]:
        pos = (gl.spheres[14].worldPosition + gl.spheres[15].worldPosition)/2
        gl.spheres[19].worldPosition = [pos[0], pos[1], pos[2]]
        gl.spheres[19].worldScale  = [1.5*gl.scale, 1.5*gl.scale, 1.5*gl.scale]


def set_cubes_position_orientation_scale():
    """Matérialisation des os par des cubes allongés."""

    for bone, [p1, p2] in gl.pairs.items():
        bone_cube_obj = gl.all_obj[bone]
        apply_objet_position_orientation(gl.spheres[p1],
                                         gl.spheres[p2],
                                         bone_cube_obj)


def keyboard():

    if gl.keyboard.events[events.UPARROWKEY] == gl.KX_INPUT_JUST_ACTIVATED:
        # en arrière
        gl.av_ar += 0.1
        print("gl.av_ar =", gl.av_ar)
    elif gl.keyboard.events[events.DOWNARROWKEY] == gl.KX_INPUT_JUST_ACTIVATED:
        # en avant
        gl.av_ar -= 0.1
        print("gl.av_ar =", gl.av_ar)
    elif gl.keyboard.events[events.RIGHTARROWKEY] == gl.KX_INPUT_JUST_ACTIVATED:
        # vers la droite
        gl.left_right += 0.1
        print("gl.left_right =", gl.left_right)
    elif gl.keyboard.events[events.LEFTARROWKEY] == gl.KX_INPUT_JUST_ACTIVATED:
        # vers la gauche
        gl.left_right -= 0.1
        print("gl.left_right =", gl.left_right)
    elif gl.keyboard.events[events.PAD8] == gl.KX_INPUT_JUST_ACTIVATED:
        # plus haut
        gl.up_down += 0.1
        print("gl.up_down =", gl.up_down)
    elif gl.keyboard.events[events.PAD2] == gl.KX_INPUT_JUST_ACTIVATED:
        # plus bas
        gl.up_down -= 0.1
        print("gl.up_down =", gl.up_down)
    elif gl.keyboard.events[events.PAD7] == gl.KX_INPUT_JUST_ACTIVATED:
        # plus grand
        gl.scale += 0.1
        print("gl.scale =", gl.scale)
    elif gl.keyboard.events[events.PAD1] == gl.KX_INPUT_JUST_ACTIVATED:
        # plus petit
        gl.scale -= 0.1
        if gl.scale < 0.01:
            gl.scale = 0.01
        print("gl.scale =", gl.scale)
    elif gl.keyboard.events[events.HKEY] == gl.KX_INPUT_JUST_ACTIVATED:
        visible_or_not()


def visible_or_not():
    """Visibilité soit du personnage, soit la matérialisation des os"""

    if gl.body_visible:
        gl.person.visible = 0
        for name, obj in gl.all_obj.items():
            if "Text" in name:
                obj.visible = 1
        for num in JOINTS.keys():
            gl.all_obj[num].visible = 1

        for cube in gl.pairs.keys():
            gl.all_obj[cube].visible = 1
        gl.body_visible = 0
    else:
        gl.person.visible = 1
        for name, obj in gl.all_obj.items():
            if "Text" in name:
                obj.visible = 0
        for num in JOINTS.keys():
            gl.all_obj[num].visible = 0
        for cube in gl.pairs.keys():
            gl.all_obj[cube].visible = 0
        gl.body_visible = 1


def main():
    gl.frame_number += 1
    gl.fps += 1
    if time() - gl.t > 10:
        gl.t = time()
        # #print(int(gl.fps/10))
        gl.fps = 0

    keyboard()

    if gl.debug:
        if gl.nums < len(gl.data):
            if gl.frame_number < 20:
                every = 1
            else:
                every = gl.every
            # les datas sans le body
            data = gl.data[gl.nums][:-1]
            if gl.frame_number % every == 0:
                # Les coordonnées xzy de opencv deviennent xyz de blender
                gl.points = get_points(data)
                gl.nums += 1
                gl.new = 1
        else:
            print("Le spectacle doit continué")

    if gl.points:
        set_sphere_position_scale()
        set_cubes_position_orientation_scale()
        set_body_position_orientation()
        set_head_location()  # pour COCO

        gl.new = 0
        gl.points = None

    gl.metarig.update()
    gl.metarig_copy.update()
