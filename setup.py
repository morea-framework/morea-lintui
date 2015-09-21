from setuptools import setup

setup(name='morea-lintui',
      version='0.1',
      description='A Morea content validator and editor',
      url='https://github.com/morea-framework/morea-lintui',
      author='Henri Casanova',
      entry_points={
          'console_scripts': ['morea-lintui=morea-lintui/morea-lintui:main']
      },
      author_email='henricasanova@gmail.com',
      license='GPL 2',
      packages=['morea-lintui'],
      zip_safe=False,
      install_requires=['urwid', 'PyYaml'],
      include_package_data=True)
