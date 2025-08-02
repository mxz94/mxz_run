# import os
#
# import requests
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
#
# def get_list():
#     params = {
#       'activityType': 'other',
#       'limit': '200',
#       'start': '0',
#       'excludeChildren': 'false',
#     }
#
#     response = requests.get(
#       'https://connect.garmin.com/activitylist-service/activities/search/activities',
#       params=params,
#       cookies=cookies,
#       headers=headers,
#     )
#     print(response.text)
#     return response.json()
#
# def change_to_run(activity_id, activity_name):
#   json_data = {
#     'activityTypeDTO': {
#       'typeId': 2,
#       'typeKey': 'running',
#       'parentTypeId': 4,
#       'isHidden': False,
#       'restricted': False,
#       'trimmable': True,
#     },
#     'activityName': activity_name
#   }
#
#   response = requests.put(
#     f'https://connect.garmin.com/activity-service/activity/{activity_id}',
#     cookies=cookies,
#     headers=headers,
#     json=json_data,
#   )
#
# def change_to_ride(activity_id, activity_name):
#   json_data = {
#     'activityTypeDTO': {
#       'typeId': 2,
#       'typeKey': 'cycling',
#       'parentTypeId': 4,
#       'isHidden': False,
#       'restricted': False,
#       'trimmable': True,
#     },
#     'activityName': activity_name
#   }
#
#   response = requests.put(
#     f'https://connect.garmin.com/activity-service/activity/{activity_id}',
#     cookies=cookies,
#     headers=headers,
#     json=json_data,
#   )
# def mps_to_kmph(speed_mps):
#   speed_kmph = speed_mps * 3.6
#   return round(speed_kmph, 2)
#
# if __name__ == '__main__':
#     list = get_list()
#     for item in list:
#       activityId = item["activityId"]
#       averageSpeed = round(item["averageSpeed"]* 3.6, 2)
#       activityName = item["activityName"]
#       activity_type_str = "跑步" if averageSpeed < 20 else "骑行"
#       activity_name = activityName.replace("其他", activity_type_str)
#       if averageSpeed > 20:
#         change_to_ride(activityId, activity_name)
#         print(f"{item['activityName']} 速度 {averageSpeed} km/h 改为骑行")
#       else:
#         change_to_run(activityId, activity_name)
#         print(f"{item['activityName']} 速度 {averageSpeed} km/h 改为跑步")
#
#
