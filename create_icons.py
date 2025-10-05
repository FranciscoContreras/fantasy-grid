#!/usr/bin/env python3
"""
Create basic placeholder icons for Fantasy Grid PWA
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple icon with the Fantasy Grid logo text"""
    # Create image with dark background
    img = Image.new('RGB', (size, size), color='#1a1a1a')
    draw = ImageDraw.Draw(img)

    # Try to use a built-in font, fallback to default
    try:
        # Use a reasonably sized font based on icon size
        font_size = max(12, size // 8)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Draw "FG" text in center
    text = "FG"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (size - text_width) // 2
    y = (size - text_height) // 2

    # Draw text in green (Fantasy Grid brand color)
    draw.text((x, y), text, fill='#22c55e', font=font)

    # Save the icon
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

def main():
    """Create all required icons for the PWA"""
    icon_sizes = [72, 96, 128, 144, 152, 192, 384, 512]

    for size in icon_sizes:
        filename = f"app/static/icons/icon-{size}x{size}.png"
        create_icon(size, filename)

    print(f"\n✅ Created {len(icon_sizes)} PWA icons")
    print("Icons created with 'FG' text on dark background")

if __name__ == "__main__":
    main()