import json
import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import ttk

# Adresse IP par défaut
DEFAULT_IP = "192.168.1.73"

# Liste des paramètres et valeurs possibles
PARAM_OPTIONS = {
    "/probe/frequency": [1, 2.25, 4, 5, 7.5, 10, 15],
    "/us/pulsetype": ["square", "spike"],
    "/us/rxmode": ["pe", "pc", "tt"],
    "/us/voltage": [100, 150, 200, 250, 300, 350, 400, 450, 500],
    "/us/filter": ["Broadband low", "Broadband High"],
    "/us/rectification": ["full", "positive", "negative", "none"],
    "/measurementselection/1": ["G1_peak_amplitude", "G1_peak_soundPath", "G1_peak_surfaceDistance", "G1_peak_depth"],
    "/measurementselection/2": ["G1_peak_amplitude", "G1_peak_soundPath", "G1_peak_surfaceDistance", "G1_peak_depth"],
    "/measurementselection/3": ["G1_peak_amplitude", "G1_peak_soundPath", "G1_peak_surfaceDistance", "G1_peak_depth"],
    "/measurementselection/4": ["G1_peak_amplitude", "G1_peak_soundPath", "G1_peak_surfaceDistance", "G1_peak_depth"],
}

# Valeurs par défaut
DEFAULT_VALUES = {
    "/probe/frequency": 5,
    "/us/pulsetype": "spike",
    "/us/rxmode": "pe",
    "/us/voltage": 200,
    "/us/filter": "Broadband low",
    "/us/rectification": "full",
    "/measurementselection/1": "G1_peak_amplitude",
    "/measurementselection/2": "G1_peak_soundPath",
    "/measurementselection/3": "G1_peak_surfaceDistance",
    "/measurementselection/4": "G1_peak_depth",
}

# Génération des topics MQTT
MQTT_TOPICS = {key: f"inspection/configuration{key}" for key in PARAM_OPTIONS.keys()}
RESPONSE_TOPICS = {f"response{key}": key for key in PARAM_OPTIONS.keys()}

# Stockage des valeurs sélectionnées
selected_values = {}

# Création de l'interface Tkinter
root = tk.Tk()
root.title("Configuration des paramètres via MQTT")
root.geometry("420x600")

# Frame principale
frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

# Champ pour l'adresse IP
ttk.Label(frame, text="Adresse IP du broker MQTT", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
ip_entry = ttk.Entry(frame, font=("Arial", 12))
ip_entry.insert(0, DEFAULT_IP)  # Valeur par défaut
ip_entry.grid(row=0, column=1, padx=10, pady=5, sticky="e")

# Labels et Menus déroulants
widgets = {}

for i, (param, options) in enumerate(PARAM_OPTIONS.items(), start=1):
    ttk.Label(frame, text=param, font=("Arial", 10, "bold")).grid(row=i, column=0, padx=10, pady=5, sticky="w")

    # Variable Tkinter pour stocker la sélection avec la valeur par défaut
    selected_values[param] = tk.StringVar(value=DEFAULT_VALUES[param])

    # Menu déroulant avec pré-sélection de la valeur par défaut
    dropdown = ttk.OptionMenu(frame, selected_values[param], DEFAULT_VALUES[param], *options)
    dropdown.grid(row=i, column=1, padx=10, pady=5, sticky="e")
    widgets[param] = dropdown

# Fonction d'envoi de configuration
def send_configuration():
    """Envoie la configuration sélectionnée via MQTT."""
    broker_ip = ip_entry.get()  # Récupère l'adresse IP entrée par l'utilisateur
    print(f"📡 Connexion au broker MQTT sur {broker_ip}...")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(broker_ip, 1883, 60)
        client.loop_start()
    except Exception as e:
        print(f"❌ Impossible de se connecter au broker MQTT : {e}")
        return

    for param, value in selected_values.items():
        topic = MQTT_TOPICS[param]
        payload = json.dumps({"value": value.get()})
        client.publish(topic, payload)
        print(f"📤 Configuration envoyée : {topic} -> {payload}")

# Bouton d'application de la configuration
apply_button = ttk.Button(frame, text="Appliquer la configuration", command=send_configuration)
apply_button.grid(row=len(PARAM_OPTIONS) + 2, column=0, columnspan=2, pady=20)

# Fonction de connexion MQTT
def on_connect(client, userdata, flags, rc):
    """Callback exécutée lors de la connexion au broker MQTT."""
    if rc == 0:
        print("✅ Connecté au broker MQTT")
        for response_topic in RESPONSE_TOPICS.keys():
            client.subscribe(response_topic)
    else:
        print(f"❌ Erreur de connexion, code retour: {rc}")

# Fonction de réception des réponses MQTT
def on_message(client, userdata, msg):
    """Callback exécutée lorsqu'un message de confirmation est reçu."""
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        param = RESPONSE_TOPICS.get(msg.topic, "Inconnu")

        if "message" in payload and payload["message"] == "success":
            print(f"✅ {param} configuré avec succès")
        else:
            print(f"⚠️ Échec de configuration pour {param}")

    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON : {e}")

# Lancer l'interface Tkinter
root.mainloop()
