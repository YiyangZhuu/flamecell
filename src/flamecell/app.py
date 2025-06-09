import streamlit as st
from streamlit_folium import st_folium
from streamlit_image_coordinates import streamlit_image_coordinates
import folium
import rasterio
from rasterio.windows import from_bounds
from rasterio.enums import Resampling
from rasterio.warp import transform_bounds
import numpy as np

from sim_utils import *
from flamecell import *

# Path to data map
TIF_PATH = "maps\DE_10m_3035_tiled.tif"

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
        resampling=Resampling.nearest,
    )
    return data, transform

def normalize(arr):
    arr = arr.astype('float32')
    arr -= arr.min()
    arr /= arr.max()
    arr *= 255
    return arr.astype('uint8')


# --- Streamlit app ---
st.title("FlameCell Forest Fire Simulator: Select Area by Zoom/Pan")

# Load big TIF map
tif_path = "maps/DE_10m_3035_tiled.tif"  

st.sidebar.header("Select Area of Interest")
resolution = st.sidebar.selectbox("Resolution", [128, 256, 512, 1024], index=0)

with rasterio.open(tif_path) as src:
    # Initial map centered on Germany
    m = folium.Map(location=[51.1657, 10.4515], zoom_start=6)

    # Display interactive map with folium and streamlit-folium
    map_data = st_folium(m, width=700, height=700)

    bounds = map_data.get("bounds")
    # Get visible bounds from map
    south = bounds['_southWest']['lat']
    west = bounds['_southWest']['lng']
    north = bounds['_northEast']['lat']
    east = bounds['_northEast']['lng']

    st.sidebar.write(f"Bounds: South={south}, West={west}, North={north}, East={east}")

    if 'grid' not in st.session_state:
        st.session_state.grid = None
    if 'img' not in st.session_state:
        st.session_state.img = None
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'ruleset' not in st.session_state:
        st.session_state.ruleset = None
    if 'sim' not in st.session_state:
        st.session_state.sim = None

    if st.sidebar.button("Generate Grid"):
        # Crop and resample the raster grid
        st.session_state.data, transform = crop_and_resample(src, bounds, output_size=(resolution, resolution))
        # Convert the raster to simulation grid
        st.session_state.grid = raster_to_grid(st.session_state.data[0])
        st.session_state.img = grid_to_img(st.session_state.grid)
        st.rerun()
    
    if st.sidebar.button("Reset"):
        st.session_state.grid = raster_to_grid(st.session_state.data[0])
        st.session_state.img = grid_to_img(st.session_state.grid)
        st.rerun()
        
        # Show the image and let user click to set fire
    if st.session_state.img is not None:
        st.subheader("Click to set fire")
        coords = streamlit_image_coordinates(st.session_state.img, width=512, key="set_fire")
        
    # calculate the fire source on the grid    
    if coords is not None:
        frac = resolution / coords["width"]
        fire_source = (round(coords["x"] * frac), round(coords["y"] * frac))
        
        if st.session_state.grid.cells[fire_source[1], fire_source[0]].state == "TREE" or st.session_state.grid.cells[fire_source[0], fire_source[1]].state == "GRASS":
            st.session_state.grid.cells[fire_source[1], fire_source[0]].state = "FIRE"
            st.session_state.img = grid_to_img(st.session_state.grid)
            st.rerun()

    if st.sidebar.button("Step Simulation"):
        st.session_state.ruleset = RuleSet()
        st.session_state.ruleset.add_rule(ignite_if_neighbor_burning)
        st.session_state.ruleset.add_rule(burning)
        st.session_state.sim = Simulation(st.session_state.grid, st.session_state.ruleset)
        st.session_state.sim.max_steps = resolution
        for _ in range(st.session_state.sim.max_steps):
            st.write(_)
            st.session_state.sim.step()
            st.session_state.img = grid_to_img(st.session_state.grid)
            st.rerun()


        