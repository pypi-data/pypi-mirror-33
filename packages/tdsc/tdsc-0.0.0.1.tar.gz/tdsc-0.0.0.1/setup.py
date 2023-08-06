import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='tdsc',
                 version='0.0.0.1',
                 description='A tiny "desired state configuration" library.',
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url='https://gitlab.com/liamdawson/tiny-desired-state-configuration',
                 author='Liam Dawson',
                 author_email='liam@ldaws.com',
                 license='MIT OR Apache-2.0',
                 packages=setuptools.find_packages(),
                 classifiers=(
                     "Development Status :: 1 - Planning",
                     "Intended Audience :: Developers",
                     "Programming Language :: Python :: 2.7",
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: Apache Software License",
                     "License :: OSI Approved :: MIT License"
                 ))
