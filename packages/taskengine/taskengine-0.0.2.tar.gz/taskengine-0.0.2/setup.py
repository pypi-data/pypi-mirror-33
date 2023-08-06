import setuptools

with open("taskengine/README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="taskengine",
    version="0.0.2",
    author="AppointmentGuru",
    author_email="tech@appointmentguru.co",
    description="TaskEngine for ProcessEngine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SchoolOrchestration/ProcessEngineV2/tree/master/taskengine",
    packages=['taskengine'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
)