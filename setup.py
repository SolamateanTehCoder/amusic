from setuptools import setup, find_packages

setup(
    name='amusic',
    version='1.0.1', 
    author='SolamateanTehCoder', # Make sure this is your GitHub username
    author_email='your.email@example.com', # Replace with your actual email
    description='A Python tool for generating MIDI visualization videos with note separation, auto-soundfont download, and color customization.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/SolamateanTehCoder/amusic', # Replace with your actual project's GitHub URL
    packages=find_packages(),
    install_requires=[
        'mido',
        'synthviz',
        'Pillow',
        'pydub',
        'numpy',
        'requests',
        'appdirs',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Video',
        'Topic :: Artistic Software',
    ],
    python_requires='>=3.8',
    keywords='midi visualizer music video synthviz piano roll',
)
