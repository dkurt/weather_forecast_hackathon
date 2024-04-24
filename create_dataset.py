import argparse
import numpy as np
import requests
import json
from tqdm import tqdm
import time

parser = argparse.ArgumentParser()
parser.add_argument("--lat", type=float)
parser.add_argument("--long", type=float)
parser.add_argument("--start_date", type=str)  # in format YYYY-MM-DD
parser.add_argument("--end_date", type=str)  # in format YYYY-MM-DD
args = parser.parse_args()

latitude_center = args.lat
longitude_center = args.long
# make step of ~5km
latitude_step = 5 / 111.1
longitude_step = 5 / 111.321
 
num_points = 30
latitude = [latitude_center + latitude_step * num_points / 2, latitude_center - latitude_step * num_points / 2]
longitude = [longitude_center - longitude_step * num_points / 2, longitude_center + longitude_step * num_points / 2]
 
latitude = np.linspace(latitude[0], latitude[1], num_points)
longitude = np.linspace(longitude[0], longitude[1], num_points)
 
metrics = [
    "temperature_2m",
    "relative_humidity_2m",
    "pressure_msl",
    "wind_speed_10m",
    "wind_speed_80m",
    "wind_speed_120m",
    "wind_speed_180m",
    "wind_direction_10m",
    "wind_direction_80m",
    "wind_direction_120m",
    "wind_direction_180m",
    "cloud_cover",
]
 
for y, lat in tqdm(enumerate(latitude)):
    for x, long in enumerate(longitude):
        print(y, x)
        res = requests.get(f"https://archive-api.open-meteo.com/v1/era5?latitude={lat}&longitude={long}&start_date={args.start_date}&end_date={args.end_date}&hourly={','.join(metrics)},")
        path = f"data/weather_{lat}_{long}.json"
        with open(path, "wt") as f:
            f.write(res.text)
 
elevation = np.zeros([num_points, num_points], dtype=np.float32)
temperature = np.zeros([48, num_points, num_points], dtype=np.float32)
humidity = np.zeros([48, num_points, num_points], dtype=np.float32)
pressure = np.zeros([48, num_points, num_points], dtype=np.float32)
wind_speed = np.zeros([48, num_points, num_points], dtype=np.float32)
wind_dir = np.zeros([48, num_points, num_points], dtype=np.float32)
cloud_cover = np.zeros([48, num_points, num_points], dtype=np.float32)
for y, lat in enumerate(latitude):
    for x, long in enumerate(longitude):
        path = f"data/weather_{lat}_{long}.json"
        with open(path, "rt") as f:
            data = json.load(f)
            elevation[y, x] = data["elevation"]
            temperature[:, y, x] = data["hourly"]["temperature_2m"]
            humidity[:, y, x] = data["hourly"]["relative_humidity_2m"]
            pressure[:, y, x] = data["hourly"]["pressure_msl"]
            wind_speed[:, y, x] = data["hourly"]["wind_speed_10m"]
            wind_dir[:, y, x] = data["hourly"]["wind_direction_10m"]
            cloud_cover[:, y, x] = data["hourly"]["cloud_cover"]
 
np.save("data/elevation.npy", elevation)
np.save("data/temperature.npy", temperature[:43])
np.save("data/pressure.npy", pressure[:43])
np.save("data/humidity.npy", humidity[:43])
np.save("data/wind_speed.npy", wind_speed[:43])
np.save("data/wind_dir.npy", wind_dir[:43])
np.save("data/cloud_cover.npy", cloud_cover[:43])
print(cloud_cover[:43].shape)
 
solution = np.stack([
    temperature[43:].reshape(-1),
    pressure[43:].reshape(-1),
    humidity[43:].reshape(-1),
    wind_speed[43:].reshape(-1),
    wind_dir[43:].reshape(-1),
    cloud_cover[43:].reshape(-1),
], axis=1)
 
import pandas as pd
 
solution = pd.DataFrame(solution, columns=["temperature", "pressure", "humidity", "wind_speed", "wind_dir", "cloud_cover"])
solution["Usage"] = "Public"
solution.to_csv("data/solution.csv", index_label="ID")
