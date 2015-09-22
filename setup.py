from setuptools import setup, find_packages

setup(name='morealintui',
      version='0.1',
      description='A Morea content validator and editor',
      url='https://github.com/morea-framework/morea-lintui',
      author='Henri Casanova',
      packages=find_packages(exclude=['build','dist']),
      #      py_modules = ['morealintui.morealintui'],
      entry_points={
          'console_scripts': ['morea-lintui = morealintui.morealintui:main'],
      },
      author_email='henricasanova@gmail.com',
      license='GPL 2',
      zip_safe=False,
      install_requires=['urwid', 'PyYaml'],
      include_package_data=True)
