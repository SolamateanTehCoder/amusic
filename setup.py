from setuptools import setup, find_packages

setup(
    name='amusic',
    version='2.2.2', # if it 3.0.0 or onwards that means its actually stable an im happy with it
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
