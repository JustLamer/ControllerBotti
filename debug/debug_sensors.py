from w1thermsensor import W1ThermSensor

try:
    sensors = W1ThermSensor.get_available_sensors()
    print("Sensori trovati:")
    for s in sensors:
        print(s.id)
except Exception as e:
    print("Errore:", e)