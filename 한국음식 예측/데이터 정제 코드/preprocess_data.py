# 데이터 정리를 위한 라이브러리 임포트
from pathlib import Path
from PIL import Image

# --- 설정 ---
# 작업할 기본 데이터 경로를 설정합니다.
BASE_DATA_PATH = "../데이터/한국 음식 이미지/kfood"


def standardize_images_in_place(data_path):
    """
    지정된 경로와 그 하위의 모든 이미지 파일을 찾아 포맷을 JPG(RGB)로 통일합니다.
    폴더 구조는 변경하지 않습니다.
    """
    base_dir = Path(data_path)
    if not base_dir.is_dir():
        print(f"[오류] 경로를 찾을 수 없습니다: {base_dir}")
        return

    print("이미지 포맷 통일 작업을 시작합니다...")
    print(f"대상 폴더 (하위 폴더 포함): {base_dir}")
    print("-" * 40)

    # rglob을 사용하여 모든 하위 폴더의 파일들을 재귀적으로 탐색합니다.
    all_files = list(base_dir.rglob("*"))

    for filepath in all_files:
        # 폴더나 숨김 파일(.DS_Store 등)은 건너뜁니다.
        if not filepath.is_file() or filepath.name.startswith('.'):
            continue

        try:
            # 이미지 파일 열기
            with Image.open(filepath) as img:
                # 이미지가 RGB 모드가 아니거나, 확장자가 .jpg가 아닌 경우 변환 대상
                if img.mode != 'RGB' or filepath.suffix.lower() not in ['.jpg']:
                    # RGB로 변환
                    rgb_img = img.convert('RGB')
                    # 확장자를 .jpg로 변경한 새로운 경로 생성 (같은 위치에 저장됨)
                    new_filepath = filepath.with_suffix('.jpg')

                    # 새로운 경로에 저장
                    rgb_img.save(new_filepath, 'jpeg', quality=95)

                    # 원본 파일과 새 파일의 경로가 다르면 (즉, 확장자가 변경되었으면) 원본 삭제
                    if filepath != new_filepath:
                        filepath.unlink()  # 원본 파일 삭제
                        print(f"  변환: '{filepath.relative_to(base_dir)}' -> '{new_filepath.relative_to(base_dir)}'")
                    else:
                        # 확장자는 같지만 모드만 변경된 경우
                        print(f"  모드 변환 (RGB): '{filepath.relative_to(base_dir)}'")

        except (IOError, OSError, Image.UnidentifiedImageError) as e:
            # PIL이 이미지로 인식하지 못하거나 손상된 파일 처리
            print(f"  [오류] 손상된 파일 '{filepath.relative_to(base_dir)}': {e}. 파일을 삭제합니다.")
            try:
                filepath.unlink()
            except OSError as e_rem:
                print(f"  [오류] 파일 삭제 실패 '{filepath.name}': {e_rem}")

    print("-" * 40)
    print("✨ 모든 이미지 포맷 통일 작업이 완료되었습니다. ✨")


# --- 스크립트 실행 ---
if __name__ == "__main__":
    standardize_images_in_place(BASE_DATA_PATH)