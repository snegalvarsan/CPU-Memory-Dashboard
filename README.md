# CPU & Memory Dashboard

A simple, real-time dashboard to monitor CPU and memory usage with graphs and spike detection.

Built with **Python**, **Dash (Plotly)**, and **Flask** — this is a lightweight, no-login monitoring tool you can run locally or on a VM.

![image](https://github.com/user-attachments/assets/bf6d397e-d0b8-47e0-8746-7609f5c67183)

---

## Features

- Real-time line graphs for CPU and Memory usage
- Highlights CPU spikes visually
- ⏸Pause/Resume live updates
- Date filter to zoom into a time range
- Download logs as a `.csv` file

---

## Tech Stack

- Python 3
- Dash (Plotly)
- Flask (as backend)
- Docker (for easy deployment)

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/snegalvarsan/CPU-Memory-Dashboard.git
cd cpu-memory-dashboard
sudo snap install docker -y
sudo docker compose up -d
```
