"""Python package description."""
from setuptools import setup, find_packages

def readme():
    """Load the readme file."""
    with open('README.md') as readme_file:
        return readme_file.read()


setup(
    name='monpyou',
    version='0.1.2',
    description='Python library to read account information from moneyou bank.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/christian.kuehnel/monpyou',
    author='Christian Kühnel',
    author_email='christian.kuehnel@gmail.com',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
    install_requires=['requests', 'typing>=3,<4', 'lxml'],
    keywords='Moneyou banking',
    zip_safe=False,
    extras_require={'testing': ['pytest']},
    scripts=['monpyou_demo'],
)
