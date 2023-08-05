from setuptools import setup, find_packages

setup(
    name='tidal-prediction',
    version='0.1.3',
    scripts=['scripts/extract_local_model.py', 'scripts/predict_tide.py'],
    packages=find_packages(),
    url='https://gitlab.com/jblarsen/tidal-prediction-python',
    install_requires=[
        'astropy',
        'configobj',
        'netCDF4',
        'numpy',
        'scipy'
    ],
    author = "Jesper Baasch-Larsen",
    author_email = "jesper@baasch-larsen.dk",
    license='MIT License'
)
