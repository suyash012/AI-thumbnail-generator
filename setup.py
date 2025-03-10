
from setuptools import setup, find_packages

setup(
    name='youtube-thumbnail-generator',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A simple AI agent for generating YouTube thumbnails.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'Pillow',  # For image processing
        'numpy',   # For numerical operations
        'tensorflow'  # If using TensorFlow for AI model
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)