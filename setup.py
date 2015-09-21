from setuptools import setup

setup(name='morealintui',
      version='0.1',
      description='A Morea content validator and editor',
      url='https://github.com/morea-framework/morea-lintui',
      author='Henri Casanova',
      entry_points={
          'console_scripts': ['morealintui = morealintui.morealintui:main']
      },
      author_email='henricasanova@gmail.com',
      license='GPL 2',
      packages=['morealintui'],
      zip_safe=False,
      install_requires=['urwid', 'PyYaml'],
      include_package_data=True)
