#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path
import configparser
import mimetypes

# Paths
CONFIG_FILE = Path.home() / ".config" / "mimeapps.list"
DESKTOP_DIRS = [
    Path("/usr/share/applications"),
    Path("/usr/local/share/applications"),
    Path.home() / ".local/share/applications"
]

def read_mimeapps():
    """Return a dict of MIME type -> desktop file"""
    mime_map = {}
    if CONFIG_FILE.exists():
        parser = configparser.ConfigParser(strict=False)
        parser.optionxform = str  # preserve case
        parser.read(CONFIG_FILE)
        for section in ("Default Applications", "Added Associations"):
            if parser.has_section(section):
                for key, value in parser.items(section):
                    desktop = value.split(';')[0]
                    if desktop:
                        mime_map[key] = desktop
    return mime_map

def find_desktop_file(name):
    """Return full path of .desktop file"""
    for d in DESKTOP_DIRS:
        path = d / name
        if path.exists():
            return path
    return None

def parse_desktop_exec(desktop_file):
    """Return Exec command from a .desktop file"""
    try:
        lines = desktop_file.read_text().splitlines()
        in_entry = False
        for line in lines:
            if line.strip() == "[Desktop Entry]":
                in_entry = True
            elif line.startswith("[") and in_entry:
                break
            elif in_entry and line.startswith("Exec="):
                exec_cmd = line.split("=", 1)[1].strip()
                for code in ['%U', '%F', '%u', '%f', '%i', '%c', '%k']:
                    exec_cmd = exec_cmd.replace(code, '')
                return exec_cmd.split()
    except Exception:
        pass
    return None

def guess_mime(file_path):
    """Fallback: guess MIME type with 'file --mime-type'"""
    try:
        result = subprocess.run(['file', '--mime-type', '-b', str(file_path)],
                                capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception:
        return None

def open_file(file_path, mime_map):
    f = Path(file_path)
    if not f.exists():
        print(f"File not found: {f}")
        return

    mime_type, _ = mimetypes.guess_type(f)
    if not mime_type:
        mime_type = guess_mime(f)

    # fallback για άδεια αρχεία
    desktop_name = mime_map.get(mime_type)
    if not desktop_name and mime_type == "inode/x-empty":
        desktop_name = mime_map.get("text/plain")

    if not desktop_name:
        print(f"No application associated with MIME type {mime_type}, skipping {f}")
        return

    desktop_file = find_desktop_file(desktop_name)
    if not desktop_file:
        print(f"Desktop file {desktop_name} not found, skipping {f}")
        return

    exec_cmd = parse_desktop_exec(desktop_file)
    if not exec_cmd:
        print(f"Cannot parse Exec from {desktop_file}, skipping {f}")
        return

    try:
        subprocess.Popen(exec_cmd + [str(f)])
    except Exception as e:
        print(f"Failed to open {f} with {exec_cmd}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: xdg-open.py <file1> [file2 ...]")
        sys.exit(1)

    mime_map = read_mimeapps()
    for file_path in sys.argv[1:]:
        open_file(file_path, mime_map)

if __name__ == "__main__":
    main()
