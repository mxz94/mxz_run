"""
If you do not want bind any account
Only the gpx files in GPX_OUT sync
"""

import argparse

from config import GPX_FOLDER, JSON_FILE, SQL_FILE

from utils import make_activities_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        default=GPX_FOLDER,
        help="directory containing GPX files to import",
    )
    parser.add_argument(
        "--only-after-latest",
        action="store_true",
        help="only import GPX files newer than the latest database activity",
    )
    options = parser.parse_args()

    print(f"sync gpx files in {options.data_dir}")
    make_activities_file(
        SQL_FILE,
        options.data_dir,
        JSON_FILE,
        deduplicate_by_start_time=True,
        merge_tracks=False,
        only_after_latest=options.only_after_latest,
    )
