from setuptools import setup, find_packages

setup(
    name='trinpyqtt',
    version='0.5.0',
    description='Trinity MQTT Tools for Python clients',
    url='https://bitbucket.org/trintel/trinpyqtt',
    author='Jan Badenhorst',
    author_email='jan@trintel.co.za',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords=['mqtt, raspberrypi', ],
    install_requires=[
        'pycryptodomex',
        'psutil',
        'paho-mqtt'
    ],
    python_requires='~=3.5',
    zip_safe=False)
