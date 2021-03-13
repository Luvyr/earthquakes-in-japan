import pandas as pd
import geopandas as gpd

import folium
from folium import Choropleth
from folium.plugins import HeatMap

def embed_map(m, file_name):
    from IPython.display import IFrame
    m.save(file_name)
    return IFrame(file_name, width='100%', height='500px')

plate_boundaries = gpd.read_file("./Plate_Boundaries.shp")
plate_boundaries['coordinates'] = plate_boundaries.apply(lambda x: [(b,a) for (a,b) in list(x.geometry.coords)], axis='columns')
plate_boundaries.drop('geometry', axis=1, inplace=True)
plate_boundaries.head()

earthquakes = pd.read_csv("./earthquakes1970-2014.csv", parse_dates=["DateTime"])
earthquakes.head()

prefectures = gpd.read_file("./japan-prefecture-boundaries.shp")
prefectures.set_index('prefecture', inplace=True)
prefectures.head()

population = pd.read_csv("./japan-prefecture-population.csv")
population.set_index('prefecture', inplace=True)

# Calculating area (in square kilometers) of each prefecture
area_sqkm = pd.Series(prefectures.geometry.to_crs(epsg=32654).area / 10**6, name='area_sqkm')
stats = population.join(area_sqkm)

# Adding density (per square kilometer) of each prefecture
stats['density'] = stats["population"] / stats["area_sqkm"]
stats.head()

m_4 = folium.Map(location=[35,136], tiles='cartodbpositron', zoom_start=5)

Choropleth(geo_data=prefectures['geometry'].__geo_interface__, 
           data=stats['density'], 
           key_on="feature.id", 
           fill_color='BuPu', 
           legend_name='population density per sqkm'
          ).add_to(m_4)
def color_producer(magnitude):
    if magnitude > 6.5:
        return 'red'
    else:
        return 'green'
for i in range(0,len(earthquakes)):
    folium.Circle(
        location=[earthquakes.iloc[i]['Latitude'], earthquakes.iloc[i]['Longitude']],
        popup=("{} ({})").format(
            earthquakes.iloc[i]['Magnitude'],
            earthquakes.iloc[i]['DateTime'].year),
        radius=earthquakes.iloc[i]['Magnitude']**5.5,
        color=color_producer(earthquakes.iloc[i]['Magnitude'])).add_to(m_4)

embed_map(m_4, 'q_4.html')