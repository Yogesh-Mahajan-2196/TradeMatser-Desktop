"""MyTradeMaster desktop launcher (local Windows desktop mode)."""
from __future__ import annotations

import asyncio
import logging
import os
import sys
import threading
import time
import traceback
import urllib.error
import urllib.request
from pathlib import Path

APP_HOST = "127.0.0.1"
APP_PORT = 8765
APP_URL = f"http://{APP_HOST}:{APP_PORT}/login"


def application_dir() -> Path:
    # In a PyInstaller onedir build, keep .env beside MyTradeMaster.exe.
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def show_error(title: str, message: str) -> None:
    try:
        import tkinter
        from tkinter import messagebox
        root = tkinter.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except Exception:
        print(f"{title}: {message}", file=sys.stderr)


def main() -> None:
    root_dir = application_dir()
    os.chdir(root_dir)
    log_path = root_dir / "desktop_startup.log"
    logging.basicConfig(
        filename=str(log_path),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    if not (root_dir / ".env").is_file():
        show_error(
            "MyTradeMaster setup required",
            "The .env file was not found. Copy .env.example to .env, configure "
            "the PostgreSQL connection and required settings, then start the app again.\n\n"
            f"Expected location: {root_dir / '.env'}",
        )
        return

    try:
        # Import every model before create_all so SQLAlchemy sees all tables.
        from utils.database import Base, engine
        import modules.models  # noqa: F401

        
        async def initialize_database() -> None:
            try:
                async with engine.begin() as connection:
                    await connection.run_sync(Base.metadata.create_all)
            finally:
                # Clear pooled connections before Uvicorn starts
                # and uses the engine from its own event loop.
                await engine.dispose()

        logging.info(
            "Creating any missing database tables from current SQLAlchemy models."
        )
        asyncio.run(initialize_database())


        import uvicorn

        server = uvicorn.Server(
            uvicorn.Config(
                "main:app",
                host=APP_HOST,
                port=APP_PORT,
                log_level="info",
                access_log=False,
                log_config=None,
            )
        )
        server_thread = threading.Thread(target=server.run, name="MyTradeMasterAPI", daemon=True)
        server_thread.start()

        ready = False
        last_error = None
        for _ in range(120):
            if not server_thread.is_alive():
                break
            try:
                with urllib.request.urlopen(APP_URL, timeout=1) as response:
                    if response.status < 500:
                        ready = True
                        break
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = exc
            time.sleep(0.5)

        if not ready:
            server.should_exit = True
            detail = f"\n\nLast connection error: {last_error}" if last_error else ""
            raise RuntimeError(
                "FastAPI did not start. Check PostgreSQL, the DATABASE_URL in .env, "
                f"and desktop_startup.log.{detail}"
            )

        import webview
        window = webview.create_window(
            "MyTradeMaster",
            APP_URL,
            maximized=True,
            min_size=(1000, 650),
            text_select=True,
        )
        try:
            webview.start(debug=False)
        finally:
            server.should_exit = True
            server_thread.join(timeout=10)
            try:
                asyncio.run(engine.dispose())
            except Exception:
                logging.exception("Error closing database engine")

    except Exception as exc:
        logging.error("Desktop startup failed:\n%s", traceback.format_exc())
        show_error(
            "MyTradeMaster could not start",
            f"{exc}\n\nCheck desktop_startup.log beside the app for details.",
        )


if __name__ == "__main__":
    main()
