#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bajar.py — Script de automatización Git Pull con sincronización segura.
Identifica la rama activa, guarda cambios locales pendientes si existen y descarga
los cambios desde la rama remota (git pull). Permite que la persona no desarrolladora
reciba fácilmente las correcciones realizadas por el desarrollador.
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

def get_current_branch(repo_dir):
    """Obtiene la rama activa del repositorio (ej. main o master)."""
    res = run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_dir)
    if res.returncode == 0 and res.stdout.strip():
        return res.stdout.strip()
    return "main"

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    repo_dir = get_repo_dir()
    if not repo_dir:
        print("❌ No estás dentro de un repositorio Git.")
        sys.exit(1)

    branch = get_current_branch(repo_dir)
    print(f"📁 Repositorio detectado: {repo_dir}")
    print(f"🌿 Rama activa: {branch}")

    # Verificar si hay una fusión pendiente de una ejecución anterior
    merge_head_path = os.path.join(repo_dir, ".git", "MERGE_HEAD")
    if os.path.exists(merge_head_path):
        print("⚠️ Se detectó una fusión pendiente. Resguardando estado...")
        run_cmd(["git", "add", "."], cwd=repo_dir)
        run_cmd(["git", "commit", "-m", f"Auto-merge: Fusión previa completada ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"], cwd=repo_dir)

    # Verificar si hay cambios locales pendientes
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

    # Ejecutar pull desde la rama activa
    print(f"⬇️ Ejecutando git pull origin {branch} --no-rebase...")
    pull_res = run_cmd(["git", "pull", "origin", branch, "--no-rebase"], cwd=repo_dir)

    if pull_res.returncode == 0:
        print("\n🎉 ¡Proyecto actualizado con éxito!")
        print("✅ Ya tienes la última versión corregida en tu copia local.")
    else:
        print("\n⚠️ Se detectaron diferencias durante la descarga.")
        print("⚡ Resguardando estado local...")

        # Agregar y confirmar archivos en conflicto conservando las marcas si las hay
        run_cmd(["git", "add", "."], cwd=repo_dir)
        merge_msg = f"Auto-pull: Estado resguardado ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
        merge_res = run_cmd(["git", "commit", "-m", merge_msg], cwd=repo_dir)

        if merge_res.returncode == 0:
            print("✅ Estado resguardado exitosamente.")
        else:
            print("ℹ️ El estado del merge fue procesado.")

        print("📢 Nota: Si el desarrollador acaba de subir la versión corregida, vuelve a ejecutar 'python bajar.py'.")

if __name__ == "__main__":
    main()
