import os
import json
import base64
from flask import Flask, render_template, request
from dotenv import load_dotenv
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# 5MB upload limit per Rekognition direct bytes API limit
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

def get_rekognition_client():
    """Initializes and returns boto3 Rekognition client using environment variables."""
    return boto3.client(
        "rekognition",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

@app.route("/", methods=["GET"])
def index():
    """Renders the image upload form."""
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Receives uploaded image, passes raw in-memory bytes directly
    to AWS Rekognition for 5 core computer vision APIs, and renders analysis results.
    """
    if "image" not in request.files:
        return render_template("index.html", error="No image file provided in upload."), 400

    file = request.files["image"]
    if file.filename == "":
        return render_template("index.html", error="No image file selected."), 400

    # Read image bytes directly in-memory (no disk persistence)
    image_bytes = file.read()
    if not image_bytes:
        return render_template("index.html", error="The uploaded file is empty."), 400

    # Prepare data URL so browser can display preview without saving to disk
    mime_type = file.mimetype or "image/jpeg"
    base64_img = base64.b64encode(image_bytes).decode("utf-8")
    image_data_url = f"data:{mime_type};base64,{base64_img}"

    try:
        rekognition = get_rekognition_client()

        # 1. detect_labels()
        labels_response = rekognition.detect_labels(
            Image={"Bytes": image_bytes},
            MaxLabels=10,
            MinConfidence=75
        )

        # 2. detect_moderation_labels()
        moderation_response = rekognition.detect_moderation_labels(
            Image={"Bytes": image_bytes},
            MinConfidence=60
        )

        # 3. detect_text()
        text_response = rekognition.detect_text(
            Image={"Bytes": image_bytes}
        )

        # 4. detect_faces()
        faces_response = rekognition.detect_faces(
            Image={"Bytes": image_bytes},
            Attributes=["ALL"]
        )

        # 5. recognize_celebrities()
        celebrities_response = rekognition.recognize_celebrities(
            Image={"Bytes": image_bytes}
        )

        # Process labels & moderation
        labels = labels_response.get("Labels", [])
        moderation_labels = moderation_response.get("ModerationLabels", [])

        # Process OCR detected text (filter to 'LINE' type to avoid duplicate word spam)
        text_detections = [
            t for t in text_response.get("TextDetections", [])
            if t.get("Type") == "LINE"
        ]

        # Process Faces
        face_details = []
        for face in faces_response.get("FaceDetails", []):
            age_range = face.get("AgeRange", {})
            # Find dominant emotion
            emotions = sorted(face.get("Emotions", []), key=lambda x: x.get("Confidence", 0), reverse=True)
            top_emotion = emotions[0] if emotions else {"Type": "UNKNOWN", "Confidence": 0}
            
            face_details.append({
                "age_range": f"{age_range.get('Low', '?')} - {age_range.get('High', '?')}",
                "emotion": top_emotion.get("Type", "").title(),
                "emotion_confidence": round(top_emotion.get("Confidence", 0), 1),
                "smile": face.get("Smile", {}).get("Value", False),
                "eyeglasses": face.get("Eyeglasses", {}).get("Value", False),
                "sunglasses": face.get("Sunglasses", {}).get("Value", False),
                "gender": face.get("Gender", {}).get("Value", "Unknown").title(),
                "confidence": round(face.get("Confidence", 0), 1)
            })

        # Process Celebrities
        celebrities = []
        for celeb in celebrities_response.get("CelebrityFaces", []):
            celebrities.append({
                "name": celeb.get("Name"),
                "confidence": round(celeb.get("MatchConfidence", 0), 1),
                "urls": celeb.get("Urls", [])
            })

        # Pretty-printed JSON strings for teaching inspection
        raw_jsons = {
            "detect_labels": json.dumps(labels_response, indent=2, default=str),
            "detect_moderation_labels": json.dumps(moderation_response, indent=2, default=str),
            "detect_text": json.dumps(text_response, indent=2, default=str),
            "detect_faces": json.dumps(faces_response, indent=2, default=str),
            "recognize_celebrities": json.dumps(celebrities_response, indent=2, default=str)
        }

        return render_template(
            "results.html",
            image_data_url=image_data_url,
            labels=labels,
            moderation_labels=moderation_labels,
            text_detections=text_detections,
            face_details=face_details,
            celebrities=celebrities,
            raw_jsons=raw_jsons
        )

    except (BotoCoreError, ClientError) as aws_err:
        return render_template("index.html", error=f"AWS Rekognition error: {str(aws_err)}"), 500
    except Exception as err:
        return render_template("index.html", error=f"Unexpected error: {str(err)}"), 500

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
