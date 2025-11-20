import time

import requests
from sqlalchemy import text
from config import JSON_FILE, SQL_FILE
from generator import Generator
import json

token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Iml3cTVtSmZaaS1wLTM4QkstWE5rei1HZG1LayJ9.eyJhdWQiOiJhMjc0YjNjMy04ZTIxLTQxM2ItYTNhNy1jY2NkZDI1MTQxYzQiLCJleHAiOjE3NDE2Nzc3NDksImlhdCI6MTc0MTU5MTM0OSwiaXNzIjoicmVsaXZlLmNjIiwic3ViIjoiODgwZTdlOWItYWU5Ni00NWFmLWJlZjYtZmVlMzg1YmY2ZTAwIiwianRpIjoiMzBhYzYwMTAtYzNmMy00ODMzLWFkMjAtMDUwMTI3MzIzNTQwIiwiYXV0aGVudGljYXRpb25UeXBlIjoiUkVGUkVTSF9UT0tFTiIsImVtYWlsIjoiODM2MzIzNDkzQHFxLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJyZWxpdmUyMjg1NTAiLCJhcHBsaWNhdGlvbklkIjoiYTI3NGIzYzMtOGUyMS00MTNiLWEzYTctY2NjZGQyNTE0MWM0IiwidGlkIjoiODM4Njk0MjQtYWVhNS00Yzk5LWE3OTctZjEyNmFkZTYzNWNhIiwicm9sZXMiOltdLCJhdXRoX3RpbWUiOjE3NDE1ODg4NzIsInNpZCI6ImNiNzM0NTVlLWY1NjMtNDQ2OC05MWE1LWY0NWUwOWQyZWUwNyIsInVzZXJfaWQiOjIwMDA5ODg0fQ.imgqvoh6u4rseVVrAO1Ij_PMryAVa3QtGFFgDaVzxiae4ZnxwTZBmeyPNrKo-qa13U3L4UzUdvIfyd1yJsLn16CyoQ_nFc1MjKhnlC1YEnJmkJgH5jyQsj9xR98Qu8sNwfruNWjx2BRow4Z0wEgOyjjaOdy1GuNMRB_iv5bWdabRfTB22gsSyysKirBlGTqDF4JFihCMRfrz1P3CRGVbhG4yvHaXh0-O0uOgXb1IHoGISmjNFsbV-wJDbGFvJ3j2Qxqwq8GXLz3tloyI3j654v7xhFI5RSDnMos3KAqi6t9gxbCm44pRtDHwEZV9sH-BBquI8d4CDwBM5fevklWHpg'
HEADERS = {
    'Host': 'mobile.api.relive.cc',
    'User-Agent': 'Relive/12266 CFNetwork/1492.0.1 Darwin/23.3.0',
    'x-reliveapp-language': 'zh-TW',
    'x-device-info': 'Apple/Apple/iPhone 14 Plus/iPhone14,8',
    'x-reliveapp-request-mac': '8a32f89a',
    'x-datadog-trace-id': '6642824766071233509',
    'x-requested-with': 'ReliveApp/5.57.0/ios/17.3',
    'x-datadog-origin': 'rum',
    'baggage': 'sentry-environment=production,sentry-public_key=8495c51998f2459298164fddc54ac7a7,sentry-trace_id=799636d7d70644e29eb230da45bec2ac',
    'x-device-country': 'CN',
    'Connection': 'keep-alive',
    'x-reliveapp-request-nonce': '1741571773780',
    'x-datadog-sampling-priority': '0',
    'Authorization': 'Bearer '+token,
    'tracestate': 'dd=s:0;o:rum;p:90ed6ef39e8c782a',
    'Accept-Language': 'zh-TW',
    'x-datadog-tags': '_dd.p.tid=67ce46bd00000000',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'sentry-trace': '799636d7d70644e29eb230da45bec2ac-b8d6eb23853e7fa5',
    'traceparent': '00-67ce46bd000000005c300dedf6d7dbe5-90ed6ef39e8c782a-00',
}
def login():
    headers = {
        'Host': 'auth.relive.cc',
        'x-datadog-parent-id': '4697803898153834645',
        'tracestate': 'dd=s:0;o:rum;p:4131f3c15de79895',
        'baggage': 'sentry-environment=production,sentry-public_key=8495c51998f2459298164fddc54ac7a7,sentry-trace_id=33634ebbb4024af1809c8045cfc5334b',
        'Authorization': 'u859L5Ljh9PFb3BqoSY659rESkPls_2nZW4IKWRUDt8=',
        'x-datadog-sampling-priority': '0',
        'Accept': '*/*',
        'x-datadog-trace-id': '14734487376766342168',
        'sentry-trace': '33634ebbb4024af1809c8045cfc5334b-b3fbe5d67c8e5ec7',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        # Already added when you pass json=
        # 'Content-Type': 'application/json',
        'User-Agent': 'Relive/12266 CFNetwork/1492.0.1 Darwin/23.3.0',
        'x-datadog-tags': '_dd.p.tid=67ce898700000000',
        'x-datadog-origin': 'rum',
        'traceparent': '00-67ce898700000000cc7b6a33d7a29418-4131f3c15de79895-00',
    }

    json_data = {
        'applicationId': 'a274b3c3-8e21-413b-a3a7-cccdd25141c4',
        'metaData': {
            'device': {
                'name': 'ios',
                'type': 'MOBILE',
                'description': '5.57.0',
            },
        },
        'loginId': '',
        'password': '',
    }

    response = requests.post('https://auth.relive.cc/api/login', headers=headers, json=json_data)
    return response.json()

def refresh_token():
    headers = {
        'Host': 'auth.relive.cc',
        'x-datadog-parent-id': '9392757412813332726',
        'tracestate': 'dd=s:0;o:rum;p:8259c71a1c27e0f6',
        'baggage': 'sentry-environment=production,sentry-public_key=8495c51998f2459298164fddc54ac7a7,sentry-trace_id=33634ebbb4024af1809c8045cfc5334b',
        'x-datadog-sampling-priority': '0',
        'Accept': '*/*',
        'x-datadog-trace-id': '8851474751542497645',
        'sentry-trace': '33634ebbb4024af1809c8045cfc5334b-b3fbe5d67c8e5ec7',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'User-Agent': 'Relive/12266 CFNetwork/1492.0.1 Darwin/23.3.0',
        'x-datadog-tags': '_dd.p.tid=67ce934500000000',
        'x-datadog-origin': 'rum',
        'traceparent': '00-67ce9345000000007ad6c163b007916d-8259c71a1c27e0f6-00',
    }
    json_data = {
        'refreshToken': 'ZV6Wk-jfoznU7T2NvNAYzXfr-I27ZaHEY-p6tcr0e1OdsOA1t_0aZw',
        'token': token,
    }

    response = requests.post('https://auth.relive.cc/api/jwt/refresh', headers=headers, json=json_data)
    print("refresh relive token")
    if response.json()['token']:
        HEADERS["Authorization"] = 'Bearer ' + response.json()['token']
    return response.json()

def generate_data(id):
    json_data = {
        'activity': {
            'id': id,
            'name': 'mxz',
            'type': 'other',
            'video_settings': {
                'places': True,
                'snow': False,
                # normal
                'speed': 'fast',
                'hd': True,
                'weather': True,
                # vertical
                'orientation': 'horizontal',
                'photo_pause_duration_ms': 600,
                'theme_color': 'relive-yellow',
                'hide_relive_credits': True,
                # explore
                # rocket  beat blur  surfing
                'sound': 'explore',
                'font': 'montserrat',
            },
            'media': [],
        },
        'edit_source': 'create-basic-video',
    }
    response = requests.post(f'https://mobile.api.relive.cc/api/1/activity/{id}?', headers=HEADERS, json=json_data)
    print(response.json())

def activity_list():
    params = {
        'limit': '500',
    }
    response = requests.get('https://mobile.api.relive.cc/api/1/feed/me/updated', params=params, headers=HEADERS)
    data = response.json()["updated_activities"]
    return data

if __name__ == '__main__':
    print("Start relive")
    refresh_token()
    data = activity_list()
    #  生成
    data = sorted(data, key=lambda x: x["id"], reverse=True)
    print(data[0])
    upList = []
    for item in data:
        video_url = item["video_url"]
        created_at = item["start_date_local"][:16].replace('T', ' ')
        if not video_url and created_at > "2025-05":
            print("generate video " + str(item["id"]))
            generate_data(item["id"])
            upList.append(item["id"])
            print("wait gennarte mp4 url")
            time.sleep(180)
    # 更新db
    if len(upList) > 0:
        generator = Generator(SQL_FILE)
        data = activity_list()
        #  根据id 进行倒叙排序 取前20个
        data = sorted(data, key=lambda x: x["id"], reverse=True)
        print("refresh mp4 url")
        for item in data:
            id = item["id"]
            if id in upList:
                print("set video to database")
                print(item)
                share_url = item["share_url"]
                video_url = item["video_url"]
                created_at = item["start_date_local"][:16].replace('T', ' ')
                if video_url:
                    generator.update(text("UPDATE activities SET relive_url='" + share_url + "', video_url = '" + video_url + "' WHERE SUBSTR(start_date_local, 1, 16) = '" + created_at + "'"))

        activities_list = generator.loadForMapping()
        with open(JSON_FILE, "w") as f:
            json.dump(activities_list, f, indent=0)
