import datetime
import json

def convert_milliseconds_to_duration(ms):
    # Convert milliseconds to seconds
    seconds = int(ms) / 1000
    # Create a timedelta object from the seconds
    duration = datetime.timedelta(seconds=seconds)
    # Format the timedelta object to a human-readable string
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return '%s:%s:%s' % (hours, minutes, seconds)

def json_to_obj(file_path) -> dict | list | None:
    with open(file_path, 'r') as f:
        return json.load(f)