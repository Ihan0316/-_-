# 이미지 확장자 확인

import os

image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
found_exts = set()

root_dir = '../데이터/한국 음식 이미지/kfood'

for foldername, subfolders, filenames in os.walk(root_dir):
    print(f"Scanning folder: {foldername}")  # 현재 탐색 폴더 출력
    for filename in filenames:
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        print(f"Checking file: {filename} with extension: {ext}")  # 파일과 확장자 출력
        if ext in image_exts:
            found_exts.add(ext)

if found_exts:
    print("발견된 이미지 확장자:", found_exts)
else:
    print("이미지 확장자 파일을 찾지 못했습니다.")
