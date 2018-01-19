from setuptools import setup

setup(
    name='VPS',
    version='0.1.0',
    description='Variant Prioratization System',
    url='https://github.com/RahmanTeamDevelopment/VPS',
    author='RahmanTeam',
    author_email='rahmanlab@icr.ac.uk',
    license='MIT',
    packages=['vps_'],
    scripts=['bin/vps', 'bin/VPS.py'],
    zip_safe=False
)