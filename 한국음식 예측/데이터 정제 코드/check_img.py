import os
from collections import defaultdict

# Define valid image extensions
image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'}

# Dictionary to store the count of each extension
ext_counts = defaultdict(int)

# Root directory of the images
root_dir = '../데이터/한국 음식 이미지/kfood'

# Walk through the directory
for foldername, subfolders, filenames in os.walk(root_dir):
    print(f"Scanning folder: {foldername}")  # Print the currently scanned folder
    for filename in filenames:
        # Split the filename to get the extension
        _, ext = os.path.splitext(filename)
        ext = ext.lower()  # Convert to lowercase for consistency

        # If the extension is a valid image extension, increment the count
        if ext in image_exts:
            ext_counts[ext] += 1
            print(f"Found image: {filename} | extension: {ext}")  # Print found file and its extension

# Check if any images were found and print the counts
if ext_counts:
    print("\n--- 확장자별 이미지 장수 ---")
    for ext, count in ext_counts.items():
        print(f"{ext}: {count}장")
else:
    print("\n이미지 파일을 찾지 못했습니다.")