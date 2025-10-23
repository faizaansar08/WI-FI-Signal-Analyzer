"""
Quick Test Script - Wi-Fi Signal Analyzer
Tests the WiFi scanner independently before running the full application
"""

import sys
from wifi_scanner import WiFiScanner

def test_scanner():
    print("\n" + "="*60)
    print("🧪 Wi-Fi Scanner Test")
    print("="*60 + "\n")
    
    try:
        # Initialize scanner
        print("1️⃣  Initializing scanner...")
        scanner = WiFiScanner()
        print("   ✅ Scanner initialized\n")
        
        # Scan for networks
        print("2️⃣  Scanning for Wi-Fi networks...")
        networks = scanner.scan_networks()
        print(f"   ✅ Found {len(networks)} network(s)\n")
        
        # Display results
        if networks:
            print("📶 Network Details:\n")
            print("-" * 80)
            print(f"{'SSID':<25} {'Signal':<12} {'Quality':<10} {'Frequency':<15} {'Security'}")
            print("-" * 80)
            
            for net in networks:
                ssid = net['ssid'][:24]
                signal = f"{net['signal_strength']} dBm"
                quality = f"{net['signal_quality']}%"
                frequency = str(net.get('frequency', 'N/A'))[:14]
                security = str(net.get('security', 'Unknown'))[:15]
                
                print(f"{ssid:<25} {signal:<12} {quality:<10} {frequency:<15} {security}")
            
            print("-" * 80)
            print(f"\n✅ Test completed successfully!\n")
            print("💡 Next step: Run the full application with 'python app.py'\n")
            return True
        else:
            print("⚠️  No networks detected")
            print("💡 This is normal if:")
            print("   - WiFi is disabled")
            print("   - Running without admin/sudo privileges")
            print("   - WiFi adapter is not available")
            print("\n📝 The application will use mock data for testing.\n")
            return True
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}\n")
        print("💡 The application will fall back to mock data.\n")
        return False

if __name__ == "__main__":
    success = test_scanner()
    
    if success:
        print("="*60)
        print("🚀 Ready to launch the full application!")
        print("="*60)
        print("\nRun one of these commands:")
        print("  • PowerShell: .\\start.ps1")
        print("  • CMD:        start.bat")
        print("  • Direct:     python app.py")
        print("\nThen open: http://localhost:5000")
        print("="*60 + "\n")
    
    sys.exit(0 if success else 1)
