import setuptools

setuptools.setup(
    name="crypto-mart",
    version="2.0.8",
    author="Stefano Katsoras",
    author_email="stefano.katsoras@gmail.com",
    license="MIT",
    packages=setuptools.find_packages(),
    install_requires=["requests", "pandas", "numpy", "pyutil @ git+ssh://git@github.com/senderr/pyutil.git"],
)
