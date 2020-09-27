import time as tm
start_time = tm.perf_counter()

import json
import random
import datetime
import concurrent.futures

from num2words import num2words
from urllib3 import PoolManager, Retry
from urllib3.exceptions import MaxRetryError

retries = Retry(connect=2, read=2, status=2)
http = PoolManager(retries=retries)

def get_time(timezone):
    time_object = json.loads(http.request("GET", "http://worldtimeapi.org/api/timezone/" + timezone).data)
    dt_in_tz = datetime.datetime.strptime(time_object["datetime"][:-6], "%Y-%m-%dT%H:%M:%S.%f")
    return dt_in_tz


try:
    zonelist = json.loads(http.request("GET", "http://worldtimeapi.org/api/timezone").data)
    zonelist = [zone for zone in zonelist if "etc" not in zone.lower() and "/" in zone.lower()]

    times = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_zone = {executor.submit(get_time, zone): zone for zone in zonelist}
        for future in concurrent.futures.as_completed(future_to_zone):
            zone = future_to_zone[future]
            try:
                time = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                if time.hour == 17:
                    place = zone
                    place_pieces = zone.split("/")
                    if len(place_pieces) > 1:
                        place = place_pieces[-1]
                    
                    min_string = num2words(time.minute)
                    if time.minute < 10:
                        min_string = "o " + min_string
                    if time.minute == 0:
                        min_string = "o clock"
                    times.append({"place": place, "time": "five {}".format(min_string)})
            
    if times:
        chosen = random.choice(times)
        toast = random.choice(["Cheers", "Bottoms up", "Prost", "Skol", "Salud"])
        speak_output = "It's {} in {}. {}!".format(chosen["time"], chosen["place"].replace("_", " "), toast)
except MaxRetryError:
    logging.error("Error connecting to World Time API", exc_info=1)
    speak_output = "I'm having trouble finding the time around the world, but it's five PM somewhere! Try again later."

print(speak_output)
print("--- %.2f seconds real ---" % (tm.perf_counter() - start_time))