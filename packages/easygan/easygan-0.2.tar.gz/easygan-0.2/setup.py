from setuptools import setup

setup(name="easygan",
      version="0.2",
      description="easygan",
      url="https://github.com/sleepy-maker/easyGAN",
      author = 'koji kanao',
      author_email = 'kk2796@nyu.edu',
      license="MIT",
      packages=["easygan"],
      scripts=["bin/easygan"],
      install_requires=["tensorflow", "bs4", "requests", "docopt==0.6.2", "keras", "Pillow", "numpy", "lxml"])
