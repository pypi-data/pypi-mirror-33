from setuptools import setup
from setuptools.extension import Extension

setup(
    name = "mauscope",
    version = "1.0.1",
    author = "Juan Barbosa",
    author_email = "js.barbosa10@uniandes.edu.co",
    description = ('Microscopy stage.'),
    license = "GPL",
    keywords = "example documentation tutorial",
    packages=['mauscope'],
    install_requires=['pyserial'],
    ext_modules = [],
    long_description="https://github.com/jsbarbosa/miniscope/",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
    headers = [],
    include_package_data = True,
)
