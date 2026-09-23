import io
import unittest
from unittest.mock import patch, MagicMock
from app import app

class TestSmartImageInspector(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_get_index(self):
        """GET / should render upload form successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Smart Image Inspector", response.data)
        self.assertIn(b"Inspect with Rekognition", response.data)

    def test_post_analyze_missing_file(self):
        """POST /analyze without file should show error"""
        response = self.client.post('/analyze', data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"No image file provided", response.data)

    @patch('app.get_rekognition_client')
    def test_post_analyze_full_features(self, mock_get_client):
        """POST /analyze with all 5 Rekognition APIs mocked"""
        mock_rekognition = MagicMock()
        mock_get_client.return_value = mock_rekognition

        # Mock detect_labels
        mock_rekognition.detect_labels.return_value = {
            "Labels": [
                {"Name": "Person", "Confidence": 99.2}
            ]
        }

        # Mock detect_moderation_labels (safe)
        mock_rekognition.detect_moderation_labels.return_value = {
            "ModerationLabels": []
        }

        # Mock detect_text
        mock_rekognition.detect_text.return_value = {
            "TextDetections": [
                {"DetectedText": "AWS REKOGNITION", "Type": "LINE", "Confidence": 98.0}
            ]
        }

        # Mock detect_faces
        mock_rekognition.detect_faces.return_value = {
            "FaceDetails": [
                {
                    "Confidence": 99.1,
                    "AgeRange": {"Low": 28, "High": 36},
                    "Gender": {"Value": "Female"},
                    "Smile": {"Value": True},
                    "Eyeglasses": {"Value": True},
                    "Sunglasses": {"Value": False},
                    "Emotions": [{"Type": "HAPPY", "Confidence": 96.5}]
                }
            ]
        }

        # Mock recognize_celebrities
        mock_rekognition.recognize_celebrities.return_value = {
            "CelebrityFaces": [
                {"Name": "Andy Jassy", "MatchConfidence": 97.4, "Urls": ["www.imdb.com/name/nm000000"]}
            ]
        }

        fake_image_bytes = b"fake-jpg-binary-bytes"
        data = {
            'image': (io.BytesIO(fake_image_bytes), 'test.jpg', 'image/jpeg')
        }

        response = self.client.post('/analyze', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)

        # Assert all features rendered
        self.assertIn(b"Content looks safe", response.data)
        self.assertIn(b"Person", response.data)
        self.assertIn(b"AWS REKOGNITION", response.data)
        self.assertIn(b"Happy (96.5%)", response.data)
        self.assertIn(b"~28 - 36 yrs", response.data)
        self.assertIn(b"Andy Jassy", response.data)
        self.assertIn(b"recognize_celebrities()", response.data)

        # Assert all API calls were made with in-memory bytes
        mock_rekognition.detect_labels.assert_called_once()
        mock_rekognition.detect_moderation_labels.assert_called_once()
        mock_rekognition.detect_text.assert_called_once()
        mock_rekognition.detect_faces.assert_called_once_with(
            Image={'Bytes': fake_image_bytes},
            Attributes=['ALL']
        )
        mock_rekognition.recognize_celebrities.assert_called_once()

if __name__ == '__main__':
    unittest.main()
