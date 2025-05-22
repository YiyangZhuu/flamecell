import streamlit as st
from streamlit_folium import st_folium
import folium
import rasterio
from rasterio.windows import from_bounds
from rasterio.enums import Resampling
from rasterio.warp import transform_bounds
import numpy as np
import matplotlib.pyplot as plt

TIF_PATH = "maps\DE_10m_3035_tiled.tif"

@st.cache_resource
def load_raster():
    return rasterio.open(TIF_PATH)

def crop_and_resample(src, bounds, output_size=(128, 128)):
    """Crop raster to bounds and resample to output_size (width, height)."""
    south = bounds['_southWest']['lat']
    west = bounds['_southWest']['lng']
    north = bounds['_northEast']['lat']
    east = bounds['_northEast']['lng']

    src_crs = src.crs  # Get CRS from the raster dataset
    bounds_projected = transform_bounds('EPSG:4326', src_crs, west, south, east, north)
    # Create window from bounds
    window = from_bounds(*bounds_projected, transform=src.transform)

    # Calculate the transform and shape of the windowed output
    transform = src.window_transform(window)
    
    # Read and resample the data in the window
    data = src.read(
        window=window,
        out_shape=(
            src.count,  # number of bands
            output_size[1],  # height
            output_size[0]   # width
        ),
        resampling=Resampling.bilinear,
    )
    return data, transform

def plot_raster(data):
    """Plot RGB or grayscale raster and return matplotlib figure."""
    if data.shape[0] >= 3:
        img = np.dstack([data[0], data[1], data[2]])
    else:
        img = data[0]

    fig, ax = plt.subplots(figsize=(6,6))
    ax.imshow(img)
    ax.axis('off')
    return fig

# --- Streamlit app ---
st.title("FlameCell Forest Fire Simulator: Select Area by Zoom/Pan")

# Load big TIF map
tif_path = "maps/DE_10m_3035_tiled.tif"  

st.sidebar.header("Select Area of Interest")
resolution = st.sidebar.selectbox("Resolution", [128, 256, 512, 1024], index=2)

with rasterio.open(tif_path) as src:
    # Initial map centered on Germany
    m = folium.Map(location=[51.1657, 10.4515], zoom_start=6)

    # Display interactive map with folium and streamlit-folium
    map_data = st_folium(m, width=700, height=500)

    bounds = map_data.get("bounds")
    # Get visible bounds from map
    south = bounds['_southWest']['lat']
    west = bounds['_southWest']['lng']
    north = bounds['_northEast']['lat']
    east = bounds['_northEast']['lng']

    st.write(f"Bounds: South={south}, West={west}, North={north}, East={east}")

    if st.button("Run simulation (crop and resample)"):
        # Crop and resample the raster to 300x300 grid
        data, transform = crop_and_resample(src, bounds, output_size=(resolution, resolution))

        # Show cropped raster image
        fig = plot_raster(data)
        st.pyplot(fig)