# 🌍 GeoPulse

**GeoPulse** is an open-source, real-time satellite monitoring and environmental change detection system.  
It automates the ingestion, processing, and analysis of Landsat and other satellite imagery to track vegetation health, surface temperature, and urban growth.

---

## 🚀 Key Features

- **📡 Automated Data Pipeline:**  
  Scheduled ingestion from USGS or Google Earth Engine using Airflow or Prefect.

- **🧮 Index Computation:**  
  Calculates NDVI, NDWI, NDBI, and LST indices using parallel workers (Dask/Spark).

- **⚠️ Anomaly Detection:**  
  Detects sudden NDVI drops, LST spikes, or NDBI surges.

- **🔔 Real-Time Alerts:**  
  Email or Slack notifications when environmental thresholds are breached.

- **📊 Live Dashboards:**  
  FastAPI backend + Streamlit frontend with WebSocket-based real-time updates.

- **🤖 Predictive Analytics:**  
  Forecasts NDVI and LST trends using ML models (LSTM/Prophet).

---

## 🧰 Tech Stack

| Layer | Tools |
|-------|-------|
| **Data Ingestion** | Apache Airflow / Prefect |
| **Processing** | Dask / Spark / Celery |
| **Backend API** | FastAPI |
| **Frontend** | Streamlit |
| **Database** | PostgreSQL + TimescaleDB |
| **Caching** | Redis |
| **Messaging** | Kafka / RabbitMQ |
| **Monitoring** | Prometheus + Grafana |

---

## ⚙️ Use Cases

- 🌿 Vegetation health tracking (NDVI)
- 🌆 Urban expansion monitoring (NDBI)
- ☀️ Surface temperature trend analysis (LST)
- 🔄 Temporal change detection between scenes
- 🔮 Environmental forecasting and alerting

---

## 📦 Project Goals

- Create a modular, event-driven Earth observation pipeline  
- Enable scalable, automated geospatial analysis  
- Support reproducibility and versioned environmental insights  

---