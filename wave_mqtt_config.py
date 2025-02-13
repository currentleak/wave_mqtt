import json
import time
import paho.mqtt.client as mqtt

# Configuration MQTT
BROKER_URL = "192.168.1.73"  # Remplacez par votre IP MQTT
BROKER_PORT = 1883

# Liste des paramètres à configurer
PARAMS = {
    "inspection/configuration/probe/frequency": {"value": 5},  # MHz
    "inspection/configuration/us/pulsetype": {"value": "spike"},  # "square" ou "spike"
    "inspection/configuration/us/rxmode": {"value": "pe"},  # "pe" ou "pc"
    "inspection/configuration/us/voltage": {"value": 200},  # 200V
    "inspection/configuration/us/filter": {"value": "Broadband low"},  # Filtrage
    "inspection/configuration/us/rectification": {"value": "full"},  # "full", "positive", "negative", "none"
    "inspection/configuration/measurementselection/1": {"value": "G1_peak_amplitude"},
    "inspection/configuration/measurementselection/2": {"value": "G1_peak_soundPath"},
    "inspection/configuration/measurementselection/3": {"value": "G1_peak_surfaceDistance"},
    "inspection/configuration/measurementselection/4": {"value": "G1_peak_depth"}
}

# Générer la liste des topics de réponse correspondants
RESPONSE_TOPICS = {f"response/{topic.split('/')[-1]}": topic for topic in PARAMS.keys()}

# Flags pour suivre les réponses
response_received = {topic: False for topic in PARAMS.keys()}

def on_connect(client, userdata, flags, rc):
    """Callback exécutée lors de la connexion au broker MQTT."""
    if rc == 0:
        print("✅ Connecté au broker MQTT")

        # S'abonner aux réponses attendues
        for response_topic in RESPONSE_TOPICS:
            client.subscribe(response_topic)
        
        # Envoyer toutes les configurations
        send_all_configurations(client)
    else:
        print(f"❌ Erreur de connexion, code retour: {rc}")

def on_message(client, userdata, msg):
    """Callback exécutée lorsqu'un message de confirmation est reçu."""
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        print(f"📩 Réponse reçue ({msg.topic}) : {payload}")

        if msg.topic in RESPONSE_TOPICS:
            config_topic = RESPONSE_TOPICS[msg.topic]
            param_name = config_topic.split("/")[-1]
            
            if "message" in payload and payload["message"] == "success":
                print(f"✅ {param_name} configuré à {PARAMS[config_topic]['value']}")
                response_received[config_topic] = True
            else:
                print(f"⚠️ La configuration de {param_name} a échoué.")

    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON : {e}")

def send_all_configurations(client):
    """Envoie toutes les commandes de configuration."""
    for topic, value in PARAMS.items():
        payload = json.dumps(value)
        client.publish(topic, payload)
        print(f"📤 Configuration envoyée : {topic} -> {payload}")

# Initialisation MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

# Connexion au broker
client.connect(BROKER_URL, BROKER_PORT, 60)
client.loop_start()  # Lancement en mode asynchrone

# Attendre la confirmation de tous les paramètres
try:
    while not all(response_received.values()):
        time.sleep(0.1)  # Évite d'utiliser trop de CPU
except KeyboardInterrupt:
    print("\n🛑 Arrêt du programme.")

# Arrêter MQTT proprement
client.loop_stop()
client.disconnect()
