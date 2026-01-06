import os
import time
import subprocess
import ctypes
import sys

# NEXUS SENTRY MODE - V1.0
# Mission: Keep the laptop awake and the Hydra worker running 24/7.

def prevent_sleep():
    """
    Prevents the Windows laptop from going to sleep or turning off the display.
    """
    print("🛡️ Sentry Mode: Preventing Sleep (ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)")
    # Windows API Constants
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002
    
    try:
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
        return True
    except Exception as e:
        print(f"⚠️ Failed to set execution state: {e}")
        return False

def start_hydra_worker():
    """
    Launches the Hydra worker in a background subprocess.
    """
    worker_path = os.path.join(os.getcwd(), "worker", "hydra_controller.py")
    if not os.path.exists(worker_path):
        print(f"❌ Error: Could not find {worker_path}")
        return None
    
    print(f"🐉 Sentry Mode: Launching Hydra Worker -> {worker_path}")
    # Run hydra in a new process group so it doesn't die with this script easily
    process = subprocess.Popen([sys.executable, worker_path], 
                                creationflags=subprocess.CREATE_NEW_CONSOLE)
    return process

def main():
    print("==" * 20)
    print("   PROJECT NEXUS: SENTRY MODE ACTIVE   ")
    print("==" * 20)
    
    prevent_sleep()
    worker_proc = start_hydra_worker()
    
    try:
        while True:
            # Heartbeat check every 60 seconds
            if worker_proc and worker_proc.poll() is not None:
                print("⚠️ Hydra Worker died! Relaunching...")
                worker_proc = start_hydra_worker()
            
            # Sublte mouse jitter (optional, but ES_DISPLAY_REQUIRED is usually enough)
            # print("💓 Sentry Heartbeat: Systems Nominal.")
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n🛑 Sentry Mode: Powering down. Systems returning to normal.")
        # Return power state to normal
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)

if __name__ == "__main__":
    main()
