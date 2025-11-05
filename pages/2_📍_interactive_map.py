import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import json
from geopy.geocoders import Nominatim  # type: ignore
import os


# ----------------------------
# Configuration
# ----------------------------
def configure_page():
    st.set_page_config(
        page_title="Interactive AOI Map",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("📍 Interactive AOI Selector & Downloader")
    st.caption(
        "Search for a location (e.g., Kathmandu) or draw a polygon on the map to select your AOI. "
        "The map will automatically navigate to the searched location. "
        "Once done, the AOI will appear on the right side and you can download it as a GeoJSON file."
    )
    st.write("---")


# ----------------------------
# Search Location
# ----------------------------
def search_location(default_lat=28.3949, default_lon=84.1240):
    location_name = st.text_input("Search Location:", "")
    if location_name:
        geolocator = Nominatim(user_agent="geo_pulse_app")
        location = geolocator.geocode(location_name)
        if location:
            return location.latitude, location.longitude
        else:
            st.warning("Location not found. Showing default map.")
    return default_lat, default_lon


# ----------------------------
# Create Map
# ----------------------------
def create_map(center_lat, center_lon, zoom_start=12):
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start)
    draw = Draw(
        export=False,
        draw_options={
            "polyline": False,
            "rectangle": False,
            "circle": False,
            "marker": False,
            "circlemarker": False,
        },
        edit_options={"edit": True},
    )
    draw.add_to(m)
    return m


# ----------------------------
# Display Map
# ----------------------------
def display_map(m, width=2000, height=900):
    return st_folium(m, width=width, height=height, returned_objects=["all_drawings"])


# ----------------------------
# Process AOI and Return GeoJSON
# ----------------------------
def process_aoi(output):
    if output and "all_drawings" in output and output["all_drawings"]:
        geometry = output["all_drawings"][0]["geometry"]

        # Wrap geometry into a FeatureCollection
        feature_collection = {
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "properties": {}, "geometry": geometry}],
        }
        return feature_collection
    return None


# ----------------------------
# Main App
# ----------------------------
def main():
    configure_page()
    col1, col2 = st.columns([7.5, 2.5], gap="small")

    with col1:
        # Get center coordinates from search
        center_lat, center_lon = search_location()
        # Create and display map at that location
        m = create_map(center_lat, center_lon)
        with st.container(border=True):
            output = display_map(m)
        geojson_data = process_aoi(output)

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("aoi.geojson")
        if geojson_data:
            with st.container(border=True, height=880):
                st.json(geojson_data)
            # Download button and save to project directory
            if st.download_button(
                label="Download AOI GeoJSON",
                data=json.dumps(geojson_data, indent=4),
                file_name="aoi.geojson",
                mime="application/json",
            ):
                os.makedirs("data", exist_ok=True)
                with open("data/aoi.geojson", "w") as f:
                    json.dump(geojson_data, f, indent=4)
                st.success("AOI saved as 'data/aoi.geojson' ✅")
        else:
            st.info("Draw a polygon on the map to see AOI here.")


if __name__ == "__main__":
    main()
