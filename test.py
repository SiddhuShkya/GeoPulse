import ee
from dotenv import load_dotenv
import os

load_dotenv()

key_file = "geopulse-key.json"
credentials = ee.ServiceAccountCredentials(
    "geopulse-service@geopulse-477105.iam.gserviceaccount.com", key_file
)

ee.Initialize(credentials, project=os.getenv("project_id"))
