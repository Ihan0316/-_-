import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import pandas as pd
import os

# --- 페이지 설정 ---
st.set_page_config(
    page_title="한식 이미지 예측 앱",
    page_icon="🍲",
    layout="centered",
)

# --- 모델 로드 ---
# @st.cache_resource 데코레이터를 사용해 모델을 캐시에 저장하여 앱 실행 중 한 번만 로드합니다.
@st.cache_resource
def load_food_model(model_path):
    """
    저장된 Keras 모델 파일을 불러옵니다.
    모델 구조와 가중치가 함께 로드됩니다.
    """
    try:
        model = tf.keras.models.load_model(model_path)
        return model
    except Exception as e:
        st.error(f"모델 로딩 중 오류 발생: {e}")
        st.error(f"'{model_path}' 파일이 app.py와 같은 폴더에 있는지, 손상되지 않았는지 확인하세요.")
        return None

# --- 이미지 전처리 ---
def preprocess_image(image, target_size=(299, 299)):
    """
    사용자가 업로드한 이미지를 Xception 모델에 맞게 전처리합니다.
    1. 이미지를 target_size로 조정합니다.
    2. Numpy 배열로 변환합니다.
    3. 모델 예측을 위해 차원을 확장합니다.
    4. Xception 모델의 전용 전처리 함수를 적용합니다.
    """
    if image.mode != "RGB":
        image = image.convert("RGB")
    image = image.resize(target_size)
    image_array = np.asarray(image)
    image_array = np.expand_dims(image_array, axis=0)
    # Xception 모델에 맞는 전처리 적용
    processed_image = tf.keras.applications.xception.preprocess_input(image_array)
    return processed_image

# --- 메인 애플리케이션 ---

st.title("🍲 한식 이미지 예측 서비스")
st.markdown("---")

# 모델 가중치 파일 경로 (학습 코드와 동일하게 'xception.keras')
MODEL_FILE = "xception.keras"

# 모델 로드
model = load_food_model(MODEL_FILE)

# 클래스 이름 (8개)
CLASS_NAMES = [
    "구이", "국", "김치", "나물", "면",
    "무침", "밥", "볶음"
]

# --- 사이드바 ---
with st.sidebar:
    st.header("🖼️ 이미지 업로드")
    image_file = st.file_uploader("예측할 한식 이미지를 업로드하세요.", type=["jpg", "jpeg", "png"])

    st.header("📝 클래스 정보")
    st.write(f"이 모델은 **{len(CLASS_NAMES)}개**의 음식 종류를 예측할 수 있습니다.")
    st.markdown(f"**- {'- '.join(CLASS_NAMES)}**")

# --- 메인 화면 ---
# 모델 파일이 없을 경우 에러 메시지 표시
if not os.path.exists(MODEL_FILE):
    st.error(f"모델 파일({MODEL_FILE})을 찾을 수 없습니다. app.py와 같은 폴더에 파일을 위치시켜주세요.")
# 모델 로딩에 실패했을 경우
elif model is None:
    st.warning("모델 로딩에 실패했습니다. 페이지를 새로고침하거나 관리자에게 문의하세요.")
# 정상 실행
else:
    if image_file is None:
        st.info("👈 사이드바에서 예측할 이미지를 업로드해주세요.")
    else:
        image = Image.open(image_file)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🖼️ 업로드된 이미지")
            st.image(image, use_container_width=True)

        # AI 예측 시작
        with st.spinner("🧠 AI가 이미지를 분석 중입니다..."):
            processed_image = preprocess_image(image)
            prediction = model.predict(processed_image)

        with col2:
            st.subheader("📊 예측 결과")

            # 예측 결과 처리
            predicted_class_index = np.argmax(prediction, axis=1)[0]
            predicted_class_name = CLASS_NAMES[predicted_class_index]
            confidence = prediction[0][predicted_class_index] * 100

            st.success(f"이 음식은 **'{predicted_class_name}'**일 확률이 **{confidence:.2f}%** 입니다.")

            st.markdown("---")
            st.write("전체 클래스에 대한 예측 확률:")

            # DataFrame 생성 및 시각화
            result_df = pd.DataFrame({
                '음식 종류': CLASS_NAMES,
                '확률 (%)': prediction[0] * 100
            })
            result_df = result_df.sort_values(by='확률 (%)', ascending=False).reset_index(drop=True)

            st.bar_chart(result_df.set_index('음식 종류'))

            with st.expander("상세 확률 보기"):
                st.dataframe(result_df)
