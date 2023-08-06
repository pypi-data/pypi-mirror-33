from setuptools import setup

setup(
    name='gnar-gear',
    version='1.0.2',
    description='The gnarliest gear in the world 🤙',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://gitlab.com/gnaar/gear',
    author='Brien R. Givens',
    author_email='ic3b3rg@gmail.com',
    license='MIT',
    packages=['gnar_gear'],
    install_requires=[
        'boto3>=1.7.55',
        'bjoern>=2.2.1',
        'flask>=1.0.2',
        'flask-bcrypt>=0.7.1',
        'flask-jwt-extended>=3.10.0',
        'postgres>=2.2.1'
    ],
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest>=3.6.3',
        'pytest-cov>=2.5.1'
    ],
    zip_safe=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Flask'
    ]
)
