import requests
import json
import os
import datetime
import time

'''
AP010014: 心知天气错误代码，免费用户超过了每小时访问量额度。一小时后自动恢复。
'''


KEY2 = 'dhxi7zagtatvtrgb' # API key 185
UID2 = 'UFD6F88B7C'  # 用户ID
KEY = 'jpc0si7sh9qjudrz'  # API key 150
UID = "U396147DF7"  # 用户ID
NOW_API = 'https://api.seniverse.com/v3/weather/now.json'  # API URL，可替换为其他 URL
DAILY_API = 'https://api.seniverse.com/v3/weather/daily.json'
LIFE_API = 'https://api.seniverse.com/v3/life/suggestion.json'
UNIT = 'c'  # 单位
LANGUAGE = 'zh-Hans'  # 查询结果的返回语言

CITYS = [] #当前API可供查询的城市名称
CITYS_WEATHER = {} #城市天气DIC数据
STATUS = False #数据是否已经准备好
CURRENT_DATE= '0' #当前数据的日期，日

def init():
    global CITYS
    global CITYS_WEATHER
    global STATUS
    global CURRENT_DATE
    #读取城市列表
    if len(CITYS)==0:
        with open("storage/city.json", 'r',encoding="utf8") as load_f:
            city_dict = json.load(load_f)
            CITYS = city_dict["citys"]
    #检查今天是否已经存储过天气数据
    if _check_weather_data():
        with open("storage/city_weather.json", 'r',encoding="utf8") as load_f:
            CITYS_WEATHER = json.load(load_f)
        STATUS = True
        CURRENT_DATE = time.localtime(time.time())[2]
        return
    #清空JSON数据文件
    with open("storage/city_weather.json",'w') as city_weather:
        city_weather.write("")
    #请求城市天气
    index = 0
    for city in CITYS:
        index += 1
        try:
            result = _brief(city)
            if result[0]:
                CITYS_WEATHER[city]=result[1]
                print(str(index)+': 正在写入 '+city+' 的数据...')
            else:
                if result[1]=='AP010014': #若请求次数满了，则换key值，重新请求当前city，若不是，则继续
                    _change()
                    result = _brief(city)
                    if result[0]:
                        CITYS_WEATHER[city]=result[1]
                        print(str(index)+': 正在写入 '+city+' 的数据...')
                    else:
                        print(result[1])
        except Exception as e:
            print(e)
    CITYS_WEATHER["date"] = datetime.date.today().strftime('%Y-%m-%d')
    #写入天气数据到数据文件
    with open("storage/city_weather.json",'w',encoding='utf8') as city_weather:
        json.dump(CITYS_WEATHER,city_weather,ensure_ascii=False)
    STATUS = True
    CURRENT_DATE = time.localtime(time.time())[2]
def _change():
    global KEY2
    global UID2
    global KEY
    global UID
    KEY,KEY2 = KEY2,KEY
    UID,UID2 = UID2,UID

def _check_weather_data():
    citys_weather = []
    with open("storage/city_weather.json", 'a+', encoding="utf8") as load_f:
        if load_f.tell()>0:
            load_f.seek(0)
            citys_weather = json.load(load_f)
    if 'date' in citys_weather:
        if citys_weather['date'] == datetime.date.today().strftime('%Y-%m-%d'):
            return True
    return False

def _now(location):
    r = requests.session()
    r.keep_alive = False
    result = r.get(NOW_API, params={
        'key': KEY,
        'location': location,
        'language': LANGUAGE,
        'unit': UNIT
    }, timeout=2)
    result = json.loads(result.text)
    if 'results' in result:
        return (True, location+'当前天气'+result['results'][0]['now']['text']+", 气温"+result['results'][0]['now']['temperature']+"摄氏度")
    return (False,result['status'])

def _daily(location):
    r = requests.session()
    r.keep_alive = False
    result = r.get(DAILY_API, params={
        'key': KEY,
        'location': location,
        'language': LANGUAGE,
        'unit': UNIT
    }, timeout=2)
    result = json.loads(result.text)
    return result

def _life(location):
    r = requests.session()
    r.keep_alive = False
    result = r.get(LIFE_API, params={
        'key': KEY,
        'location': location,
        'language': LANGUAGE,
    }, timeout=2)
    result = json.loads(result.text)
    return result

def _all(location):
    result = {}
    result['daily'] = _daily(location)
    result['life'] = _life(location)
    return result

#获取目的城市的天气简报
def _brief(location):
    content = _all(location)
    result = ""
    #如果查询出结果
    if 'results' in content['life']:
        today = content['daily']['results'][0]['daily'][0]
        suggestion = content['life']['results'][0]['suggestion']
        result = '%s今天(%s)白天%s,夜间%s,最高温度%s摄氏度,最低温度%s摄氏度,%s风。%s洗车，天气%s,运动%s' % (location, today['date'], today['text_day'], today['text_night'], today['high'], today['low'], today['wind_direction'],suggestion['car_washing']['brief'],suggestion['dressing']['brief'],suggestion['sport']['brief'])
        return (True, result)
    else:#如果没有
        print(content['life'])
        if 'status_code' in content['life']:
            if content['life']['status_code'] == 'AP010014':
                return (False, 'AP010014')
            else:
                return (False, content['life']['status'])
        return (False, '未知错误')




'''Now formate
{
    "results": [
        {
            "location": {
                "id": "WX4FBXXFKE4F",
                "name": "北京",
                "country": "CN",
                "path": "北京,北京,中国",
                "timezone": "Asia/Shanghai",
                "timezone_offset": "+08:00"
            },
            "now": {
                "text": "多云",
                "code": "4",
                "temperature": "25"
            },
            "last_update": "2018-07-09T20:25:00+08:00"
        }
    ]
}

{
    "status": "The location can not be found.",
    "status_code": "AP010010"
}
'''

'''
{
    "results": [
        {
            "location": {
                "id": "WX4FBXXFKE4F",
                "name": "北京",
                "country": "CN",
                "path": "北京,北京,中国",
                "timezone": "Asia/Shanghai",
                "timezone_offset": "+08: 00"
            },
            "daily": [
                {
                    "date": "2018-07-09",
                    "text_day": "雷阵雨",
                    "code_day": "11",
                    "text_night": "阴",
                    "code_night": "9",
                    "high": "29",
                    "low": "22",
                    "precip": "",
                    "wind_direction": "东南",
                    "wind_direction_degree": "135",
                    "wind_speed": "10",
                    "wind_scale": "2"
                },
                {
                    "date": "2018-07-10",
                    "text_day": "多云",
                    "code_day": "4",
                    "text_night": "小雨",
                    "code_night": "13",
                    "high": "30",
                    "low": "22",
                    "precip": "",
                    "wind_direction": "南",
                    "wind_direction_degree": "180",
                    "wind_speed": "10",
                    "wind_scale": "2"
                },
                {
                    "date": "2018-07-11",
                    "text_day": "小雨",
                    "code_day": "13",
                    "text_night": "小雨",
                    "code_night": "13",
                    "high": "25",
                    "low": "22",
                    "precip": "",
                    "wind_direction": "南",
                    "wind_direction_degree": "180",
                    "wind_speed": "10",
                    "wind_scale": "2"
                }
            ],
            "last_update": "2018-07-09T11: 00: 00+08: 00"
        }
    ]
}
'''