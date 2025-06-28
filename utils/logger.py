import os
import csv
import datetime

LOG_DIR = "data/logs"

def log_event(event_type, nome, messaggio):
    # Log minimale su file eventi (puoi anche lasciarla vuota se non ti serve)
    file_path = os.path.join(LOG_DIR, "eventi.log")
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(file_path, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().isoformat(sep=" ")
        f.write(f"[{timestamp}] {event_type} {nome}: {messaggio}\n")

def log_botte_csv(nome_botte, timestamp, temperatura, min_temp, max_temp, valvola):
    os.makedirs(LOG_DIR, exist_ok=True)
    file_path = os.path.join(LOG_DIR, f"{nome_botte.replace(' ', '_')}.csv")
    write_header = not os.path.exists(file_path)
    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        if write_header:
            writer.writerow(["timestamp", "temperatura", "min_temp", "max_temp", "valvola"])
        # timestamp in ISO formato leggibile
        if isinstance(timestamp, datetime.datetime):
            timestamp = timestamp.isoformat(sep=" ")
        writer.writerow([timestamp, temperatura, min_temp, max_temp, valvola])