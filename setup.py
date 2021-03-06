from setuptools import setup, find_packages

setup(name='morea-lintui',
      version='0.1',
      description='A Morea content validator and editor',
      url='https://github.com/morea-framework/morea-lintui',
      author='Henri Casanova',
      packages=find_packages(exclude=['build','dist']),
      entry_points={
          'console_scripts': ['morea-lintui = morealintui.morealintui:main'],
      },
      author_email='henricasanova@gmail.com',
      license='GPL 2',
      zip_safe=False,
      install_requires=['urwid>=1.3.0', 'PyYaml'],
      include_package_data=True)
