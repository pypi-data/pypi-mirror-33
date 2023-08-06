import setuptools

setuptools.setup(
    name='petroleum',
    version="0.0.1",
    author='Bas Wind',
    author_email='mailtobwind+petroleum@gmail.com',
    description='A pure workflow engine for Python',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/bwind/petroleum',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
    ],
)
