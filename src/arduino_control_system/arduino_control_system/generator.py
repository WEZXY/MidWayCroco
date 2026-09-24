import csv
import random
from datetime import datetime, timedelta

def generate_large_logs(filename="smart_home_logs.csv"):
    start_date = datetime(2026, 8, 1, 0, 0, 0)
    end_date = datetime(2026, 9, 24, 6, 0, 0)
    
    total_seconds = int((end_date - start_date).total_seconds())
    print(f"Generating ~{total_seconds:,} log records into 16 distinct columns...")

    fieldnames = [
        "Date", "Time", "Temp", "Gas", "Humidity", "Light", 
        "IR", "PIR", "Keypad", "Buzzer", "Window", "Door", 
        "Fan", "RoomLight", "LCD_Message", "Code"
    ]
    
    current_time = start_date
    batch_size = 100000
    rows = []
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(fieldnames)

        for i in range(total_seconds):
            date_str = current_time.strftime("%Y-%m-%d")
            time_str = current_time.strftime("%H:%M:%S")

            temp = random.randint(20, 35)
            gas = random.randint(100, 350)
            hum = random.randint(40, 70)
            light = random.randint(100, 800)
            ir = random.choice([0, 1])
            pir = random.choice([0, 1])
            keypad = 0 if random.random() > 0.05 else random.randint(1000, 9999)
            buzzer = 1 if gas > 300 else 0

            window = random.choice([0, 1])
            door = random.choice([0, 1])
            fan = random.choice([0, 1])
            room_light = random.choice([0, 1])
            lcd_msg = "WARNING: GAS!" if gas > 300 else "System Normal"
            code = i

            row = [
                date_str, time_str, temp, gas, hum, light,
                ir, pir, keypad, buzzer, window, door,
                fan, room_light, lcd_msg, code
            ]

            rows.append(row)
            current_time += timedelta(seconds=1)

            if len(rows) >= batch_size:
                writer.writerows(rows)
                rows = []
                print(f"Progress: {i:,} / {total_seconds:,} rows written...")

        if rows:
            writer.writerows(rows)

    print("Log generation complete! File saved as smart_home_logs.csv")

if __name__ == "__main__":
    generate_large_logs()