from setuptools import setup

setup(
    name="alias.rc",
    version="0.0.3",
    author='Omer M. A.',
    description='Keep your .zshrc/.bashrc in sync across all your devices',
    author_email="om@env.li",
    license='Apache2',
    py_modules=['rc'],
    install_requires=[
        'Click', 'usersettings', 'simple-crypt'
    ],
    entry_points='''
        [console_scripts]
        rc=rc:cli
    '''
)