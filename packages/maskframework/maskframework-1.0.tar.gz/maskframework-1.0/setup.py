from distutils.core import setup

setup(name='maskframework',
      version='1.0',
      author='Andreas Frutiger',
      author_email='afrutig89@gmail.com',
      url="https://github.com/afrutig/gdsMaskFramework",
      install_requires=[
        "numpy", "matplotlib","fsc.export"
      ],
      py_modules=['maskframework'],
      )
