"""
Smart Bluetooth Finder - Prototype BLE Scanner + Logger
Author: Preethi Ciliveru
Requirements:
 - Python 3.8+
 - bleak (pip install bleak)
Usage:
 - Run: python smart_bluetooth_finder.py
 - The script will continuously scan BLE devices and log data to device_log.csv
"""

import asyncio
from bleak import BleakScanner
import csv
from datetime import datetime
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "device_log.csv")

# --------------------- Utility Functions ---------------------
def rssi_to_proximity(rssi):
    try:
        r = int(rssi)
    except:
        return "Unknown"
    if r >= -50:
        return "Very Near"
    if -60 <= r < -50:
        return "Near"
    if -80 <= r < -60:
        return "Medium"
    return "Far"

def ensure_csv_exists():
    """Create the CSV file with headers if it doesn’t exist."""
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["device_name", "mac", "rssi", "location", "time_utc", "proximity"])

# --------------------- BLE Scanning Loop ---------------------
async def scan_and_log(interval=10):
    print("🔍 Starting Smart Bluetooth Finder (Press Ctrl+C to stop)\n")
    ensure_csv_exists()

    try:
        while True:
            print(f"Scanning nearby BLE devices... ({datetime.utcnow().strftime('%H:%M:%S')} UTC)")
            # Get devices (Bleak 0.21+ returns tuples of (device, advertisement_data))
            devices = await BleakScanner.discover(timeout=5.0)

            if not devices:
                print("No devices found in range.\n")
            else:
                for entry in devices:
                    # Handle both old and new bleak response formats
                    if isinstance(entry, tuple):
                        d, adv = entry
                        rssi = getattr(adv, "rssi", "N/A")
                    else:
                        d = entry
                        rssi = getattr(d, "rssi", "N/A")

                    name = d.name or "Unknown"
                    mac = d.address
                    proximity = rssi_to_proximity(rssi)
                    timestamp = datetime.utcnow().isoformat() + "Z"
                    location = "ECE_Lab_Test"  # you can rename this spot name

                    # Log into CSV
                    with open(CSV_PATH, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([name, mac, rssi, location, timestamp, proximity])

                    print(f"📡 {timestamp} | {name} | {mac} | RSSI: {rssi} dBm | {proximity}")
                print("-" * 70)

            await asyncio.sleep(interval)

    except KeyboardInterrupt:
        print("\n🛑 Scan stopped. Log saved to device_log.csv")

# --------------------- Main Execution ---------------------
if __name__ == "__main__":
    asyncio.run(scan_and_log())
