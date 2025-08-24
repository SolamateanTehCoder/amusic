from setuptools import setup, find_packages

setup(
    name='amusic',
    version='2.0.1',
    packages=find_packages(),
    install_requires=[
        'mido',
        'pygame',
        'moviepy',
        'Pillow'
    ],
    author='SolamateanTehCoder',
    description='A tool to generate MIDI visualization videos with visual effects.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/SolamateanTehCoder/amusic',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
