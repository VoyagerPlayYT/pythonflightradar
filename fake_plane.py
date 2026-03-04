import socket
import time
import random
import math

ICAO_HEX = "ABCDEF"  # меняй на уникальный hex, если нужно
CALLSIGN = "J36     "  # ровно 8 символов (пробелы в конце!)
SQUAWK   = "7000"

LAT_CENTER = 41.2999
LON_CENTER = 69.2400
RADIUS_KM  = 0.12  # чуть больше, чтобы видно было движение

HOST = "127.0.0.1"
PORT = 30003  # или твой 30002 — подставь

def send_line(sock, line):
    full = line + "\r\n"
    sock.sendall(full.encode('ascii'))
    print(f"Sent: {line}")

while True:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    try:
        sock.connect((HOST, PORT))
        print("Подключено! Запускаю J36...")

        ts = time.strftime("%Y/%m/%d,%H:%M:%S")

        # MSG,1 - идентификация (обязательно сначала)
        ident = f"MSG,1,1,1,{ICAO_HEX},1,{ts},{ts},{CALLSIGN},,,,,,,,,,,0"
        send_line(sock, ident)
        time.sleep(1)  # пауза, чтобы VRS принял

        angle = 0
        while True:
            angle += 0.1
            lat = LAT_CENTER + (RADIUS_KM / 111.0) * math.cos(angle)
            lon = LON_CENTER + (RADIUS_KM / (111.0 * math.cos(math.radians(LAT_CENTER)))) * math.sin(angle)
            
            alt = 35000 + random.randint(-1500, 1500)
            gs = 460 + random.randint(-50, 50)
            track = (angle * 180 / math.pi) % 360
            vs = random.randint(-1000, 1000)

            # MSG,3 - позиция (ровно 22 поля!)
            pos = (
                f"MSG,3,1,1,{ICAO_HEX},1,"
                f"{ts},{ts},"
                f"{CALLSIGN},"
                f"{alt},"
                f"{gs},"
                f"{track:.1f},"
                f"{lat:.4f},"
                f"{lon:.4f},"
                f"{vs},"
                f"{SQUAWK},"
                f"0,"  # alert
                f"0,"  # emergency
                f"0,"  # spi
                f"0"   # reserved / shouldAlert
            )
            send_line(sock, pos)

            # Иногда шлём MSG,4 - ground speed + heading (помогает VRS)
            if random.random() < 0.3:
                gs_line = f"MSG,4,1,1,{ICAO_HEX},1,{ts},{ts},,{gs},{track:.1f},,,,,,,,,0"
                send_line(sock, gs_line)

            time.sleep(1)  # чаще = стабильнее

    except Exception as e:
        print("Ошибка (retry 5 сек):", e)
        time.sleep(5)
    finally:
        sock.close()
