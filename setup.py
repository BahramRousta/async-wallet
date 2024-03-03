from setuptools import setup, find_packages


setup(
    name="async-wallet",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "run = presentation.main:app",
        ]
    },
    install_requires=["fastapi"],
)
