"""
Quick test script to verify WiFi scanning works
"""
from wifi_scanner import WiFiScanner

print("="*60)
print("Testing WiFi Scanner")
print("="*60)

scanner = WiFiScanner()
print("\nScanning for networks...")

networks = scanner.scan_networks()

print(f"\n✅ Found {len(networks)} network(s):\n")

for i, network in enumerate(networks, 1):
    print(f"{i}. {network['ssid']}")
    print(f"   Signal: {network['signal_strength']} dBm ({network['signal_quality']}%)")
    print(f"   Frequency: {network['frequency']}")
    print(f"   Security: {network['security']}")
    print(f"   Channel: {network['channel']}")
    print()

print("="*60)
print("✅ Scanner test complete!")
print("="*60)
