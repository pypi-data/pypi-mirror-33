from setuptools import setup, find_packages

setup(
    name='fabkit',
    version='0.1.0.dev1',
    packages=find_packages(),
    license='MIT',
    install_requires=[
        "fabric3>=1.7.0",
    ],
    python_requires='>=3.6',
    zip_safe=False,
    author="Karol Horowski",
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
