from setuptools import setup, find_packages

import fabkit

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='fabkit',
    version=fabkit.__version__,
    packages=find_packages(),
    license=fabkit.__licence__,
    install_requires=[
        "fabric3>=1.7.0",
        "jinja2"
    ],
    description='Group of tools extending fabric v1.x tasks',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/karolhor/fabkit",
    python_requires='>=3.6',
    zip_safe=True,
    author=fabkit.__author__,
    author_email="karol.hor@gmail.com",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Systems Administration',
    ]
)
