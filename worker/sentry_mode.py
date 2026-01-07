import subprocess
import time
import sys
import os
from datetime import datetime

# CONFIGURATION
WORKER_SCRIPT = "worker/hydra_controller.py"
RESTART_DELAY = 5  # Seconds to wait before restart

def log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🛡️ SENTRY: {message}")

def start_hydra():
    """Starts the Hydra worker as a subprocess."""
    log(f"Spawning Hydra process ({WORKER_SCRIPT})...")
    # Using python from current env
    python_executable = sys.executable
    return subprocess.Popen([python_executable, WORKER_SCRIPT])

def sentry_loop():
    """Main surveillance loop."""
    log("Initialization complete. Watching over The Beast.")
    
    process = start_hydra()
    
    try:
        while True:
            # Check if process is still running
            ret_code = process.poll()
            
            if ret_code is not None:
                log(f"⚠️ Hydra died with code {ret_code}. Resurrection initiated in {RESTART_DELAY}s...")
                time.sleep(RESTART_DELAY)
                process = start_hydra()
                log("♻️ Hydra resurrected successfully.")
            
            # Heartbeat check could be added here (e.g., checking a file timestamp)
            time.sleep(2)
            
    except KeyboardInterrupt:
        log("Sentry deactivated by user. Killing Hydra...")
        process.terminate()
        sys.exit(0)

if __name__ == "__main__":
    print("""
    ░█▀▀░█▀▀░█▀█░▀█▀░█▀▄░█░█
    ░▀▀█░█▀▀░█░█░░█░░█▀▄░▀▄▀
    ░▀▀▀░▀▀▀░▀░▀░░▀░░▀░▀░░▀░
    -- ETERNAL PERSISTENCE MODULE --
    """)
    sentry_loop()
