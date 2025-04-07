# In order to make it work on MacOS
# Create a virtual environment:
# python3 -m venv myenv
#
# Activate the virtual environment:
# source myenv/bin/activate
# 
# Install Pillow within the virtual environment:
# pip install pillow

import argparse
from PIL import Image

def scale_rgb_value(value, bit_depth):
    max_value = (1 << bit_depth) - 1
    return (value * max_value + 127) // 255  # Improved scaling by adding 127 for rounding

def adjust_color_values(r, g, b):
    # Adjust the red and blue values slightly
    adjusted_r = min(r, 255)  # Increase red slightly
    adjusted_b = max(b - 50, 0)    # Decrease blue slightly
    return adjusted_r, g, adjusted_b

def convert_to_rgb565(image_path, output_width, output_height):
    try:
        # Open the image file specified by the user
        bitmap = Image.open(image_path)
        # Ensure the image is in RGBA mode to handle alpha channel
        bitmap = bitmap.convert("RGBA")
        
        # Resize the image to the desired dimensions
        bitmap = bitmap.resize((output_width, output_height), Image.LANCZOS)
        
        # Get image dimensions
        width, height = bitmap.size
        
        # Create a list to store the RGB565 data
        rgb565_data = []
        
        for y in range(height):
            for x in range(width):
                # Get RGBA color tuple at pixel (x, y)
                r, g, b, a = bitmap.getpixel((x, y))
                # If alpha is 0 (completely transparent), treat as black
                if a == 0:
                    r, g, b = 255, 255, 255
                else:
                    # Adjust the color values slightly
                    r, g, b = adjust_color_values(r, g, b)
                # Scale RGB values to their respective bit depths
                # r5 = scale_rgb_value(r, 5)
                # g6 = scale_rgb_value(g, 6)
                # b5 = scale_rgb_value(b, 5)
                # Combine into RGB565 format
                rgb565 = ((b & 0xF8) << 8) | ((g & 0xFC) << 3) | (r >> 3) #; (b5 << 11) | (g6 << 5) | r5
                                
                rgb565_data.append(rgb565)

        # Generate the Arduino array
        filename = image_path.rsplit('.', 1)[0]
        # arduino_array = "const uint16_t " + filename +"Symbol[" + str(output_width) +" * " + str(output_height) + "] PROGMEM = {\n"
        arduino_array = "const uint16_t " + filename +"Symbol[imageWidth * imageHeight] PROGMEM = {\n"
        for i, value in enumerate(rgb565_data):
            if i % output_width == 0:
                arduino_array += "\n"
            arduino_array += "0x{:04X}, ".format(value)
        arduino_array = arduino_array.rstrip(", ") + "\n};\n"

        # Save the Arduino array to a file
        output_file = filename + '_arduino_array.txt'
        with open(output_file, 'w') as f:
            f.write(arduino_array)
        
        print(f"Arduino array saved to {output_file}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert a bitmap image to RGB565 format for Arduino.')
    parser.add_argument('image_path', help='Path to the input image file')
    parser.add_argument('output_width', type=int, help='Desired width of the output image')
    parser.add_argument('output_height', type=int, help='Desired height of the output image')
    args = parser.parse_args()
    convert_to_rgb565(args.image_path, args.output_width, args.output_height)
