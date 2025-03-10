import unittest
from src.ai.model import ThumbnailModel
from src.ai.generator import ThumbnailGenerator
from PIL import Image

class TestThumbnailGenerator(unittest.TestCase):

    def setUp(self):
        self.model = ThumbnailModel()
        self.generator = ThumbnailGenerator(self.model)
        # Create a test image instead of loading from a path
        self.test_image = Image.new('RGB', (1280, 720), color='white')

    def test_thumbnail_model_load(self):
        self.model.load_model()
        self.assertIsNotNone(self.model)

    def test_thumbnail_generation(self):
        thumbnail = self.generator.generate_thumbnail(self.test_image)
        self.assertIsNotNone(thumbnail)
        self.assertEqual(thumbnail.size, (1280, 720))

if __name__ == '__main__':
    unittest.main()