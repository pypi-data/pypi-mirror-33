from setuptools import setup, find_packages


setup(name='x-mroy-1046',
    version='0.2.6',
    description='a anayzer package',
    url='https://github.com/Qingluan/.git',
    author='Qing luan',
    author_email='darkhackdevil@gmail.com',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    install_requires=['rsa', 'mroylib-min','fabric3', 'qrcode', 'pillow','image', 'xlwt','xlrd'],
    entry_points={
        'console_scripts': ['x-relay=seed.mrpackage.services:main', 'x-control=seed.mrclients.controll:main', 'x-bak=seed.mrpackage.services:main_start_bak','x-async=seed.mrservers.local:start_socket_service', 'x-asyncs=seed.mrservers.local:run_local_async']
    },

)
