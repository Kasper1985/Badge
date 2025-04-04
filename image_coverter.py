import argparse
from pathlib import Path
from PIL import Image

def load_image(file_path, width, height):
    """
    Load an image (BMP or JPEG) and extract pixel data.
    """
    print(f"Loading image from {file_path} ...")

    # Open the image
    img = Image.open(file_path)

    img = img.convert("L") # Convert to grayscale

    # Crop the image to the specified width and height
    crop_box = (0, 0, width, height)
    img = img.crop(crop_box)
    print(f"Image cropped to {width}x{height}")

    # Extract pixel data as a flat list
    pixel_data = list(img.getdata())

    print(f"Image loaded successfully.")
    return pixel_data


def process_pixels(pixels, depth):
    """
    Process pixel values to scale them to the specified depth in bits.
    
    :param pixels: List of grayscale pixel values (0-255).
    :param depth: Depth in bits (e.g., 1, 2, 4, 8).
    :return: List of scaled pixel values as hex strings.
    """
    hex_data = []

    # Calculate the number of levels based on the depth in bits
    levels = 2 ** depth

    # Scale each pixel value to the specified depth
    scaled_pixels = [min(int(pixel / 256 * levels), levels - 1) for pixel in pixels]

    # Pack scaled pixels into bytes
    pixels_per_byte = 8 // depth # Number of pixels that fit into one byte
    for i in range(0, len(scaled_pixels), pixels_per_byte):
        byte = 0
        for j in range(pixels_per_byte):
            if i + j < len(scaled_pixels):
                # Shift the pixel value to its position in the byte
                byte |= scaled_pixels[i + j] << (8 - depth * (j + 1))
        hex_data.append(f"0x{byte:02X}")


    return hex_data


def write_file(output_path, hex_data, width, height, depth):
    """
    Write the hex data to a file.
    """
    print(f"Writing hex data ...")
    with open(output_path, "w") as file:
        file.write("#define width " + str(width) + "\n")
        file.write("#define height " + str(height) + "\n")
        file.write("#define depth " + str(depth) + "\n")
        cnt = 0
        for hex_byte in hex_data:
            file.write(f"{hex_byte[2:]} ")
            cnt += 1
            if cnt % (width / (8 / depth)) == 0:
                file.write("\n")

    print(f"Hex data written successfully to {output_path}.")


def convert_image(image_path, output_path, width, height, depth):
    # Load the image
    pixels = load_image(image_path, width, height)

    # convert the pixel list to a hex list
    hex_data = process_pixels(pixels, depth)

    # Write the hex data to a file
    write_file(output_path, hex_data, width, height, depth)

if __name__=='__main__':
    # Getting input paramenters
    parser = argparse.ArgumentParser(description="Convert an image to hex data for e-paper displays.")
    parser.add_argument("image_path", type=str, help="Path to the input image (BMP or JPEG).")
    parser.add_argument("width", type=int, help="Width of the image in pixels.")
    parser.add_argument("height", type=int, help="Height of the image in pixels.")
    parser.add_argument("depth", type=int, choices=[1, 2, 4, 8], help="Color depth in bits (1, 2, 4, or 8).")

    # Parse arguments
    args = parser.parse_args()

    # Generate the output file path
    input_path = Path(args.image_path)
    output_file_name = f"{input_path.stem}_{args.width}x{args.height}_{args.depth}bit.xbm"
    output_path = input_path.parent / output_file_name

    # Convert the image
    convert_image(args.image_path, output_path, args.width, args.height, args.depth)

