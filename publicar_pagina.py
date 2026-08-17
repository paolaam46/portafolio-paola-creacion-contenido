#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publicar_pagina.py — Script de publicación para GitHub Pages en la rama 'website'.
Flujo:
1. Guarda y confirma los cambios locales pendientes.
2. Va a la rama 'main' y ejecuta git pull origin main.
3. Cambia a la rama 'website' y sincroniza (pull).
4. Hace rebase de 'website' con respecto a 'main'.
5. Hace commit si hay cambios pendientes y push a origin website.
6. Regresa automáticamente a la rama 'main'.
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
    """Obtiene la rama activa del repositorio."""
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
    notify(title, "Ocurrió un error en la publicación. Se abrirá el registro con detalles.", is_error=True)
    
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

    print(f"📁 Repositorio: {repo_dir}")

    # Determinar el mensaje de commit
    if len(sys.argv) > 1 and sys.argv[1].strip():
        provided = sys.argv[1].strip()
        commit_msg = provided if not _is_path_like(provided) else f"Publicación automática ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
    else:
        try:
            user_input = input("💬 Ingresa el mensaje del commit (Enter para mensaje por defecto): ").strip()
            commit_msg = user_input if user_input and not _is_path_like(user_input) else f"Publicación automática ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
        except (KeyboardInterrupt, EOFError):
            commit_msg = f"Publicación automática ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"

    # 1. Guardar cambios locales existentes en la rama actual si los hay
    status_res = run_cmd(["git", "status", "--porcelain"], cwd=repo_dir)
    if status_res.stdout.strip():
        print("📦 Guardando cambios locales pendientes...")
        run_cmd(["git", "add", "."], cwd=repo_dir)
        c_res = run_cmd(["git", "commit", "-m", commit_msg], cwd=repo_dir)
        if c_res.returncode != 0 and "nothing to commit" not in c_res.stdout.lower():
            print("❌ Error al guardar cambios locales:")
            print(c_res.stderr.strip())
            show_error_and_open_notepad("Error al guardar cambios locales", c_res.stderr or c_res.stdout, repo_dir)
            pause_if_windows()
            sys.exit(1)

    # 2. Ir a main y hacer git pull origin main
    print("🌿 Cambiando a rama 'main'...")
    checkout_main = run_cmd(["git", "checkout", "main"], cwd=repo_dir)
    if checkout_main.returncode != 0:
        print("❌ Error al cambiar a main:")
        print(checkout_main.stderr.strip())
        show_error_and_open_notepad("Error checkout main", checkout_main.stderr or checkout_main.stdout, repo_dir)
        pause_if_windows()
        sys.exit(1)

    print("⬇️ Haciendo git pull origin main...")
    pull_main = run_cmd(["git", "pull", "origin", "main"], cwd=repo_dir)
    if pull_main.returncode != 0:
        print("❌ Error al hacer pull en main:")
        print(pull_main.stderr.strip())
        show_error_and_open_notepad("Error pull origin main", pull_main.stderr or pull_main.stdout, repo_dir)
        pause_if_windows()
        sys.exit(1)

    # 3. Cambiar a la rama 'website'
    print("🌿 Cambiando a rama 'website'...")
    checkout_website = run_cmd(["git", "checkout", "website"], cwd=repo_dir)
    if checkout_website.returncode != 0:
        # Intentar crearla si no existe localmente pero sí en origin
        checkout_website = run_cmd(["git", "checkout", "-b", "website", "origin/website"], cwd=repo_dir)
        if checkout_website.returncode != 0:
            print("❌ Error al cambiar/crear rama website:")
            print(checkout_website.stderr.strip())
            show_error_and_open_notepad("Error checkout website", checkout_website.stderr or checkout_website.stdout, repo_dir)
            run_cmd(["git", "checkout", "main"], cwd=repo_dir)
            pause_if_windows()
            sys.exit(1)

    print("⬇️ Sincronizando rama website con remoto (git pull origin website)...")
    run_cmd(["git", "pull", "origin", "website", "--no-rebase"], cwd=repo_dir)

    # 4. Hacer rebase de website sobre main
    print("🔄 Aplicando rebase de 'website' sobre 'main'...")
    rebase_res = run_cmd(["git", "rebase", "main"], cwd=repo_dir)
    if rebase_res.returncode != 0:
        print("⚠️ Hubo un conflicto durante el rebase. Abortando rebase y restaurando...")
        run_cmd(["git", "rebase", "--abort"], cwd=repo_dir)
        show_error_and_open_notepad("Conflicto en Rebase (website sobre main)", rebase_res.stderr or rebase_res.stdout, repo_dir)
        run_cmd(["git", "checkout", "main"], cwd=repo_dir)
        pause_if_windows()
        sys.exit(1)

    # 5. Verificar si hay cambios pendientes antes de pushear
    status_web = run_cmd(["git", "status", "--porcelain"], cwd=repo_dir)
    if status_web.stdout.strip():
        run_cmd(["git", "add", "."], cwd=repo_dir)
        run_cmd(["git", "commit", "-m", commit_msg], cwd=repo_dir)

    # 6. Hacer push a website
    print("⬆️ Subiendo cambios a 'website' (git push origin website)...")
    push_res = run_cmd(["git", "push", "origin", "website", "--force-with-lease"], cwd=repo_dir)
    if push_res.returncode != 0:
        # Reintentar push normal si force-with-lease no aplica
        push_res = run_cmd(["git", "push", "origin", "website"], cwd=repo_dir)

    if push_res.returncode != 0:
        print("❌ Error al subir a origin website:")
        print(push_res.stderr.strip())
        show_error_and_open_notepad("Error push website", push_res.stderr or push_res.stdout, repo_dir)
        run_cmd(["git", "checkout", "main"], cwd=repo_dir)
        pause_if_windows()
        sys.exit(1)

    # 7. Regresar a main
    print("↩️ Regresando a la rama 'main'...")
    run_cmd(["git", "checkout", "main"], cwd=repo_dir)

    print("\n🎉 ¡Página publicada con éxito en GitHub Pages (rama 'website')!")
    print("🌿 Actualmente te encuentras en la rama 'main'.")
    notify("Publicación Exitosa", "🎉 ¡Sitio publicado en la rama 'website' y regresaste a 'main'!")
    pause_if_windows()

if __name__ == "__main__":
    main()
