#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
subir.py — Script de automatización Git Push con resolución de conflictos preservados.
Identifica el repositorio y la rama actual, guarda todos los cambios locales (incluyendo archivos nuevos),
realiza git pull de la rama activa y, si existen conflictos, los confirma preservando ambas versiones
(marcas <<<<<<< / ======= / >>>>>>>) y realiza git push para que un desarrollador los resuelva.
Incluye notificaciones de Windows y apertura automática de Notepad en caso de error.
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

def notify(title, message, is_error=False):
    """Muestra una notificación nativa en Windows / consola."""
    print(f"\n📢 [{title}] {message}")
    if os.name == 'nt':
        ps_cmd = (
            f'[void][System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms"); '
            f'$icon = [System.Windows.Forms.ToolTipIcon]::{"Error" if is_error else "Info"}; '
            f'$notification = New-Object System.Windows.Forms.NotifyIcon; '
            f'$notification.Icon = [System.Drawing.SystemIcons]::{"Error" if is_error else "Information"}; '
            f'$notification.BalloonTipIcon = $icon; '
            f'$notification.BalloonTipTitle = "{title}"; '
            f'$notification.BalloonTipText = "{message}"; '
            f'$notification.Visible = $True; '
            f'$notification.ShowBalloonTip(5000);'
        )
        try:
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, timeout=5)
        except Exception:
            pass

def show_error_and_open_notepad(title, error_text, repo_dir):
    """Genera un archivo de log con el error y abre Notepad en Windows."""
    notify(title, "Ocurrió un error. Se abrirá el Bloc de notas con los detalles.", is_error=True)
    
    log_file = os.path.join(repo_dir, "error_git_log.txt")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    content = (
        f"====================================================\n"
        f"  {title.upper()}\n"
        f"  Fecha: {timestamp}\n"
        f"====================================================\n\n"
        f"DETALLE DEL ERROR DE GIT:\n"
        f"----------------------------------------------------\n"
        f"{error_text.strip()}\n"
        f"----------------------------------------------------\n\n"
        f"Por favor envía o muestra este archivo al desarrollador para resolverlo.\n"
    )
    
    try:
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"\n❌ Se guardó el registro de error en: {log_file}")
        
        if os.name == 'nt':
            print("📖 Abriendo Bloc de notas (Notepad) con el reporte de error...")
            subprocess.Popen(["notepad.exe", log_file])
        else:
            try:
                subprocess.Popen(["xdg-open", log_file])
            except Exception:
                pass
    except Exception as e:
        print(f"No se pudo escribir el log de error: {e}")

def pause_if_windows():
    """Mantiene la ventana de consola abierta si el usuario ejecutó haciendo doble clic en Windows."""
    if os.name == 'nt':
        try:
            input("\nPresiona Enter para cerrar esta ventana...")
        except (KeyboardInterrupt, EOFError):
            pass

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    repo_dir = get_repo_dir()
    if not repo_dir:
        print("❌ No estás dentro de un repositorio Git.")
        notify("Git Error", "No estás dentro de un repositorio Git.", is_error=True)
        pause_if_windows()
        sys.exit(1)

    branch = get_current_branch(repo_dir)
    print(f"📁 Repositorio detectado: {repo_dir}")
    print(f"🌿 Rama activa: {branch}")

    def _is_path_like(value):
        value = value.strip()
        return (
            os.path.isabs(value)
            or value.startswith(".")
            or value.startswith("/")
            or value.startswith("\\")
            or os.path.sep in value
            or value.startswith("file://")
        )

    # Determinar el mensaje de commit
    if len(sys.argv) > 1 and sys.argv[1].strip():
        provided = sys.argv[1].strip()
        commit_msg = provided if not _is_path_like(provided) else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        try:
            user_input = input("💬 Ingresa el mensaje del commit (Enter para mensaje por defecto): ").strip()
            commit_msg = user_input if user_input and not _is_path_like(user_input) else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except (KeyboardInterrupt, EOFError):
            commit_msg = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Verificar si hay una fusión pendiente de una ejecución anterior
    merge_head_path = os.path.join(repo_dir, ".git", "MERGE_HEAD")
    if os.path.exists(merge_head_path):
        print("⚠️ Se detectó una fusión pendiente. Resguardando estado...")
        run_cmd(["git", "add", "."], cwd=repo_dir)
        run_cmd(["git", "commit", "-m", f"Auto-merge: Fusión previa completada ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"], cwd=repo_dir)

    # Verificación de cambios locales (modificados o nuevos archivos untracked)
    status_res = run_cmd(["git", "status", "--porcelain"], cwd=repo_dir)
    has_local_changes = bool(status_res.stdout.strip())

    if has_local_changes:
        print("📦 Guardando cambios locales (incluyendo nuevos archivos)...")
        run_cmd(["git", "add", "."], cwd=repo_dir)

        print(f"📝 Realizando commit: '{commit_msg}'...")
        commit_res = run_cmd(["git", "commit", "-m", commit_msg], cwd=repo_dir)
        if commit_res.returncode != 0 and "nothing to commit" not in commit_res.stdout.lower():
            print("❌ Error al realizar commit local:")
            print(commit_res.stderr.strip())
            show_error_and_open_notepad("Error en Git Commit Local", commit_res.stderr or commit_res.stdout, repo_dir)
            pause_if_windows()
            sys.exit(1)
    else:
        print("ℹ️ No hay cambios locales nuevos pendientes de commit.")

    # Hacer pull previo sincronizando la rama activa
    print(f"⬇️ Ejecutando git pull origin {branch} --no-rebase...")
    pull_res = run_cmd(["git", "pull", "origin", branch, "--no-rebase"], cwd=repo_dir)

    had_conflict = False
    if pull_res.returncode != 0:
        had_conflict = True
        print("\n⚠️ Se detectó una diferencia/conflicto con los cambios del servidor.")
        print("⚡ Preservando ambas versiones (marcas <<<<<<< / ======= / >>>>>>>) para el desarrollador...")

        run_cmd(["git", "add", "."], cwd=repo_dir)
        merge_msg = f"Auto-merge: Conflictos de fusión preservados ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
        merge_res = run_cmd(["git", "commit", "-m", merge_msg], cwd=repo_dir)
        if merge_res.returncode == 0:
            print("✅ Conflictos empaquetados exitosamente en un commit de fusión.")
        else:
            print("ℹ️ El estado del merge fue procesado.")

    # Hacer push sincronizando la rama activa
    print(f"⬆️ Subiendo cambios a remoto (git push origin {branch})...")
    push_res = run_cmd(["git", "push", "origin", branch], cwd=repo_dir)

    if push_res.returncode == 0:
        print("\n🎉 ¡Subida completada con éxito!")
        print("📢 Tus cambios (y los conflictos resguardados, si hubo) ya están en el servidor para el desarrollador.")
        if had_conflict:
            notify("Git Subir - Conflictos Preservados", "Se subieron tus cambios y los conflictos para revisión del desarrollador.")
        else:
            notify("Git Subir - Éxito", "🎉 ¡Tus cambios fueron subidos con éxito!")
    else:
        print("\n❌ Error al hacer git push:")
        print(push_res.stderr.strip())
        show_error_and_open_notepad("Error al hacer Git Push", push_res.stderr or push_res.stdout, repo_dir)
        pause_if_windows()
        sys.exit(1)

    pause_if_windows()

if __name__ == "__main__":
    main()
