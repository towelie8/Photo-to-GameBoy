#!/usr/bin/env python3
"""
Photo to Game Boy Converter
Author: https://github.com/towelie8
"""

from PIL import Image, ImageEnhance
import sys
import os
import argparse

# Game Boy Palette (4 Graustufen)
GB_PALETTE = [
    (255, 255, 255),  # Weiß
    (170, 170, 170),  # Hellgrau
    (85, 85, 85),     # Dunkelgrau
    (0, 0, 0),        # Schwarz
]

def rgb_to_gb_color(rgb):
    """Konvertiert RGB zu nächster GB Farbe"""
    r, g, b = rgb
    # Helligkeit berechnen
    brightness = (r + g + b) / 3
    
    # Zu nächster GB Farbe mappen
    if brightness > 191:
        return GB_PALETTE[0]  # Weiß
    elif brightness > 127:
        return GB_PALETTE[1]  # Hellgrau
    elif brightness > 63:
        return GB_PALETTE[2]  # Dunkelgrau
    else:
        return GB_PALETTE[3]  # Schwarz

def convert_to_gameboy(input_path, output_path, width=160, height=144, 
                       contrast=1.2, sharpness=1.2, dithering=True):
    """
    Konvertiert ein Foto zu Game Boy Format
    
    Args:
        input_path: Pfad zum Input-Bild
        output_path: Pfad zum Output-Bild
        width: Zielbreite (Standard: 160 = voller GB Screen)
        height: Zielhöhe (Standard: 144 = voller GB Screen)
        contrast: Kontrast-Verstärkung (1.0 = normal, höher = mehr Kontrast)
        sharpness: Schärfe (1.0 = normal)
        dithering: Floyd-Steinberg Dithering für mehr Details
    """
    
    print(f"📸 Lade Bild: {input_path}")
    
    try:
        # Bild laden
        img = Image.open(input_path)
        
        # Zu RGB konvertieren (falls RGBA oder andere Formate)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        print(f"   Original: {img.size[0]}x{img.size[1]} Pixel")
        
        # Kontrast und Schärfe verbessern (hilft bei der Konvertierung)
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)
        
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(sharpness)
        
        # Auf Zielgröße skalieren (mit gutem Resampling)
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        print(f"   Skaliert: {width}x{height} Pixel")
        
        # Zu Graustufen konvertieren
        img = img.convert('L')
        
        if dithering:
            # Floyd-Steinberg Dithering für bessere Details
            print("   Wende Dithering an...")
            img = img.convert('1', dither=Image.Dither.FLOYDSTEINBERG)
            img = img.convert('L')
        
        # Zu GB 4-Farben Palette konvertieren
        print("   Konvertiere zu Game Boy Palette...")
        pixels = img.load()
        
        for y in range(height):
            for x in range(width):
                gray = pixels[x, y]
                # Zu nächster GB Farbe
                if gray > 191:
                    pixels[x, y] = 255
                elif gray > 127:
                    pixels[x, y] = 170
                elif gray > 63:
                    pixels[x, y] = 85
                else:
                    pixels[x, y] = 0
        
        # Zurück zu RGB für PNG-Export
        img = img.convert('RGB')
        
        # Speichern
        img.save(output_path, 'PNG')
        print(f"✅ Gespeichert: {output_path}")
        print(f"   Format: {width}x{height} PNG, 4 Graustufen")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

def batch_convert(input_dir, output_dir, **kwargs):
    """Konvertiert alle Bilder in einem Ordner"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')
    files = [f for f in os.listdir(input_dir) 
             if f.lower().endswith(supported_formats)]
    
    print(f"\n📁 Batch-Konvertierung: {len(files)} Dateien gefunden\n")
    
    success_count = 0
    for i, filename in enumerate(files, 1):
        input_path = os.path.join(input_dir, filename)
        output_filename = os.path.splitext(filename)[0] + '_gb.png'
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"[{i}/{len(files)}] {filename}")
        
        if convert_to_gameboy(input_path, output_path, **kwargs):
            success_count += 1
        print()
    
    print(f"\n✨ Fertig! {success_count}/{len(files)} Bilder erfolgreich konvertiert")

def main():
    parser = argparse.ArgumentParser(
        description='Konvertiert Fotos zu Game Boy kompatiblen Bildern'
    )
    
    parser.add_argument('input', help='Input-Bild oder Ordner')
    parser.add_argument('output', help='Output-Bild oder Ordner')
    parser.add_argument('--width', type=int, default=160, 
                       help='Breite in Pixel (Standard: 160)')
    parser.add_argument('--height', type=int, default=144, 
                       help='Höhe in Pixel (Standard: 144)')
    parser.add_argument('--contrast', type=float, default=1.2,
                       help='Kontrast-Verstärkung (Standard: 1.2)')
    parser.add_argument('--sharpness', type=float, default=1.2,
                       help='Schärfe (Standard: 1.2)')
    parser.add_argument('--no-dithering', action='store_true',
                       help='Kein Dithering verwenden')
    parser.add_argument('--batch', action='store_true',
                       help='Batch-Modus: Alle Bilder in Ordner konvertieren')
    
    args = parser.parse_args()
    
    kwargs = {
        'width': args.width,
        'height': args.height,
        'contrast': args.contrast,
        'sharpness': args.sharpness,
        'dithering': not args.no_dithering
    }
    
    if args.batch:
        batch_convert(args.input, args.output, **kwargs)
    else:
        convert_to_gameboy(args.input, args.output, **kwargs)

if __name__ == "__main__":
    # Beispiele zeigen wenn ohne Argumente aufgerufen
    if len(sys.argv) == 1:
        print("📸 Photo to Game Boy Converter\n")
        print("Verwendung:")
        print("  python3 photo_to_gameboy.py foto.jpg foto_gb.png")
        print("\nOptionen:")
        print("  --width 160        Breite (Standard: 160)")
        print("  --height 144       Höhe (Standard: 144)")
        print("  --contrast 1.5     Kontrast erhöhen")
        print("  --sharpness 1.3    Schärfe erhöhen")
        print("  --no-dithering     Ohne Dithering")
        print("  --batch            Alle Bilder in Ordner konvertieren")
        print("\nBeispiele:")
        print("  # Einzelnes Bild")
        print("  python3 photo_to_gameboy.py portrait.jpg portrait_gb.png")
        print("\n  # Kleineres Bild für Sprite")
        print("  python3 photo_to_gameboy.py katze.jpg katze_gb.png --width 32 --height 32")
        print("\n  # Batch-Konvertierung")
        print("  python3 photo_to_gameboy.py fotos/ fotos_gb/ --batch")
        print("\n  # Mehr Kontrast für bessere Sichtbarkeit")
        print("  python3 photo_to_gameboy.py foto.jpg foto_gb.png --contrast 1.5")
        sys.exit(0)
    
    main()
