# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 2025

@author: kco_h
"""
import json
import paho.mqtt.client as mqtt

# Configuration MQTT

###############################################################
###############################################################
BROKER_URL = "192.168.1.73"  # Remplacez par votre IP MQTT
###############################################################
###############################################################

BROKER_PORT = 1883
TOPIC = "inspection/ascan"

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
        print(f"📩 Données reçues : {payload}")

        # Parcourir toutes les mesures disponibles (measurement.1, measurement.2, etc.)
        for i in range(1, 5):  # Supposons qu'il y ait 4 gates
            key = f"measurement.{i}"
            if key in payload:
                measurement = payload[key]
                name = measurement.get("name", "Inconnu")
                value = measurement.get("value", None)
                
                if value is not None:
                    print(f"📊 {name} -> Valeur : {value:.2f}")
                else:
                    print(f"⚠️ Pas de valeur trouvée pour {name}")

    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON : {e}")

# Initialisation du client MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

# Connexion au broker MQTT
client.connect(BROKER_URL, BROKER_PORT, 60)

# Démarrer la boucle MQTT pour écouter les messages en continu
client.loop_forever()

