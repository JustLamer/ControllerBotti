from .pinmap import BARREL_PINMAP
import requests
import serial  # Per RS485
import time

def _modbus_crc(data: bytes) -> bytes:
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])

class Actuator:
    BASE_URL = "http://192.168.4.1"
    wifi_available = True
    relay_states = {}
    _serial_instance = None  # Singleton per la seriale RS485
    _last_rs485 = False  # Tiene traccia dell'ultima modalità istanziata

    RS485_COMMANDS = {
        0: bytes.fromhex("06 05 00 01 55 00 A2 ED"),
        1: bytes.fromhex("06 05 00 02 55 00 52 ED"),
        2: bytes.fromhex("06 05 00 03 55 00 03 2D"),
        3: bytes.fromhex("06 05 00 04 55 00 B2 EC"),
        4: bytes.fromhex("06 05 00 05 55 00 E3 2C"),
        5: bytes.fromhex("06 05 00 06 55 00 13 2C"),
        "on_all": bytes.fromhex("06 05 00 FF FF 00 BD BD"),
        "off_all": bytes.fromhex("06 05 00 FF 00 00 FC 4D"),
    }

    def __init__(self, barrel_name, use_rs485=True, serial_device="/dev/ttyUSB0", baudrate=9600):
        self.name = barrel_name
        self.channel = BARREL_PINMAP[barrel_name]["valve_pin"]
        self.use_rs485 = use_rs485
        Actuator._last_rs485 = use_rs485  # Ricorda l'ultima modalità usata

        if use_rs485 and Actuator._serial_instance is None:
            try:
                Actuator._serial_instance = serial.Serial(
                    port=serial_device,
                    baudrate=baudrate,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=1
                )
                print("[DEBUG] Porta RS485 aperta:", serial_device)
            except Exception as e:
                print("[ERROR] Impossibile aprire la porta RS485:", e)
                raise

    @staticmethod
    def batch_set_valves(state_dict, actuators=None, delay=0.5):
        """
        Imposta in modo sicuro gli stati di più canali.
        - state_dict: dict {nome_botte: stato_desiderato}
        - actuators: dict {nome_botte: Actuator} (se già istanziati) oppure None (allora crea/reusa con registry interno)
        - delay: tempo tra i comandi (in secondi)
        """
        for nome, stato_desiderato in state_dict.items():
            if actuators is not None:
                actuator = actuators[nome]
            else:
                actuator = Actuator.reuse_or_create(nome)
            current = Actuator.relay_states.get(actuator.channel, "Unknown")
            if current != stato_desiderato:
                actuator.set_valve(stato_desiderato)
                # set_valve aggiorna relay_states appena il comando viene eseguito
                time.sleep(delay)

    @staticmethod
    def reuse_or_create(nome, use_rs485=True):
        if not hasattr(Actuator, "_global_registry"):
            Actuator._global_registry = {}
        if nome in Actuator._global_registry:
            return Actuator._global_registry[nome]
        actuator = Actuator(nome, use_rs485=use_rs485)
        Actuator._global_registry[nome] = actuator
        return actuator

    @staticmethod
    def all_off(use_rs485=None):
        if use_rs485 is None:
            use_rs485 = Actuator._last_rs485
        if not use_rs485:
            try:
                r = requests.get(f"{Actuator.BASE_URL}/AllOff", timeout=2)
                if r.status_code == 200:
                    print("[DEBUG] Comando AllOff inviato con successo (Wi-Fi)")
                    for i in range(6):
                        Actuator.relay_states[i] = "Chiusa"
                else:
                    print(f"[WARNING] Errore HTTP AllOff: {r.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"[WARNING] Fallita richiesta AllOff: {e}")
                Actuator.wifi_available = False
        else:
            try:
                s = Actuator._serial_instance
                if s is None:
                    raise Exception("Seriale RS485 non inizializzata")
                s.write(Actuator.RS485_COMMANDS["off_all"])
                print("[DEBUG] Comando AllOff inviato su RS485")
                for i in range(6):
                    Actuator.relay_states[i] = "Chiusa"
            except Exception as e:
                print("[ERROR] Invio comando RS485 fallito:", e)

        Actuator._set_all_closed()

    def set_valve(self, state):
        if state not in ("Aperta", "Chiusa"):
            print(f"[ERROR] Stato non valido: {state}")
            return

        if not self.use_rs485 and not Actuator.wifi_available:
            print(f"[DEBUG] Skipping {self.name} (Wi-Fi non disponibile)")
            return

        if self.channel not in Actuator.relay_states:
            print(f"[DEBUG] Stato relè per {self.name} non presente, forzo sync...")
            Actuator.update_states(self.use_rs485)

        current = self.get_current_state().strip()
        desired = state.strip()
        print(f"[DEBUG] Richiesta per {self.name}: voglio '{desired}', attualmente è '{current}'")

        if desired == current:
            print(f"[DEBUG] {self.name} è già in stato {desired}, nessun comando.")
            return

        if self.use_rs485:
            try:
                s = Actuator._serial_instance
                if s is None:
                    raise Exception("Seriale RS485 non inizializzata")
                s.write(Actuator.RS485_COMMANDS[self.channel])
                print(f"[DEBUG] Comando RS485 toggle su canale {self.channel+1} inviato")
                Actuator.relay_states[self.channel] = state
            except Exception as e:
                print("[ERROR] Invio comando RS485 fallito:", e)
        else:
            relay_number = self.channel + 1
            url = f"{Actuator.BASE_URL}/Switch{relay_number}"
            try:
                r = requests.get(url, timeout=2)
                if r.status_code == 200:
                    print(f"[DEBUG] Toggle {self.name} (canale {relay_number}) inviato → nuovo stato atteso: {state}")
                    Actuator.relay_states[self.channel] = state
                else:
                    print(f"[WARNING] HTTP {r.status_code} per {self.name}")
            except requests.exceptions.RequestException as e:
                print(f"[WARNING] Richiesta fallita: {e}")
                Actuator.wifi_available = False

    def pulse_valve(self, state, seconds=2):
        previous = self.get_current_state()
        self.set_valve(state)
        time.sleep(seconds)
        if previous in ("Aperta", "Chiusa"):
            self.set_valve(previous)

    def get_current_state(self):
        stato = Actuator.relay_states.get(self.channel, "Unknown")
        print(f"[DEBUG] Stato attuale di {self.name} (canale {self.channel}): {stato}")
        return stato

    @staticmethod
    def _set_all_closed():
        for i in range(6):
            Actuator.relay_states[i] = "Chiusa"

    @staticmethod
    def update_states(use_rs485=None):
        Actuator._set_all_closed()

    def __repr__(self):
        return f"<Actuator name={self.name}, pin={self.channel}, state={self.get_current_state()}, rs485={self.use_rs485}>"
