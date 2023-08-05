from setuptools import setup

setup(
    name='espoem_facts',
    version='0.0.6',
    packages=["espoem_facts",],
    url='http://github.com/emre/espoem_facts',
    license='MIT',
    author='emre yilmaz',
    author_email='mail@emreyilmaz.me',
    description='an @espoem fact bot on steem blockchain',
    entry_points={
        'console_scripts': [
            'espoem_facts = espoem_facts.main:main',
        ],
    },
    install_requires=["steem"]
)
