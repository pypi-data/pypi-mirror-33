from setuptools import find_packages, setup

PACKAGE_NAME = 'django-my-imgur'
VERSION = '0.0.0-a2'

setup(
    name=PACKAGE_NAME,
    packages=find_packages(),
    version=VERSION,
    include_package_data=True,
    description='Django and Imgur.',
    author='poipoii',
    author_email='earth.sama@gmail.com',
    url='https://github.com/poipoii/django-my-imgur',
    download_url='https://github.com/poipoii/django-my-imgur/releases',
    keywords=[],
    classifiers=[],
    install_requires=[
        'Pillow==5.1.0',
        'ppyimgur'
    ]
)
