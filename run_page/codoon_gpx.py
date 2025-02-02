import argparse
import base64
import hashlib
import hmac
import json
import os
import time
import urllib.parse
import xml.etree.ElementTree as ET
from collections import namedtuple
from datetime import datetime, timedelta

import eviltransform
import gpxpy
import numpy as np
import polyline
import requests
from config import (
  BASE_TIMEZONE,
  GPX_FOLDER,
  JSON_FILE,
  SQL_FILE,
  TCX_FOLDER,
  run_map,
  start_point,
)
from generator import Generator
from tzlocal import get_localzone
from utils import adjust_time_to_utc, adjust_timestamp_to_utc, to_date

# struct body
FitType = np.dtype(
  {
    "names": [
      "time",
      "bpm",
      "lati",
      "longi",
      "elevation",
    ],  # unix timestamp, heart bpm, LatitudeDegrees, LongitudeDegrees, elevation
    "formats": ["i", "S4", "S32", "S32", "S8"],
  }
)

# device info
user_agent = "CodoonSport(8.9.0 1170;Android 7;Sony XZ1)"
did = "24-00000000-03e1-7dd7-0033-c5870033c588"

# fixed params
base_url = "https://api.codoon.com"
davinci = "0"
basic_auth = "MDk5Y2NlMjhjMDVmNmMzOWFkNWUwNGU1MWVkNjA3MDQ6YzM5ZDNmYmVhMWU4NWJlY2VlNDFjMTk5N2FjZjBlMzY="
client_id = "099cce28c05f6c39ad5e04e51ed60704"

# for multi sports
TYPE_DICT = {
  0: "hiking",
  1: "running",
  2: "cycling",
}
TYPE_DICT_STR = {
  0: "徒步",
  1: "跑步",
  2: "骑行",
}

# for tcx type
TCX_TYPE_DICT = {
  0: "Hike",
  1: "Running",
  2: "Ride",
}

# only for running sports, if you want others, please change the True to False
IS_ONLY_RUN = False

# If your points need trans from gcj02 to wgs84 coordinate which use by Mappbox
TRANS_GCJ02_TO_WGS84 = False
# trans the coordinate data until the TRANS_END_DATE, work with TRANS_GCJ02_TO_WGS84 = True
TRANS_END_DATE = "2014-03-24"


# decrypt from libencrypt.so Java_com_codoon_jni_JNIUtils_encryptHttpSignature
# sha1 -> base64
def make_signature(message):
  key = bytes("ecc140ad6e1e12f7d972af04add2c7ee", "UTF-8")
  message = bytes(message, "UTF-8")
  digester = hmac.new(key, message, hashlib.sha1)
  signature1 = digester.digest()
  signature2 = base64.b64encode(signature1)
  return str(signature2, "UTF-8")


def device_info_headers():
  return {
    "accept-encoding": "gzip",
    "user-agent": user_agent,
    "did": did,
    "davinci": davinci,
  }


def download_codoon_gpx(gpx_data, log_id):
  try:
    print(f"downloading codoon {str(log_id)} gpx")
    file_path = os.path.join(GPX_FOLDER, str(log_id) + ".gpx")
    with open(file_path, "w", encoding="utf-8") as fb:
      fb.write(gpx_data)
  except:
    print(f"wrong id {log_id}")
    pass

class CodoonAuth:
  def __init__(self, refresh_token=None):
    self.params = {}
    self.refresh_token = refresh_token
    self.token = ""

    if refresh_token:
      session = requests.Session()
      session.headers.update(device_info_headers())
      query = f"client_id={client_id}&grant_type=refresh_token&refresh_token={refresh_token}&scope=user%2Csports"
      r = session.post(
        f"{base_url}/token?" + query,
        data=query,
        auth=self.reload(query),
        )
      if not r.ok:
        print(r.json())
        raise Exception("refresh_token expired")

      self.token = r.json()["access_token"]

  def reload(self, params={}, token=""):
    self.params = params
    if token:
      self.token = token
    return self

  @classmethod
  def __get_signature(cls, token="", path="", body=None, timestamp=""):
    arr = path.split("?")
    path = arr[0]
    query = arr[1] if len(arr) > 1 else ""
    body_str = body if body else ""
    if body is not None and not isinstance(body, str):
      body_str = json.dumps(body)
    if query != "":
      query = urllib.parse.unquote(query)

    pre_string = f"Authorization={token}&Davinci={davinci}&Did={did}&Timestamp={str(timestamp)}|path={path}|body={body_str}|{query}"
    return make_signature(pre_string)

  def __call__(self, r):
    params = self.params
    body = params
    if not isinstance(self.params, str):
      params = self.params.copy()
      body = json.dumps(params)

    sign = ""
    if r.method == "GET":
      timestamp = 0
      r.headers["authorization"] = "Basic " + basic_auth
      r.headers["timestamp"] = timestamp
      sign = self.__get_signature(
        r.headers["authorization"], r.path_url, timestamp=timestamp
      )
    elif r.method == "POST":
      timestamp = int(time.time())
      r.headers["timestamp"] = timestamp
      if "refresh_token" in params:
        r.headers["authorization"] = "Basic " + basic_auth
        r.headers["content-type"] = (
          "application/x-www-form-urlencode; charset=utf-8"
        )
      else:
        r.headers["authorization"] = "Bearer " + self.token
        r.headers["content-type"] = "application/json; charset=utf-8"
      sign = self.__get_signature(
        r.headers["authorization"], r.path_url, body=body, timestamp=timestamp
      )
      r.body = body

    r.headers["signature"] = sign
    return r

def get_time_period(now):
  """
  根据当前时间判断是凌晨、早上、上午、中午、下午、傍晚、晚上或深夜。

  参数:
      now (datetime): 当前时间

  返回值:
      str: "凌晨"、"早上"、"上午"、"中午"、"下午"、"傍晚"、"晚上" 或 "深夜"
  """
  current_hour = now.hour

  # 判断时间段
  if 0 <= current_hour < 6:
    return "凌晨"
  elif 6 <= current_hour < 9:
    return "早上"
  elif 9 <= current_hour < 12:
    return "上午"
  elif 12 <= current_hour < 14:
    return "中午"
  elif 14 <= current_hour < 18:
    return "下午"
  elif 18 <= current_hour < 20:
    return "傍晚"
  elif 20 <= current_hour < 24:
    return "晚上"
  else:
    return "深夜"  # 深夜一般属于凌晨时段

class Codoon:
  def __init__(self, mobile="", password="", refresh_token=None, user_id=""):
    self.mobile = mobile
    self.password = password
    self.refresh_token = refresh_token
    self.user_id = user_id

    self.session = requests.Session()

    self.session.headers.update(device_info_headers())

    self.auth = CodoonAuth(self.refresh_token)
    self.auth.token = self.auth.token

  @classmethod
  def from_auth_token(cls, refresh_token, user_id):
    return cls(refresh_token=refresh_token, user_id=user_id)

  def login_by_phone(self):
    params = {
      "client_id": client_id,
      "email": self.mobile,
      "grant_type": "password",
      "password": self.password,
      "scope": "user",
    }
    r = self.session.get(
      f"{base_url}/token",
      params=params,
      auth=self.auth.reload(params),
    )
    login_data = r.json()
    if login_data.__contains__("status") and login_data["status"] == "Error":
      raise Exception(login_data["description"])
    self.refresh_token = login_data["refresh_token"]
    self.token = login_data["access_token"]
    self.user_id = login_data["user_id"]
    self.auth.reload(token=self.token)
    print(
      f"your refresh_token and user_id are {str(self.refresh_token)} {str(self.user_id)}"
    )

  def get_runs_records(self, page=1):
    payload = {"limit": 500, "page": page, "user_id": self.user_id}
    r = self.session.post(
      f"{base_url}/api/get_old_route_log",
      data=payload,
      auth=self.auth.reload(payload),
    )
    if not r.ok:
      print(r.json())
      raise Exception("get runs records error")

    runs = r.json()["data"]["log_list"]
    if IS_ONLY_RUN:
      runs = [run for run in runs if run["sports_type"] == 1]
    print(f"{len(runs)} runs to parse")
    if r.json()["data"]["has_more"]:
      return runs + self.get_runs_records(page + 1)
    return runs

  @staticmethod
  def parse_latlng(points):
    if not points:
      return []
    try:
      points = [[p["latitude"], p["longitude"]] for p in points]
    except Exception as e:
      print(str(e))
      points = []
    return points

  def parse_points_to_gpx(self, run_points_data, cast_type, nname):
    # TODO for now kind of same as `keep` maybe refactor later
    points_dict_list = []
    for point in run_points_data[:-1]:
      points_dict = {
        "latitude": point["latitude"],
        "longitude": point["longitude"],
        "elevation": point["elevation"],
        "time": adjust_time_to_utc(to_date(point["time_stamp"]), BASE_TIMEZONE),
      }
      points_dict_list.append(points_dict)
    gpx = gpxpy.gpx.GPX()
    gpx.nsmap["gpxtpx"] = "http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx_track.name = nname
    gpx_track.type = cast_type
    gpx.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    for p in points_dict_list:
      point = gpxpy.gpx.GPXTrackPoint(**p)
      gpx_segment.points.append(point)
    return gpx.to_xml()

  def get_single_run_record(self, route_id):
    print(f"Get single run for codoon id {route_id}")
    payload = {
      "route_id": route_id,
    }
    r = self.session.post(
      f"{base_url}/api/get_single_log",
      data=payload,
      auth=self.auth.reload(payload),
    )
    if not r.ok:
      print(r)
      raise Exception("get runs records error")
    data = r.json()
    return data

  @staticmethod
  def _gt(dt_str):
    dt, _, us = dt_str.partition(".")
    return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")

  def parse_raw_data_to_namedtuple(
    self, run_data, old_gpx_ids, with_gpx=False, with_tcx=False
  ):
    run_data = run_data["data"]
    log_id = run_data["id"]
    sport_type = run_data["sports_type"]
    # only support run now, if you want all type comments these two lines
    if IS_ONLY_RUN and sport_type != 1:
      return
    cast_type = TYPE_DICT[sport_type] if sport_type in TYPE_DICT else sport_type
    cast_type_str = TYPE_DICT_STR[sport_type] if sport_type in TYPE_DICT_STR else sport_type
    if with_tcx:
      tcx_job(run_data)  # TCX part

    start_time = run_data.get("start_time")
    if not start_time:
      return
    end_time = run_data["end_time"]
    run_points_data = run_data["points"] if "points" in run_data else None

    latlng_data = self.parse_latlng(run_points_data)
    if TRANS_GCJ02_TO_WGS84:
      trans_end_date = time.strptime(TRANS_END_DATE, "%Y-%m-%d")
      start_date = time.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
      if trans_end_date > start_date:
        latlng_data = [
          list(eviltransform.gcj2wgs(p[0], p[1])) for p in latlng_data
        ]
      if run_points_data:
        for i, p in enumerate(run_points_data):
          p["latitude"] = latlng_data[i][0]
          p["longitude"] = latlng_data[i][1]

    # pass the track no points
    if str(log_id) not in old_gpx_ids and run_points_data:
      gpx_data = self.parse_points_to_gpx(run_points_data, cast_type, get_time_period(datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")) + cast_type_str )
      download_codoon_gpx(gpx_data, str(log_id))

  def get_old_tracks(self):
    run_records = self.get_runs_records()
    old_gpx_ids = os.listdir(GPX_FOLDER + "/codoon")
    old_gpx_ids = [i.split(".")[0] for i in old_gpx_ids if not i.startswith(".")]
    new_run_routes = [i for i in run_records if str(i["log_id"]) not in old_gpx_ids]
    for i in new_run_routes:
      run_data = self.get_single_run_record(i["route_id"])
      run_data["data"]["id"] = i["log_id"]
      self.parse_raw_data_to_namedtuple(
        run_data, old_gpx_ids
      )


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("mobile_or_token", help="codoon phone number or refresh token")
  parser.add_argument("password_or_user_id", help="codoon password or user_id")
  parser.add_argument(
      "--with-gpx",
      dest="with_gpx",
      action="store_true",
      help="get all keep data to gpx and download",
  )
  parser.add_argument(
      "--with-tcx",
      dest="with_tcx",
      action="store_true",
      help="get all keep data to tcx and download",
  )
  parser.add_argument(
      "--from-auth-token",
      dest="from_refresh_token",
      action="store_true",
      help="from authorization token for download data",
  )
  options = parser.parse_args()
  if options.from_refresh_token:
      j = Codoon.from_auth_token(
          refresh_token=str(options.mobile_or_token),
          user_id=str(options.password_or_user_id),
      )
  else:
    j = Codoon(
      mobile=str(options.mobile_or_token),
      password=str(options.password_or_user_id),
    )
    j.login_by_phone()
  j.get_old_tracks()

