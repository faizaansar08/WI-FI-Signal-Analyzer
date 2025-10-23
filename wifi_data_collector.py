"""
Wi-Fi Data Collector - Member 2 Component
Collects RSSI (signal strength) data at different locations
Stores readings with coordinates in CSV format
Supports multiple scans for accuracy
"""

import csv
import time
import os
from datetime import datetime
from wifi_scanner import WiFiScanner


class WiFiDataCollector:
    """Collects WiFi signal data with location coordinates"""
    
    def __init__(self, output_file="wifi_data.csv"):
        self.output_file = output_file
        self.scanner = WiFiScanner()
        self.data_points = []
        
        # Initialize CSV file with headers if it doesn't exist
        if not os.path.exists(output_file):
            self._create_csv_file()
    
    def _create_csv_file(self):
        """Create CSV file with headers"""
        headers = [
            'timestamp',
            'location_x',
            'location_y',
            'location_name',
            'ssid',
            'bssid',
            'rssi_dbm',
            'signal_quality',
            'frequency',
            'channel',
            'security',
            'scan_number'
        ]
        
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        
        print(f"✅ Created CSV file: {self.output_file}")
    
    def collect_data_point(self, location_x, location_y, location_name="", scan_number=1):
        """
        Collect WiFi data at a specific location
        
        Args:
            location_x: X coordinate (meters or grid position)
            location_y: Y coordinate (meters or grid position)
            location_name: Human-readable location name (e.g., "Living Room")
            scan_number: Scan iteration number (for multiple scans)
        
        Returns:
            List of collected data points
        """
        print(f"\n📍 Collecting data at location ({location_x}, {location_y}) - {location_name}")
        print(f"   Scan #{scan_number}")
        
        # Scan for networks
        networks = self.scanner.scan_networks()
        
        if not networks:
            print(f"⚠️ No networks found at this location")
            return []
        
        # Prepare data points
        points = []
        timestamp = datetime.now().isoformat()
        
        for network in networks:
            data_point = {
                'timestamp': timestamp,
                'location_x': location_x,
                'location_y': location_y,
                'location_name': location_name,
                'ssid': network['ssid'],
                'bssid': network.get('bssid', 'Unknown'),
                'rssi_dbm': network['signal_strength'],
                'signal_quality': network['signal_quality'],
                'frequency': network.get('frequency', 'N/A'),
                'channel': network.get('channel', 'N/A'),
                'security': network.get('security', 'Unknown'),
                'scan_number': scan_number
            }
            points.append(data_point)
            self.data_points.append(data_point)
        
        print(f"✅ Collected {len(points)} network readings")
        return points
    
    def save_to_csv(self, data_points=None):
        """
        Save collected data points to CSV file
        
        Args:
            data_points: List of data points to save (if None, saves all collected points)
        """
        if data_points is None:
            data_points = self.data_points
        
        if not data_points:
            print("⚠️ No data points to save")
            return
        
        with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data_points[0].keys())
            writer.writerows(data_points)
        
        print(f"✅ Saved {len(data_points)} data points to {self.output_file}")
    
    def collect_multiple_scans(self, location_x, location_y, location_name="", 
                              num_scans=3, delay=2):
        """
        Perform multiple scans at the same location for accuracy
        
        Args:
            location_x: X coordinate
            location_y: Y coordinate
            location_name: Location name
            num_scans: Number of scans to perform (default: 3)
            delay: Delay between scans in seconds (default: 2)
        
        Returns:
            List of all collected data points
        """
        print(f"\n🔄 Performing {num_scans} scans at location ({location_x}, {location_y})")
        
        all_points = []
        
        for scan_num in range(1, num_scans + 1):
            points = self.collect_data_point(
                location_x, 
                location_y, 
                location_name, 
                scan_number=scan_num
            )
            all_points.extend(points)
            
            # Save after each scan
            self.save_to_csv(points)
            
            # Wait before next scan (except for last scan)
            if scan_num < num_scans:
                print(f"⏳ Waiting {delay} seconds before next scan...")
                time.sleep(delay)
        
        return all_points
    
    def collect_grid_survey(self, grid_size=(5, 5), spacing=1.0, num_scans=3):
        """
        Perform a grid-based site survey
        
        Args:
            grid_size: Tuple of (rows, cols) for grid dimensions
            spacing: Distance between grid points in meters
            num_scans: Number of scans per location
        
        Returns:
            Total number of data points collected
        """
        rows, cols = grid_size
        total_points = 0
        
        print(f"\n🗺️ Starting grid survey: {rows}x{cols} grid, {spacing}m spacing")
        print(f"   Total locations: {rows * cols}")
        print(f"   Scans per location: {num_scans}")
        print("="*60)
        
        for row in range(rows):
            for col in range(cols):
                x = col * spacing
                y = row * spacing
                location_name = f"Grid_{row}_{col}"
                
                points = self.collect_multiple_scans(
                    x, y, location_name, num_scans=num_scans, delay=2
                )
                total_points += len(points)
                
                print(f"   Progress: {row * cols + col + 1}/{rows * cols} locations")
        
        print("="*60)
        print(f"✅ Grid survey complete! Collected {total_points} total data points")
        return total_points
    
    def collect_custom_locations(self, locations, num_scans=3):
        """
        Collect data at custom location points
        
        Args:
            locations: List of tuples [(x, y, name), ...]
            num_scans: Number of scans per location
        
        Returns:
            Total number of data points collected
        """
        total_points = 0
        
        print(f"\n📍 Collecting data at {len(locations)} custom locations")
        print("="*60)
        
        for i, location in enumerate(locations, 1):
            x, y, name = location
            
            points = self.collect_multiple_scans(
                x, y, name, num_scans=num_scans, delay=2
            )
            total_points += len(points)
            
            print(f"   Progress: {i}/{len(locations)} locations")
        
        print("="*60)
        print(f"✅ Custom location survey complete! Collected {total_points} total data points")
        return total_points
    
    def get_summary(self):
        """Get summary of collected data"""
        if not self.data_points:
            return "No data collected yet"
        
        unique_locations = set((p['location_x'], p['location_y']) for p in self.data_points)
        unique_ssids = set(p['ssid'] for p in self.data_points)
        
        avg_rssi = sum(p['rssi_dbm'] for p in self.data_points) / len(self.data_points)
        
        summary = f"""
📊 Data Collection Summary
{'='*60}
Total Data Points:      {len(self.data_points)}
Unique Locations:       {len(unique_locations)}
Unique Networks:        {len(unique_ssids)}
Average RSSI:           {avg_rssi:.2f} dBm
Output File:            {self.output_file}
{'='*60}
        """
        return summary


def run_interactive_collection():
    """Interactive data collection mode"""
    print("\n" + "="*70)
    print("🌐 Wi-Fi Data Collection Tool")
    print("="*70)
    
    collector = WiFiDataCollector()
    
    while True:
        print("\n📋 Collection Options:")
        print("  1. Single location scan")
        print("  2. Multiple scans at one location")
        print("  3. Grid survey (automated)")
        print("  4. Custom locations survey")
        print("  5. Quick demo (3 sample locations)")
        print("  6. View summary")
        print("  7. Exit")
        
        choice = input("\n👉 Select option (1-7): ").strip()
        
        if choice == '1':
            try:
                x = float(input("  Enter X coordinate (meters): "))
                y = float(input("  Enter Y coordinate (meters): "))
                name = input("  Enter location name: ")
                
                points = collector.collect_data_point(x, y, name)
                collector.save_to_csv(points)
            except ValueError:
                print("❌ Invalid input. Please enter numbers for coordinates.")
        
        elif choice == '2':
            try:
                x = float(input("  Enter X coordinate (meters): "))
                y = float(input("  Enter Y coordinate (meters): "))
                name = input("  Enter location name: ")
                num_scans = int(input("  Number of scans (default 3): ") or "3")
                
                collector.collect_multiple_scans(x, y, name, num_scans=num_scans)
            except ValueError:
                print("❌ Invalid input.")
        
        elif choice == '3':
            try:
                rows = int(input("  Grid rows (default 5): ") or "5")
                cols = int(input("  Grid columns (default 5): ") or "5")
                spacing = float(input("  Spacing in meters (default 1.0): ") or "1.0")
                num_scans = int(input("  Scans per location (default 3): ") or "3")
                
                collector.collect_grid_survey((rows, cols), spacing, num_scans)
            except ValueError:
                print("❌ Invalid input.")
        
        elif choice == '4':
            try:
                num_locations = int(input("  Number of locations: "))
                locations = []
                
                for i in range(num_locations):
                    print(f"\n  Location {i+1}:")
                    x = float(input("    X coordinate: "))
                    y = float(input("    Y coordinate: "))
                    name = input("    Name: ")
                    locations.append((x, y, name))
                
                num_scans = int(input("\n  Scans per location (default 3): ") or "3")
                collector.collect_custom_locations(locations, num_scans)
            except ValueError:
                print("❌ Invalid input.")
        
        elif choice == '5':
            # Quick demo with sample locations
            demo_locations = [
                (0.0, 0.0, "Room_Corner_A"),
                (2.5, 2.5, "Room_Center"),
                (5.0, 5.0, "Room_Corner_B")
            ]
            print("\n🎯 Running quick demo at 3 sample locations...")
            collector.collect_custom_locations(demo_locations, num_scans=2)
        
        elif choice == '6':
            print(collector.get_summary())
        
        elif choice == '7':
            print("\n👋 Exiting data collection. Goodbye!")
            print(collector.get_summary())
            break
        
        else:
            print("❌ Invalid option. Please select 1-7.")


if __name__ == "__main__":
    # Example usage
    print("\n" + "="*70)
    print("🧪 Testing WiFi Data Collector")
    print("="*70)
    
    # Create collector
    collector = WiFiDataCollector("wifi_data.csv")
    
    # Collect sample data
    print("\n📍 Collecting sample data at 3 locations...")
    
    sample_locations = [
        (0.0, 0.0, "Living_Room"),
        (3.0, 0.0, "Kitchen"),
        (3.0, 3.0, "Bedroom")
    ]
    
    for x, y, name in sample_locations:
        collector.collect_multiple_scans(x, y, name, num_scans=2, delay=1)
    
    # Show summary
    print(collector.get_summary())
    
    print("\n💡 For interactive collection, run:")
    print("   python wifi_data_collector.py")
    print("\nOr uncomment the line below to start interactive mode:")
    print("# run_interactive_collection()")
