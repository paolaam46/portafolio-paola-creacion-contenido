#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bajar.py — Script de automatización Git Pull con resolución de conflictos en sucio.
Identifica el repositorio actual, guarda cambios locales (commit previo) y realiza git pull.
Si existen conflictos de fusión, agrega y confirma las marcas de conflicto (código sucio con
ambas versiones) dejando el estado listo para que el usuario lo revise o corrija después.
"""

import os
import sys
import subprocess
from datetime import datetime

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

def main():
    repo_dir = get_repo_dir()
    if not repo_dir:
        print("❌ No estás dentro de un repositorio Git.")
        sys.exit(1)

    print(f"📁 Repositorio detectado: {repo_dir}")

    # Verificar si hay cambios locales
    status_res = run_cmd(["git", "status", "--porcelain"], cwd=repo_dir)
    has_local_changes = bool(status_res.stdout.strip())

    if has_local_changes:
        print("📦 Se detectaron cambios locales pendientes. Guardando antes de bajar...")
        run_cmd(["git", "add", "."], cwd=repo_dir)
        auto_msg = f"Guardado automático de cambios locales antes de bajar ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
        commit_res = run_cmd(["git", "commit", "-m", auto_msg], cwd=repo_dir)
        if commit_res.returncode == 0:
            print("✅ Cambios locales guardados en commit previo.")
        else:
            print("⚠️ No se pudo realizar el commit previo de cambios locales.")

    # Ejecutar pull
    print("⬇️ Ejecutando git pull --no-rebase...")
    pull_res = run_cmd(["git", "pull", "--no-rebase"], cwd=repo_dir)

    if pull_res.returncode == 0:
        print("🎉 ¡Repositorio actualizado con éxito sin conflictos!")
    else:
        print("\n⚠️ Se detectaron conflictos de fusión durante el pull.")
        print("⚡ Preservando código sucio con ambas versiones (marcas <<<<<<< / ======= / >>>>>>>)...")

        # Agregar y confirmar archivos en conflicto conservando las marcas
        run_cmd(["git", "add", "."], cwd=repo_dir)
        merge_msg = f"Auto-pull: Conflictos de fusión preservados ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
        merge_res = run_cmd(["git", "commit", "-m", merge_msg], cwd=repo_dir)

        if merge_res.returncode == 0:
            print("✅ Conflictos guardados en commit como código sucio.")
        else:
            print("ℹ️ El estado del merge fue procesado.")

        print("📢 Nota: Los archivos contienen las marcas de conflicto (<<<<<<< / ======= / >>>>>>>) listos para que los revises después.")

if __name__ == "__main__":
    main()
