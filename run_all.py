import subprocess
import sys
import time
import requests

# Backend and frontend commands
BACKEND_CMD = [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
FRONTEND_CMD = ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]

# Start backend
backend_proc = subprocess.Popen(BACKEND_CMD)
print("?? Starting backend...")

# Wait until backend is ready
backend_ready = False
BACKEND_URL = "http://localhost:8000/status"
max_wait = 30  # max seconds to wait
start_time = time.time()

while time.time() - start_time < max_wait:
    try:
        r = requests.get(BACKEND_URL)
        if r.status_code == 200:
            backend_ready = True
            print("? Backend is ready!")
            break
    except requests.exceptions.RequestException:
        pass
    time.sleep(1)

if not backend_ready:
    print("? Backend did not start within 30 seconds.")
    backend_proc.terminate()
    sys.exit(1)

# Start frontend
frontend_proc = subprocess.Popen(FRONTEND_CMD)
print("?? Starting Streamlit frontend...")

# Wait for both processes
try:
    backend_proc.wait()
    frontend_proc.wait()
except KeyboardInterrupt:
    print("\n?? Terminating processes...")
    backend_proc.terminate()
    frontend_proc.terminate()
