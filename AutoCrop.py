from PIL import Image, ImageEnhance, ImageOps
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tqdm import tqdm
from colorama import Fore, Style, init
import time


print("AutoCrop - This script will ask for a directory and automatically crop all transparent image background -- the blank space around the img -- so that the image fits perfectly. Crop to fit - Batch Process.")

# Initialize colorama
init(autoreset=True)

def crop_logo(image_path):
    """Function to crop logo images with a 1px margin."""
    img = Image.open(image_path).convert("RGBA")
    
    # Split the image into RGBA channels
    r, g, b, alpha = img.split()
    
    # Find the bounding box of the non-zero regions in the alpha channel
    bbox = alpha.getbbox()
    
    if bbox:
        # Expand the bounding box by 1 pixel on all sides
        left, upper, right, lower = bbox
        left = max(0, left - 1)
        upper = max(0, upper - 1)
        right = min(img.width, right + 1)
        lower = min(img.height, lower + 1)
        
        # Crop the image using the expanded bounding box
        new_img = img.crop((left, upper, right, lower))
        return new_img
    else:
        # If no bounding box found, return the original image
        return img

def process_images(input_dir):
    supported_formats = ('.png', '.webp')
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
        if file.lower().endswith(supported_formats):
            image_path = os.path.join(input_dir, file)
            temp_path = os.path.join(input_dir, f"_{file}")
            
            original_size += os.path.getsize(image_path)
            
            cropped_image = crop_logo(image_path)
            cropped_image.save(temp_path, format=file.split('.')[-1].upper())
            
            new_size += os.path.getsize(temp_path)
            
            os.remove(image_path)
            os.rename(temp_path, image_path)
            processed_count += 1
    
    end_time = time.time()
    time_taken = end_time - start_time
    space_saved = (original_size - new_size) / (1024 * 1024)  # in MB
    
    print(Fore.GREEN + f"\nTotal files processed: {processed_count}")
    print(Fore.GREEN + f"Time taken: {time.strftime('%H:%M:%S', time.gmtime(time_taken))}")
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
