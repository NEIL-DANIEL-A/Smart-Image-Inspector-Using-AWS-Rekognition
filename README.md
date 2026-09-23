# 🔍 Smart Image Inspector

A standalone, beginner-friendly Flask application designed to demonstrate and teach **AWS Rekognition**.

This project connects directly to AWS Rekognition using `boto3` and passes in-memory image bytes (`Image={'Bytes': ...}`) — **no S3 buckets, databases, or user authentication required**.

---

## 🌟 What is AWS Rekognition?

**Amazon Rekognition** is a cloud-based computer vision service provided by Amazon Web Services (AWS). It uses pre-trained deep learning models to automatically analyze images without requiring machine learning expertise.

This project demonstrates **5 fundamental Rekognition capabilities**:
1. **`detect_labels()`**: Identifies thousands of common objects, scenes, concepts, and actions (e.g., "Dog", "Car", "Sunset") with confidence scores (0–100%).
2. **`detect_moderation_labels()`**: Scans images for unsafe, explicit, suggestive, or inappropriate content to automate content moderation.
3. **`detect_text()`**: Optical Character Recognition (OCR) that extracts text from street signs, receipts, clothing, and documents.
4. **`detect_faces()`**: Detects facial details including estimated age range, dominant emotions (Happy, Calm, etc.), smile detection, and glasses.
5. **`recognize_celebrities()`**: Identifies thousands of famous personalities, actors, politicians, and athletes.

---

## 🔑 How to Get AWS Credentials

If you have never used AWS before, follow these steps to generate credentials:

1. **Sign into AWS Console**: Go to [aws.amazon.com/console](https://aws.amazon.com/console).
2. **Open IAM**: Search for **IAM** in the top search bar.
3. **Create an IAM User**:
   - Go to **Users** → **Create user**.
   - Set a username (e.g., `smart-image-inspector-user`).
   - Leave the console access checkbox *unchecked* (programmatic API access only).
4. **Attach Permissions**:
   - Select **Attach policies directly**.
   - Search for and select: `AmazonRekognitionReadOnlyAccess`.
5. **Generate Access Keys**:
   - Select your new user → **Security credentials** tab.
   - Scroll down to **Access keys** and click **Create access key**.
   - Select **Local code** (or *Application running outside AWS*).
   - Check the confirmation box and proceed.
   - Copy your **Access Key ID** and **Secret Access Key**.

---

## 🚀 How to Run the App Locally

### 1. Prerequisites
- Python 3.9+ installed on your machine.

### 2. Setup Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file from `.env.example`:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and fill in your AWS credentials:
```env
AWS_ACCESS_KEY_ID=AKIA...your_access_key...
AWS_SECRET_ACCESS_KEY=your_secret_key...
AWS_REGION=us-east-1
```

### 5. Start the Flask Server
```bash
python app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your web browser.

---

## 🧪 Running Automated Tests
To run unit tests with mock Rekognition responses (does not consume AWS credits):
```bash
python -m unittest test_app.py
```

---

## 🔬 How the Code Works (Teaching Guide)

### 1. Direct In-Memory Bytes (No S3 Needed)
```python
image_bytes = file.read()
# Preview rendered via Data URL:
image_data_url = f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('utf-8')}"
```

### 2. The 5 Rekognition Calls in `app.py`
- **Labels**: `rekognition.detect_labels(Image={'Bytes': image_bytes}, MaxLabels=10, MinConfidence=75)`
- **Safety**: `rekognition.detect_moderation_labels(Image={'Bytes': image_bytes}, MinConfidence=60)`
- **OCR Text**: `rekognition.detect_text(Image={'Bytes': image_bytes})`
- **Faces**: `rekognition.detect_faces(Image={'Bytes': image_bytes}, Attributes=['ALL'])`
- **Celebrities**: `rekognition.recognize_celebrities(Image={'Bytes': image_bytes})`

### 3. Raw Response Inspection
Each API call's verbatim JSON response is formatted and rendered in collapsible `<details>` blocks at the bottom of the results page for live student inspection.

---

## 📁 Project Structure

```
Smart Image Inspector/
├── .env.example            # Sample environment variables template
├── .gitignore              # Ignores virtualenv, .env, and caches
├── README.md               # Beginner guide & documentation
├── SESSION_NOTES.md        # Teaching session notes & curriculum outline
├── app.py                  # Flask server and Rekognition logic
├── requirements.txt        # Python package dependencies
├── test_app.py             # Mock unit test suite
├── static/
│   └── style.css           # Projector-friendly CSS styles
└── templates/
    ├── index.html          # Image upload page
    └── results.html        # Multi-feature results & JSON inspection page
```
