import os
import json
import ee
import tempfile
import zipfile
import requests
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
from fastkml import kml
import fiona
from shapely.geometry import mapping, shape
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
import threading

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
app.config['UPLOAD_FOLDER'] = 'data/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'geojson', 'kml', 'kmz', 'zip'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data/AOIs', exist_ok=True)
os.makedirs('data/satellite_images', exist_ok=True)

# Global flag to track Earth Engine initialization status
EE_INITIALIZED = False

# Global dictionary to store background tasks
TASKS = {}

# Initialize Earth Engine
def init_ee():
    global EE_INITIALIZED
    project_id = os.getenv("PROJECT_ID")
    service_account = os.getenv("SERVICE_ACCOUNT")
    
    # Try service account authentication first
    if service_account and os.path.exists("geopulse-key.json"):
        try:
            credentials = ee.ServiceAccountCredentials(
                service_account, "geopulse-key.json"
            )
            if project_id:
                ee.Initialize(credentials, project=project_id)
            else:
                ee.Initialize(credentials)
            EE_INITIALIZED = True
            print("✅ Earth Engine initialized with service account")
            return True
        except Exception as e:
            print(f"⚠️  Service account authentication failed: {e}")
    
    # Try with project ID only (for user authentication)
    if project_id:
        try:
            # Check if already initialized
            try:
                ee.Number(0).getInfo()
                EE_INITIALIZED = True
                print("✅ Earth Engine already initialized")
                return True
            except:
                pass
            
            # Try to initialize with project
            ee.Initialize(project=project_id)
            EE_INITIALIZED = True
            print(f"✅ Earth Engine initialized with project ID: {project_id}")
            return True
        except Exception as e:
            print(f"⚠️  Project ID initialization failed: {e}")
            print("💡 Trying interactive authentication...")
    
    # Try interactive authentication as last resort
    try:
        # Check if already initialized
        try:
            ee.Number(0).getInfo()
            EE_INITIALIZED = True
            print("✅ Earth Engine already initialized")
            return True
        except:
            pass
        
        print("⚠️  Attempting interactive authentication...")
        print("💡 If this fails, run 'earthengine authenticate' in your terminal first")
        ee.Authenticate()
        ee.Initialize()
        EE_INITIALIZED = True
        print("✅ Earth Engine initialized with interactive authentication")
        return True
    except Exception as e:
        print(f"❌ Earth Engine initialization failed: {e}")
        print("\n" + "="*60)
        print("⚠️  EARTH ENGINE NOT INITIALIZED")
        print("="*60)
        print("The app will run, but satellite data fetching will not work.")
        print("\nTo fix this:")
        print("1. Run 'earthengine authenticate' in your terminal")
        print("2. Or set up a service account with geopulse-key.json")
        print("3. Or set PROJECT_ID in your .env file")
        print("="*60 + "\n")
        EE_INITIALIZED = False
        return False

# Initialize on startup
init_ee()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def load_geojson(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def load_kml(file_path):
    k = kml.KML()
    with open(file_path, 'rb') as f:
        k.from_string(f.read().decode("utf-8"))

    features = []
    for doc in k.features():
        for folder in doc.features():
            for f in folder.features():
                geom = mapping(f.geometry)
                features.append({
                    "type": "Feature",
                    "properties": {},
                    "geometry": geom
                })

    return {
        "type": "FeatureCollection",
        "features": features
    }

def load_kmz(file_path):
    with zipfile.ZipFile(file_path, 'r') as kmz:
        kml_filename = [f for f in kmz.namelist() if f.endswith(".kml")][0]
        kml_content = kmz.read(kml_filename).decode("utf-8")

    k = kml.KML()
    k.from_string(kml_content)

    features = []
    for doc in k.features():
        for folder in doc.features():
            for f in folder.features():
                geom = mapping(f.geometry)
                features.append({
                    "type": "Feature",
                    "properties": {},
                    "geometry": geom
                })

    return {
        "type": "FeatureCollection",
        "features": features
    }

def load_shapefile_zip(file_path):
    features = []
    with fiona.open(file_path) as shp:
        for feat in shp:
            features.append({
                "type": "Feature",
                "properties": feat["properties"],
                "geometry": feat["geometry"],
            })

    return {
        "type": "FeatureCollection",
        "features": features
    }

def load_aoi_file(file_path, filename):
    ext = filename.rsplit('.', 1)[1].lower()

    if ext == "geojson":
        return load_geojson(file_path)
    elif ext == "kml":
        return load_kml(file_path)
    elif ext == "kmz":
        return load_kmz(file_path)
    elif ext == "zip":
        return load_shapefile_zip(file_path)
    
    return None

def mask_s2_clouds(image):
    scl = image.select("SCL")
    mask = scl.neq(3).And(scl.neq(8))
    return image.updateMask(mask)

def mask_l8_clouds(image):
    # Landsat-8 Collection 2 uses QA_PIXEL band
    qa = image.select('QA_PIXEL')
    # Bits 3 and 4 are cloud and cloud shadow
    cloud_mask = qa.bitwiseAnd(1 << 3).eq(0).And(qa.bitwiseAnd(1 << 4).eq(0))
    return image.updateMask(cloud_mask)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/interactive_map')
def interactive_map():
    return render_template('interactive_map.html')

@app.route('/fetch_satellite_data')
def fetch_satellite_data():
    return render_template('fetch_satellite_data.html')

@app.route('/api/ee_status', methods=['GET'])
def ee_status():
    """Check Earth Engine initialization status"""
    global EE_INITIALIZED
    if EE_INITIALIZED:
        try:
            # Test if EE is actually working
            ee.Number(0).getInfo()
            return jsonify({'initialized': True, 'status': 'ready'})
        except:
            EE_INITIALIZED = False
            return jsonify({'initialized': False, 'status': 'error'})
    return jsonify({'initialized': False, 'status': 'not_configured'})

@app.route('/api/search_location', methods=['POST'])
def search_location():
    data = request.json
    location_name = data.get('location', '')
    
    if not location_name:
        return jsonify({'error': 'Location name required'}), 400
    
    try:
        geolocator = Nominatim(user_agent="geo_pulse_app")
        location = geolocator.geocode(location_name, timeout=10)
        if location:
            return jsonify({
                'lat': location.latitude,
                'lon': location.longitude
            })
        else:
            return jsonify({'error': 'Location not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload_aoi', methods=['POST'])
def upload_aoi():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            geojson_data = load_aoi_file(file_path, filename)
            if geojson_data:
                # Save to AOIs folder
                aoi_filename = f"aoi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.geojson"
                aoi_path = os.path.join('data/AOIs', aoi_filename)
                with open(aoi_path, 'w') as f:
                    json.dump(geojson_data, f, indent=4)
                
                # Clean up uploaded file
                os.remove(file_path)
                
                return jsonify({
                    'success': True,
                    'geojson': geojson_data,
                    'filename': aoi_filename
                })
            else:
                return jsonify({'error': 'Failed to parse file'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/download_aoi', methods=['POST'])
def download_aoi():
    data = request.json
    geojson_data = data.get('geojson')
    
    if not geojson_data:
        return jsonify({'error': 'No GeoJSON data provided'}), 400
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.geojson', mode='w')
    json.dump(geojson_data, temp_file, indent=4)
    temp_file.close()
    
    return send_file(
        temp_file.name,
        as_attachment=True,
        download_name='aoi.geojson',
        mimetype='application/json'
    )

def remove_z_coordinates(geometry):
    """Recursively remove Z coordinates from geometry coordinates."""
    if 'coordinates' in geometry:
        geometry['coordinates'] = _remove_z_recurse(geometry['coordinates'])
    return geometry

def _remove_z_recurse(coords):
    if not coords:
        return coords
    
    # Check if this is a coordinate point (list of numbers)
    if isinstance(coords[0], (int, float)):
        return coords[:2]  # Keep only x, y
    
    # Otherwise, it's a list of lists (or list of list of lists...)
    return [_remove_z_recurse(c) for c in coords]

@app.route('/api/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = TASKS.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task)

@app.route('/api/fetch_satellite_data', methods=['POST'])
def fetch_satellite_data_api():
    global EE_INITIALIZED
    
    if not EE_INITIALIZED:
        return jsonify({
            'error': 'Earth Engine is not initialized. Please configure Google Earth Engine authentication first.'
        }), 503
    
    data = request.json
    geojson_data = data.get('geojson')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    cloud_coverage = data.get('cloud_coverage', 20)
    satellite = data.get('satellite', 'Sentinel-2')
    
    if not all([geojson_data, start_date, end_date]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        # Parse geometry
        if geojson_data["type"] == "FeatureCollection":
            geom_dict = geojson_data["features"][0]["geometry"]
        else:
            geom_dict = geojson_data["geometry"]
            
        # Sanitize geometry (remove Z coordinates if present)
        geom_dict = remove_z_coordinates(geom_dict)
        
        geom = ee.Geometry(geom_dict)
        
        geom = geom.simplify(100)
        
        # Create task
        task_id = str(uuid.uuid4())
        TASKS[task_id] = {
            'status': 'processing',
            'progress': 0,
            'message': 'Initializing...',
            'details': 'Starting download process'
        }
        
        # Start fetching in background thread
        thread = threading.Thread(
            target=fetch_satellite_images,
            args=(geom, start_date, end_date, cloud_coverage, satellite, task_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Satellite data fetching started.'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def fetch_satellite_images(geom, start_date, end_date, cloud_coverage, satellite, task_id):
    try:
        TASKS[task_id]['message'] = 'Searching for images...'
        TASKS[task_id]['progress'] = 5
        if satellite == 'Sentinel-2':
            collection_name = "COPERNICUS/S2_SR_HARMONIZED"
            mask_func = mask_s2_clouds
            bands = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B9", "B11", "B12"]
            prefix = "S2"
        elif satellite == 'Landsat-8':
            collection_name = "LANDSAT/LC08/C02/T1_L2"
            mask_func = mask_l8_clouds
            bands = ["SR_B1", "SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7"]
            prefix = "L8"
        else:
            print(f"Unknown satellite: {satellite}")
            return
        
        # Build collection with filters
        col = ee.ImageCollection(collection_name).filterBounds(geom).filterDate(start_date, end_date)
        
        # Cloud coverage filter (property name differs between collections)
        if satellite == 'Sentinel-2':
            col = col.filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_coverage))
        elif satellite == 'Landsat-8':
            col = col.filter(ee.Filter.lt("CLOUD_COVER", cloud_coverage))
        
        # Apply cloud masking
        col = col.map(mask_func)
        
        TASKS[task_id]['message'] = 'Counting images...'
        TASKS[task_id]['progress'] = 10
        
        count = col.size().getInfo()
        if count == 0:
            print("No satellite images found.")
            TASKS[task_id]['status'] = 'error'
            TASKS[task_id]['message'] = 'No satellite images found for the specified criteria.'
            TASKS[task_id]['progress'] = 100
            return
        
        TASKS[task_id]['message'] = f'Found {count} images. Preparing download...'
        TASKS[task_id]['progress'] = 15
        
        imgs = col.toList(count)
        months_saved = set()
        
        downloaded_count = 0
        
        for i in range(count):
            img = ee.Image(imgs.get(i))
            
            date_str = img.date().format("YYYYMMdd").getInfo()
            y = img.date().format("YYYY").getInfo()
            m = img.date().format("MMMM").getInfo()
            
            # Skip if month already downloaded
            if (y, m) in months_saved:
                continue
            months_saved.add((y, m))
            
            folder = os.path.join("data/satellite_images", satellite.lower().replace('-', '-'), y, m)
            os.makedirs(folder, exist_ok=True)
            
            img = img.clip(geom)
            region = geom.bounds().getInfo()["coordinates"]
            
            TASKS[task_id]['message'] = f'Downloading image for {m} {y}...'
            
            for band_idx, band in enumerate(bands):
                filename = f"{prefix}_{band}_{date_str}.TIF"
                path = os.path.join(folder, filename)
                
                scale = 10 if satellite == 'Sentinel-2' and band in ["B2", "B3", "B4", "B8"] else 30
                
                url = img.select(band).getDownloadURL({
                    "scale": scale,
                    "region": region,
                    "format": "GEO_TIFF",
                })
                
                r = requests.get(url)
                if r.status_code == 200:
                    with open(path, "wb") as f:
                        f.write(r.content)
                    print(f"Saved: {path}")
                else:
                    print(f"Failed: {path}")
                
                # Update progress
                # Calculate progress based on (i / count) + (band_idx / len(bands)) / count
                # But since we skip months, this is approximate. Let's just increment.
                
            downloaded_count += 1
            # Progress from 15% to 95%
            progress = 15 + (downloaded_count / len(months_saved) if months_saved else 1) * 80
            TASKS[task_id]['progress'] = min(95, int(progress))
        
        print(f"✅ All monthly GeoTIFFs downloaded successfully for {satellite}!")
        TASKS[task_id]['status'] = 'success'
        TASKS[task_id]['message'] = f'Successfully downloaded images for {len(months_saved)} months.'
        TASKS[task_id]['progress'] = 100
        
    except Exception as e:
        print(f"Error fetching satellite data: {e}")
        TASKS[task_id]['status'] = 'error'
        TASKS[task_id]['message'] = f'Error: {str(e)}'
        TASKS[task_id]['progress'] = 100

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
