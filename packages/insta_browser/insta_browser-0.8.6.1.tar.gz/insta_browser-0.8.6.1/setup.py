from setuptools import setup
from insta_browser import version as v


description = open('README.rst').read()

version = v.__version__

setup(
    name='insta_browser',
    packages=['insta_browser'],
    include_package_data=True,
    version=version,
    description='parsing/automation instagram.com',
    long_description=description,
    author='Aleksej Krichevsky',
    author_email='krich.al.vl@gmail.com',
    url='https://github.com/kricha/insta_browser',
    download_url='https://github.com/kricha/insta_browser/archive/{}.tar.gz'.format(version),
    keywords=['parsing', 'bot', 'instabot', 'automation', 'likes'],
    license='MIT',
    classifiers=[  # look here https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Browsers',
    ],
    install_requires=[
        'selenium',
        'tqdm',
        'requests'
    ],
)
