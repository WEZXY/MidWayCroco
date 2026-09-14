from setuptools import find_packages, setup

package_name = 'arduino_control_system'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='elmoslimany',
    maintainer_email='elmoslimanym@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'arduino_serial = arduino_control_system.arduino_serial:main',
            'control_unit = arduino_control_system.control_unit:main',
        ],
    },
)
