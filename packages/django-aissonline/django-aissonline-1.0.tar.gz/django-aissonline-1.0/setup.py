import setuptools

with open("README.md", "r", encoding='utf8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-aissonline",
    version="1.0",
    author='ercjul',
    author_email='geofvt@gmail.com',
    license='MIT License',
    description='基于django的在线aiss套图',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ercJuL/django-aissonline",
    packages=setuptools.find_packages(),
    package_data={
        'django-aissonline':['static/aissonline/*.html'],
    },
    install_requires = [
        'Django>=2',
        'requests>=2',
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)