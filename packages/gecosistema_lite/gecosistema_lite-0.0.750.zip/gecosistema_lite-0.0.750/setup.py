from distutils.core import setup

setup(name='gecosistema_lite',
      version='0.0.750',
      description='A simple python package',
      author='Valerio Luzzi',
      author_email='valerio.luzzi@gecosistema.it',
      url='https://github.com/valluzzi/libcore/',
      license='MIT',
      packages=['gecosistema_lite'],

      package_data={
          "gecosistema_lite": ["R/qkrige_v4.r"]
      },
      zip_safe=False,
      install_requires=['pyproj', 'rarfile', 'xlrd', 'xlwt', 'xlutils', 'jinja2', 'xmljson',
                        'openpyxl',
                        #'pycrypto', #some problems id msvc is not installed
                        'pyodbc',
                        'future', 'six'
                       ],
      python_requires='>=2.7'
      )
