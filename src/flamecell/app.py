import streamlit as st
from streamlit_folium import st_folium
from streamlit_image_coordinates import streamlit_image_coordinates
import folium
import rasterio
import os
from flamecell.sim_utils import *


# Path to data map
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # directory of current script
TIF_PATH = os.path.join(BASE_DIR, 'data', 'DE_10m_3035_tiled.tif')


# --- Streamlit app ---
st.title("FlameCell Forest Fire Simulator: Select Area by Zoom/Pan")

with rasterio.open(TIF_PATH) as src:
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

    st.sidebar.write(f"Bounds:")
    st.sidebar.write(f"South={south}, West={west}, North={north}, East={east}")

    # desired resolution for the grid
    resolution = st.sidebar.selectbox("Resolution", [128, 256, 512, 1024, "Custom"], index=0)
    if resolution == "Custom":
        resolution = st.sidebar.number_input("Enter custom resolution", min_value=10, max_value=2000, value=256, step=1)

    # access to the current weather data
    # set weather data source
    wind_source = st.sidebar.selectbox("Wind", ["Current", "Custom"])
    
    if wind_source == "Current":
        wspd, wdir = get_current_wind((south+north)/2, (west+east)/2)
        st.sidebar.write(f"Current wind speed: {wspd} km/h")
        st.sidebar.write(f"Current wind direction: {wdir} Degree")
    if wind_source == "Custom":
        wdir = st.sidebar.number_input("Enter custom wind direction", min_value=0, max_value=360, value=0)
        wspd = st.sidebar.number_input("Enter custom wind speed", min_value=0, value=0)
    cell_length = abs(south-north) * 111.32 / resolution
    wind = np.array([wspd*np.cos(np.radians(wdir)), wspd*np.sin(np.radians(wdir))])

    humidity_source = st.sidebar.selectbox("Humidity", ["Current", "Custom"])
    if humidity_source == "Current":
        rel_humi = get_current_humidity((south+north)/2, (west+east)/2)
        st.sidebar.write(f"Current relative humidity: {rel_humi} %")
    if humidity_source == "Custom":
        rel_humi = st.sidebar.number_input("Enter custom relative humidity %", min_value=0, max_value=100, value=0)

    temperature_source = st.sidebar.selectbox("Temperature", ["Current", "Custom"])
    if temperature_source == "Current":
        temp = get_current_temperature((south+north)/2, (west+east)/2)
        st.sidebar.write(f"Current temperature: {temp}°C")
    if temperature_source == "Custom":
        temp = st.sidebar.number_input("Enter custom temperature", min_value=0, max_value=100, value=0)
    

    if 'grid' not in st.session_state:
        st.session_state.grid = None
    if 'img' not in st.session_state:
        st.session_state.img = None
    if 'data' not in st.session_state:
        st.session_state.data = None
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
        
        if st.session_state.grid.state[fire_source[1], fire_source[0]] in ["TREE", "GRASS"]:
            st.session_state.grid.state[fire_source[1], fire_source[0]] = "FIRE"
            st.session_state.img = grid_to_img(st.session_state.grid)
            st.rerun()

    st.sidebar.write("Choose Parameters")
    prob = st.sidebar.slider("Ignition Probability per Neighbor on fire", min_value=0.0, max_value=1.0, value=0.2, step=0.01)

    if st.sidebar.button("Run Simulation"):
        ruleset = RuleSet()
        ruleset.add_rule(burning)
        ruleset.add_rule(ignite)
        #ruleset.add_rule(ignite1)

        # Reuse existing grid (assumed to have fire source already set)
        sim = Simulation(st.session_state.grid, ruleset)
        sim.max_steps = resolution
        st.session_state.sim

        # Create a placeholder for dynamic plot
        plot_area = st.empty()

        # Run and update
        while sim.step_count < sim.max_steps:
            sim.step(prob=prob, humidity=rel_humi, wind=wind, temp=temp)
            fig = plot_grid(st.session_state.grid)
            plot_area.pyplot(fig, use_container_width=True)
            # time.sleep(0.1)  # optional: slow down to see progress
        
        # plot risk map
        risk_fig = plot_risk_map(sim)
        plot_area.pyplot(risk_fig, use_container_width=True)


        