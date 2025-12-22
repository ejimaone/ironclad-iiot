import time
import sys
import os
import sqlite3
import random
from systemd import daemon

DB_PATH = '/opt/iiot_edge/data.db'
TRIGGER_CRASH = '/opt/iiot_edge/trigger_crash'
TRIGGER_FREEZE = '/opt/iiot_edge/trigger_freeze'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            val REAL,
            ts TEXT
        )
    ''')
    conn.commit()
    return conn

def main():
    print(" [INFO] IronClad Agent Started.")
    
    try:
        conn = init_db()
        c = conn.cursor()
        
        daemon.notify('READY=1')

        while True:
            if os.path.exists(TRIGGER_CRASH):
                print(" [ALERT] CHAOS: Crash Trigger Activated!")
                sys.exit(1)

            if os.path.exists(TRIGGER_FREEZE):
                print(" [WARN] CHAOS: Freeze Trigger Activated!")
                while True: time.sleep(1) 

            
            val = random.uniform(50.0, 150.0)
            
            if val > 120.0:
                print(f" [CRITICAL] Pressure Surge {val:.2f} PSI")
            elif val > 100.0:
                print(f" [WARNING] Pressure High {val:.2f} PSI")
            else:
                #  
                pass
            
            # Save to DB
            c.execute('INSERT INTO readings (val, ts) VALUES (?, datetime("now"))', (val,))

            conn.commit()

            # --- THE HEARTBEAT ---
            daemon.notify('WATCHDOG=1')
            
            time.sleep(5)

    except Exception as e:
        print(f" [FATAL] Agent Crashed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()