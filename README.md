# PRALAYA-NET: Unified Disaster Command System 

**Real-time Crisis Intelligence and Predictive Infrastructure Resilience.**

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![FastAPI](https://img.shields.io/badge/fastapi-0.104+-brightgreen)
![React](https://img.shields.io/badge/react-18.2+-61dafb)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🌋 Problem Statement
During national-level disasters, response teams face three critical gaps:
1. **Data Fragmentation**: Local sensor data is often disconnected from global satellite and seismic feeds.
2. **Hidden Cascades**: The failure of one infrastructure node (e.g., a power substation) often triggers unpredictable secondary failures in healthcare and water systems.
3. **Navigation Blackouts**: Rescue drones often lose GPS signal in smoke-filled or high-interference "denied" zones.

---

## 🛰️ Solution Overview
**PRALAYA-NET** is an end-to-end disaster command system that bridges these gaps. It ingests live global disaster data, processes it through a **GNN-based Digital Twin** to predict infrastructure cascades, and orchestrates autonomous reconnaissance drones using **Visual SLAM** for GPS-denied navigation. All insights are broadcast via **WebSockets** to a tactical command dashboard.

---

## ✨ Key Features
- **🌍 Live Strategic Ingestion**: Automatically polls **USGS Earthquakes**, **NASA FIRMS (Wildfires)**, and **OpenWeather** APIs to detect real-world crises as they happen.
- **🕸️ Cascading Risk GNN**: Uses a Graph Neural Network (NetworkX-driven) to model infrastructure dependencies and predict the **"Next Likely Failure Node"** with probability scores.
- **🚁 Hybrid V-SLAM Reconnaissance**: Operates drones with **ORB Feature Tracking**. It supports live webcam feeds, pre-recorded drone footage, or synthetic patterns if no camera is detected.
- **📺 WebSocket Tactical Dashboard**: Real-time bidirectional mission control with interactive Leaflet maps, intelligence feeds, and drone visual tracking.
- **📡 Hardware Alert Loop**: A dedicated API for **ESP32 controllers** to trigger physical sirens and pulsating LEDs based on real-time risk scores.
- **🛡️ Resilience Engineering**: Built-in API retries, global UI error boundaries, and "Safe Demo Mode" for offline/limited-environment stability.

---

## 🏗️ System Architecture

```text
       [GLOBAL DATA SOURCES]          [LOCAL RECONNAISSANCE]
       (USGS, NASA FIRMS, OW)             (Drone V-SLAM)
                |                               |
                v                               v
    ┌───────────────────────┐       ┌───────────────────────┐
    │   DATA INGESTOR       │       │   CV ANOMALY PREDICTOR│
    └───────────┬───────────┘       └───────────┬───────────┘
                │                               │
                v                               v
    ┌───────────────────────────────────────────────────────┐
    │           STRATEGIC BACKEND (FastAPI)                 │
    │  [Decision Engine] [GNN Risk Engine] [Alert Manager]  │
    └───────────┬───────────────┬───────────────┬───────────┘
                │               │               │
                v               v               v
    ┌───────────────────┐  ┌─────────────┐  ┌───────────────┐
    │ TACTICAL DASHBOARD│  │ WS BROADCAST│  │ ESP32 HARDWARE│
    │ (React + Leaflet) │  │ (Real-time) │  │ (IoT Alerts)  │
    └───────────────────┘  └─────────────┘  └───────────────┘
```

---

## 💻 Tech Stack
- **Backend**: FastAPI, Uvicorn, Python-Dotenv, Pydantic.
- **Intelligence**: NetworkX (Graph Logic), OpenCV (Vision/SLAM), NumPy (Analysis).
- **Frontend**: React (Vite), Leaflet (Mapping), Recharts (Telemetry), WebSockets.
- **Ingestion**: HTTPX Async, USGS/NASA REST APIs.
- **Infrastructure**: Render (Backend), Vercel (Frontend), Git.

---

## 🚀 Installation & Setup

### **1. Clone & Prerequisites**
```bash
git clone https://github.com/user/pralaya-net.git
cd pralaya-net
```

### **2. Backend Setup**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# (Optional) Create .env with DATA_GOV_KEY, NASA_API_KEY
```

### **3. Frontend Setup**
```bash
cd ../dashboard
npm install
```

### **4. Run (One Command)**
**Windows (Recommended):**
```bash
run_demo.bat
```
**Linux/Mac:**
```bash
chmod +x run_demo.sh
./run_demo.sh
```

---

## ☁️ Production Deployment

### **Deploy Backend (Render)**
1.  **Create Web Service**: Connect your GitHub repository.
2.  **Runtime**: Python 3.
3.  **Build Command**: `pip install -r backend/requirements.txt`
4.  **Start Command**: `cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT`
5.  **Env Vars**: Set `NASA_API_KEY`, `DATA_GOV_KEY`, `OPENWEATHER_API_KEY`.

### **Deploy Frontend (Vercel)**
1.  **Import Project**: Connect GitHub.
2.  **Root Directory**: `dashboard`.
3.  **Framework Preset**: Vite.
4.  **Env Vars**: Set `VITE_API_URL` to your Render backend URL.
5.  **Build**: Automatic `npm run build`.

---

## 🔌 API Documentation

### **Risk Alert (ESP32 Polling)**
**GET** `/api/risk-alert`
- **Response Example**:
```json
{
  "risk_score": 0.85,
  "risk_level": "high",
  "hardware_trigger": {
    "buzzer": true,
    "red_led": true,
    "pulse": true,
    "intensity": 216
  },
  "message": "High risk detected: Power Grid A"
}
```

### **Manual Disaster Injection**
**POST** `/api/trigger/disaster`
- **Request Body**:
```json
{
  "disaster_type": "flood",
  "severity": 0.9,
  "location": {"lat": 28.6139, "lon": 77.2090, "name": "Zone Alpha"}
}
```

---

## 🎮 Demo Flow
1. **Initialization**: Run `run_demo.bat`. The system starts the backend and auto-injects an initial USGS earthquake scenario.
2. **Tactical Viewing**: Open the browser. Observe the Red Disaster Zone and the pulsating infrastructure nodes on the map.
3. **Failure Intelligence**: Look at the **"Failure Intelligence"** panel on the right. The AI will display the next likely node to fail (e.g., "City Hospital") based on graph propagation.
4. **Drone Mission**: Open the Drone Feed window. Witness the ORB SLAM tracking features in the drone's visual field, navigating independently of GPS.
5. **Hardware Feedback**: The backend will pulse the connected ESP32 controllers as risk levels escalate.

---

## 💡 Innovation: What Makes This Unique?
- **Predictive Propagation**: Unlike static maps, PRALAYA-NET uses Graph Theory to predict *how* a disaster will travel through critical infrastructure.
- **Visual Intelligence**: The V-SLAM module provides a "Vision as Data" layer, allowing drones to maintain situational awareness when electronic signals are jammed or degraded.
- **Unified Orchestration**: It successfully integrates strategic global datasets with tactical local assets in a single reactive loop.

---

## 🚀 Future Improvements
- **Multi-Agent Coordination**: Swarm logic for multiple drones.
- **Edge AI**: Offloading GNN calculations to localized edge nodes.
- **Satellite Super-resolution**: Using GANs to enhance low-res satellite imagery.

---

## 👥 Contributors
- **PRALAYA-NET Engineering Team**
- **DeepMind Agentic AI Support**

---
*Developed for National Resilience and Crisis Management.*
