from setuptools import setup, find_packages

with open('README.md') as readme_file:
    long_desc = readme_file.read()

setup(
    name='lektor-gitlab',
    version='0.1.0',
    packages=find_packages(),
    url='https://gitlab.com/NiekKeijzer/lektor-gitlab',
    license='MIT',
    author='Niek Keijzer',
    author_email='info@niekkeijzer.com',
    description='Query the Gitlab API right from your Lektor templates',
    long_description=long_desc,
    install_requires=[
        'lektor',
        'python-gitlab',
    ],
    entry_points={
        'lektor.plugins': [
            'gitlab = lektor_gitlab:GitlabPlugin',
        ]
    },
    classifiers=[
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Framework :: Lektor',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
    ],
)
