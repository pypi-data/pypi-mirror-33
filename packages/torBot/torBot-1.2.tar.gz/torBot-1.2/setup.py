from setuptools import setup, find_packages

setup(
    name="torBot",
    version="1.2",
    packages=find_packages(),
    scripts=['torBot.py'],
    install_requires=['beautifulsoup4>=4.6.0',
                      'PySocks>=1.6.7',
                      'termcolor>=1.1.0',
                      'requests>=2.18.4',
                      'requests_mock>=1.4.0',
                      'tldextract>=2.2.0',
                      'pyinstaller>=3.3.1',
                      'pytest>=3.4.2'],
    package_data={
    '': ['*.text', '*.rst', '*.so']
    },
    description="OSINT tool for Deep and Dark Web",
    license="GNU GPLV3.0",
    keywords="tor dark web osint",
    url="https://github.com/DedSecInside/TorBot"
)
