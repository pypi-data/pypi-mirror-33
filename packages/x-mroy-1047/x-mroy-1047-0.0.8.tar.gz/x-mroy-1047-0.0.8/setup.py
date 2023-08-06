from setuptools import setup, find_packages


setup(name='x-mroy-1047',
    version='0.0.8',
    description='a anayzer package',
    url='https://github.com/Qingluan/.git',
    author='Qing luan',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    install_requires=[ 'mroylib-min>=1.5.1', 'geoip2','fabric3', 'qrcode', 'pillow','image', 'xlwt','xlrd'],
    entry_points={
        'console_scripts': ['x-web=web.main:main', 'x-web-cmd=web.vultr:main']
    },

)
