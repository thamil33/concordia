"""Install script for setuptools."""

import setuptools


def _remove_excluded(description: str) -> str:
  description, *sections = description.split('<!-- GITHUB -->')
  for section in sections:
    excluded, included = section.split('<!-- /GITHUB -->')
    del excluded
    description += included
  return description


with open('README.md') as f:
  LONG_DESCRIPTION = _remove_excluded(f.read())


setuptools.setup(
    name='gdm-concordia',
    version='2.0.1',
    license='Apache 2.0',
    license_files=['LICENSE'],
    url='https://github.com/google-deepmind/concordia',
    download_url='https://github.com/google-deepmind/concordia/releases',
    author='DeepMind | Tyler Hamilton',
    author_email='tyler.hamilton9897@gmail.com',
    description=(
        'A library for building a generative model of social interacions.'
    ),
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    keywords=(
        'multi-agent agent-based-simulation generative-agents python'
        ' machine-learning'
    ),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    packages=setuptools.find_packages(include=['concordia', 'concordia.*']),
    package_data={},
    python_requires='>=3.11',
    install_requires=(
        'absl-py',
        'boto3',
        'google-cloud-aiplatform',
        'google-generativeai>=0.8',
        'ipython',
        'jinja2',
        'langchain-community',
        'matplotlib',
        'mistralai',
        'numpy>=1.26',
        'ollama',
        'openai>=1.3.0',
        'pandas',
        'python-dateutil',
        'reactivex',
        'retry',
        'termcolor',
        'together',
        'transformers',
        'typing-extensions',
    ),
    extras_require={
        # Used in development.
        'dev': [
            'build',
            'isort',
            'jupyter',
            'pipreqs',
            'pip-tools',
            'pyink',
            'pylint',
            'pytest-xdist',
            'pytype',
            'twine',
        ],
    },
)
