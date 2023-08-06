from setuptools import setup

REQUIRES = [
    "numpy"
]
TEST_REQUIRES = [
    "numpy", "pytest-cov", "coverage"
]
setup(
        name='Symple',
        version='0.0.3',
        packages=['Symple', 'Symple.Nodes', 'Symple.Nodes.Ops',
            'Symple.tests.Node', 'Symple.tests.Node.Ops'],
        url='https://github.com/harveyslash/Sympyle',
        license='GNU GENERAL PUBLIC LICENSE',
        author='Harshvardhan Gupta',
        author_email='theharshvardhangupta@gmail.com',
        description='Simple Automatic Differentiation in Python ',
        install_requires=REQUIRES,
        test_requires=TEST_REQUIRES,
)
