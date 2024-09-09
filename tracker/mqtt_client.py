import paho.mqtt.client as mqtt
from datetime import datetime, date, time

gps_data = {"UserName":"","Date":date(2000, 1, 1),"Time":time(12, 00, 00),"Lat":0.0, "Lng":0.0}
#확실한 이유는 모르겠지만 default 값 설정해놓아야 하는 듯

def _parsing(data:str) -> dict:
    data_dict = {}
    for item in data.split(", "):
        key, value = item.split(": ")

        # 날짜 및 시간 관련 키 확인 후 변환
        if key == "Date":
            data_dict[key] = datetime.strptime(value, "%Y-%m-%d").date()  # 날짜로 변환
        elif key == "Time":
            data_dict[key] = datetime.strptime(value, "%H:%M:%S").time()  # 시간으로 변환
        # 위도 및 경도 관련 키 확인 후 변환
        elif key in ["Lat", "Lng"]:
            data_dict[key] = float(value)  # float으로 변환
        else:
            data_dict[key] = value
    
    return data_dict

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("arduino/gps")

def on_message(client, userdata, msg):
    global gps_data
    if msg:
        payload = msg.payload.decode('utf-8')
        
        gps_data['Lat'], gps_data['Lng'] = payload.split(", ")
        
        gps_data['UserName'] = "이준경"
        gps_data['Date'] = date.today()
        gps_data['Time'] = datetime.now()
    
    # lat, lng = map(float, payload.split(','))
    # gps_data['lat'] = lat
    # gps_data['lng'] = lng
    

def start_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("43.203.100.121", 1883, 60)
    client.loop_start()
