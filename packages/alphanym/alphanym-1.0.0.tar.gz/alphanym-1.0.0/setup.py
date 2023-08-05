
import setuptools

with open('README.md') as f:
    setuptools.setup(
        name='alphanym',
        version='1.0.0',
        description='Official Alphanym Python Client',
        long_description=f.read().strip(),
        author='Drew French',
        author_email='french@alphanym.com',
        url='https://www.alphanym.com',
        py_modules=[
            'alphanym',
        ],
        install_requires=[
            'requests',
        ],
        license='MIT License',
        zip_safe=False,
        keywords='Alphanym',
        classifiers=[],
    )
