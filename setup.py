from setuptools import setup, find_packages

setup(
    name='amusic', # Changed package name to 'amusic'
    version='0.1.1',
    author='SolamaeteanTehCoder',
    author_email='arjunshmaadhava@gmail.com', # Replace with your email
    description='A Python tool for generating MIDI visualization videos.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/SolamaeteanTehCoder/amusic',
    packages=find_packages(),
    install_requires=[
        'mido',
        'synthviz',
        'Pillow',
        'pydub',
        'numpy',
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

