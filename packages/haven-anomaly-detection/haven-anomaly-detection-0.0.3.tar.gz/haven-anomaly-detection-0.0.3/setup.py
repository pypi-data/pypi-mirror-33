from setuptools import setup

setup(
    name="haven-anomaly-detection",
    packages=["anomaly_detection"],
    version="0.0.3",
    install_requires=["scipy", "statsmodels"],
    description="A python implementation of https://github.com/twitter/AnomalyDetection",
)
