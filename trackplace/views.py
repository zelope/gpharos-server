from django.shortcuts import render, get_object_or_404
from tracker.mqtt_client import gps_data
import folium
import requests
import urllib.request
import json
from trackplace.models import CulturewalkTable
import re
import json
from django.conf import settings
from pathlib import Path

# .config 파일 경로 설정 (manage.py와 같은 계층에 있는 .config 파일)
config_path = settings.BASE_DIR / '.config'

# 파일 열기
with open(config_path, 'r') as file:
    config = json.load(file)

"""저장된 DB
 0   ID            
 1   CTPRVN_NM     광역/특별시 or 도
 2   SIGNGU_NM     구 insnull = ""
 3   LEGALDONG_NM  동 insnull = ""
 4   FCLTY_NM      건물(장소) 이름
 5   MLSFC_NM      분류
 6   ADR_NM        도로명 주소

"""



def _gps2addr(lat,lng):
    
    lat = str(lat).strip()
    lng = str(lng).strip()
    coords =  lng+ ","+lat
    orders =  "legalcode"
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
    
    
    try:
        legal_str, legal_list= _showlist(geo_data["results"][0]['region'])
        
    except:

        legal_str = ""
        legal_list = []
        
    return  legal_str, legal_list
    
def _showlist(code_list:list) -> str:
    adrr_str = ""
    addr_list = list()
    for i, r in enumerate(code_list):
        if i == 0:
            continue
        adrr_str = adrr_str + " "+code_list[r]["name"]
        addr_list.append(code_list[r]["name"])
    return adrr_str, addr_list

def _addr2gps(addr: str, lat:float, lng: float):
    url = config['api']['geocoding']
    headers = {
        "X-NCP-APIGW-API-KEY-ID": config['api']['id'],
        "X-NCP-APIGW-API-KEY": config['api']['key']
    }
    params = {"query": addr,
            "coordinate" : f"{lng},{lat}",
            
            }
    response = requests.get(url, headers=headers, params=params)
    geo_data = response.json()
    
    return geo_data['addresses'][0]
    
def send_crud(db_class, crud_lat, crud_lng):
    send_mss = list()
    for data in db_class:
        send_dc = dict()
        send_dc["id"] = str(data.id)
        send_dc["hot_name"] = data.fclty_nm
        geo  = _addr2gps(data.adr_nm, crud_lat ,crud_lng)
        
        geo_lat = geo["y"]
        geo_lng = geo["x"]
        map = folium.Map(location=[geo_lat, geo_lng], zoom_start=17)
        folium.Marker([geo_lat, geo_lng], tooltip="Current Location").add_to(map)
        map = map._repr_html_()
        send_dc["img_path"] = map
        send_mss.append(send_dc)
    return send_mss

def call_blog(serch_tag:str):
    client_id = config['blog']['id']
    client_secret = config['blog']['secret']
    serch = serch_tag + " 후기"
    encText = urllib.parse.quote(serch)
    url = config['blog']['api'] + encText + f"&display=2" # JSON 결과
    # url = "https://openapi.naver.com/v1/search/blog.xml?query=" + encText # XML 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request)
    response_body = response.read().decode('utf-8')
    json_data = json.loads(response_body)
    
    return json_data['items']

def hotplace(request):
    
    try :
        lat = gps_data.get('Lat', 0)
        lng = gps_data.get('Lng', 0)
        legal_str, legal_list= _gps2addr(lat,lng)
        
        user_data = {"name" : gps_data.get('UserName'),
                    "location" : legal_str}
        assert user_data['name'], "The 'name' field cannot be empty."
        
    except AssertionError:
        user_data = {"name":""}
        send_cw = [
            {"img_path" : "img/no_img.png", "is_map": False,"hot_name" : "로딩중" },
            {"img_path" : "img/no_img.png", "is_map": False,"hot_name" : "로딩중" },
            {"img_path" : "img/no_img.png", "is_map": False,"hot_name" : "로딩중" },
            
        ]
        send_le = [
            {"img_path" : "img/no_img.png", "is_map": False,"hot_name" : "로딩중" },
            {"img_path" : "img/no_img.png", "is_map": False,"hot_name" : "로딩중" },
            {"img_path" : "img/no_img.png", "is_map": False,"hot_name" : "로딩중" },
            
        ]

    else:
        """
        데이터 베이스에서 admcode or legalcode 와 일치하는 주소에서 장소정보 가려오는 코드
        """
        culture_walk = CulturewalkTable.objects.filter(ctprvn_nm=legal_list[0],signgu_nm=legal_list[1],legaldong_nm= legal_list[2]).exclude(mlsfc_nm="문화시설")
        leisure = CulturewalkTable.objects.filter(ctprvn_nm=legal_list[0],signgu_nm=legal_list[1],legaldong_nm= legal_list[2], mlsfc_nm__in=["자연_공원", "무장애_나눔길"])
        
        send_cw = send_crud(culture_walk,lat,lng)
        send_le = send_crud(leisure,lat,lng)
        
        
    finally:
    
        context = {
            "user" : user_data,
            "culture_walk" : send_cw,  
            "leisure" : send_le,
            
        }
    
    
    return render(request, 'trackplace/hot.html',context=context)


def click_address(request, title):    
    
    if title:
        #result = get_object_or_404(dummy_model, festival_name=title)
        deatail_data = CulturewalkTable.objects.filter(id=title)
        
        
        
        lat = gps_data.get('Lat', 0)
        lng = gps_data.get('Lng', 0)
        
        crud_data = _addr2gps(deatail_data[0].adr_nm,lat,lng)
        distance = float(crud_data['distance'])/1000
        result = {
            "festival_name" : deatail_data[0].fclty_nm,
            "location" : deatail_data[0].adr_nm,
            "distance" :distance ,
            "tag" : deatail_data[0].mlsfc_nm,    
            
        }
        
        blog_crud = call_blog(deatail_data[0].fclty_nm)
        blog_data = list()
        for blog in blog_crud:
            data = dict()
            data['name'] =re.sub(r'<[^>]*>', '', blog['title']) 
            data['url'] = blog['link']
            blog_data.append(data)
            
            
        result["blog"] = blog_data
        
        map = folium.Map(location=[lat, lng], zoom_start=14)
        folium.Marker([lat, lng], tooltip="Current Location").add_to(map)
        folium.Marker([crud_data['y'], crud_data['x']], tooltip=deatail_data[0].fclty_nm, icon=folium.Icon(color='red')).add_to(map)
        map = map._repr_html_()
        
    context = {
        'festival': result,
        'img_path': map
    }

    return render(request, 'trackplace/place.html', context)
    