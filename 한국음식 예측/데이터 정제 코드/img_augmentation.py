import os
import random
from PIL import Image
from torchvision import transforms
from collections import defaultdict
from tqdm import tqdm
import uuid  # 고유 ID 생성을 위한 라이브러리

# ✅ 1. 설정
# ==============================================================================
# 📁 원본 이미지가 들어있는 최상위 경로를 지정하세요.
root_dir = '/Users/ihanjo/Documents/미니 프로젝트/한국음식 예측/데이터/한국 음식 이미지_증강전/kfood' 

# ✨ 증강된 이미지가 저장될 최상위 경로를 지정하세요. (폴더가 없으면 자동 생성됩니다)
output_dir = '/Users/ihanjo/Documents/미니 프로젝트/한국음식 예측/데이터/한국 음식 이미지_증강후/kfood'

# 🎯 각 클래스 폴더마다 확보하고 싶은 최소 이미지 수를 지정하세요.
target_count_per_class = 5000
# ==============================================================================


# ✅ 2. 이미지 증강 변환 정의
# 필요한 변환을 자유롭게 추가하거나 제거할 수 있습니다.
augmentations = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),  # 50% 확률로 좌우 반전
    transforms.RandomRotation(15),           # 최대 15도까지 회전
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),  # 밝기, 대비 등 색상 속성 조정
])

print(f"📁 원본 폴더: {os.path.abspath(root_dir)}")
print(f"✨ 저장 폴더: {os.path.abspath(output_dir)}")
print(f"🎯 클래스별 목표 개수: {target_count_per_class}\n")


# ✅ 3. 클래스별 이미지 확인 및 증강 실행
# 원본 루트 디렉토리의 각 항목(클래스 폴더)을 순회합니다.
for class_name in os.listdir(root_dir):
    class_path = os.path.join(root_dir, class_name)
    
    # 파일은 건너뛰고 디렉토리만 처리합니다.
    if not os.path.isdir(class_path):
        continue
    
    # ✨ 새로운 저장 경로를 설정하고, 폴더가 없으면 생성합니다.
    output_class_path = os.path.join(output_dir, class_name)
    os.makedirs(output_class_path, exist_ok=True)
        
    # 원본 이미지 파일 목록을 가져옵니다 (기존에 증강된 'aug_' 파일은 제외).
    image_files = [f for f in os.listdir(class_path) if f.lower().endswith((".jpg", ".jpeg", ".png")) and not f.startswith("aug_")]
    current_count = len(image_files) # 💡 원본 이미지 개수를 기준으로 판단합니다.

    # --- 증강 로직 ---
    # 현재 이미지 수가 목표치보다 적고, 증강에 사용할 원본 이미지가 있을 경우에만 실행합니다.
    if current_count < target_count_per_class and len(image_files) > 0:
        num_needed = target_count_per_class - current_count
        
        print(f"🔁 '{class_name}' 클래스 증강: {current_count}개 -> {target_count_per_class}개 ({num_needed}개 필요)")
        
        # tqdm을 사용하여 진행률 표시줄을 생성합니다.
        for i in tqdm(range(num_needed), desc=f"{class_name} 처리 중"):
            # 원본 이미지 중에서 무작위로 하나를 선택합니다.
            source_img_name = random.choice(image_files)
            source_img_path = os.path.join(class_path, source_img_name)
            
            try:
                # 원본 이미지를 엽니다.
                with Image.open(source_img_path).convert("RGB") as image:
                    # 정의된 증강 기법을 적용합니다.
                    augmented_image = augmentations(image)
                    
                    # 새롭고 깔끔한 파일 이름을 생성합니다.
                    original_basename, original_ext = os.path.splitext(source_img_name)
                    unique_id = str(uuid.uuid4())[:4]  # 충돌을 방지하기 위한 짧은 고유 ID
                    new_filename = f"aug_{original_basename}_{unique_id}.jpg"
                    
                    # ✨ 저장 경로를 output_class_path로 변경합니다.
                    save_path = os.path.join(output_class_path, new_filename)
                    
                    # 증강된 이미지를 JPEG 형식으로 저장합니다.
                    augmented_image.save(save_path, "JPEG")

            except FileNotFoundError:
                print(f"⚠️ 경고: 원본 파일을 찾을 수 없어 건너뜁니다: {source_img_path}")
            except Exception as e:
                print(f"❗️ {source_img_path} 처리 중 오류 발생: {e}")
                
    elif len(image_files) == 0:
         print(f"⚠️ '{class_name}' 건너뛰기: 증강에 사용할 원본 이미지가 없습니다.")
    else:
        print(f"✅ '{class_name}' 클래스는 이미지가 충분합니다 ({current_count}개).")

print("\n🎉 이미지 증강 작업이 완료되었습니다!")