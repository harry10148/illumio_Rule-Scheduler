import os
import sys
import time
import argparse

# ==========================================
# File Paths & Core Init
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(SCRIPT_DIR, "rule_schedules.json")
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")

from src.core import ConfigManager, ScheduleDB, PCEClient, ScheduleEngine

def init_core() -> dict:
    """Initialize core dependencies (Config, DB, PCE, Runtime Engine)"""
    cfg = ConfigManager(CONFIG_FILE)
    cfg.load()
    
    import src.i18n as i18n
    i18n.set_lang(cfg.config.get('lang', 'en'))

    db = ScheduleDB(DB_FILE)
    pce = PCEClient(cfg)
    engine = ScheduleEngine(db, pce)
    return {'cfg': cfg, 'db': db, 'pce': pce, 'engine': engine}

# ==========================================
# Application Entry Point
# ==========================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Illumio Rule Scheduler - Automate Illumio Core Policy Rules",
        epilog="If no arguments are provided, the CLI interactive menu will launch."
    )
    parser.add_argument("--gui", action="store_true", help="Launch the Web GUI mode")
    parser.add_argument("--port", type=int, default=5000, help="Port for the Web GUI (default: 5000)")
    parser.add_argument("--monitor", action="store_true", help="Run in continuous background daemon mode")
    
    args = parser.parse_args()
    
    core_system = init_core()

    if args.monitor:
        print("[*] Service Started (Daemon mode).")
        interval = int(os.environ.get("ILLUMIO_CHECK_INTERVAL", "300"))
        while True:
            try:
                core_system['engine'].check(silent=True)
            except Exception as e:
                import traceback
                print(f"[DAEMON ERROR] {e}")
                traceback.print_exc()
            time.sleep(interval)

    elif args.gui:
        try:
            from src.gui_ui import launch_gui
            launch_gui(core_system, port=args.port)
        except ImportError:
            print("[!] Web GUI requires Flask. Install with:")
            print("      pip install flask")
            print("    CLI mode works without Flask.")

    else:
        # Default to CLI mode (backward compatibility)
        from src.cli_ui import CLI
        cli_app = CLI(core_system)
        cli_app.run(core_system=core_system)
