import argparse
import asyncio
import os
import time
from datetime import datetime

import gpxpy as mod_gpxpy
from stravalib.exc import ActivityUploadFailed, RateLimitTimeout
from stravaweblib import DataFormat

from config import GPX_FOLDER
from run_page.garmin_sync import Garmin


def get_to_generate_files(last_time):
  """
  reuturn to values one dict for upload
  and one sorted list for next time upload
  """
  file_names = os.listdir(GPX_FOLDER+ "/codoon")
  gpx_files = []
  for f in file_names:
    if f.endswith(".gpx"):
      file_path = os.path.join(GPX_FOLDER+ "/codoon", f)
      with open(file_path, "rb") as r:
        try:
          gpx = mod_gpxpy.parse(r)
        except Exception as e:
          print(f"Something is wring with {file_path} err: {str(e)}")
          continue
        # if gpx file has no start time we ignore it.
        if gpx.get_time_bounds()[0]:
          gpx_files.append((gpx, file_path))
  gpx_files_dict = {
    int(i[0].get_time_bounds()[0].timestamp()): i[1]
    for i in gpx_files
    if int(i[0].get_time_bounds()[0].timestamp()) > last_time
  }
  gpx_tracks_dict = {
    int(i[0].get_time_bounds()[0].timestamp()): i[0]
    for i in gpx_files
    if int(i[0].get_time_bounds()[0].timestamp()) > last_time
  }
  return sorted(list(gpx_files_dict.keys())), gpx_files_dict, gpx_tracks_dict

async def upload_to_activities(
  secret_string, auth_domain
):
  garmin_client = Garmin(secret_string, auth_domain, False)
  print("Need to load all gpx files maybe take some time")
  last_time = 0

  last_activity = await garmin_client.get_activities(0, 1)
  if not last_activity:
    print("no garmin activity")
    filters = {}
  else:
    # is this startTimeGMT must have ?
    after_datetime_str = last_activity[0]["startTimeGMT"]
    after_datetime = datetime.strptime(after_datetime_str, "%Y-%m-%d %H:%M:%S").timestamp()
    last_time = after_datetime
    print("garmin last activity date: ", after_datetime)

  to_upload_time_list,  to_upload_dict, gpx_tracks_dict = get_to_generate_files(last_time)
  index = 1
  print(f"{len(to_upload_time_list)} gpx files is going to upload")
  for i in to_upload_time_list:
    gpx_file = to_upload_dict.get(i)
    gpx_track = gpx_tracks_dict.get(i)
    aname = gpx_track.tracks[0].name
    try:
      await garmin_client.upload_activity_from_file(gpx_file)
    except RateLimitTimeout as e:
      timeout = e.timeout
      print(f"Strava API Rate Limit Timeout. Retry in {timeout} seconds\n")
      time.sleep(timeout)
      # try previous again
    except ActivityUploadFailed as e:
      print(f"Upload faild error {str(e)}")
    # spider rule
    time.sleep(1)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "secret_string", nargs="?", help="secret_string fro get_garmin_secret.py"
  )
  parser.add_argument(
    "--is-cn",
    dest="is_cn",
    action="store_true",
    help="if garmin accout is cn",
  )
  parser.add_argument(
    "--use_fake_garmin_device",
    action="store_true",
    default=False,
    help="whether to use a faked Garmin device",
  )
  options = parser.parse_args()
  auth_domain = "CN" if options.is_cn else ""

  try:
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(
      upload_to_activities(
        options.secret_string,
        auth_domain
      )
    )
    loop.run_until_complete(future)
  except Exception as err:
    print(err)
