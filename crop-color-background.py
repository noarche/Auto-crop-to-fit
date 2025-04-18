from PIL import Image, ImageFile
import os
import time
from tqdm import tqdm
from collections import Counter
from colorama import Fore, init

# Initialize
init(autoreset=True)
ImageFile.LOAD_TRUNCATED_IMAGES = True

def get_edge_color(img, tolerance=5):
    """Detect the most common color on the edges of the image."""
    pixels = img.load()
    w, h = img.size
    edge_pixels = []

    # Top and bottom rows
    for x in range(w):
        edge_pixels.append(pixels[x, 0])
        edge_pixels.append(pixels[x, h - 1])
    
    # Left and right columns
    for y in range(1, h - 1):
        edge_pixels.append(pixels[0, y])
        edge_pixels.append(pixels[w - 1, y])

    # Count colors
    counter = Counter(edge_pixels)
    most_common_color, _ = counter.most_common(1)[0]
    return most_common_color

def crop_by_background_color(img, bg_color, tolerance=5):
    """Crop areas matching the background color with 1px margin."""
    img_data = img.getdata()
    mask_data = []

    def is_similar(c1, c2):
        return all(abs(a - b) <= tolerance for a, b in zip(c1[:3], c2[:3]))  # Ignore alpha

    for pixel in img_data:
        mask_data.append(0 if is_similar(pixel, bg_color) else 255)

    mask = Image.new("L", img.size)
    mask.putdata(mask_data)
    bbox = mask.getbbox()

    if bbox:
        left, upper, right, lower = bbox
        left = max(0, left - 1)
        upper = max(0, upper - 1)
        right = min(img.width, right + 1)
        lower = min(img.height, lower + 1)
        return img.crop((left, upper, right, lower))
    else:
        return img

def crop_logo(image_path):
    """Crop transparent or solid-background images with 1px margin."""
    try:
        img = Image.open(image_path).convert("RGBA")
    except Exception as e:
        print(Fore.RED + f"Failed to open image {image_path}: {e}")
        return None

    if any(pixel[3] < 255 for pixel in img.getdata()):
        bbox = img.split()[-1].getbbox()
        if bbox:
            left, upper, right, lower = bbox
            return img.crop((max(0, left - 1), max(0, upper - 1), min(img.width, right + 1), min(img.height, lower + 1)))
    else:
        bg_color = get_edge_color(img)
        return crop_by_background_color(img, bg_color)

    return img

def process_images(input_dir):
    supported_formats = ('.png', '.webp', '.jpg', '.jpeg')  # Added .jpg and .jpeg
    processed_count = 0
    total_files = len([f for f in os.listdir(input_dir) if f.lower().endswith(supported_formats)])
    original_size = 0
    new_size = 0

    if total_files == 0:
        print(Fore.RED + "No supported files found in the directory.")
        return processed_count, 0

    print(Fore.CYAN + f"Processing {total_files} images...\n")
    start_time = time.time()

    for file in tqdm(os.listdir(input_dir), total=total_files, ncols=80, desc="Progress"):
        if not file.lower().endswith(supported_formats):
            continue

        image_path = os.path.join(input_dir, file)
        temp_path = os.path.join(input_dir, f"_{file}")
        original_size += os.path.getsize(image_path)

        cropped_image = crop_logo(image_path)
        if cropped_image is None:
            continue

        try:
            ext = file.split('.')[-1].lower()
            cropped_image.save(temp_path, format=ext.upper())
            new_size += os.path.getsize(temp_path)
            os.remove(image_path)
            os.rename(temp_path, image_path)
            processed_count += 1
        except Exception as e:
            print(Fore.RED + f"Failed to save image {file}: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)

    end_time = time.time()
    space_saved = (original_size - new_size) / (1024 * 1024)

    print(Fore.GREEN + f"\nTotal files processed: {processed_count}")
    print(Fore.GREEN + f"Time taken: {time.strftime('%H:%M:%S', time.gmtime(end_time - start_time))}")
    print(Fore.GREEN + f"Space saved: {space_saved:.2f} MB\n")

    return processed_count, space_saved

def select_directory():
    while True:
        input_dir = input(Fore.YELLOW + "Enter the directory path (or type 'exit'/'e' to quit): ").strip()
        if input_dir.lower() in ['exit', 'e']:
            print(Fore.RED + "Exiting the script.")
            break
        if os.path.isdir(input_dir):
            processed_count, space_saved = process_images(input_dir)
            print(Fore.MAGENTA + f"\nTotal space saved: {space_saved:.2f} MB")
        else:
            print(Fore.RED + "Invalid directory. Please try again.")

def main():
    select_directory()

if __name__ == "__main__":
    main()
