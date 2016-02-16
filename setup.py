from setuptools import setup

setup(
    name='pyjmap',
    version='0.0.0',
    description='jmap.io implementation server',
    url='https://github.com/ligro/pyjmap',
    packages=['pyjmap'],
    entry_points={
        'console_scripts': ['pyjmap=pyjmap.__main__:cli'],
    },
    install_requires=[
        'Flask==0.10.1',
        'Flask-SQLAlchemy==2.1',
        'itsdangerous==0.24',
        'Jinja2==2.8',
        'MarkupSafe==0.23',
        'psycopg2==2.6.1',
        'SQLAlchemy==1.0.11',
        'Werkzeug==0.11.3',
        'wheel==0.24.0',
        'click==6.2',
    ],
)
