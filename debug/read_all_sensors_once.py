import glob

base_dir = '/sys/bus/w1/devices/'
device_folders = glob.glob(base_dir + '28-*')

if not device_folders:
    print("Nessuna sonda 1-Wire trovata!")
else:
    for folder in device_folders:
        serial = folder.split('/')[-1]
        device_file = folder + '/w1_slave'
        try:
            with open(device_file, 'r') as f:
                lines = f.readlines()
            if lines[0].strip()[-3:] == 'YES':
                temp_pos = lines[1].find('t=')
                if temp_pos != -1:
                    temp_c = float(lines[1][temp_pos+2:]) / 1000.0
                    print(f"Seriale: {serial} | Temperatura: {temp_c:.2f}°C")
            else:
                print(f"Seriale: {serial} | Errore lettura dati!")
        except Exception as e:
            print(f"Seriale: {serial} | Errore: {e}")
