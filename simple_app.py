"""
SIMPLE Flask App - Guaranteed to Work
"""
from flask import Flask, render_template
import sys

print("="*60)
print("🚀 SIMPLE Flask Server Starting...")
print("="*60)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return render_template('test.html')

if __name__ == '__main__':
    print("\n✅ Server starting on http://localhost:8080")
    print("✅ Press Ctrl+C to stop\n")
    try:
        app.run(host='0.0.0.0', port=8080, debug=False)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n⚠️ Press any key to exit...")
        input()
        sys.exit(1)
