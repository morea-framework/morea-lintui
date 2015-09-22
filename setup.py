from setuptools import setup

setup(name='morealintui',
      version='0.1',
      description='A Morea content validator and editor',
      url='https://github.com/morea-framework/morea-lintui',
      author='Henri Casanova',
#      py_modules = ['morealintui.MOREA', 'morealintui.Testing', 'morealintui.Toolbox', 'morealin.TUI'],
      entry_points={
          'console_scripts': ['morea-lintui = morealintui.morealintui:main'],
      },
      author_email='henricasanova@gmail.com',
      license='GPL 2',
      packages=['morealintui', 'morealintui.MOREA', 'morealintui.Toolbox', 'morealintui.TUI', 'morealintui.Testing'],
      zip_safe=False,
      install_requires=['urwid', 'PyYaml'],
      include_package_data=True)
