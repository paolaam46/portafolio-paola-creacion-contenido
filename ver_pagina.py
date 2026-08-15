#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ver_pagina.py — Servidor local para previsualizar el portafolio en el navegador.
Inicia un servidor HTTP local en el puerto 3000, abre automáticamente el navegador
predeterminado y mantiene la terminal abierta y visible en Windows.
"""

import os
import sys
import time
import socket
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT_DEFAULT = 3000

def get_project_dir():
    """Obtiene el directorio raíz del proyecto donde se encuentra este archivo."""
    return os.path.dirname(os.path.abspath(__file__))

def find_available_port(start_port=3000, max_attempts=10):
    """Verifica si el puerto está libre o busca el siguiente disponible."""
    port = start_port
    for _ in range(max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                port += 1
    return start_port

def open_browser(url, delay=1.0):
    """Abre el navegador por defecto tras una breve pausa para asegurar que el servidor esté activo."""
    def _open():
        time.sleep(delay)
        webbrowser.open(url)
    thread = threading.Thread(target=_open, daemon=True)
    thread.start()

def pause_if_windows():
    """Evita que la ventana se cierre de golpe si se ejecutó con doble clic en Windows."""
    if os.name == 'nt':
        try:
            input("\nPresiona Enter para cerrar esta ventana...")
        except (KeyboardInterrupt, EOFError):
            pass

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    project_dir = get_project_dir()
    os.chdir(project_dir)

    port = find_available_port(PORT_DEFAULT)
    url = f"http://localhost:{port}"

    class CustomHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=project_dir, **kwargs)

        def log_message(self, format, *args):
            # Formato de log más limpio y amigable
            sys.stdout.write(f"[{self.log_date_time_string()}] {args[0]} {args[1]} -> {args[2]}\n")

    try:
        server = HTTPServer(("0.0.0.0", port), CustomHandler)
    except Exception as e:
        print(f"\n❌ Error al iniciar el servidor local en el puerto {port}: {e}")
        pause_if_windows()
        sys.exit(1)

    print("=" * 60)
    print("  🌐 PORTAFOLIO PAOLA ANDREA — SERVIDOR LOCAL ACTIVO")
    print("=" * 60)
    print(f"📁 Directorio raíz : {project_dir}")
    print(f"🔗 URL Local       : {url}")
    print(f"🔗 URL en Red      : http://127.0.0.1:{port}")
    print("=" * 60)
    print("🚀 Abriendo tu navegador automáticamente...")
    print("💡 Para detener el servidor, presiona: Ctrl + C")
    print("=" * 60 + "\n")

    # Abrir el navegador en segundo plano
    open_browser(url, delay=0.8)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado en el servidor: {e}")
    finally:
        server.server_close()
        print("✅ Servidor cerrado correctamente.")
        pause_if_windows()

if __name__ == "__main__":
    main()
