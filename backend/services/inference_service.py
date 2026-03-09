import io
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
import torchvision.transforms as transforms
import torchvision.models as tv_models
from ultralytics import YOLO


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = PROJECT_ROOT / "models"
YOLO_CONFIDENCE_THRESHOLD = 0.25

_MODEL_CACHE = None

CLASS_NAMES = [
    "Center",
    "Donut",
    "Edge-loc",
    "Edge-ring",
    "Loc",
    "Near-full",
    "None",
    "Random",
    "Scratch"
]

transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=3),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def _model_path(filename: str) -> str:
    return str(MODELS_DIR / filename)


def _load_state_dict(filename: str):
    return torch.load(_model_path(filename), map_location=device)


def load_models():
    resnet = tv_models.resnet18(weights=None)
    resnet.fc = torch.nn.Linear(resnet.fc.in_features, 9)
    resnet.load_state_dict(_load_state_dict("resnet_model.pth"))
    resnet.to(device)
    resnet.eval()

    mobilenet = tv_models.mobilenet_v2(weights=None)
    mobilenet.classifier[1] = torch.nn.Linear(mobilenet.last_channel, 9)
    mobilenet.load_state_dict(_load_state_dict("mobilenet_model.pth"))
    mobilenet.to(device)
    mobilenet.eval()

    efficientnet = tv_models.efficientnet_b0(weights=None)
    efficientnet.classifier[1] = torch.nn.Linear(
        efficientnet.classifier[1].in_features, 9
    )
    efficientnet.load_state_dict(_load_state_dict("efficientnet_model.pth"))
    efficientnet.to(device)
    efficientnet.eval()

    yolo_model = YOLO(_model_path("best (5).pt"))

    return [resnet, mobilenet, efficientnet], yolo_model


def get_models():
    global _MODEL_CACHE

    if _MODEL_CACHE is None:
        _MODEL_CACHE = load_models()

    return _MODEL_CACHE


def cnn_predict(image):
    cnn_models, _ = get_models()
    image_tensor = transform(image).unsqueeze(0).to(device)
    probs = []

    with torch.no_grad():
        for model in cnn_models:
            output = model(image_tensor)
            probs.append(torch.softmax(output, dim=1))

    probs = torch.stack(probs)
    avg_probs = torch.mean(probs, dim=0)
    conf, pred = torch.max(avg_probs, 1)

    return {
        "defect_type": CLASS_NAMES[pred.item()],
        "confidence": float(conf.item()),
        "class_index": int(pred.item()),
    }


def detect_defects(image_path):
    _, yolo_model = get_models()
    results = yolo_model(image_path)
    detections = []

    for r in results:
        boxes = r.boxes
        if boxes is None:
            continue

        for box in boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            if conf < YOLO_CONFIDENCE_THRESHOLD:
                continue

            xyxy = box.xyxy[0].tolist()

            detections.append({
                "class": yolo_model.names[cls],
                "confidence": conf,
                "bbox": xyxy
            })

    detections.sort(key=lambda item: item["confidence"], reverse=True)

    return detections


def generate_gradcam_heatmap(image, class_index=None):
    cnn_models, _ = get_models()
    model = cnn_models[0]
    model.eval()

    activations = []
    gradients = []

    def forward_hook(_, __, output):
        activations.append(output.detach())

    def backward_hook(_, grad_input, grad_output):
        gradients.append(grad_output[0].detach())

    handle_fwd = model.layer4.register_forward_hook(forward_hook)
    handle_bwd = model.layer4.register_full_backward_hook(backward_hook)

    try:
        image_tensor = transform(image).unsqueeze(0).to(device)
        image_tensor.requires_grad_(True)

        output = model(image_tensor)

        if class_index is None:
            class_index = int(output.argmax(dim=1).item())

        model.zero_grad(set_to_none=True)
        score = output[:, class_index]
        score.backward()

        feature_maps = activations[0]
        grads = gradients[0]

        weights = grads.mean(dim=(2, 3), keepdim=True)
        cam = (weights * feature_maps).sum(dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = F.interpolate(cam, size=(224, 224), mode="bilinear", align_corners=False)

        cam = cam.squeeze().cpu().numpy()
        cam = cam - cam.min()
        cam = cam / (cam.max() + 1e-8)

        base_image = image.resize((224, 224)).convert("RGB")
        base_np = np.array(base_image).astype(np.float32)

        heat = np.zeros((224, 224, 3), dtype=np.float32)
        heat[..., 0] = cam * 255
        heat[..., 1] = np.clip((cam - 0.3) * 255, 0, 255)

        overlay = 0.6 * base_np + 0.4 * heat
        overlay = np.clip(overlay, 0, 255).astype(np.uint8)

        result_image = Image.fromarray(overlay)

        buffer = io.BytesIO()
        result_image.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer.getvalue()

    finally:
        handle_fwd.remove()
        handle_bwd.remove()


def run_inference(image_path):
    image = Image.open(image_path).convert("RGB")

    prediction = cnn_predict(image)
    detections = detect_defects(image_path)
    heatmap_bytes = generate_gradcam_heatmap(
        image=image,
        class_index=prediction["class_index"],
    )

    prediction.pop("class_index", None)

    return {
        "prediction": prediction,
        "detections": detections,
        "heatmap_bytes": heatmap_bytes,
    }