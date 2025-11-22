# 🌍 GeoPulse

**GeoPulse** is an open-source, real-time satellite monitoring and environmental change detection system.  
It automates the ingestion, processing, and analysis of Landsat and other satellite imagery to track vegetation health, surface temperature, and urban growth.

---

## 🚀 Key Features

- **📍 Interactive Map:**  
  Search for locations, draw polygons, and create Area of Interest (AOI) files. Supports GeoJSON, KML, KMZ, and Shapefile formats.

- **🛰️ Satellite Data Fetching:**  
  Fetch satellite imagery from Google Earth Engine (Sentinel-2 and Landsat-8) with cloud filtering and date range selection.

- **📡 Automated Data Pipeline:**  
  Scheduled ingestion from Google Earth Engine.

- **🧮 Index Computation:**  
  Calculates NDVI, NDWI, NDBI, and LST indices.

- **📊 Interactive Dashboards:**  
  Flask-based web interface with interactive maps and real-time data visualization.

---

## 🧰 Tech Stack

| Layer | Tools |
|-------|-------|
| **Backend** | Flask |
| **Frontend** | HTML, CSS, JavaScript, Bootstrap, Leaflet |
| **Mapping** | Leaflet.js, Folium |
| **Satellite Data** | Google Earth Engine API |
| **Geospatial** | GeoPandas, Shapely, Fiona |
| **File Formats** | GeoJSON, KML, KMZ, Shapefile |

---

## 📋 Prerequisites

- Python 3.8+
- Google Earth Engine account (sign up at https://earthengine.google.com/)
- Google Cloud Project with Earth Engine API enabled
- Service account key file (optional, for server authentication)

---

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd GeoPulse
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google Earth Engine:**

   **Option A: Interactive Authentication (Recommended for development)**
   ```bash
   earthengine authenticate
   ```
   This will open a browser for authentication. After authentication, create a `.env` file:
   ```env
   PROJECT_ID=your-google-cloud-project-id
   SECRET_KEY=your-secret-key-for-flask-sessions
   ```

   **Option B: Service Account (Recommended for production)**
   - Create a service account in Google Cloud Console
   - Download the service account key JSON file
   - Rename it to `geopulse-key.json` and place it in the project root
   - Create a `.env` file:
     ```env
     PROJECT_ID=your-google-cloud-project-id
     SERVICE_ACCOUNT=your-service-account@project-id.iam.gserviceaccount.com
     SECRET_KEY=your-secret-key-for-flask-sessions
     ```
   - Make sure the service account has the "Earth Engine User" role

   **Note:** The PROJECT_ID should be your full Google Cloud Project ID (e.g., `my-project-123456`), not just the project name.

5. **Create necessary directories:**
   ```bash
   mkdir -p data/uploads data/AOIs data/satellite_images
   ```

6. **Verify Earth Engine setup:**
   ```bash
   python -c "import ee; ee.Initialize(); print('✅ Earth Engine initialized successfully')"
   ```

---

## 🚀 Running the Application

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **Open your browser:**
   Navigate to `http://localhost:5000`

3. **Use the application:**
   - **Interactive Map:** Draw polygons or upload AOI files to create and download GeoJSON files
   - **Fetch Satellite Data:** Upload an AOI, configure date range and cloud coverage, then fetch satellite imagery

---

## 📖 Usage

### Interactive Map
1. Go to "📍 Interactive Map"
2. Search for a location or upload an AOI file
3. Draw a polygon on the map or use the uploaded AOI
4. Download the AOI as a GeoJSON file

### Fetch Satellite Data
1. Go to "🛰️ Fetch Satellite Data"
2. Upload an AOI file (GeoJSON, KML, KMZ, or Shapefile ZIP)
3. Configure:
   - Start and end dates
   - Maximum cloud coverage percentage
   - Satellite type (Sentinel-2 or Landsat-8)
4. Click "🚀 Fetch GeoTIFFs"
5. Check the `data/satellite_images/` folder for downloaded images

---

## ⚙️ Use Cases

- 🌿 Vegetation health tracking (NDVI)
- 🌆 Urban expansion monitoring (NDBI)
- ☀️ Surface temperature trend analysis (LST)
- 🔄 Temporal change detection between scenes
- 🗺️ Area of Interest (AOI) management

---

## 📦 Project Structure

```
GeoPulse/
├── app.py                 # Main Flask application
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── interactive_map.html
│   └── fetch_satellite_data.html
├── static/                # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── interactive_map.js
│       └── fetch_satellite_data.js
├── data/                  # Data directories
│   ├── uploads/           # Temporary uploads
│   ├── AOIs/              # Saved AOI files
│   └── satellite_images/   # Downloaded satellite images
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

---

## 🔧 Configuration

The application uses environment variables for configuration. Create a `.env` file with:

- `PROJECT_ID`: Your Google Cloud Project ID (required for service account auth, optional for interactive auth)
- `SERVICE_ACCOUNT`: Service account email (optional, only needed if using service account)
- `SECRET_KEY`: Flask session secret key (required)

### Troubleshooting Earth Engine Issues

If you see errors like "Invalid URL" or "Caller does not have required permission":

1. **For interactive authentication:**
   ```bash
   earthengine authenticate
   ```
   Then restart the app.

2. **For service account:**
   - Verify `geopulse-key.json` exists and is valid
   - Check that SERVICE_ACCOUNT matches the email in the key file
   - Ensure the service account has "Earth Engine User" role
   - Verify PROJECT_ID is correct (full project ID, not just name)

3. **Check Earth Engine API is enabled:**
   - Go to Google Cloud Console
   - Enable "Earth Engine API" for your project

The app will still run even if Earth Engine isn't initialized, but satellite data fetching will be disabled.

---

## 📝 Notes

- Satellite data fetching runs in the background and may take several minutes
- Downloaded images are organized by satellite type, year, and month
- The application supports multiple AOI file formats for maximum flexibility

---