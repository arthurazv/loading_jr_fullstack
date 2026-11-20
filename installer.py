#!/usr/bin/env python3
"""Self-contained demo runner for Central de Solicitações.

Creates an isolated virtual environment, installs dependencies, runs backend
(FastAPI) and frontend (Vite) in the background, and cleans up all temporary
artifacts on exit so only the raw source files remain.
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
VENV_DIR = ROOT_DIR / ".demo_venv"


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def npm_executable() -> str:
    return "npm.cmd" if os.name == "nt" else "npm"


def wait_for_http(url: str, timeout: float = 20.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.5) as resp:
                if 200 <= resp.status < 500:
                    return True
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            time.sleep(0.4)
    return False


def terminate_process(proc: subprocess.Popen | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    try:
        if os.name != "nt":
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        else:
            proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        try:
            if os.name != "nt":
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            else:
                proc.kill()
        except Exception:
            pass


def cleanup_artifacts(created_node_modules: bool, created_backend_db: bool) -> None:
    print("\n🧹 Limpando ambiente temporário...")

    if VENV_DIR.exists():
        shutil.rmtree(VENV_DIR, ignore_errors=True)

    if created_node_modules:
        node_modules = FRONTEND_DIR / "node_modules"
        if node_modules.exists():
            shutil.rmtree(node_modules, ignore_errors=True)

    if created_backend_db:
        db_file = BACKEND_DIR / "database.db"
        if db_file.exists():
            db_file.unlink(missing_ok=True)

    for cache_dir in BACKEND_DIR.rglob("__pycache__"):
        shutil.rmtree(cache_dir, ignore_errors=True)

    pytest_cache = ROOT_DIR / ".pytest_cache"
    if pytest_cache.exists():
        shutil.rmtree(pytest_cache, ignore_errors=True)

    print("✅ Ambiente limpo. Apenas os arquivos originais do projeto foram mantidos.")


def main() -> int:
    had_node_modules = (FRONTEND_DIR / "node_modules").exists()
    had_backend_db = (BACKEND_DIR / "database.db").exists()

    backend_proc: subprocess.Popen | None = None
    frontend_proc: subprocess.Popen | None = None

    try:
        print("1/4 Criando virtualenv temporário...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)

        py = str(venv_python())
        print("2/4 Instalando dependências do backend no virtualenv...")
        subprocess.run(
            [py, "-m", "pip", "install", "--quiet", "-r", str(BACKEND_DIR / "requirements.txt")],
            check=True,
        )

        if not had_node_modules:
            print("3/4 Instalando dependências do frontend (npm install)...")
            subprocess.run(
                [npm_executable(), "install", "--no-audit", "--no-fund", "--silent"],
                cwd=str(FRONTEND_DIR),
                check=True,
            )
        else:
            print("3/4 Dependências do frontend já presentes.")

        print("4/4 Iniciando backend e frontend em segundo plano...")
        popen_kwargs: dict = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }
        if os.name != "nt":
            popen_kwargs["start_new_session"] = True

        backend_proc = subprocess.Popen(
            [py, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=str(BACKEND_DIR),
            **popen_kwargs,
        )

        if not wait_for_http("http://127.0.0.1:8000/health", timeout=20.0):
            raise RuntimeError("Backend não respondeu em http://127.0.0.1:8000/health.")

        frontend_proc = subprocess.Popen(
            [npm_executable(), "run", "dev", "--", "--port", "5173"],
            cwd=str(FRONTEND_DIR),
            **popen_kwargs,
        )
        wait_for_http("http://localhost:5173", timeout=15.0)

        print("\n🚀 Aplicação rodando!")
        print("   • Interface Web: http://localhost:5173")
        print("   • Swagger / API: http://127.0.0.1:8000/docs")
        print("\nPressione ENTER (ou Ctrl+C) para encerrar e limpar tudo...")

        try:
            input()
        except (KeyboardInterrupt, EOFError):
            pass

        return 0
    except KeyboardInterrupt:
        return 0
    except Exception as exc:
        print(f"\n❌ Erro ao iniciar o ambiente: {exc}", file=sys.stderr)
        return 1
    finally:
        terminate_process(frontend_proc)
        terminate_process(backend_proc)
        cleanup_artifacts(
            created_node_modules=not had_node_modules,
            created_backend_db=not had_backend_db,
        )


if __name__ == "__main__":
    raise SystemExit(main())
