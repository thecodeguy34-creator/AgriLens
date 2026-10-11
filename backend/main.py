import io
import os
import urllib.request
import numpy as np
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf

app = FastAPI(title="AgriLens AI Engine API")

# Enable CORS for local testing, web clients, and mobile apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Target tomato leaf disease classes matching your trained model
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

# Post-training temperature scaling parameter for logit calibration
TEMPERATURE = 0.4793

# Directory for models
os.makedirs("models", exist_ok=True)

# Direct URLs for both models from your GitHub Release
MODELS = {
    "models/agrilens_gate_v2_best.keras": "https://github.com/thecodeguy34-creator/AgriLens/releases/download/v1.0.0/agrilens_gate_v2_best.keras",
   "models/agrilens_final_v2_best.keras": "https://github.com/thecodeguy34-creator/AgriLens/releases/download/v1.0.0/agrilens_final_v2.keras"
}

for path, url in MODELS.items():
    if not os.path.exists(path):
        print(f"Downloading {path} from {url}...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as response, open(path, "wb") as out_file:
                out_file.write(response.read())
            print(f"Successfully downloaded {path}")
        except Exception as e:
            print(f"Failed to download {path}. Error: {e}")
            raise e

# Load Keras models directly
gate_model = tf.keras.models.load_model("models/agrilens_gate_v2_best.keras", compile=False)
classifier_model = tf.keras.models.load_model("models/agrilens_final_v2_best.keras", compile=False)

def preprocess_image(image_bytes: bytes, target_size=(224, 224)):
    """Convert raw input bytes into a normalized RGB NumPy array."""
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

        # 1. First Pass: Gate Model Filter Check (In-Distribution Validation)
        gate_pred = gate_model.predict(img_array, verbose=0)[0][0]
        if gate_pred < 0.5:
            return {
                "status": "rejected",
                "message": "Non-plant image detected. Please upload a clear photo of a tomato leaf."
            }

        # 2. Second Pass: Extract Pre-softmax Logits & Apply Temperature Scaling
        probs = classifier_model.predict(img_array, verbose=0)[0]
        epsilon = 1e-7
        probs_clipped = np.clip(probs, epsilon, 1.0 - epsilon)
        logits = np.log(probs_clipped)

        # Scale logits with temperature T=0.4793 and recompute Softmax
        scaled_logits = logits / TEMPERATURE
        scaled_probs = tf.nn.softmax(scaled_logits).numpy()

        top_idx = int(np.argmax(scaled_probs))
        confidence = float(scaled_probs[top_idx])

        # 3. Decision Logic & Safety Bucketing
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