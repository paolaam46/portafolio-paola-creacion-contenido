#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validar.py — Script para validar el estado actual del repositorio Git.
Muestra la rama activa, la salida completa de 'git status' y, si existe,
el archivo de registro 'error_git_log.txt'. Mantiene la ventana de la consola abierta
hasta que el usuario la cierre manualmente.
"""

import os
import sys
import subprocess

def run_cmd(cmd, cwd=None):
    """Ejecuta un comando de consola y devuelve el objeto CompletedProcess."""
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, shell=isinstance(cmd, str))

def get_repo_dir():
    """Identifica el directorio raíz del repositorio Git actual."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    res = run_cmd(["git", "rev-parse", "--show-toplevel"], cwd=script_dir)
    if res.returncode == 0:
        return res.stdout.strip()
    return None

def get_current_branch(repo_dir):
    """Obtiene la rama activa del repositorio."""
    res = run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_dir)
    if res.returncode == 0 and res.stdout.strip():
        return res.stdout.strip()
    return "desconocida"

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 65)
    print(" 🔍 VALIDACIÓN DE ESTADO DEL REPOSITORIO GIT")
    print("=" * 65)

    repo_dir = get_repo_dir()
    if not repo_dir:
        print("\n❌ No estás dentro de un repositorio Git válido.")
    else:
        branch = get_current_branch(repo_dir)
        print(f"\n📁 Repositorio: {repo_dir}")
        print(f"🌿 Rama activa: {branch}")
        print("-" * 65)
        print("📌 ESTADO DETALLADO DEL REPOSITORIO (git status):")
        print("-" * 65)

        status_res = run_cmd(["git", "status"], cwd=repo_dir)
        print(status_res.stdout.strip() or status_res.stderr.strip())

        # Verificar si existe un registro de error generado previamente por subir.py o bajar.py
        log_file = os.path.join(repo_dir, "error_git_log.txt")
        if os.path.exists(log_file):
            print("\n" + "=" * 65)
            print(" ⚠️ REPORTE DE ERROR GUARDADO (error_git_log.txt):")
            print("=" * 65)
            try:
                with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                    print(f.read().strip())
            except Exception as e:
                print(f"No se pudo leer el archivo de reporte: {e}")

    print("\n" + "=" * 65)
    print(" 📌 FIN DE LA VALIDACIÓN.")
    print(" ℹ️ La ventana permanecerá abierta hasta que la cierres manualmente.")
    print("=" * 65)

    try:
        input("\nPresiona Enter para cerrar esta ventana...")
    except (KeyboardInterrupt, EOFError):
        pass

if __name__ == "__main__":
    main()
