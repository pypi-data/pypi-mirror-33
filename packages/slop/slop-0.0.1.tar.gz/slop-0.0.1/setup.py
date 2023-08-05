import setuptools

extension_mod = setuptools.Extension('slop', sources=['slop_module.c'], libraries=['slopy'])

with open("README.md", "r") as fp:
    long_description = fp.read()

setuptools.setup(
    name='slop',
    version='0.0.1',
    author='naelstrof',
    description='slop bindings for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/naelstrof/slop-python',
    ext_modules=[extension_mod],
    classifiers=(
        'Programming Language :: Python :: 3',
    ),
)
