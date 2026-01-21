
import os
import sys

with open("debug_log.txt", "w") as f:
    f.write(f"Python is running!\n")
    f.write(f"CWD: {os.getcwd()}\n")
    f.write(f"Sys Path: {sys.path}\n")
    try:
        import playwright
        f.write("Playwright imported successfully\n")
    except ImportError as e:
        f.write(f"Playwright missing: {e}\n")
print("Debug script finished")
