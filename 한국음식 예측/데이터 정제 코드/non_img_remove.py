# 이미지가 아닌 파일 삭제

import os

# 삭제하고 싶은 폴더의 경로 입력
folder_path = '../데이터/한국 음식 이미지/kfood'

image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']

# 모든 하위 폴더 돌면서 파일 삭제
for root, dirs, files in os.walk(folder_path):
    for filename in files:
        file_path = os.path.join(root, filename)
        _, ext = os.path.splitext(filename)
        if ext.lower() not in image_extensions:
            try:
                os.remove(file_path)
                print(f"삭제됨: {file_path}")
            except Exception as e:
                print(f"에러: {file_path}, {e}")
