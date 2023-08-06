import setuptools


setuptools.setup(
    name='eventcore-sqs',
    version='0.0.1',
    description='Produce and consume events with SQS.',
    author='Maikel van den Boogerd',
    author_email='maikelboogerd@gmail.com',
    url='https://github.com/maikelboogerd/eventcore-sqs',
    keywords=['event', 'sqs', 'producer', 'consumer'],
    packages=['eventcore_sqs'],
    install_requires=['eventcore', 'boto3'],
    license='MIT',
    zip_safe=False
)
