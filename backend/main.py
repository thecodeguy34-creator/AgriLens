import io
import os
import numpy as np
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
from huggingface_hub import hf_hub_download

app = FastAPI(title="AgriLens AI Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLASSES = [
    "bacterial_spot", 
    "early_blight", 
    "healthy", 
    "late_blight",
    "leaf_mold", 
    "septoria_leaf_spot", 
    "spider_mites",
    "target_spot", 
    "mosaic_virus", 
    "yellow_leaf_curl_virus"
]

TEMPERATURE = 0.4793
HF_REPO_ID = "stranger890/agrilens-models"

# Global variables for lazy-loading
_gate_model = None
_classifier_model = None

def get_gate_model():
    global _gate_model
    if _gate_model is None:
        print("Downloading/loading gate model...")
        path = hf_hub_download(repo_id=HF_REPO_ID, filename="agrilens_gate_v2_best.keras")
        _gate_model = tf.keras.models.load_model(path, compile=False)
    return _gate_model

def get_classifier_model():
    global _classifier_model
    if _classifier_model is None:
        print("Downloading/loading classifier model...")
        path = hf_hub_download(repo_id=HF_REPO_ID, filename="agrilens_final_v2_best.keras")
        _classifier_model = tf.keras.models.load_model(path, compile=False)
    return _classifier_model

def preprocess_image(image_bytes: bytes, target_size=(224, 224)):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.resize(target_size)
    arr = np.array(image, dtype=np.float32)
    return np.expand_dims(arr, axis=0)

@app.get("/")
def read_root():
    return {"status": "online", "service": "AgriLens Engine v2.0"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        img_array = preprocess_image(contents)

        # Lazy load models on demand to save startup memory
        gate_model = get_gate_model()
        classifier_model = get_classifier_model()

        gate_pred = gate_model.predict(img_array, verbose=0)[0][0]
        if gate_pred < 0.5:
            return {
                "status": "rejected",
                "message": "Non-plant image detected. Please upload a clear photo of a tomato leaf."
            }

        probs = classifier_model.predict(img_array, verbose=0)[0]
        epsilon = 1e-7
        probs_clipped = np.clip(probs, epsilon, 1.0 - epsilon)
        logits = np.log(probs_clipped)

        scaled_logits = logits / TEMPERATURE
        scaled_probs = tf.nn.softmax(scaled_logits).numpy()

        top_idx = int(np.argmax(scaled_probs))
        confidence = float(scaled_probs[top_idx])

        if confidence < 0.35:
            return {
                "status": "rejected",
                "message": "Image quality is too low or blurry to provide a safe diagnosis."
            }

        return {
            "status": "success",
            "disease": CLASSES[top_idx],
            "confidence_percentage": round(confidence * 100, 2),
            "decision": "high_confidence" if confidence >= 0.70 else "uncertain"
        }

    except Exception as e:
        return {
            "status": "rejected",
            "message": f"Error processing image: {str(e)}"
        }