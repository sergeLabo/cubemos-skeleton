
from json import dumps
from datetime import datetime
from oscpy.client import OSCClient
from time import time

class OscClt:
    """Un client OSC spécifique pour envoyer les points Cubemos,
    et enregistrer ces points dans un fichier pour debug.
    """

    def __init__(self, ip, port):
        """ ip = "192.168.1.101"
            ip = b'localhost'
        """
        self.ip = ip
        self.port = port
        # Pour l'enregistrement d'un json à la fin de la capture
        self.all_data = []

        self.client = OSCClient(self.ip, self.port)

    def send_global_message(self, points3D, bodyId=110):
        """Envoi du point en OSC en 3D
            Liste de n°body puis toutes les coordonnées sans liste de 3
            oscpy n'envoie pas de liste de listes
        """

        msg = []
        for point in points3D:
            if point:
                for i in range(3):
                    # Envoi en int
                    msg.append(int(point[i]*1000))
            # Si pas de point ajout arbitraire de 3 fois -1000000
            # pour avoir toujours 3*18 valeurs dans la liste
            else:
                msg.extend((-1000000, -1000000, -1000000))  # tuple ou list

        # N° body à la fin
        msg.append(bodyId)
        self.all_data.append([msg, time()])
        self.client.send_message(b'/points', msg)

    def send_mutiples_message(self, points3D, bodyId=110):
        """Envoi d'un message OSC pour chaque point: n = 0 à 17
        point = [x, y, z]
        il faudrait une adresse du type
        /point_{n}_{bodyId}
        mais je ne sait pas recevoir çà
        d'où ce mix
        msg = [bodyId, n, x, y, z]
        """
        msg = [bodyId]
        for point in points3D:
            if point:
                n = points3D.index(point)
                msg.append(n)
                for i in range(3):
                    msg.append(point[i])
                self.client.send_message(b'/point', msg)

    def send_msg(self, adress, note):
        self.client.send_message(adress, [note])

    def save(self):
        """Enregistrement des messages envoyés pour debug de la réception"""

        dt_now = datetime.now()
        dt = dt_now.strftime("%Y_%m_%d_%H_%M")
        fichier = f"json/cap_{dt}.json"  # dans le home
        with open(fichier, "w") as fd:
            fd.write(dumps(self.all_data))
            print(f"{fichier} enregistré.")
        fd.close()
