import setuptools
from flake8_prevent_fails import __version__

requires = [
    "flake8 > 3.0.0",
]

setuptools.setup(
    name="flake8-prevent-fails",
    license="MIT",
    version=__version__,
    description="",
    author="Atterratio",
    author_email="606837+Atterratio@users.noreply.github.com",
    url="https://github.com/Atterratio/flake8-prevent-fails",
    packages=[
        "flake8_prevent_fails",
    ],
    install_requires=requires,
    entry_points={
        'flake8.extension': [
            'PF=flake8_prevent_fails:FailsChecker',
        ],
    },
    classifiers=[
        "Framework :: Flake8",
        "Environment :: Console",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
)
