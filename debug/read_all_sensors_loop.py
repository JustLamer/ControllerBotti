import glob
import time

base_dir = '/sys/bus/w1/devices/'

def read_temp(device_folder):
    device_file = device_folder + '/w1_slave'
    try:
        with open(device_file, 'r') as f:
            lines = f.readlines()
        if lines[0].strip()[-3:] == 'YES':
            temp_pos = lines[1].find('t=')
            if temp_pos != -1:
                temp_c = float(lines[1][temp_pos+2:]) / 1000.0
                return temp_c
        return None
    except Exception as e:
        return None

while True:
    device_folders = glob.glob(base_dir + '28-*')
    if not device_folders:
        print("Nessuna sonda 1-Wire trovata!")
    else:
        for folder in device_folders:
            serial = folder.split('/')[-1]
            temp_c = read_temp(folder)
            if temp_c is not None:
                print(f"Seriale: {serial} | Temperatura: {temp_c:.2f}°C")
            else:
                print(f"Seriale: {serial} | Errore lettura dati!")
    print("-" * 40)
    time.sleep(2)
