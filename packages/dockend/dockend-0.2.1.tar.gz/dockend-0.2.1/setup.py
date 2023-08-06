from setuptools import setup

setup(
    name='dockend',
    version='0.2.1',
    author='Christian Vidal',
    author_email='chris.vidal10@gmail.com',
    url='https://github.com/ChrisVidal10/dockend',
    packages=['dockend'],
    description='Change backend for BYR-Microservices and DLA-backend-services',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],
    keywords='sample setuptools development docker',
    install_requires=[
        "docker",
        "termcolor"
    ],
    entry_points={
        'console_scripts': [
            'dockend = dockend.dockend:main',
        ],
    }
)
