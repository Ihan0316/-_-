from PIL import Image
import glob
import os
from tqdm import tqdm

DATA_PATH = '/Users/ihanjo/Documents/미니 프로젝트/한국음식 예측/데이터/한국 음식 이미지/kfood'

print(f"데이터셋 정리 및 변환 시작...")
print(f"대상 경로: {os.path.abspath(DATA_PATH)}")
print("-" * 30)

# 모든 jpg, png, jpeg 파일을 찾습니다.
image_files = glob.glob(os.path.join(DATA_PATH, '**', '*.*'), recursive=True)
image_files = [f for f in image_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'))]

converted_count = 0
# tqdm을 사용하여 진행률 표시
for file_path in tqdm(image_files, desc="파일 변환 중"):
    try:
        # 파일 경로에서 파일명과 확장자 분리
        dir_name, file_name = os.path.split(file_path)
        base_name, ext = os.path.splitext(file_name)

        with Image.open(file_path) as img:
            # 변환이 필요한지 상태를 저장할 변수
            needs_save = False

            # 원본 이미지의 포맷과 모드를 저장
            original_format = img.format
            original_mode = img.mode

            # 이미지가 RGB 모드가 아니면 RGB로 변환
            if original_mode != 'RGB':
                img = img.convert('RGB')
                needs_save = True

            # 포맷이 JPEG가 아니거나 확장자가 .jpg가 아닌 경우 저장 필요
            if original_format != 'JPEG' or ext.lower() != '.jpg':
                needs_save = True

            # 변환이 필요한 경우에만 저장 로직을 실행
            if needs_save:
                # 새로운 파일 경로 (.jpg로 통일)
                new_file_path = os.path.join(dir_name, base_name + '.jpg')

                # ==================== 핵심 수정 부분 ====================
                # 만약 저장할 경로에 파일이 이미 존재한다면, 새 이름을 만듭니다.
                # (단, 자기 자신을 덮어쓰는 경우는 제외)
                if os.path.exists(new_file_path) and file_path != new_file_path:
                    counter = 1
                    # 중복되지 않는 새 이름을 찾을 때까지 반복합니다.
                    while True:
                        new_base_name = f"{base_name}_{counter}"
                        new_file_path = os.path.join(dir_name, new_base_name + '.jpg')
                        if not os.path.exists(new_file_path):
                            break  # 유니크한 이름을 찾았으면 반복 중단
                        counter += 1
                # ======================================================

                img.save(new_file_path, 'JPEG')
                converted_count += 1

                # 원본 파일과 새 파일 경로가 다르면 (즉, .png -> .jpg 변환 등) 원본 삭제
                if file_path != new_file_path:
                    os.remove(file_path)

    except Exception as e:
        print(f"\n⚠️ 처리 오류: {file_path} (오류: {e})")

print("\n" + "=" * 30)
if converted_count > 0:
    print(f"🎉 총 {converted_count}개의 파일을 JPEG/RGB 형식으로 변환 및 정리했습니다.")
else:
    print("🎉 모든 이미지가 이미 JPEG/RGB 형식이므로 추가 작업이 필요 없습니다.")
print("=" * 30)