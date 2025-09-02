import os
import shutil
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel

# --- ⚙️ 설정 (사용자 직접 수정) ---

# 1. 검증할 데이터셋의 상위 폴더 경로
DATASET_PATH = '../../데이터/data/kfood'

# 2. 검증 후 신뢰도가 낮은 이미지를 옮겨놓을 폴더 경로
#    (스크립트 실행 시 자동으로 생성됩니다)
OUTPUT_PATH = '../../데이터/data/kfood_low_confidence'

# 3. 신뢰도 임계값 (이 점수 미만인 이미지를 '의심' 파일로 분류)
#    - 너무 높으면 정상 이미지도 걸러낼 수 있으니 0.2 ~ 0.25 정도로 시작하는 것을 추천합니다.
CONFIDENCE_THRESHOLD = 0.22

# 4. CLIP 모델에 사용할 프롬프트 템플릿 (영어가 성능이 더 좋습니다)
PROMPT_TEMPLATE = "a photograph of {}"


def validate_and_filter_dataset(dataset_path, output_path, threshold):
    """
    데이터셋의 각 이미지를 CLIP으로 평가하여, 레이블과의 신뢰도 점수가
    설정된 임계값보다 낮은 이미지를 별도의 폴더로 이동시킵니다.
    """
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"✅ Using device: {device}")

    # 모델 불러오기
    model_name = "openai/clip-vit-base-patch32"
    print(f"✅ Loading model '{model_name}'...")
    try:
        model = CLIPModel.from_pretrained(model_name).to(device)
        processor = CLIPProcessor.from_pretrained(model_name)
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    print("✅ Model loaded successfully.")

    if not os.path.exists(dataset_path):
        print(f"❌ Error: Dataset path '{dataset_path}' not found.")
        return

    # 출력 폴더 생성
    os.makedirs(output_path, exist_ok=True)
    print(f"✅ Low-confidence images will be moved to: {output_path}")

    class_labels = [d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))]
    if not class_labels:
        print("No class folders found in the dataset path.")
        return

    total_moved_count = 0
    total_processed_count = 0

    print(f"\n--- Starting Dataset Validation (Threshold: {threshold:.2f}) ---\n")

    for label_name in class_labels:
        label_path = os.path.join(dataset_path, label_name)
        output_label_path = os.path.join(output_path, label_name)

        image_files = [f for f in os.listdir(label_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not image_files:
            continue

        print(f"--- Analyzing class: [{label_name}] ---")

        # 해당 클래스의 결과 저장 폴더 생성
        os.makedirs(output_label_path, exist_ok=True)

        moved_in_class = 0

        for i, file_name in enumerate(image_files):
            total_processed_count += 1
            img_path = os.path.join(label_path, file_name)

            try:
                print(f"  Processing ({i + 1}/{len(image_files)}): {file_name}", end='\r')

                image = Image.open(img_path).convert("RGB")
                text_prompt = PROMPT_TEMPLATE.format(label_name)

                # 이미지와 '자신의 정답 레이블' 텍스트만으로 점수 계산
                inputs = processor(text=[text_prompt], images=image, return_tensors="pt", padding=True).to(device)

                with torch.no_grad():
                    outputs = model(**inputs)

                # 로짓 값 자체가 이미지-텍스트 유사도 점수. 100을 곱해 스케일링
                confidence_score = outputs.logits_per_image.item() / 100.0

                if confidence_score < threshold:
                    moved_in_class += 1
                    total_moved_count += 1

                    # 파일을 낮은 신뢰도 폴더로 이동
                    destination_path = os.path.join(output_label_path, file_name)
                    shutil.move(img_path, destination_path)

                    # 진행률 표시 줄을 지우고, 이동 로그 출력
                    print(f"  [MOVED] Low score ({confidence_score:.3f}): {file_name} {' ' * 20}")

            except Exception as e:
                print(f"\n❌ Could not process file {img_path}: {e}")

        if moved_in_class > 0:
            print(f"\n  ▶ Class [{label_name}] result: Moved {moved_in_class} image(s).")
        else:
            print(f"\n  ▶ Class [{label_name}] result: All images are above the threshold.")

    print("\n" + "=" * 70)
    print("✅ Validation Complete!")
    print(f"Total images processed: {total_processed_count}")
    print(f"Total images moved: {total_moved_count}")
    print("=" * 70)


if __name__ == '__main__':
    validate_and_filter_dataset(DATASET_PATH, OUTPUT_PATH, CONFIDENCE_THRESHOLD)