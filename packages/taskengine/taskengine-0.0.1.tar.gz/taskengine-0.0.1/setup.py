import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="taskengine",
    version="0.0.1",
    author="AppointmentGuru",
    author_email="tech@appointmentguru.co",
    description="TaskEngine for ProcessEngine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SchoolOrchestration/ProcessEngineV2/tree/master/taskengine",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
)