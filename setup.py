import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="text_frontend",
    version="0.0.1",
    author="Ivan Vovk",
    author_email="ivanvovk4@yandex.ru",
    description="Text processing API interface for cleaning, IPA phonemization, tokenization, etc.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ivanvovk/text-frontend-tts",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
    python_requires='>=3.6',
    package_data={'': ['*.txt']}
)
