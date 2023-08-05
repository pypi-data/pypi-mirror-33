
import setuptools

setuptools.setup(
    name='alphanym',
    version='1.0.2',
    description='Official Alphanym Python Client',
    long_description='Official Alphanym Python Client',
    author='Drew French',
    author_email='french@alphanym.com',
    url='https://www.alphanym.com',
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
    ],
    license='MIT License',
    zip_safe=False,
    keywords='Alphanym',
    classifiers=[],
)
