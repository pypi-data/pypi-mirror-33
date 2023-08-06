from setuptools import setup, find_packages

setup(
    name='ajelastic',
    version='0.1',
    packages=find_packages(exclude=["tests*"]),
    url='https://github.com/aasaanjobs/ajelastic-sdk',
    license='MIT',
    author='Sohel Tarir',
    author_email='sohel.tarir@aasaanjobs.com',
    description='Python - Elasticsearch Integration (for Aasaanjobs Internal Usage)',
    zip_safe=False
)
