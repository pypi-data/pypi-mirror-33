from distutils.core import setup

setup(
    name="naughties",
    version="0.1.2",
    author="Chad Estioco",
    author_email="chadestioco@gmail.com",
    packages=["naughties"],
    data_files=[("", ["blns.json"])],
    install_requires=["Faker==0.8.16"],
    license="MIT",
    description="Fakers that return naughty strings."
)
