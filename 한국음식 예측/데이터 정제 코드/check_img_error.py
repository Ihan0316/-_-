import os
from PIL import Image
from tqdm import tqdm

def fix_jpeg_error_recursive(root_folder):
    """
    지정된 폴더와 그 모든 하위 폴더 내의 JPEG 파일에서
    'extraneous bytes' 오류를 찾아 수정합니다.
    """
    if not os.path.isdir(root_folder):
        print(f"오류: '{root_folder}' 폴더를 찾을 수 없습니다.")
        return

    print(f"'{root_folder}'와 모든 하위 폴더의 JPEG 파일을 스캔합니다...")

    # os.walk를 사용하여 모든 하위 폴더의 파일 목록을 먼저 가져옵니다.
    jpeg_files = []
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith(('.jpg', '.jpeg')):
                jpeg_files.append(os.path.join(dirpath, filename))

    if not jpeg_files:
        print("검사할 JPEG 파일이 없습니다.")
        return

    # tqdm으로 진행 상황을 보며 파일을 하나씩 검사합니다.
    for file_path in tqdm(jpeg_files, desc="JPEG 파일 검사 중"):
        try:
            with Image.open(file_path) as img:
                img.load()  # 이미지 데이터를 강제로 읽어 오류 발생 여부 확인

        except (IOError, SyntaxError) as e:
            if 'extraneous bytes' in str(e):
                try:
                    with Image.open(file_path) as img_to_fix:
                        if img_to_fix.mode in ('RGBA', 'P', 'LA'):
                            img_to_fix = img_to_fix.convert('RGB')
                        
                        # quality 옵션을 조절하여 저장할 수 있습니다.
                        img_to_fix.save(file_path, 'jpeg', quality=95)
                
                except Exception as save_e:
                    # tqdm.write는 진행률 표시줄을 방해하지 않고 메시지를 출력합니다.
                    tqdm.write(f"⚠️ 수정 실패: {os.path.basename(file_path)} - {save_e}")
            else:
                tqdm.write(f"🔍 처리 불가 오류: {os.path.basename(file_path)} - {e}")
                
    print("\n✅ 모든 파일 검사가 완료되었습니다.")


# --- 사용 예시 ---
# 이미지가 저장된 최상위 폴더 경로를 지정하세요.
image_folder = "/Users/ihanjo/Documents/미니 프로젝트/한국음식 예측/데이터/한국 음식 이미지/kfood" 
fix_jpeg_error_recursive(image_folder)