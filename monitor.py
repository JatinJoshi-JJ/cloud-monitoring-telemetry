import os
import time
import requests
import csv
from datetime import datetime, timezone

TARGET_ENDPOINTS = [
    {"name": "Google", "url": "https://www.google.com"},
    {"name": "GitHub Status", "url": "https://www.githubstatus.com"},
    {"name": "Simulated Down Endpoint", "url": "https://httpstat.us/503"}
]

LATENCY_THRESHOLD_MS = 2500  # Threshold thoda balance rakha hai
LOG_FILE = "uptime_logs.csv"

def initialize_log_file():
    """Initializes CSV log file with header columns if not present."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Service", "URL", "Status_Code", "Latency_ms", "Status", "Alert_Triggered"])

def send_alert(service_name, url, status_code, latency_ms, reason):
    """Prints automated alert notification for incidents."""
    current_time = datetime.now(timezone.utc).isoformat()
    alert_message = (
        f"🚨 [INCIDENT ALERT] Service degradation detected for {service_name}!\n"
        f"  URL: {url}\n"
        f"  Reason: {reason}\n"
        f"  Status Code: {status_code}\n"
        f"  Latency: {latency_ms:.2f} ms\n"
        f"  Timestamp: {current_time}"
    )
    print("\n" + "=" * 65)
    print(alert_message)
    print("=" * 65 + "\n")

def run_health_check():
    """Executes ping health check on all endpoints, records metrics and alerts."""
    initialize_log_file()
    now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    print(f"[{now_str}] Starting cloud health checks...\n")

    for endpoint in TARGET_ENDPOINTS:
        name = endpoint["name"]
        url = endpoint["url"]
        alert_triggered = False
        start_time = time.time()
        
        try:
            response = requests.get(url, timeout=5)
            latency_ms = (time.time() - start_time) * 1000
            status_code = response.status_code

            if status_code >= 400:
                alert_triggered = True
                send_alert(name, url, status_code, latency_ms, f"Unhealthy HTTP response code: {status_code}")
            elif latency_ms > LATENCY_THRESHOLD_MS:
                alert_triggered = True
                send_alert(name, url, status_code, latency_ms, f"Latency breached threshold ({LATENCY_THRESHOLD_MS} ms)")
            else:
                print(f"✅ [OK] {name} | Status: {status_code} | Latency: {latency_ms:.2f} ms")

            status = "UP" if status_code < 400 else "DOWN"

        except requests.exceptions.RequestException as error:
            latency_ms = (time.time() - start_time) * 1000
            status_code = 0
            status = "DOWN"
            alert_triggered = True
            send_alert(name, url, status_code, latency_ms, f"Network/Connection error: {str(error)}")

        with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now(timezone.utc).isoformat(),
                name,
                url,
                status_code,
                round(latency_ms, 2),
                status,
                alert_triggered
            ])

if __name__ == "__main__":
    run_health_check()