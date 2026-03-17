import paho.mqtt.client as mqtt
import serial
import time
import pymysql
import requests

# ==========================================
# [Configuration]
MQTT_BROKER = "10.10.141.167"
MQTT_PORT = 1883

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'homeassistant',
    'password': 'password',
    'db': 'homeassistant',
    'charset': 'utf8mb4'
}

HA_BASE_URL = "http://127.0.0.1:8123/api/states/"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI5MjgwODllM2EyNDg0ZTVmOGMwZGE4NTgwYmY2NzQzOSIsImlhdCI6MTc3Mjg4MTU3OCwiZXhwIjoyMDg4MjQxNTc4fQ.VQKoXijF0jaXezAokmBaDNcxGHTzy11L3IBgXPJeqz8"

# Serial Port Configuration
STM32_PORT = '/dev/ttySTM32'
ARDUINO_PORT = '/dev/ttyArduino'
BAUD_RATE = 115200
# ==========================================

def get_ha_status(user_id):
    url = f"{HA_BASE_URL}input_boolean.{user_id}"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            current_state = response.json().get('state')
            return "집" if current_state == "on" else "외출 중"
        else:
            return "확인불가"
    except Exception as e:
        print(f">> HA 연결 에러 ({user_id}): {e}")
        return "연결오류"

def save_to_db(display_name, user_id):
    try:
        status = get_ha_status(user_id)
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        sql = "INSERT INTO rfid_log (user_name, status) VALUES (%s, %s)"
        cursor.execute(sql, (display_name, status))
        conn.commit()
        conn.close()
        print(f">> [DB 저장 완료] {display_name}: {status}")
    except Exception as e:
        print(f">> [DB 에러] {e}")

# --- [새로 추가된 DB 저장 함수들] ---
def save_bell_to_db():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        sql = "INSERT INTO door_bell (event_name) VALUES (%s)"
        cursor.execute(sql, ("Bell Ring",))
        conn.commit()
        conn.close()
        print(f">> [DB 추가] 도어벨 울림 저장 완료")
    except Exception as e:
        print(f">> [DB 에러] 도어벨 저장 실패: {e}")

def save_lock_to_db(status):
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        sql = "INSERT INTO door_lock (status) VALUES (%s)"
        cursor.execute(sql, (status,))
        conn.commit()
        conn.close()
        print(f">> [DB 추가] 도어락 {status} 상태 저장 완료")
    except Exception as e:
        print(f">> [DB 에러] 도어락 저장 실패: {e}")
# -----------------------------------

# 1. Serial Connection (STM32 & Arduino 분리 연결)
try:
    # STM32 연결
    ser_stm = serial.Serial(STM32_PORT, BAUD_RATE, timeout=1)
    print(f">> STM32 Serial Connected: {STM32_PORT}")

    # Arduino 연결
    ser_ard = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
    print(f">> Arduino Serial Connected: {ARDUINO_PORT}")
except Exception as e:
    print(f">> Serial Connection Failed: {e}")
    exit()

# 2. MQTT Connection Setup
client = mqtt.Client("Bridge_Python")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(">> MQTT Connected Successfully")
        client.subscribe("home/control")
        client.subscribe("home/floor1")
    else:
        print(f">> MQTT Connection Failed (Code: {rc})")

def on_message(client, userdata, msg):
    command = msg.payload.decode('utf-8')
    print(f"[MQTT -> Devices] Command: {command}")

    # STM32로 명령어 전송
    ser_stm.write((command + '\n').encode('utf-8'))
    # 필요한 경우 Arduino로도 전송 (현재는 동일하게 전송되도록 설정)
    ser_ard.write((command + '\n').encode('utf-8'))

    # [추가 로직] 문 열림/닫힘 명령 시 DB 저장
    if command == "OPEN":
        save_lock_to_db("OPEN")
    elif command == "CLOSE":
        save_lock_to_db("CLOSE")

client.on_connect = on_connect
client.on_message = on_message

# 3. Start MQTT Client
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
except Exception as e:
    print(f">> MQTT Broker Connection Failed: {e}")
    exit()

client.loop_start()

# 4. Main Loop (STM32와 Arduino 모두 감시)
print(">> Bridge System Started... (Press Ctrl+C to stop)")

try:
    while True:
        # STM32 데이터 수신
        if ser_stm.in_waiting > 0:
            line = ser_stm.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"[STM32 -> MQTT] Message: {line}")
                if line == "BELL":
                    client.publish("home/doorbell", "RING")
                    # [추가 로직] 벨 울림 시 DB 저장
                    save_bell_to_db()

        # Arduino 데이터 수신 (RFID 인식 시)
        if ser_ard.in_waiting > 0:
            ard_line = ser_ard.readline().decode('utf-8', errors='ignore').strip()
            if ard_line in ["USER1_TAGGED", "USER2_TAGGED"]:
                # 유저 정보 설정
                user_id = "USER1" if ard_line == "USER1_TAGGED" else "USER2"
                user_name = "채수빈" if user_id == "USER1" else "이다경"
                
                # [중요] 현재 상태를 먼저 확인합니다.
                current_status = get_ha_status(user_id)
                print(f">> [RFID 인식] {user_name}님 현재 상태: {current_status}")

                if current_status == "외출 중":
                    ser_stm.write("OPEN\n".encode('utf-8'))
                    print(f">> [Command] {user_name}님 귀가: OPEN 전송")

                    # (2) MQTT 및 DB 저장
                    client.publish("home/rfid", user_id)
                    save_to_db(user_name, user_id)
                    save_lock_to_db("OPEN")

                    # (3) 자동 닫힘 기능 (5초 대기)
                    time.sleep(3)
                    ser_stm.write("CLOSE\n".encode('utf-8'))
                    save_lock_to_db("CLOSE")
                    
                elif  current_status == "집":
                    client.publish("home/rfid", user_id)
                    save_to_db(user_name, user_id)


        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n>> System Stopping...")
    client.loop_stop()
    ser_stm.close()
    ser_ard.close()
