import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from shapely.geometry import Polygon, Point
from time import sleep

# Client must receive a Polygon shape via
# Polygon object from `shapely` package

# - resolution: Integer - the number of grid points in one axes.
# The number increases at rate resolution^2 

# - chunk_size: the number of elevation points sent to
# open-elevation.com. Requests for large numbers could be rejected.
# - sleep_time: In seconds. If large number of points are required,
# Open-elevation can block user. sleep_time slows down the data requests. 

class Client:
    def __init__(self, polygon, resolution = 100, chunk_size = 50, sleep_time = 0):
        self.polygon = polygon
        self.resolution = resolution
        self.chunk_size = chunk_size
        self.sleep_time = sleep_time
        self.points = self.__polygon_grid()
        self.data = None

    def __polygon_grid(self):
        latmin, lonmin, latmax, lonmax = self.polygon.bounds
        points = []
        
        for lat in np.linspace(latmin, latmax, self.resolution):
            for lon in np.linspace(lonmin, lonmax, self.resolution):
                current_point = Point([lat, lon])
                if (current_point.within(self.polygon)):
                    points.append(current_point)
        return points
    
    def plot_polygon(self, title = 'Polygon Shape', **kwargs):
        y, x = self.polygon.exterior.xy
        plt.figure(figsize = (10,10))
        plt.title('Polygon Shape with Coordinates')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.plot(x,y, **kwargs)
        plt.show()

    def __get_OE_link(self, data_points):
        api_url_end = ''
        for p in data_points:
            api_url_end += str(p.x) + ',' + str(p.y) + '|'
        api_url_end = 'https://api.open-elevation.com/api/v1/lookup?locations=' + api_url_end[:-1]
        return api_url_end

    def get_data(self):
        all_data = []
        len_points = len(self.points)
        for chunk in np.array_split(range(len_points), np.ceil(len_points/self.chunk_size)):
            current_points = [self.points[i] for i in chunk]
            current_link = self.__get_OE_link(current_points)
            current_data = requests.get(current_link).json()
            current_data = current_data['results']
            all_data = all_data + current_data
            sleep(self.sleep_time)
        self.data = pd.DataFrame(all_data)
        return pd.DataFrame(all_data).head()
    
    def plot_elevation(self, figsize = (10,10), **kwargs):
        if (self.data is None):
            print('.get_data() function is called to acquire elevation data.')
            self.get_data()
        fig, ax = plt.subplots(figsize=figsize)
        ax.scatter(self.data.longitude, self.data.latitude, c=self.data.elevation, cmap='gist_earth', **kwargs)
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.show()