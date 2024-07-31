import subprocess

# Run Flask app
subprocess.Popen(["python", "backend/app.py"])

# Run Svelte app
subprocess.Popen(["npm", "run", "dev"], cwd="frontend")
