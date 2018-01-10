from setuptools import setup

setup(
    name='VPS',
    version='0.1.0',
    description='Variant Prioratization System',
    url='www',
    author='Marton Munz',
    author_email='munzmarci@gmail.com',
    license='MIT',
    packages=['vps_'],
    scripts=['bin/vps', 'bin/VPS.py'],
    zip_safe=False
)
