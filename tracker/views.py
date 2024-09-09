from django.http import JsonResponse
from django.shortcuts import render
from tracker.mqtt_client import gps_data
import folium
from datetime import datetime,timedelta
import requests
import json
from django.conf import settings
from pathlib import Path

# .config 파일 경로 설정 (manage.py와 같은 계층에 있는 .config 파일)
config_path = settings.BASE_DIR / '.config'

# 파일 열기
with open(config_path, 'r') as file:
    config = json.load(file)


gps_log = [
    dict()
]

def _log_update(lat, lng):
    log_dict = {"Date":"","Time":"","admcode":"", "addr":""}
    if (lat != 0.0 ) and (lng != 0.0 ):
        admcode, addr = _gps2addr(lat, lng)
        log_dict["Date"] = gps_data.get('Date', 0)
        log_dict["Time"] = gps_data.get('Time', 0)
        log_dict["kor_time"] = log_dict["Time"].strftime("%p %I시 %M분 %S초").replace('AM', '오전').replace('PM', '오후')
        log_dict["admcode"] = admcode
        log_dict["addr"] = addr
        try:
            if log_dict["kor_time"] == gps_log[-1]["kor_time"]:
                pass
            else:
                gps_log.append(log_dict)
        except:
            gps_log.append(log_dict)

    try:
        del_nt = []
        reference_t= datetime.combine(log_dict["Date"], log_dict["Time"])
        
        for i, log in enumerate(gps_log[1:]):
            datetime_obj = datetime.combine(log["Date"], log["Time"])
            time_difference = reference_t - datetime_obj 
            if time_difference >= timedelta(hours=1):
                del_nt.apeend(i + 1)
        
        if del_nt:
            pass
        else:
            del_nt.sort(reverse=True)

            # 요소 삭제
            for index in del_nt:
                del gps_log[index]
        
        while (len(gps_log) > 9):
            del gps_log[1]
    except:
        pass

def _gps2addr(lat,lng):
    lat = str(lat).strip()
    lng = str(lng).strip()
    coords =  lng+ ","+lat
    orders = "admcode,addr"
    output = "json"

    url = config['api']['gc']
    headers = {
        "X-NCP-APIGW-API-KEY-ID": config['api']['id'],
        "X-NCP-APIGW-API-KEY": config['api']['key']
    }
    params = {"coords": coords,
            "orders" : orders,
            "output" : output,
            }
    response = requests.get(url, headers=headers, params=params)
    geo_data = response.json()
    
    
    
    admcode = _showlist(geo_data["results"][0]['region'])
    addr = _showlist(geo_data["results"][1]['region'])

    
    return admcode, addr
    

def _showlist(code_list:list) -> str:
    adrr_str = ""
    for i, r in enumerate(code_list):
        if i == 0:
            continue
        adrr_str = adrr_str + " "+code_list[r]["name"]
    
    return adrr_str

def get_gps_data(request):
    return JsonResponse(gps_data)

def map_view(request):
    # GPS 데이터를 가져옴   
    
    lat = gps_data.get('Lat', 0)
    lng = gps_data.get('Lng', 0)
    
    # 초기 위치 설정
    m = folium.Map(location=[lat, lng], zoom_start=17)
    
    # 마커 추가
    folium.Marker([lat, lng], tooltip="Current Location").add_to(m)
    
    # 지도를 HTML로 변환
    m = m._repr_html_()
    
    context = {
        'map': m,
        'log_datas' : gps_log[1:],
        "name": gps_data.get("UserName")
    }
   
    _log_update(lat,lng)

    return render(request, 'map.html', context)
