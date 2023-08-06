import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easy_scrape",
    version="0.0.2",
    author="Sarthak Negi",
    author_email="sarthaknegi609@gmail.com",
    description="Helps in Scraping the Web",
    url="https://github.com/sarthaknegi/easy_scrape",
    packages=setuptools.find_packages(),
    install_required=['requests','BeautifulSoup','selenium','pandas','webdriver'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)