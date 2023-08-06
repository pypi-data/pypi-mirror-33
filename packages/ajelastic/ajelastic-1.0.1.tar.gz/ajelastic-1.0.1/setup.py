from setuptools import setup, find_packages


def read(f):
    return open(f, 'r', encoding='utf-8').read()


setup(
    name='ajelastic',
    version='1.0.1',
    packages=find_packages(exclude=["tests*"]),
    url='https://github.com/aasaanjobs/ajelastic-sdk',
    license='MIT',
    author='Sohel Tarir',
    author_email='sohel.tarir@aasaanjobs.com',
    description='Python - Elasticsearch Integration (for Aasaanjobs Internal Usage)',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'aj-es-reindex=ajelastic.commands.reindex:main'
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)
