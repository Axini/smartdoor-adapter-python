from setuptools import setup

# The information here can also be placed in setup.cfg - better separation of
# logic and declaration, and simpler if you include description/version in a file.
setup(
    name="SmartDoor Python Example Adapter",
    version="0.0.1",
    author="Axini B.V.",
    author_email="info@axini.com",
    description="Axini AMP Plugin Adapter for the SmartDoor example",
    package_dir={"": "src"},
    python_requires='>=3.10',
)
