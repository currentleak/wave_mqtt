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
TOPIC_WRITE = "inspection/configuration/probe/frequency"  # Topic pour configurer la fréquence
TOPIC_RESPONSE = "response/probe/frequency"  # Topic pour la confirmation

###############################################################
###############################################################
# Nouvelle fréquence de la sonde (5 MHz)
NEW_FREQUENCY = 5.4  # En MHz
###############################################################
###############################################################

# Flag pour suivre la réponse
response_received = False

def on_connect(client, userdata, flags, rc):
    """Callback exécutée lors de la connexion au broker MQTT."""
    if rc == 0:
        print("✅ Connecté au broker MQTT")
        client.subscribe(TOPIC_RESPONSE)  # S'abonner pour recevoir la confirmation
        send_probe_frequency(client)  # Envoyer la commande
    else:
        print(f"❌ Erreur de connexion, code retour: {rc}")

def on_message(client, userdata, msg):
    """Callback exécutée lorsqu'un message de confirmation est reçu."""
    global response_received

    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        print(f"📩 Réponse reçue : {payload}")

        # Vérifier si le message indique un succès
        if "message" in payload and payload["message"] == "success":
            print(f"✅ Fréquence de la sonde configurée avec succès à {NEW_FREQUENCY / 1e6} MHz")
            response_received = True
        else:
            print("⚠️ La configuration de la fréquence a échoué.")

    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON : {e}")

def send_probe_frequency(client):
    """Envoie la commande pour configurer la fréquence de la sonde."""
    payload = json.dumps({"value": NEW_FREQUENCY})
    client.publish(TOPIC_WRITE, payload)
    print(f"📤 Configuration envoyée : {payload}")

# Initialisation MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

# Connexion au broker
client.connect(BROKER_URL, BROKER_PORT, 60)
client.loop_start()  # Lancement en mode asynchrone

# Attendre la réponse
# try:
#     while not response_received:
#         time.sleep(0.1)
# except KeyboardInterrupt:
#     print("\n🛑 Arrêt du programme.")

# Arrêter MQTT proprement
client.loop_stop()
client.disconnect()

