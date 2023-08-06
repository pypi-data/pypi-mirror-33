import setuptools

long_description = "Functions to estimate the expected best-out-of-n (Boon) result from a set of validation and " \
                   "test results for a machine learning architecture. The measure is fully described in the paper" \
                   "Bajgar, O., Kadlec, R., and Kleindienst, J. A Boo(n) for Evaluating Architecture Performance. " \
                   "ICML 2018."


setuptools.setup(
    name="boon",
    version="0.1.0",
    author="Ondrej Bajgar",
    author_email="OBajgar@cz.ibm.com",
    description="Functions to estimate the expected best-out-of-n result from a set of validation and test results.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='Apache-2.0',
    url="https://gitlab.com/obajgar/boon/",
    packages=setuptools.find_packages(),
    install_requires=['numpy'],
    classifiers=(
        "Programming Language :: Python",
        "Operating System :: OS Independent",
    ),
)
