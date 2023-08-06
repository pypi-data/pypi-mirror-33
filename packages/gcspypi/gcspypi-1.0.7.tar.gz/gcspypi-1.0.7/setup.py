from setuptools import setup, find_packages

setup(
    name='gcspypi',
    version='1.0.7',
    author='Ethronsoft',
    author_email='dev@ethronsoft.com',
    license=open("LICENSE").read(),
    keywords="pypi private repository gcs google cloud storage",
    url="https://github.com/ethronsoft/gcspypi",
    include_package_data=True,
    description="Private packages repository backed by Google Cloud Storage",
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        "tqdm",
        "colorama",
        "six==1.11.0",
        "google-cloud-storage==1.5.0",
    ],
    tests_require=[
        "pytest",
        "pytest-cov"
    ],
    setup_requires=[
        "pytest-runner"
    ],
    entry_points={
        'console_scripts': [
            'gcspypi = ethronsoft.gcspypi.__main__:main'
        ]
    }
)
