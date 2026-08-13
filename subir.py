#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
subir.py — Script de automatización Git Push con resolución de conflictos en sucio.
Identifica el repositorio actual, guarda cambios locales, realiza git pull y si existen
conflictos, los confirma manteniendo ambas versiones (código sucio con marcas <<<<<<< / ======= / >>>>>>>)
y realiza git push.
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

    # Determinar el mensaje de commit
    if len(sys.argv) > 1 and sys.argv[1].strip():
        commit_msg = sys.argv[1].strip()
    else:
        try:
            user_input = input("💬 Ingresa el mensaje del commit (Enter para mensaje por defecto): ").strip()
            commit_msg = user_input if user_input else f"Actualización automática {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        except (KeyboardInterrupt, EOFError):
            commit_msg = f"Actualización automática {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # Verificación de cambios locales
    status_res = run_cmd(["git", "status", "--porcelain"], cwd=repo_dir)
    has_local_changes = bool(status_res.stdout.strip())

    if has_local_changes:
        print("📦 Guardando cambios locales...")
        run_cmd(["git", "add", "."], cwd=repo_dir)

        print(f"📝 Realizando commit: '{commit_msg}'...")
        commit_res = run_cmd(["git", "commit", "-m", commit_msg], cwd=repo_dir)
        if commit_res.returncode != 0 and "nothing to commit" not in commit_res.stdout.lower():
            print("❌ Error al realizar commit local:")
            print(commit_res.stderr.strip())
            sys.exit(1)
    else:
        print("ℹ️ No hay cambios locales nuevos pendientes de commit.")

    # Hacer pull previo
    print("⬇️ Ejecutando git pull --no-rebase...")
    pull_res = run_cmd(["git", "pull", "--no-rebase"], cwd=repo_dir)

    if pull_res.returncode != 0:
        print("\n⚠️ Se detectó un conflicto durante el pull.")
        print("⚡ Preservando código sucio con ambas versiones (marcas <<<<<<< / ======= / >>>>>>>)...")

        # Agregar los archivos con marcas de conflicto e intentar commit de fusión
        run_cmd(["git", "add", "."], cwd=repo_dir)
        merge_msg = f"Auto-merge: Conflictos de fusión preservados ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
        merge_res = run_cmd(["git", "commit", "-m", merge_msg], cwd=repo_dir)
        if merge_res.returncode == 0:
            print("✅ Conflictos confirmados exitosamente como código sucio.")
        else:
            print("ℹ️ El estado del merge fue procesado.")

    # Hacer push
    print("⬆️ Subiendo cambios a remoto (git push)...")
    push_res = run_cmd(["git", "push"], cwd=repo_dir)

    if push_res.returncode == 0:
        print("🎉 ¡Subida (push) completada con éxito!")
    else:
        print("❌ Error al hacer git push:")
        print(push_res.stderr.strip())
        sys.exit(1)

if __name__ == "__main__":
    main()
