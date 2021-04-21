
from time import sleep
from json import load
from oscpy.client import OSCClient


def send(data):
    client = OSCClient(b'localhost', 8003)
    for points in data:
        points = points[:-1]
        client.send_message(b'/points', points)
        print(points)
        sleep(0.1)

def read_json(fichier):
    try:
        with open(fichier) as f:
            data = load(f)
        f.close()
    except:
        data = None
        print("Fichier inexistant ou impossible à lire.")
    return data


if __name__ == '__main__':

    fichier = "./cap_2021_04_19_10_11.json"
    data = read_json(fichier)
    send(data)
