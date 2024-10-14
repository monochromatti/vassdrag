# %% Imports

from pathlib import Path

import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import rasterio
from IPython.display import display
from folium.raster_layers import ImageOverlay
from matplotlib.colors import Normalize
from pyproj import Transformer
from rasterio.merge import merge
from shapely.geometry import box
from rasterio.warp import transform_bounds
import numpy as np 

# %% Magasin shapes

magasin_data = gpd.GeoDataFrame.from_file(
    Path("./data/magasin/Vannkraft_Magasin.shp")
)
centroid = magasin_data.geometry.centroid

magasin_data = magasin_data.to_crs(epsg=4326)
centroid = centroid.to_crs(epsg=4326)

magasin_data[["magNavn", "lrv_moh", "hrv_moh", "geometry"]]

# %% Høydedata

raster_overlays = []
for raster_file in Path("./data/høyde").glob("*.tif"):
    with rasterio.open(raster_file, "r") as src:

        raster_data, transform = rasterio.warp.reproject(
                        source=rasterio.band(src, 1),
                        src_crs=src.crs,
                        dst_crs='EPSG:4326',
                        resampling=rasterio.warp.Resampling.bilinear,
                        resolution=0.001
                    )

        norm = Normalize(vmin=0, vmax=2000)
        image = plt.cm.terrain(norm(raster_data[0]))

        bounds = rasterio.warp.transform_bounds(src.crs, 'EPSG:4326', *src.bounds)

        raster_overlays.append({
            "image": image,
            "bounds": [
                [bounds[1], bounds[0]],  # [south, west]
                [bounds[3], bounds[2]]   # [north, east]
            ]
        })

# %% Show interactive map

m = folium.Map(
    location=[centroid.y.mean(), centroid.x.mean()],
    zoom_start=10,
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri",
)
folium.GeoJson(magasin_data[["geometry"]]).add_to(m)

for overlay in raster_overlays:
    ImageOverlay(
        image=overlay["image"],
        bounds=overlay["bounds"],
        opacity=1.0,
        interactive=True,
        cross_origin=False,
        zindex=1,
    ).add_to(m)

folium.LayerControl().add_to(m)

display(m)

# %% Holevatn

holevatn_shape = magasin_data[magasin_data.magNavn == "HOLEVATN"].geometry.item()
display(holevatn_shape)