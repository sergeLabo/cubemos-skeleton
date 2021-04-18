
from json import dumps
from datetime import datetime
from oscpy.client import OSCClient

class OscClt:
    def __init__(self, ip, port):

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
        self.all_data.append(msg)
        self.client.send_message(b'/points', msg)

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
