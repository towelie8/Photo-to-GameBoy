#!/usr/bin/env python3
"""
Master Converter - Führt beide Konverter auf alle Bilder aus
"""

import subprocess
import sys
import os

def run_conversion():
    """Führt beide Konverter nacheinander aus"""
    
    # Pfade definieren
    input_dir = "picture_to_convert"
    gameboy_output = "converted_to_gameboy"
    gbstudio_output = "converted_to_gbstudio"
    
    print("=" * 60)
    print("Game Boy Konverter - Master Script")
    print("=" * 60)
    print()
    
    # Prüfe ob Input-Ordner existiert
    if not os.path.exists(input_dir):
        print(f"Fehler: Ordner '{input_dir}' nicht gefunden!")
        return False
    
    # Zähle Bilder
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')
    files = [f for f in os.listdir(input_dir) 
             if f.lower().endswith(supported_formats)]
    
    if not files:
        print(f"Keine Bilder in '{input_dir}' gefunden!")
        return False
    
    print(f"Gefunden: {len(files)} Bilder")
    print()
    
    # 1. Game Boy Konvertierung
    print("=" * 60)
    print("SCHRITT 1: Game Boy Konvertierung (4 Graustufen)")
    print("=" * 60)
    print()
    
    try:
        result = subprocess.run([
            sys.executable,
            "photo_to_gameboy.py",
            input_dir,
            gameboy_output,
            "--batch"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Fehler bei Game Boy Konvertierung: {e}")
        return False
    
    print()
    
    # 2. GB Studio Konvertierung
    print("=" * 60)
    print("SCHRITT 2: GB Studio Konvertierung (4-Farben-Palette)")
    print("=" * 60)
    print()
    
    try:
        result = subprocess.run([
            sys.executable,
            "photo_to_gbstudio.py",
            input_dir,
            gbstudio_output,
            "--batch",
            "--auto-size"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Fehler bei GB Studio Konvertierung: {e}")
        return False
    
    print()
    print("=" * 60)
    print("FERTIG! Alle Bilder wurden konvertiert")
    print("=" * 60)
    print()
    print(f"Game Boy Bilder: {gameboy_output}/")
    print(f"GB Studio Bilder: {gbstudio_output}/")
    print()
    
    return True

if __name__ == "__main__":
    success = run_conversion()
    sys.exit(0 if success else 1)