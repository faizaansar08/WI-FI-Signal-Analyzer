"""
Wi-Fi Scanner Module
Cross-platform WiFi signal strength scanner
Supports Windows, Linux, and macOS
"""

import subprocess
import re
import platform
import sys


class WiFiScanner:
    """WiFi network scanner with cross-platform support"""
    
    def __init__(self):
        self.platform = platform.system()
        print(f"🖥️ Detected platform: {self.platform}")
    
    def scan_networks(self):
        """
        Scan for available WiFi networks
        Returns: List of network dictionaries
        """
        try:
            if self.platform == "Windows":
                return self._scan_windows()
            elif self.platform == "Linux":
                return self._scan_linux()
            elif self.platform == "Darwin":  # macOS
                return self._scan_macos()
            else:
                print(f"⚠️ Unsupported platform: {self.platform}")
                return self._generate_mock_data()
        except Exception as e:
            print(f"❌ Scanning error: {str(e)}")
            return self._generate_mock_data()
    
    def _scan_windows(self):
        """Scan WiFi networks on Windows using netsh"""
        try:
            # Run netsh command to get WiFi networks
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=Bssid'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode != 0:
                print(f"⚠️ netsh command failed, using mock data")
                return self._generate_mock_data()
            
            networks = []
            current_network = {}
            
            lines = result.stdout.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Parse SSID
                if line.startswith('SSID'):
                    if current_network and 'ssid' in current_network:
                        networks.append(current_network)
                        current_network = {}
                    
                    ssid_match = re.search(r'SSID \d+ : (.+)', line)
                    if ssid_match:
                        ssid = ssid_match.group(1).strip()
                        if ssid:
                            current_network['ssid'] = ssid
                
                # Parse signal strength
                elif 'Signal' in line:
                    signal_match = re.search(r'(\d+)%', line)
                    if signal_match and 'ssid' in current_network:
                        quality = int(signal_match.group(1))
                        current_network['signal_quality'] = quality
                        # Convert percentage to approximate dBm
                        current_network['signal_strength'] = self._quality_to_dbm(quality)
                
                # Parse authentication
                elif 'Authentication' in line:
                    auth_match = re.search(r'Authentication\s+:\s+(.+)', line)
                    if auth_match and 'ssid' in current_network:
                        current_network['security'] = auth_match.group(1).strip()
                
                # Parse channel
                elif 'Channel' in line:
                    channel_match = re.search(r'Channel\s+:\s+(\d+)', line)
                    if channel_match and 'ssid' in current_network:
                        current_network['channel'] = int(channel_match.group(1))
            
            # Add last network
            if current_network and 'ssid' in current_network:
                networks.append(current_network)
            
            # Fill in missing data
            for network in networks:
                if 'signal_quality' not in network:
                    network['signal_quality'] = 50
                    network['signal_strength'] = -70
                if 'security' not in network:
                    network['security'] = 'Unknown'
                if 'channel' not in network:
                    network['channel'] = 'N/A'
                network['frequency'] = self._channel_to_frequency(network.get('channel', 1))
            
            print(f"✅ Found {len(networks)} networks on Windows")
            
            # If only 1 network found (Windows limitation when connected), add mock networks
            if len(networks) <= 1:
                print("⚠️ Windows netsh shows limited networks (likely connected). Adding nearby simulated networks...")
                mock_networks = self._generate_mock_data()
                # Keep the real connected network and add mock ones
                for mock in mock_networks:
                    # Don't duplicate the real network
                    if not any(n['ssid'] == mock['ssid'] for n in networks):
                        networks.append(mock)
                print(f"📡 Total networks (real + simulated): {len(networks)}")
            
            return networks if networks else self._generate_mock_data()
            
        except Exception as e:
            print(f"❌ Windows scan error: {str(e)}")
            return self._generate_mock_data()
    
    def _scan_linux(self):
        """Scan WiFi networks on Linux using iwlist or nmcli"""
        try:
            # Try nmcli first (more common on modern Linux)
            result = subprocess.run(
                ['nmcli', '-f', 'SSID,SIGNAL,CHAN,SECURITY', 'dev', 'wifi'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                networks = []
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2:
                        ssid = parts[0]
                        quality = int(parts[1]) if parts[1].isdigit() else 50
                        channel = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 1
                        security = parts[3] if len(parts) > 3 else 'Unknown'
                        
                        networks.append({
                            'ssid': ssid,
                            'signal_strength': self._quality_to_dbm(quality),
                            'signal_quality': quality,
                            'channel': channel,
                            'frequency': self._channel_to_frequency(channel),
                            'security': security
                        })
                
                print(f"✅ Found {len(networks)} networks on Linux")
                return networks if networks else self._generate_mock_data()
            
        except FileNotFoundError:
            print("⚠️ nmcli not found on Linux")
        except Exception as e:
            print(f"❌ Linux scan error: {str(e)}")
        
        return self._generate_mock_data()
    
    def _scan_macos(self):
        """Scan WiFi networks on macOS using airport"""
        try:
            result = subprocess.run(
                ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-s'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                networks = []
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 3:
                        ssid = parts[0]
                        signal = int(parts[2])
                        channel = int(parts[3]) if len(parts) > 3 else 1
                        security = parts[6] if len(parts) > 6 else 'Unknown'
                        
                        networks.append({
                            'ssid': ssid,
                            'signal_strength': signal,
                            'signal_quality': self.calculate_quality(signal),
                            'channel': channel,
                            'frequency': self._channel_to_frequency(channel),
                            'security': security
                        })
                
                print(f"✅ Found {len(networks)} networks on macOS")
                return networks if networks else self._generate_mock_data()
            
        except Exception as e:
            print(f"❌ macOS scan error: {str(e)}")
        
        return self._generate_mock_data()
    
    def _generate_mock_data(self):
        """Generate mock WiFi data for testing or when scanning fails"""
        import random
        
        mock_networks = [
            {'ssid': 'Neighbor_WiFi_5G', 'base_signal': -55, 'security': 'WPA2-Personal'},
            {'ssid': 'TP-Link_Home', 'base_signal': -62, 'security': 'WPA2-Personal'},
            {'ssid': 'Office_Network', 'base_signal': -68, 'security': 'WPA2-Enterprise'},
            {'ssid': 'Guest_Hotspot', 'base_signal': -72, 'security': 'Open'},
            {'ssid': 'Netgear_2.4G', 'base_signal': -75, 'security': 'WPA2-Personal'},
            {'ssid': 'Linksys_5GHz', 'base_signal': -78, 'security': 'WPA2-Personal'},
            {'ssid': 'CoffeeShop_Free', 'base_signal': -81, 'security': 'Open'},
            {'ssid': 'Apartment_203', 'base_signal': -84, 'security': 'WPA2-Personal'},
        ]
        
        networks = []
        for i, mock in enumerate(mock_networks):
            # Add random variation to simulate real signal fluctuation (-3 to +3 dBm)
            signal_strength = mock['base_signal'] + random.randint(-3, 3)
            # Mix of 2.4GHz (channels 1-11) and 5GHz (channels 36-165)
            if i % 2 == 0:
                channel = random.choice([1, 6, 11])  # 2.4 GHz
            else:
                channel = random.choice([36, 40, 44, 48, 149, 153, 157, 161])  # 5 GHz
            
            networks.append({
                'ssid': mock['ssid'],
                'signal_strength': signal_strength,
                'signal_quality': self.calculate_quality(signal_strength),
                'channel': channel,
                'frequency': self._channel_to_frequency(channel),
                'security': mock['security']
            })
        
        print(f"⚠️ Using mock data: {len(networks)} simulated networks")
        return networks
    
    def calculate_quality(self, signal_dbm):
        """
        Convert signal strength (dBm) to quality percentage
        dBm range: -30 (excellent) to -90 (poor)
        """
        if signal_dbm >= -30:
            return 100
        elif signal_dbm <= -90:
            return 0
        else:
            # Linear interpolation
            return int(((signal_dbm + 90) / 60) * 100)
    
    def _quality_to_dbm(self, quality_percent):
        """Convert quality percentage to approximate dBm"""
        return int(-90 + (quality_percent / 100) * 60)
    
    def _channel_to_frequency(self, channel):
        """Convert WiFi channel to frequency in GHz"""
        if isinstance(channel, str) or channel == 'N/A':
            return 'N/A'
        
        if 1 <= channel <= 14:
            return f"2.4 GHz (Ch {channel})"
        elif 36 <= channel <= 165:
            return f"5 GHz (Ch {channel})"
        else:
            return 'Unknown'


# Test the scanner when run directly
if __name__ == "__main__":
    print("\n🔍 Testing WiFi Scanner...\n")
    scanner = WiFiScanner()
    networks = scanner.scan_networks()
    
    print(f"\n📶 Found {len(networks)} networks:\n")
    for net in networks:
        print(f"  • {net['ssid']}")
        print(f"    Signal: {net['signal_strength']} dBm ({net['signal_quality']}%)")
        print(f"    Channel: {net['channel']} | Frequency: {net['frequency']}")
        print(f"    Security: {net['security']}\n")
