# Photo-to-GameBoy

A collection of Python scripts to convert real photos into Game Boy compatible images for use in GB Studio and other Game Boy development projects.

## Features

- **photo_to_gameboy.py**: Converts photos to 4-shade grayscale Game Boy palette
- **photo_to_gbstudio.py**: Converts photos to GB Studio's 4-color background palette
- **convert_all.py**: Batch processes all images through both converters

Both converters support:
- Custom resolution (with automatic 8x8 tile alignment for GB Studio)
- Contrast and sharpness adjustment
- Floyd-Steinberg dithering for improved detail
- Single file or batch directory processing

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Setup

1. Clone or download this repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD)**:
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - **Linux/macOS**:
     ```bash
     source .venv/bin/activate
     ```

4. Install required dependencies:
   ```bash
   pip install Pillow
   ```

## Usage

### Quick Start - Batch Convert All Images

The easiest way to convert multiple images:

1. Place your images in the `picture_to_convert/` directory
2. Run the master converter:
   ```bash
   python convert_all.py
   ```

This will process all images and output them to:
- `converted_to_gameboy/` - 4-shade grayscale versions
- `converted_to_gbstudio/` - GB Studio 4-color palette versions

### Single Image Conversion

#### Game Boy Grayscale (4 shades)

```bash
python photo_to_gameboy.py input.jpg output.png
```

With custom parameters:
```bash
python photo_to_gameboy.py input.jpg output.png --width 160 --height 144 --contrast 1.5
```

#### GB Studio Background (4-color palette)

```bash
python photo_to_gbstudio.py input.jpg background.png
```

With automatic size adjustment and monochrome override:
```bash
python photo_to_gbstudio.py input.jpg background.png --auto-size --mono
```

### Batch Processing

Convert all images in a directory:

```bash
# Game Boy grayscale
python photo_to_gameboy.py input_folder/ output_folder/ --batch

# GB Studio format
python photo_to_gbstudio.py input_folder/ output_folder/ --batch --auto-size
```

## Command Line Options

### photo_to_gameboy.py

| Option | Default | Description |
|--------|---------|-------------|
| `--width` | 160 | Width in pixels |
| `--height` | 144 | Height in pixels |
| `--contrast` | 1.2 | Contrast enhancement (1.0 = normal) |
| `--sharpness` | 1.2 | Sharpness enhancement (1.0 = normal) |
| `--no-dithering` | False | Disable Floyd-Steinberg dithering |
| `--batch` | False | Batch process all images in directory |

### photo_to_gbstudio.py

| Option | Default | Description |
|--------|---------|-------------|
| `--width` | 160 | Width in pixels |
| `--height` | 144 | Height in pixels |
| `--contrast` | 1.2 | Contrast enhancement (1.0 = normal) |
| `--sharpness` | 1.2 | Sharpness enhancement (1.0 = normal) |
| `--no-dithering` | False | Disable Floyd-Steinberg dithering |
| `--auto-size` | False | Auto-adjust to valid 8px multiple |
| `--mono` | False | Create monochrome override (.mono.png) |
| `--batch` | False | Batch process all images in directory |

## GB Studio Requirements

For backgrounds in GB Studio, images must meet these requirements:

- **Dimensions**: Must be multiples of 8 pixels (use `--auto-size` for automatic adjustment)
- **Minimum size**: 160x144 pixels (Game Boy screen resolution)
- **Maximum size**: 2040x2040 pixels
- **Maximum area**: 1048320 pixels
- **Tile limit**: 
  - Monochrome mode: 192 unique 8x8 tiles
  - Color mode: 384 unique 8x8 tiles

The scripts will automatically validate these requirements and show warnings if exceeded.

## Examples

### Standard Game Boy screen
```bash
python photo_to_gameboy.py photo.jpg gameboy.png
```

### Small sprite (32x32)
```bash
python photo_to_gameboy.py portrait.jpg sprite.png --width 32 --height 32
```

### Large scrolling background for GB Studio
```bash
python photo_to_gbstudio.py landscape.jpg level_bg.png --width 512 --height 288 --auto-size
```

### High contrast conversion with monochrome support
```bash
python photo_to_gbstudio.py photo.jpg background.png --contrast 1.5 --mono
```

### Batch convert vacation photos
```bash
python convert_all.py
# Or manually:
python photo_to_gameboy.py vacation_photos/ gameboy_output/ --batch
python photo_to_gbstudio.py vacation_photos/ gbstudio_output/ --batch --auto-size
```

## Supported Image Formats

Input formats: JPG, JPEG, PNG, BMP, GIF, WEBP

Output format: PNG (with appropriate palette)

## Tips for Best Results

1. **Use high contrast images**: Photos with clear subject separation work best
2. **Increase contrast**: Try `--contrast 1.5` for better visibility
3. **Enable dithering**: Keeps more detail in complex images (enabled by default)
4. **Proper lighting**: Well-lit photos convert better than dark or backlit ones
5. **Simple compositions**: Images with fewer details translate better to limited palettes

## Directory Structure

```
Photo-to-GameBoy/
├── picture_to_convert/      # Place input images here
├── converted_to_gameboy/    # Game Boy grayscale output
├── converted_to_gbstudio/   # GB Studio palette output
├── photo_to_gameboy.py      # Grayscale converter
├── photo_to_gbstudio.py     # GB Studio converter
├── convert_all.py           # Master batch converter
└── README.md
```

## Troubleshooting

### "No module named 'PIL'"
Install Pillow: `pip install Pillow`

### "can't open file"
Make sure you're using the correct file extension (.py not .ppy)

### Virtual environment not activating (Windows)
Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Tiles exceed limit warning
- Reduce image complexity before conversion
- Use `--no-dithering` to reduce unique tiles
- Simplify the source image (blur, reduce details)

## License

Created by [towelie8](https://github.com/towelie8)

## Contributing

Contributions, issues, and feature requests are welcome.