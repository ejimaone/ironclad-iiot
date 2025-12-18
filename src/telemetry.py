import time
import sys
import os
import sqlite3
import random
# We import daemon for the Watchdog, but NOT journal
from systemd import daemon

# --- CONFIGURATION ---
DB_PATH = '/opt/iiot_edge/data.db'
TRIGGER_CRASH = '/opt/iiot_edge/trigger_crash'
TRIGGER_FREEZE = '/opt/iiot_edge/trigger_freeze'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS readings (val REAL, ts TEXT)')
    conn.commit()
    return conn

def main():
    # OLD WAY: Just printing to the screen (stdout)
    print(" [INFO] IronClad Agent Started.")
    
    try:
        conn = init_db()
        c = conn.cursor()
        
        # Signal Ready to Systemd (Module 1 Feature)
        daemon.notify('READY=1')

        while True:
            # --- CHAOS TRIGGERS ---
            if os.path.exists(TRIGGER_CRASH):
                print(" [ALERT] CHAOS: Crash Trigger Activated!")
                sys.exit(1)

            if os.path.exists(TRIGGER_FREEZE):
                print(" [WARN] CHAOS: Freeze Trigger Activated!")
                while True: time.sleep(1) 

            # --- THE WORK ---
            val = random.uniform(50.0, 150.0)
            
            # OLD WAY: Simple print statements
            if val > 120.0:
                print(f" [CRITICAL] Pressure Surge {val:.2f} PSI")
            elif val > 100.0:
                print(f" [WARNING] Pressure High {val:.2f} PSI")
            else:
                # Optional: Don't print everything to save space
                # print(f" [INFO] Normal: {val:.2f}")
                pass
            
            # Save to DB
            c.execute('INSERT INTO readings VALUES (?, datetime("now"))', (val,))
            conn.commit()

            # --- THE HEARTBEAT ---
            daemon.notify('WATCHDOG=1')
            
            time.sleep(5)

    except Exception as e:
        # OLD WAY: Printing the error to stderr
        print(f" [FATAL] Agent Crashed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()