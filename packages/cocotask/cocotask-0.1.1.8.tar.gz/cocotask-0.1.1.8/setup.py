from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
	name='cocotask',
    
	version='0.1.1.8',
    
    description='An unified framework to build task queue on Rabbitmq | Kafka | Redis',
    long_description=long_description,
    long_description_content_type='text/markdown', 

    url='https://github.com/likexx/cocotask',
    
    author='Like Zhang',
    
    author_email='zlike@yahoo.com',

    license='MIT',  
    
#    packages=[''],
    packages=find_packages(exclude=['release.sh']),

    zip_safe=False,
      
    entry_points={
        'console_scripts': [
            'cocotask = cocotask.taskrunner:main',
        ],
    },

	keywords='task message queue MQ Pika kafka-python rabbitmq kafka redis rmq producer consumer celery',
    
    install_requires=['pika', 'kafka-python', 'redis', 'jsmin'],

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/likexx/cocotask/issues',
        'Funding': 'https://github.com/likexx/cocotask/',
        'Say Thanks!': 'https://github.com/likexx/cocotask/',
        'Source': 'https://github.com/likexx/cocotask/',
    },
)

