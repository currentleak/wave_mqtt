# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 2025

@author: kco_h
"""
import json
import paho.mqtt.client as mqtt
from collections import deque

# Configuration MQTT

###############################################################
###############################################################
BROKER_URL = "192.168.1.73"  # Remplacez par votre IP MQTT
###############################################################
###############################################################

BROKER_PORT = 1883
TOPIC = "inspection/ascan"

# Stocker les 60 dernières valeurs de G1^ dans un deque
last_values = deque(maxlen=60)

def on_connect(client, userdata, flags, rc):
    """Callback exécutée lors de la connexion au broker MQTT."""
    if rc == 0:
        print("✅ Connecté au broker MQTT")
        client.subscribe(TOPIC)
    else:
        print(f"❌ Erreur de connexion, code retour: {rc}")

def on_message(client, userdata, msg):
    """Callback exécutée lorsqu'un message est reçu sur le topic MQTT."""
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        # Recherche de la mesure dont le nom est "G1^"
        found = False
        for key, measurement in payload.items():
            if isinstance(measurement, dict) and measurement.get("name") == "G1^":
                value = measurement.get("value")
                if value is not None:
                    # Stocker la nouvelle valeur
                    last_values.append(value)
                    # Calcul de la moyenne mobile sur les valeurs recueillies (60 au max)
                    moving_average = sum(last_values) / len(last_values)
                    print(f"📊 G1^ -> Dernière valeur : {value:.2f} ; Moyenne mobile (60) : {moving_average:.2f}")
                else:
                    print("⚠️ Pas de valeur trouvée pour G1^")
                found = True
                break  # On arrête la boucle dès qu'on a trouvé G1^
        if not found:
            print("⚠️ G1^ non trouvé dans le payload")
    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON : {e}")

# Initialisation du client MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

# Connexion au broker MQTT
client.connect(BROKER_URL, BROKER_PORT, 60)

# Boucle infinie pour recevoir les messages
client.loop_forever()
