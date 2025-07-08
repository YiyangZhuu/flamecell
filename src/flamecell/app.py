"""
Streamlit app for interactive forest fire simulation (FlameCell).

This app allows users to:
- Select a region in Germany on an interactive map.
- Generate a simulation grid from raster data.
- Set environmental parameters (wind, humidity, temperature).
- Start a fire by clicking on the grid.
- Run and visualize a step-by-step cellular automaton fire spread simulation.
- View a risk map based on simulation results.

Requirements:
- rasterio, folium, numpy, streamlit, streamlit-folium, streamlit-image-coordinates
"""

import streamlit as st
from streamlit_folium import st_folium
from streamlit_image_coordinates import streamlit_image_coordinates
import folium
import rasterio
import os
import numpy as np
import sys
sys.path.append("../src")
from flamecell.sim_utils import *


def main():
    st.title("FlameCell Forest Fire Simulator: Select Area by Zoom/Pan")

    # Load raster
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TIF_PATH = os.path.join(BASE_DIR, 'data', 'DE_10m_3035_tiled.tif')

    with rasterio.open(TIF_PATH) as src:
        m = folium.Map(location=[51.1657, 10.4515], zoom_start=6)
        map_data = st_folium(m, width=700, height=700)

        bounds = map_data.get("bounds")
        if not bounds:
            st.warning("Waiting for map bounds...")
            return

        south = bounds['_southWest']['lat']
        west = bounds['_southWest']['lng']
        north = bounds['_northEast']['lat']
        east = bounds['_northEast']['lng']

        st.sidebar.write("Bounds:")
        st.sidebar.write(f"South={south}, West={west}, North={north}, East={east}")

        # Resolution
        resolution = st.sidebar.selectbox("Resolution", [128, 256, 512, 1024, "Custom"], index=0)
        if resolution == "Custom":
            resolution = st.sidebar.number_input("Enter custom resolution", min_value=10, max_value=2000, value=256)

        # Wind
        wind_source = st.sidebar.selectbox("Wind", ["Current", "Custom"])
        if wind_source == "Current":
            wspd, wdir = get_current_wind((south + north) / 2, (west + east) / 2)
            st.sidebar.write(f"Current wind speed: {wspd} km/h")
            st.sidebar.write(f"Direction: {wdir}°")
        else:
            wdir = st.sidebar.number_input("Custom wind direction", min_value=0, max_value=360, value=0)
            wspd = st.sidebar.number_input("Custom wind speed", min_value=0, value=0)

        wind = np.array([
            wspd * np.cos(np.radians(wdir)),
            wspd * np.sin(np.radians(wdir))
        ])

        # Humidity
        humidity_source = st.sidebar.selectbox("Humidity", ["Current", "Custom"])
        if humidity_source == "Current":
            rel_humi = get_current_humidity((south + north) / 2, (west + east) / 2)
            st.sidebar.write(f"Humidity: {rel_humi}%")
        else:
            rel_humi = st.sidebar.number_input("Custom humidity %", min_value=0, max_value=100, value=40)

        # Temperature
        temperature_source = st.sidebar.selectbox("Temperature", ["Current", "Custom"])
        if temperature_source == "Current":
            temp = get_current_temperature((south + north) / 2, (west + east) / 2)
            st.sidebar.write(f"Temperature: {temp}°C")
        else:
            temp = st.sidebar.number_input("Custom temperature", min_value=0, max_value=100, value=20)

        # Session state setup
        for key in ["grid", "img", "data", "sim"]:
            if key not in st.session_state:
                st.session_state[key] = None

        if st.sidebar.button("Generate Grid"):
            st.session_state.data, transform = crop_and_resample(src, bounds, output_size=(resolution, resolution))
            st.session_state.grid = raster_to_grid(st.session_state.data[0])
            st.session_state.img = grid_to_img(st.session_state.grid)
            st.rerun()

        if st.sidebar.button("Reset"):
            st.session_state.grid = raster_to_grid(st.session_state.data[0])
            st.session_state.img = grid_to_img(st.session_state.grid)
            st.rerun()

        if st.session_state.img is not None:
            st.subheader("Click to set fire")
            coords = streamlit_image_coordinates(st.session_state.img, width=512, key="set_fire")
            if coords:
                frac = resolution / coords["width"]
                fire_source = (round(coords["x"] * frac), round(coords["y"] * frac))
                if st.session_state.grid.state[fire_source[1], fire_source[0]] in ["TREE", "GRASS"]:
                    st.session_state.grid.state[fire_source[1], fire_source[0]] = "FIRE"
                    st.session_state.img = grid_to_img(st.session_state.grid)
                    st.rerun()

        # Run simulation
        prob = st.sidebar.slider("Ignition Probability per Neighbor", 0.0, 1.0, 0.2, 0.01)

        if st.sidebar.button("Run Simulation"):
            ruleset = RuleSet()
            ruleset.add_rule(burning)
            ruleset.add_rule(ignite)

            sim = Simulation(st.session_state.grid, ruleset)
            sim.max_steps = resolution
            st.session_state.sim = sim

            plot_area = st.empty()
            while sim.step_count < sim.max_steps:
                sim.step(prob=prob, humidity=rel_humi, wind=wind, temp=temp)
                fig = plot_grid(st.session_state.grid)
                plot_area.pyplot(fig, use_container_width=True)

            risk_fig = plot_risk_map(sim)
            plot_area.pyplot(risk_fig, use_container_width=True)


if __name__ == "__main__":
    main()
