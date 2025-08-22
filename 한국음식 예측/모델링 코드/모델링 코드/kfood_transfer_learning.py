#%%
#0. 작업 준비
import numpy as np
import matplotlib.pyplot as plt
import keras
import tensorflow as tf
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.models import load_model
#%%
# 데이터셋 시각화
def make_it_plt(dataset, class_names):
    plt.figure(figsize=(12, 12))
    for images, labels in dataset.take(1):
        # 전이 학습 모델에 맞는 입력 형식으로 변환 (0-1 사이 값)
        images_to_show = images.numpy() / 255.0
        for i in range(min(25, len(images))):
            ax = plt.subplot(5, 5, i + 1)
            plt.imshow(images_to_show[i])
            plt.title(class_names[labels[i]])
            plt.axis("off")
    plt.tight_layout()
    plt.show()
#%%
# 모델 생성 (전이 학습)
def model_create_transfer(input_shape, num_classes, optimizer_fn, loss_fn, metrics_fn):
    # 1. 기반 모델(Base Model) 로드 (사전 학습된 가중치 사용)
    base_model = tf.keras.applications.EfficientNetB4(
        include_top=False, # 분류기는 직접 추가할 것이므로 False
        weights='imagenet', # ImageNet으로 사전 학습된 가중치 사용
        input_shape=input_shape
    )

    # 2. 기반 모델의 가중치를 동결 (초기 학습 단계에서는 변경되지 않도록)
    base_model.trainable = False

    # 3. 새로운 모델 구성 (Functional API 사용)
    inputs = keras.Input(shape=input_shape)
    # EfficientNetB0는 자체적으로 Rescaling을 포함하므로 별도 레이어 필요 없음
    x = base_model(inputs, training=False) # BatchNormalization 레이어가 동결되도록 training=False
    x = keras.layers.GlobalAveragePooling2D()(x)
    x = keras.layers.Dropout(0.3)(x) # 과적합 방지
    outputs = keras.layers.Dense(num_classes, activation="softmax")(x)

    model = keras.Model(inputs, outputs)

    model.compile(optimizer=optimizer_fn, loss=loss_fn, metrics=metrics_fn)
    model.summary()
    return model, base_model
#%%
# --- 메인 실행 로직 ---

# 랜덤 난수 고정
seed = 53
tf.random.set_seed(seed)
np.random.seed(seed)

# 데이터셋 경로 및 파라미터
DATA_PATH = '/Users/ihanjo/Documents/미니 프로젝트/한국음식 예측/데이터/한국 음식 이미지/kfood'
MODEL_PATH = '../model'
IMG_SIZE = (224, 224) # EfficientNetB4 권장 사이즈
BATCH_SIZE = 32
VALIDATION_SPLIT = 0.2

# 데이터셋 로드
print("Loading training and validation datasets...")
train_dataset = tf.keras.utils.image_dataset_from_directory(
    DATA_PATH,
    validation_split=VALIDATION_SPLIT,
    subset="training",
    seed=seed,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

validation_dataset = tf.keras.utils.image_dataset_from_directory(
    DATA_PATH,
    validation_split=VALIDATION_SPLIT,
    subset="validation",
    seed=seed,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

class_names = train_dataset.class_names
print(f"Found {len(class_names)} classes.")

# 데이터 로딩 파이프라인 최적화
AUTOTUNE = tf.data.AUTOTUNE
train_dataset = train_dataset.cache().prefetch(buffer_size=AUTOTUNE)
validation_dataset = validation_dataset.cache().prefetch(buffer_size=AUTOTUNE)

# 모델 옵티마이저, 손실함수, 평가지표 정의
op = keras.optimizers.Adam(learning_rate=0.001)
ls = keras.losses.SparseCategoricalCrossentropy()
acc = keras.metrics.SparseCategoricalAccuracy()

# 모델 생성
model, base_model = model_create_transfer(
    input_shape=IMG_SIZE + (3,),
    num_classes=len(class_names),
    optimizer_fn=op,
    loss_fn=ls,
    metrics_fn=[acc]
)

# 모델 callback 정의
es = EarlyStopping(patience=5, monitor="val_loss", restore_best_weights=True)
ck_path = "best_kfood_transfer_model.keras"
ck = ModelCheckpoint(ck_path, save_best_only=True, monitor='val_loss')
#%%
# --- 1단계: 전이 학습 ---
print("\n--- Phase 1: Transfer Learning ---")
history_transfer = model.fit(
    train_dataset,
    validation_data=validation_dataset,
    epochs=10,
    callbacks=[es, ck]
)

# --- 2단계: 미세 조정 (Fine-tuning) ---
print("\n--- Phase 2: Fine-tuning ---")
base_model.trainable = True # 기반 모델 동결 해제

# 상위 일부 레이어만 학습 가능하도록 설정 (예: 마지막 20개 레이어)
for layer in base_model.layers[:-20]:
    layer.trainable = False

#%%
plt.plot(history_transfer.history['loss'])
plt.plot(history_transfer.history['val_loss'])
#%%
# 매우 낮은 학습률로 모델을 다시 컴파일
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-5),
    loss=ls,
    metrics=[acc]
)
model.summary()

history_fine = model.fit(
    train_dataset,
    validation_data=validation_dataset,
    epochs=10, # Fine-tuning은 보통 짧게 진행
    initial_epoch=history_transfer.epoch[-1] + 1, # 이전 학습에 이어서 시작
    callbacks=[es, ck] # 동일한 콜백 사용
)
#%%
plt.plot(history_fine.history['loss'])
plt.plot(history_fine.history['val_loss'])
#%%
# --- 최종 평가 및 예측 ---

print("\n--- Final Evaluation and Prediction ---")
# 가장 성능이 좋았던 모델 로드
best_model = load_model(ck_path)

loss, accuracy = best_model.evaluate(validation_dataset)
print(f"Final Validation Loss: {loss:.4f}")
print(f"Final Validation Accuracy: {accuracy:.4f}")

print("\nTesting prediction on a sample batch...")
for test_images, test_labels in validation_dataset.take(1):
    predictions = best_model.predict(test_images)
    predicted_labels = np.argmax(predictions, axis=1)

    true_class_names = [class_names[i] for i in test_labels.numpy()[:10]]
    predicted_class_names = [class_names[i] for i in predicted_labels[:10]]
    print(f"\nTrue Food Names:      {true_class_names}")
    print(f"Predicted Food Names: {predicted_class_names}")
    break