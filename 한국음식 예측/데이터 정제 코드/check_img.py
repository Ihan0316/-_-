import os

image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
found_exts = set()

root_dir = '/Users/ihanjo/Library/CloudStorage/GoogleDrive-ihann5726@gmail.com/내 드라이브/인공지능 사관학교/Coding/미니프로젝트/한국음식 예측/데이터'  # 탐색할 폴더 경로 (필요하면 변경)

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
