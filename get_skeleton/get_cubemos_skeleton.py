
from pprint import pprint
import cv2
from time import time
import math
import numpy as np

from my_config import MyConfig
from gestures import Gestures
from osc_client import OscClt

import pyrealsense2 as rs

# Script particulier de cubemos dans le dossier de ce projet avec la clé !!
from skeletontracker import skeletontracker
import util as cm


class CubemosSkeleton:
    """Détection d'un squelette par Cubemos avec un capteur
    Intel RealSense.
    """

    def __init__(self, **kwargs):

        self.ip = kwargs.get('ip', b'localhost')
        self.port = kwargs.get('port', 8003)
        self.gest = kwargs.get('gestures', 0)
        self.specific_message = kwargs.get('specific_message', 0)

        self.clt = OscClt(self.ip, self.port)
        if self.gest:
            self.gestures = Gestures(self.clt)

    def render_ids_3d(self, color_image, skeletons_2d, depth_map,
                            depth_intrinsic, joint_confidence):
        """Calcul les coordonnées 3D des squelettes."""

        rows, cols, channel = color_image.shape[:3]
        # kernel = distance_kernel_size
        kernel = 5
        joints_2D = 0
        point_3d = None
        # A la fin, points_3D = liste de 18
        points_3D = [None]*18

        for skeleton_index in range(len(skeletons_2d)):
            skeleton_2D = skeletons_2d[skeleton_index]
            joints_2D = skeleton_2D.joints
            skeleton_id = skeleton_2D.id

            for joint_index in range(len(joints_2D)):
                # check if the joint was detected and has valid coordinate
                if skeleton_2D.confidences[joint_index] > joint_confidence:
                    distance_in_kernel = []
                    l = int(joints_2D[joint_index].x - math.floor(kernel/2))
                    low_bound_x = max(0, l)
                    m = int(joints_2D[joint_index].x + math.ceil(kernel/2))
                    upper_bound_x = min(cols - 1, m)
                    n = int(joints_2D[joint_index].y - math.floor(kernel / 2))
                    low_bound_y = max(0, n)
                    o = int(joints_2D[joint_index].y + math.ceil(kernel / 2))
                    upper_bound_y = min(rows - 1, o)
                    for x in range(low_bound_x, upper_bound_x):
                        for y in range(low_bound_y, upper_bound_y):
                            distance_in_kernel.append(depth_map.get_distance(x, y))
                    median_distance = np.percentile(np.array(distance_in_kernel), 50)

                    depth_pixel = [int(joints_2D[joint_index].x),
                                   int(joints_2D[joint_index].y)]

                    if median_distance >= 0.3:
                        point_3d = rs.rs2_deproject_pixel_to_point(depth_intrinsic,
                                                                   depth_pixel,
                                                                   median_distance)
                        points_3D[joint_index] = point_3d

            # Envoi en OSC des points cubemos
            if not self.specific_message:
                self.clt.send_global_message(points_3D, skeleton_id)
            else:
                self.clt.send_mutiples_message(points_3D, skeleton_id)

            # Reconnaissance de gestes
            self.gestures.add_points(points_3D)

    def run(self):
        # Configure depth and color streams of the intel realsense
        config = rs.config()
        config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

        # Start the realsense pipeline
        pipeline = rs.pipeline()
        pipeline.start()

        # Create align object to align depth frames to color frames
        align = rs.align(rs.stream.color)

        # Get the intrinsics information for calculation of 3D point
        unaligned_frames = pipeline.wait_for_frames()
        frames = align.process(unaligned_frames)
        depth = frames.get_depth_frame()
        depth_intrinsic = depth.profile.as_video_stream_profile().intrinsics

        # Initialize the cubemos api with a valid license key in default_license_dir()
        skeletrack = skeletontracker(cloud_tracking_api_key="")
        joint_confidence = 0.2

        # Create window for initialisation
        window_name = "Cubemos skeleton tracking with RealSense D400 series"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL + cv2.WINDOW_KEEPRATIO)
        t0 = time()
        n = 0
        while True:
            # Create a pipeline object.
            # This object configures the streaming camera and owns it's handle
            unaligned_frames = pipeline.wait_for_frames()
            frames = align.process(unaligned_frames)
            depth = frames.get_depth_frame()
            color = frames.get_color_frame()
            if not depth or not color:
                continue

            # Convert images to numpy arrays
            depth_image = np.asanyarray(depth.get_data())
            color_image = np.asanyarray(color.get_data())

            # perform inference and update the tracking id
            skeletons = skeletrack.track_skeletons(color_image)

            # render the skeletons on top of the acquired image and display it
            color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
            cm.render_result(skeletons, color_image, joint_confidence)
            self.render_ids_3d(color_image, skeletons, depth,
                                depth_intrinsic, joint_confidence)

            cv2.imshow(window_name, color_image)
            n += 1
            t = time()
            if t - t0 > 10:
                print("FPS =", round(n/10, 1))
                t0 = t
                n = 0
            if cv2.waitKey(1) == 27:
                break

        pipeline.stop()
        cv2.destroyAllWindows()
        self.clt.save()


if __name__ == "__main__":

    # Chargement de la configuration
    ini_file = 'get_cubemos_skeleton.ini'
    my_conf = MyConfig(ini_file)

    kwargs = my_conf.conf['cubemos']
    print("\nDétection de squelette par Cubemos")
    print("\n     Configuration \n")
    pprint(kwargs)
    print()

    cubemos_skeleton = CubemosSkeleton(**kwargs)
    cubemos_skeleton.run()
    print("C'est fini !")
