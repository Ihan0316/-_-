# check_channels.py

from pathlib import Path
from PIL import Image

# --- 설정 ---
# 이미지를 검색할 기본 데이터 경로를 설정합니다.
BASE_DATA_PATH = "../데이터/한국 음식 이미지/kfood"


def find_multi_channel_images(data_path, min_channels=4):
    """
    지정된 경로와 그 하위의 모든 이미지 파일을 확인하여,
    채널 수가 min_channels 이상인 파일의 경로를 출력합니다.
    """
    base_dir = Path(data_path)
    if not base_dir.is_dir():
        print(f"[오류] 경로를 찾을 수 없습니다: {base_dir}")
        return

    print(f"채널이 {min_channels}개 이상인 이미지 검색을 시작합니다...")
    print(f"대상 폴더: {base_dir}")
    print("-" * 40)

    found_files = []
    # rglob을 사용하여 모든 하위 폴더의 파일들을 재귀적으로 탐색
    for filepath in base_dir.rglob("*"):
        # 폴더나 숨김 파일은 건너뛰기
        if not filepath.is_file() or filepath.name.startswith('.'):
            continue

        try:
            # 이미지 파일 열기
            with Image.open(filepath) as img:
                # 이미지의 채널 수 확인
                # img.getbands()는 ('R', 'G', 'B', 'A') 같은 튜플을 반환
                num_channels = len(img.getbands())

                # 채널 수가 기준 이상이면 경로 저장
                if num_channels >= min_channels:
                    # .relative_to()를 사용하면 기준 경로로부터의 상대 경로만 예쁘게 보임
                    relative_path = filepath.relative_to(base_dir)
                    found_files.append(f"  - {relative_path} (모드: {img.mode}, 채널 수: {num_channels})")

        except (IOError, Image.UnidentifiedImageError):
            # PIL이 이미지로 인식하지 못하는 파일은 조용히 무시
            continue

    if found_files:
        print(f"✨ 총 {len(found_files)}개의 {min_channels}채널 이상 이미지를 찾았습니다.")
        for f in found_files:
            print(f)
    else:
        print(f"✨ {min_channels}채널 이상인 이미지를 찾지 못했습니다.")

    print("-" * 40)
    print("검색이 완료되었습니다.")


# --- 스크립트 실행 ---
if __name__ == "__main__":
    find_multi_channel_images(BASE_DATA_PATH)