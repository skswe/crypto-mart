import setuptools

setuptools.setup(
    name="crypto-arb",
    version="1.0.0",
    author="Stefano Katsoras",
    author_email="stefano.katsoras@gmail.com",
    license="MIT",
    packages=setuptools.find_packages(),
    install_requires=["requests", "pandas", "numpy", "IPython", "plotly"],
)
