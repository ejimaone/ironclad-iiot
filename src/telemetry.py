import time
import sys
import os
import sqlite3
import systemd.journal as journal
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
    journal.send("IronClad Agent: Startup Initiated.", PRIORITY=journal.LOG_INFO)
    
    try:
        conn = init_db()
        c = conn.cursor()
        
        daemon.notify('READY=1')

        while True:
            if os.path.exists(TRIGGER_CRASH):
            
                journal.send("CHAOS: Crash Trigger Activated! Exiting...", PRIORITY=journal.LOG_ALERT)
                sys.exit(1)

            if os.path.exists(TRIGGER_FREEZE):
                journal.send("CHAOS: Freeze Trigger Activated! Entering sleep loop...", PRIORITY=journal.LOG_WARNING)
                while True: time.sleep(1) 

            
            val = random.uniform(50.0, 150.0)
            
            if val > 120.0:
               journal.send(f"CRITICAL: Pressure Surge {val:.2f} PSI", PRIORITY=journal.LOG_CRITICAL)
            elif val > 100.0:
               journal.send(f"WARNING: Pressure High {val:.2f} PSI", PRIORITY=journal.LOG_WARNING)
            else:
                journal.send(f"Sensor read normal: {val:.2f} PSI", PRIORITY=journal.LOG_DEBUG) 
                
            
            # Save to DB
            c.execute('INSERT INTO readings (val, ts) VALUES (?, datetime("now"))', (val,))

            conn.commit()

            # --- THE HEARTBEAT ---
            daemon.notify('WATCHDOG=1')
            
            time.sleep(5)

    except Exception as e:
        journal.send(f"FATAL: Agent Crashed with error: {e}", PRIORITY=journal.LOG_ERR)
        sys.exit(1)

if __name__ == '__main__':
    main()