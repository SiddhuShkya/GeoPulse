# pages/02_fetch_satellite_data.py
import streamlit as st
import ee
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from shapely.geometry import shape, mapping
from dotenv import load_dotenv
import os
import json

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()


def configure_page():
    st.set_page_config(
        page_title="Satellite Data Fetcher",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("🛰️ Fetch Satellite Imagery Using AOI")
    st.write("---")


# ----------------------------
# Initialize Earth Engine
def init_ee():
    if "ee_initialized" not in st.session_state:
        try:
            project_id = os.getenv("PROJECT_ID")  # Load from .env
            service_account = os.getenv(
                "SERVICE_ACCOUNT"
            )  # Optional, if using service account

            if service_account and os.path.exists("geopulse-key.json"):
                # Use service account credentials
                credentials = ee.ServiceAccountCredentials(
                    service_account, "geopulse-key.json"
                )
                ee.Initialize(credentials, project=project_id)
            else:
                # Use default personal Earth Engine account
                ee.Initialize(project=project_id)

        except Exception:
            # Interactive login fallback
            ee.Authenticate()
            ee.Initialize(project=os.getenv("project_id"))

        st.session_state.ee_initialized = True


# ----------------------------
# EE helper functions
# ----------------------------
def mask_s2_clouds(image):
    scl = image.select("SCL")
    mask = scl.neq(3).And(scl.neq(8))
    return image.updateMask(mask)


def add_ndvi(image):
    return image.addBands(image.normalizedDifference(["B8", "B4"]).rename("NDVI"))


def median_ndvi(aoi, start, end, max_cloud=20):
    col = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(aoi)
        .filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", max_cloud))
        .map(mask_s2_clouds)
        .map(add_ndvi)
    )
    median = col.select("NDVI").median()
    return median


def vectorize_delta(delta_img, aoi, threshold, min_area_m2=500):
    binary = delta_img.lte(threshold)
    vectors = binary.changeProj(
        delta_img.projection(), ee.Projection("EPSG:4326")
    ).reduceToVectors(
        geometry=aoi,
        scale=30,
        geometryType="polygon",
        eightConnected=False,
        labelProperty="change",
        reducer=None,
    )
    feat_list = vectors.getInfo().get("features", [])
    geoms = []
    for feat in feat_list:
        geom = feat.get("geometry")
        props = feat.get("properties", {})
        geoms.append({"type": "Feature", "geometry": geom, "properties": props})
    return {"type": "FeatureCollection", "features": geoms}


def gc_to_gdf(fc):
    gdf = gpd.GeoDataFrame.from_features(fc)
    if gdf.empty:
        return gdf
    gdf = gdf.set_crs(epsg=4326, allow_override=True)
    gdf["area_m2"] = gdf.to_crs(epsg=3857).geometry.area
    return gdf


def render_aoi_map(
    aoi_json: dict, width: int = 1200, height: int = 800, map_type: str = "standard"
):
    gdf = gpd.GeoDataFrame.from_features(aoi_json["features"])
    centroid = gdf.geometry.centroid.iloc[0]
    # Initialize map without tiles
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=8, tiles=None)
    # Add the selected base layer
    if map_type.lower() == "satellite":
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Tiles © Esri & Maxar",
            name="Satellite",
            overlay=False,
            control=False,
        ).add_to(m)
    else:  # default OpenStreetMap
        folium.TileLayer(
            "OpenStreetMap", name="OSM", overlay=False, control=True
        ).add_to(m)

    # Add AOI polygon
    folium.GeoJson(
        aoi_json,
        name="AOI",
        style_function=lambda x: {
            "color": "#FF2D2D",
            "weight": 3,
            "opacity": 0.7,
        },
    ).add_to(m)

    # Layer control to allow switching layers if needed
    folium.LayerControl(collapsed=False).add_to(m)

    # Hide attribution (optional)
    st.markdown(
        """
        <style>
            .leaflet-control-attribution {display:none !important;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st_folium(m, width=width, height=height)


# ----------------------------
# Streamlit App
# ----------------------------
def main():
    configure_page()
    col1, col2 = st.columns([4, 5], gap="small")
    with col1:
        with st.container(border=True):
            uploaded_file = st.file_uploader("Upload aoi.geojson", type=["geojson"])
        if uploaded_file:
            geojson_data = json.load(uploaded_file)
            with st.container(border=True, height=880):
                render_aoi_map(aoi_json=geojson_data)  # Just call it, don't return
    # if uploaded_file:
    #     # Initialize EE first
    #     init_ee()
    #     geojson_data = json.load(uploaded_file)
    #     st.success("AOI loaded successfully!")
    #     # Convert to ee.Geometry
    #     geom = ee.Geometry(
    #         geojson_data["geometry"]
    #         if geojson_data.get("type") == "Feature"
    #         else geojson_data
    #     )

    #     # Date selection
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         start_date = st.date_input("Start date")
    #     with col2:
    #         end_date = st.date_input("End date")

    #     if st.button("Fetch NDVI Median"):
    #         st.info("Fetching data from Google Earth Engine. Please wait...")
    #         try:
    #             init_ee()
    #             median_image = median_ndvi(geom, str(start_date), str(end_date))
    #             # Export or get info
    #             url = median_image.getThumbURL(
    #                 {"min": 0, "max": 1, "palette": ["red", "yellow", "green"]}
    #             )
    #             st.image(url, caption="Median NDVI")
    #             st.success("NDVI fetched successfully!")
    #         except Exception as e:
    #             st.error(f"Error fetching data: {e}")

    #     st.markdown("### Uploaded AOI GeoJSON")
    #     st.json(geojson_data)


if __name__ == "__main__":
    main()
