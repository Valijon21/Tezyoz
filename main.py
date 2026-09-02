"""
TypeMaster entry point.
Initializes logging and bootstrap.
"""
import sys
import logging
from app.config import LOG_PATH, APP_NAME, APP_VERSION
from app.application import Application

def setup_logging():
    """Configure system-wide logging."""
    try:
        # Guarantee parent directory exists before logging
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            filename=str(LOG_PATH),
            filemode='a',
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            level=logging.INFO
        )
        
        # Console output for dev context, keeping it minimal
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)
        
    except Exception as e:
        # Back up console output if log file configuration fails
        logging.basicConfig(level=logging.INFO)
        logging.error(f"Failed to configure standard file logging: {e}")

def main():
    """Main application runner."""
    setup_logging()
    
    # Enable DPI awareness before bootstrapping Tkinter
    if sys.platform.startswith("win"):
        try:
            import ctypes
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(2) # PROCESS_PER_MONITOR_DPI_AWARE
            except Exception:
                ctypes.windll.shcore.SetProcessDpiAwareness(1) # PROCESS_SYSTEM_DPI_AWARE
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

    logger = logging.getLogger("main")

    logger.info(f"Starting {APP_NAME} v{APP_VERSION}...")
    
    try:
        # Initialize SQLite Database Schema
        from database.schema import initialize_schema
        initialize_schema()
        
        app = Application()
        app.run()
        logger.info("Application closed cleanly.")
    except Exception as err:
        logger.critical("Uncaught diagnostic traceback occurred in main execution", exc_info=True)
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "System Error",
                f"An unexpected system exception occurred during startup. Details are recorded in the logs.\n\nError: {err}"
            )
            root.destroy()
        except Exception:
            print(f"\n[CRITICAL ERROR] An unexpected system error occurred: {err}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
