#!/usr/bin/env python3
"""
Photo to GB Studio Converter
Converts photos to GB Studio-compatible background images with 4-color palette
Author: https://github.com/towelie8
"""

from PIL import Image, ImageEnhance
import sys
import os
import argparse
from collections import defaultdict

# GB Studio Palette (4 Farben für Backgrounds)
GB_STUDIO_PALETTE = [
    (7, 24, 33),      # #071821 - Dunkelblau
    (48, 104, 80),    # #306850 - Dunkelgrün
    (134, 192, 108),  # #86c06c - Hellgrün
    (224, 248, 207),  # #e0f8cf - Creme/Hellgelb
]

def validate_background_size(width, height):
    """
    Validiert die Größe gegen GB Studio Anforderungen

    Args:
        width: Breite in Pixel
        height: Höhe in Pixel

    Returns:
        Tuple (is_valid, warnings) - bool, list of warning strings
    """
    warnings = []

    # Größe muss Vielfaches von 8px sein (Tile-Anforderung)
    if width % 8 != 0:
        warnings.append(f"Warnung: Breite ({width}px) ist kein Vielfaches von 8")
    if height % 8 != 0:
        warnings.append(f"Warnung: Höhe ({height}px) ist kein Vielfaches von 8")

    # Mindestgröße
    if width < 160 or height < 144:
        warnings.append(f"Warnung: Größe ({width}x{height}) ist kleiner als Minimum (160x144)")

    # Maximale Größe
    if width > 2040:
        warnings.append(f"Warnung: Breite ({width}px) überschreitet Maximum (2040px)")
    if height > 2040:
        warnings.append(f"Warnung: Höhe ({height}px) überschreitet Maximum (2040px)")

    # Flächen-Limit
    if width * height > 1048320:
        warnings.append(f"Warnung: Fläche ({width*height}px) überschreitet Maximum (1048320px)")

    is_valid = len(warnings) == 0
    return is_valid, warnings

def auto_adjust_size(width, height):
    """
    Passt Größe auf nächstes gültiges Vielfaches von 8px an

    Args:
        width: Breite in Pixel
        height: Höhe in Pixel

    Returns:
        Tuple (adjusted_width, adjusted_height)
    """
    adjusted_width = (width + 7) // 8 * 8
    adjusted_height = (height + 7) // 8 * 8

    return adjusted_width, adjusted_height

def rgb_to_gb_studio_color(rgb):
    """Konvertiert RGB zu nächster GB Studio Farbe"""
    r, g, b = rgb

    min_distance = float('inf')
    nearest_color = GB_STUDIO_PALETTE[0]

    for color in GB_STUDIO_PALETTE:
        # Euklidische Distanz im RGB-Raum
        distance = (r - color[0])**2 + (g - color[1])**2 + (b - color[2])**2
        if distance < min_distance:
            min_distance = distance
            nearest_color = color

    return nearest_color

def count_unique_tiles(img, tile_size=8):
    """
    Zählt unique 8x8px Tiles im Bild

    Args:
        img: PIL Image
        tile_size: Tile-Größe in Pixel (Standard: 8)

    Returns:
        int - Anzahl der unique Tiles
    """
    tiles = set()
    img_width, img_height = img.size

    for y in range(0, img_height, tile_size):
        for x in range(0, img_width, tile_size):
            # Extrahiere Tile-Daten
            box = (x, y, min(x + tile_size, img_width), min(y + tile_size, img_height))
            tile = img.crop(box)

            # Konvertiere zu Tuple für Hashability
            tile_data = tuple(tile.tobytes())
            tiles.add(tile_data)

    return len(tiles)

def create_monochrome_override(img, output_path):
    """
    Erstellt monochrome Version des Bildes

    Args:
        img: PIL Image (RGB)
        output_path: Pfad zum Output-Bild
    """
    # Konvertiere zu Grayscale
    mono_img = img.convert('L')

    # Speichere als .mono.png
    base_name = os.path.splitext(output_path)[0]
    mono_output = f"{base_name}_mono.png"
    mono_img.save(mono_output, 'PNG')
    return mono_output

def convert_to_gbstudio(input_path, output_path, width=None, height=None,
                        contrast=1.2, sharpness=1.2, dithering=True,
                        auto_size=False, mono=False):
    """
    Konvertiert ein Foto zu GB Studio Format

    Args:
        input_path: Pfad zum Input-Bild
        output_path: Pfad zum Output-Bild
        width: Zielbreite in Pixel (Standard: 160)
        height: Zielhöhe in Pixel (Standard: 144)
        contrast: Kontrast-Verstärkung (1.0 = normal)
        sharpness: Schärfe (1.0 = normal)
        dithering: Floyd-Steinberg Dithering verwenden
        auto_size: Automatisch auf gültiges Vielfaches von 8px anpassen
        mono: Monochrome Override erstellen
    """

    # Standardwerte setzen
    if width is None:
        width = 160
    if height is None:
        height = 144

    print(f"Lade Bild: {input_path}")

    try:
        # Bild laden
        img = Image.open(input_path)

        # Zu RGB konvertieren
        if img.mode != 'RGB':
            img = img.convert('RGB')

        print(f"   Original: {img.size[0]}x{img.size[1]} Pixel")

        # Size Validation vor Anpassung
        valid, warnings = validate_background_size(width, height)
        if not valid and not auto_size:
            for warning in warnings:
                print(f"   {warning}")

        # Auto-Anpassung wenn gewünscht
        if auto_size:
            old_width, old_height = width, height
            width, height = auto_adjust_size(width, height)
            if (old_width, old_height) != (width, height):
                print(f"   Auto-angepasst: {old_width}x{old_height} -> {width}x{height}")

        # Kontrast und Schärfe verbessern
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)

        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(sharpness)

        # Auf Zielgröße skalieren
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        print(f"   Skaliert: {width}x{height} Pixel")

        # Zu GB Studio 4-Farben Palette konvertieren
        print("   Konvertiere zu GB Studio Palette...")

        if dithering:
            print("   Wende Dithering an...")
            # Nutze PIL's quantize mit Dithering zur GB Studio Palette
            # Erstelle Palette: 4 Farben * 3 Kanäle (RGB)
            palette_data = []
            for color in GB_STUDIO_PALETTE:
                palette_data.extend(color)

            # Quantisiere mit Floyd-Steinberg Dithering
            img_indexed = img.quantize(colors=4, dither=Image.Dither.FLOYDSTEINBERG)

            # Erstelle neue Palette mit GB Studio Farben
            img_indexed.putpalette(palette_data)
            img_output = img_indexed.convert('RGB')
        else:
            # Direkte Quantisierung ohne Dithering
            img_output = Image.new('RGB', (width, height))
            pixels_out = img_output.load()

            for y in range(height):
                for x in range(width):
                    rgb_pixel = img.getpixel((x, y))
                    gb_color = rgb_to_gb_studio_color(rgb_pixel)
                    pixels_out[x, y] = gb_color

        # Tile-Analyse
        unique_tiles = count_unique_tiles(img_output)
        tile_warning = ""
        if unique_tiles > 384:
            tile_warning = " (WARNUNG: über 384 Tiles für Color Only Mode)"
        elif unique_tiles > 192:
            tile_warning = " (WARNUNG: über 192 Tiles für Monochrome Mode)"

        print(f"   Tile-Analyse: {unique_tiles} unique 8x8px Tiles{tile_warning}")

        # Speichern
        img_output.save(output_path, 'PNG')
        print(f"Gespeichert: {output_path}")
        print(f"   Format: {width}x{height} PNG, GB Studio kompatibel")

        # Monochrome Override wenn gewünscht
        if mono:
            mono_path = create_monochrome_override(img_output, output_path)
            print(f"Monochrome Override: {mono_path}")

        return True

    except Exception as e:
        print(f"Fehler: {e}")
        return False

def batch_convert(input_dir, output_dir, **kwargs):
    """Konvertiert alle Bilder in einem Ordner"""

    os.makedirs(output_dir, exist_ok=True)

    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')
    files = [f for f in os.listdir(input_dir)
             if f.lower().endswith(supported_formats)]

    print(f"\nBatch-Konvertierung: {len(files)} Dateien gefunden\n")

    success_count = 0
    for i, filename in enumerate(files, 1):
        input_path = os.path.join(input_dir, filename)
        output_filename = os.path.splitext(filename)[0] + '_gb.png'
        output_path = os.path.join(output_dir, output_filename)

        print(f"[{i}/{len(files)}] {filename}")

        if convert_to_gbstudio(input_path, output_path, **kwargs):
            success_count += 1
        print()

    print(f"\nFertig! {success_count}/{len(files)} Bilder erfolgreich konvertiert")

def main():
    parser = argparse.ArgumentParser(
        description='Konvertiert Fotos zu GB Studio kompatiblen Backgrounds'
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
    parser.add_argument('--auto-size', action='store_true',
                       help='Automatisch auf gültiges Vielfaches von 8px anpassen')
    parser.add_argument('--mono', action='store_true',
                       help='Monochrome Override (.mono.png) erstellen')
    parser.add_argument('--batch', action='store_true',
                       help='Batch-Modus: Alle Bilder in Ordner konvertieren')

    args = parser.parse_args()

    kwargs = {
        'width': args.width,
        'height': args.height,
        'contrast': args.contrast,
        'sharpness': args.sharpness,
        'dithering': not args.no_dithering,
        'auto_size': args.auto_size,
        'mono': args.mono
    }

    if args.batch:
        batch_convert(args.input, args.output, **kwargs)
    else:
        convert_to_gbstudio(args.input, args.output, **kwargs)

if __name__ == "__main__":
    # Beispiele zeigen wenn ohne Argumente aufgerufen
    if len(sys.argv) == 1:
        print("Photo to GB Studio Converter\n")
        print("Verwendung:")
        print("  python3 photo_to_gbstudio.py foto.jpg szene.png")
        print("\nOptionen:")
        print("  --width 160        Breite (Standard: 160)")
        print("  --height 144       Höhe (Standard: 144)")
        print("  --contrast 1.5     Kontrast erhöhen")
        print("  --sharpness 1.3    Schärfe erhöhen")
        print("  --no-dithering     Ohne Dithering")
        print("  --auto-size        Automatisch auf gültiges Vielfaches von 8px anpassen")
        print("  --mono             Monochrome Override (.mono.png) erstellen")
        print("  --batch            Alle Bilder in Ordner konvertieren")
        print("\nBeispiele:")
        print("  # Einzelnes Bild mit Standard-Größe")
        print("  python3 photo_to_gbstudio.py foto.jpg szene.png")
        print("\n  # Mit Monochrome Override für GB Classic")
        print("  python3 photo_to_gbstudio.py foto.jpg szene.png --mono")
        print("\n  # Custom Größe mit Auto-Anpassung")
        print("  python3 photo_to_gbstudio.py foto.jpg szene.png --width 320 --height 288 --auto-size")
        print("\n  # Batch-Konvertierung")
        print("  python3 photo_to_gbstudio.py fotos/ assets/backgrounds/ --batch")
        print("\n  # Mit erhöhtem Kontrast und Monochrome Override")
        print("  python3 photo_to_gbstudio.py foto.jpg szene.png --contrast 1.5 --mono")
        sys.exit(0)

    main()
