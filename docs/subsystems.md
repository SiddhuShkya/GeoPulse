# 🌍 Real-Time Satellite Monitoring System — Subsystems Overview

---

## ✅ 1. Data Ingestion Subsystem
**🎯 Purpose:** Acquire and organize satellite imagery.  

**🧩 Components:**
- 🕒 **Scheduler:** Apache Airflow or Prefect to fetch Landsat imagery weekly/monthly  
- 🚨 **Event Listener:** Detect new datasets from USGS/Google Earth Engine  
- 📩 **Ingestion Queue:** Kafka or RabbitMQ (`raw_imagery`)  
- 💾 **Storage:** Raw imagery → S3 or local blob store, metadata → PostgreSQL  

**🔗 Interfaces:**
- **Input:** USGS/EE API  
- **Output:** Message queue (`raw_imagery`) + metadata DB  

---

## ✅ 2. Preprocessing Subsystem
**🎯 Purpose:** Clean and prepare imagery for analysis.  

**🧩 Components:**
- ⚙️ **Worker Pool:** Async Celery/Kafka consumers  
- 🧼 **Operations:** Cloud masking, band extraction, AOI clipping  
- 🗂️ **Output Format:** GeoTIFF or NetCDF  
- ⚡ **Caching:** Redis for intermediate ND arrays  

**🔗 Interfaces:**
- **Input:** `raw_imagery` queue  
- **Output:** `clean_imagery` queue  

---

## ✅ 3. Index Computation Subsystem
**🎯 Purpose:** Compute NDVI, NDWI, NDBI, and LST indices.  

**🧩 Components:**
- 🧮 **Workers:** Independent index processors  
- 📊 **Algorithms:** Apply index formulas (NumPy/Rasterio)  
- 🧠 **Parallelization:** Dask or Spark for distributed computing  
- 🕓 **Versioning:** Store run ID, AOI, timestamp, and index version  

**🔗 Interfaces:**
- **Input:** `clean_imagery` queue  
- **Output:** `index_results` topic  

---

## ✅ 4. Change Detection & Anomaly Subsystem
**🎯 Purpose:** Detect significant environmental changes.  

**🧩 Components:**
- 🔍 **Comparators:** Analyze consecutive scenes  
- 🚦 **Rules Engine:**  
  - NDVI drop > 20%  
  - LST spike > 5°C  
  - NDBI sudden increase  
- 📢 **Output:** JSON alerts  

**🔗 Interfaces:**
- **Input:** `index_results` topic  
- **Output:** `alerts` topic  

---

## ✅ 5. Notification & Alerting Subsystem
**🎯 Purpose:** Notify users of anomalies and threshold breaches.  

**🧩 Components:**
- ✉️ **Notification Service:** Consumes `alerts` topic  
- 🔔 **Channels:** Email (SMTP) or Slack webhook  
- 🧾 **Templates:** Custom alert messages + severity levels  

**🔗 Interfaces:**
- **Input:** `alerts` topic  
- **Output:** Email/Slack/User endpoints  

---

## ✅ 6. Storage & Caching Subsystem
**🎯 Purpose:** Manage all stored and cached data.  

**🧩 Components:**
- 🗃️ **Time-Series DB:** TimescaleDB or InfluxDB  
- ⚡ **Cache Layer:** Redis for hot index data  
- 🗄️ **Archival Storage:** S3 or local volume for historical imagery  

**🔗 Interfaces:**
- **Input:** `index_results`, `alerts`  
- **Output:** APIs + dashboards  

---

## ✅ 7. Visualization Subsystem
**🎯 Purpose:** Display real-time analytics and metrics.  

**🧩 Components:**
- 💻 **Frontend:** Streamlit or React-based dashboard  
- ⚙️ **Backend:** FastAPI serving REST + WebSocket APIs  
- 🔄 **Live Updates:** Server-Sent Events (SSE) or WebSocket streams  

**🔗 Interfaces:**
- **Input:** Database, Redis, WebSocket feed  
- **Output:** User UI  

---

## ✅ 8. Predictive Analytics Subsystem
**🎯 Purpose:** Forecast vegetation and temperature trends.  

**🧩 Components:**
- 🤖 **Model Trainer:** LSTM/Prophet on historical NDVI/LST  
- 📈 **Inference Engine:** Predict upcoming environmental shifts  
- 🌐 **Integration:** Feed predictions into visualization dashboard  

---

## ✅ 9. Orchestration & Monitoring Subsystem
**🎯 Purpose:** Coordinate and monitor all services.  

**🧩 Components:**
- 🔁 **Orchestrator:** Airflow/Prefect DAGs for workflows  
- 📊 **Metrics:** Prometheus + Grafana for system health  
- 🪵 **Logging:** ELK Stack or OpenTelemetry  

---

### ⚙️ Summary
| Subsystem | Key Tools | Core Function |
|------------|------------|----------------|
| Data Ingestion | Airflow, Kafka | Fetch + queue imagery |
| Preprocessing | Celery, Redis | Clean + prepare data |
| Index Computation | Dask, Spark | Calculate indices |
| Change Detection | Rules Engine | Detect anomalies |
| Notification | Slack, SMTP | Alert users |
| Storage | TimescaleDB, Redis | Store + cache results |
| Visualization | Streamlit, FastAPI | Live dashboards |
| Predictive Analytics | LSTM, Prophet | Forecast trends |
| Orchestration | Airflow, Grafana | Manage + monitor system |

---

🚀 **Next Step:**  
Would you like a **system architecture diagram** or a **microservice folder structure** next?
