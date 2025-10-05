#!/usr/bin/env python3
"""
Create Pilon PWA icons from the vector logo
"""
from PIL import Image, ImageDraw
import os

def svg_to_png(svg_path, size, output_path):
    """Convert SVG to PNG with specified size"""
    try:
        # Try to use cairosvg if available
        import cairosvg
        cairosvg.svg2png(
            url=svg_path,
            write_to=output_path,
            output_width=size,
            output_height=size,
            background_color='white'
        )
        print(f"Created {output_path} ({size}x{size}) using cairosvg")
        return True
    except ImportError:
        print("cairosvg not available, falling back to simple method")
        return False

def create_simple_icon(size, output_path):
    """Create a simple Pilon icon fallback"""
    # Create image with white background
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)

    # Draw a simple "P" shape inspired by the logo
    # Calculate proportions based on size
    margin = size // 8
    stroke_width = max(2, size // 20)

    # Main vertical line of P
    x1 = margin
    y1 = margin
    x2 = x1
    y2 = size - margin

    # Top horizontal line
    x3 = x1
    y3 = y1
    x4 = size - margin * 2
    y4 = y3

    # Middle horizontal line (for P shape)
    x5 = x1
    y5 = size // 2
    x6 = size - margin * 2.5
    y6 = y5

    # Draw the P shape
    draw.rectangle([x1, y1, x1 + stroke_width, y2], fill='#000000')  # Vertical line
    draw.rectangle([x1, y1, x4, y1 + stroke_width], fill='#000000')  # Top line
    draw.rectangle([x1, y5, x6, y5 + stroke_width], fill='#000000')  # Middle line
    draw.rectangle([x4 - stroke_width, y1, x4, y5 + stroke_width], fill='#000000')  # Right vertical (top half)

    # Save the icon
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, 'PNG')
    print(f"Created {output_path} ({size}x{size}) using simple method")

def main():
    """Create all required icons for the PWA"""
    icon_sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    svg_path = "assets/icon.svg"

    # Check if SVG file exists
    if not os.path.exists(svg_path):
        print(f"Error: {svg_path} not found")
        return

    success_count = 0

    for size in icon_sizes:
        output_path = f"app/static/icons/icon-{size}x{size}.png"

        # Try SVG conversion first, fallback to simple method
        if not svg_to_png(svg_path, size, output_path):
            create_simple_icon(size, output_path)

        success_count += 1

    print(f"\nCreated {success_count} Pilon PWA icons")
    print("Icons created with Pilon branding")

if __name__ == "__main__":
    main()