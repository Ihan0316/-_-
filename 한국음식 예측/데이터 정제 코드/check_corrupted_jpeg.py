# find_corrupted_and_warning_files.py

import warnings
from pathlib import Path
from PIL import Image, ImageFile
from tqdm import tqdm

# --- 설정 ---
BASE_DATA_PATH = "/Users/ihanjo/Documents/미니 프로젝트/한국음식 예측/데이터/한국 음식 이미지/kfood"


def find_problematic_images(data_path):
    """
    지정된 경로와 그 하위에서 손상되었거나 경고를 발생시키는 모든 이미지 파일을 찾습니다.
    """
    base_dir = Path(data_path)
    if not base_dir.is_dir():
        print(f"[오류] 경로를 찾을 수 없습니다: {base_dir}")
        return

    print("손상 및 경고 유발 이미지 파일 검색을 시작합니다...")
    print(f"대상 폴더: {base_dir}")
    print("-" * 40)

    # 모든 이미지 확장자 검색
    image_files = [p for p in base_dir.rglob("*") if p.suffix.lower() in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg')]
    if not image_files:
        print("검색할 이미지 파일이 없습니다.")
        return

    problem_files = []
    for filepath in tqdm(image_files, desc="이미지 파일 검사 중"):
        problem_found = False
        try:
            # 경고를 잡아내기 위한 컨텍스트 매니저
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")  # 모든 경고를 항상 표시하도록 설정

                img = Image.open(filepath)
                img.verify()

                # 만약 경고가 발생했다면, 리스트 w에 기록됨
                if w:
                    problem_found = True
                    relative_path = filepath.relative_to(base_dir)
                    # 가장 첫 번째 경고 메시지를 사유로 기록
                    reason = str(w[0].message)
                    problem_files.append(f"  - {relative_path} (사유: 경고 발생 - {reason})")

        except (IOError, SyntaxError, Image.UnidentifiedImageError) as e:
            # 심각한 에러가 발생한 경우
            problem_found = True
            relative_path = filepath.relative_to(base_dir)
            problem_files.append(f"  - {relative_path} (사유: 에러 발생 - {e})")

    if problem_files:
        print(f"\n❌ 총 {len(problem_files)}개의 문제 파일을 찾았습니다.")
        for f in problem_files:
            print(f)
    else:
        print("\n🎉 검증 완료: 문제 파일을 찾지 못했습니다.")

    print("-" * 40)
    print("검색이 완료되었습니다.")


# --- 스크립트 실행 ---
if __name__ == "__main__":
    find_problematic_images(BASE_DATA_PATH)