"""
Student client for detecting BLE beacons and showing attendance popup.
"""
import asyncio
import threading
import json
import time
import requests
import logging
from tkinter import Tk, Label, Button, messagebox
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from .device_utils import get_device_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = "http://localhost:8000/api/v1"
BEACON_SERVICE_UUID = "0000ffff-0000-1000-8000-00805f9b34fb"
SCAN_INTERVAL = 10  # seconds

class AttendanceClient:
    def __init__(self, student_id: str):
        self.student_id = student_id
        self.device_id = get_device_id()
        self.beacon_detected = False
        self.current_session_id = None
        self.scanning = False
        
    async def scan_for_beacons(self):
        """Scan for BLE beacons."""
        def detection_callback(device: BLEDevice, advertisement_data: AdvertisementData):
            if BEACON_SERVICE_UUID.lower() in advertisement_data.service_uuids:
                logger.info(f"Detected beacon from {device.name}")
                self.beacon_detected = True
                # Extract session ID from beacon data (simplified)
                # In a real implementation, you'd parse the beacon data properly
                self.current_session_id = 1  # Placeholder
                
                # Show popup in main thread
                self.root.after(0, self.show_attendance_popup)
        
        self.scanning = True
        scanner = BleakScanner(detection_callback)
        
        try:
            await scanner.start()
            while self.scanning:
                await asyncio.sleep(1)
            await scanner.stop()
        except Exception as e:
            logger.error(f"Error scanning for beacons: {e}")
            self.fallback_to_polling()
    
    def fallback_to_polling(self):
        """Fallback to HTTP polling if BLE is not available."""
        logger.info("Falling back to HTTP polling")
        while self.scanning:
            try:
                response = requests.get(f"{BACKEND_URL}/current_session")
                if response.status_code == 200 and response.json():
                    session = response.json()
                    self.current_session_id = session["id"]
                    self.beacon_detected = True
                    self.root.after(0, self.show_attendance_popup)
                    # Wait a while after detection
                    time.sleep(60)
                else:
                    time.sleep(SCAN_INTERVAL)
            except requests.RequestException as e:
                logger.error(f"HTTP polling error: {e}")
                time.sleep(SCAN_INTERVAL)
    
    def show_attendance_popup(self):
        """Show attendance confirmation popup."""
        if not self.beacon_detected:
            return
            
        result = messagebox.askyesno(
            "Attendance Confirmation",
            "You are in class. Mark attendance?",
            icon="question"
        )
        
        if result:
            self.mark_attendance()
        
        self.beacon_detected = False
    
    def mark_attendance(self):
        """Mark attendance on the backend."""
        try:
            data = {
                "student_id": self.student_id,
                "session_id": self.current_session_id,
                "device_id": self.device_id
            }
            
            response = requests.post(
                f"{BACKEND_URL}/mark_attendance",
                json=data
            )
            
            if response.status_code == 200:
                messagebox.showinfo("Success", "Attendance marked successfully!")
            elif response.status_code == 400:
                messagebox.showwarning("Notice", response.json().get("detail", "Attendance already marked"))
            else:
                messagebox.showerror("Error", "Failed to mark attendance")
                
        except requests.RequestException as e:
            logger.error(f"Error marking attendance: {e}")
            messagebox.showerror("Error", "Could not connect to attendance server")
    
    def run(self):
        """Run the client application."""
        # Create GUI
        self.root = Tk()
        self.root.title("Attendance Client")
        self.root.geometry("300x150")
        
        Label(self.root, text="Attendance Client", font=("Arial", 16)).pack(pady=10)
        Label(self.root, text=f"Student ID: {self.student_id}").pack(pady=5)
        Label(self.root, text="Waiting for class beacon...").pack(pady=5)
        
        # Start beacon scanning in background thread
        def start_scanning():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.scan_for_beacons())
        
        scan_thread = threading.Thread(target=start_scanning)
        scan_thread.daemon = True
        scan_thread.start()
        
        # Run GUI
        self.root.mainloop()
        self.scanning = False

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python student_client.py <student_id>")
        sys.exit(1)
    
    client = AttendanceClient(sys.argv[1])
    client.run()