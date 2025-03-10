import unittest
from src.image_processing.resize import resize_image
from src.image_processing.filters import apply_filter
from PIL import Image

class TestImageProcessing(unittest.TestCase):

    def setUp(self):
        self.image = Image.new('RGB', (100, 100), color='red')

    def test_resize_image(self):
        resized_image = resize_image(self.image, (50, 50))
        self.assertEqual(resized_image.size, (50, 50))

    def test_apply_filter(self):
        filtered_image = apply_filter(self.image, 'BLUR')
        self.assertIsNotNone(filtered_image)

if __name__ == '__main__':
    unittest.main()