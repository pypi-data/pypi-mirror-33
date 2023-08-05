from setuptools import setup,find_packages
setup(  
      name='gsapp',
      version='0.1.2',
      description="gamescience python simple gsapp framework ",
      keywords=['app framework'],  
      author='jj4jj',
      author_email='resc@vip.qq.com',
      license='MIT License',
      py_modules = ['gsapp',],
      requires = ['tornado'],
      include_package_data = True,
      data_files = ['config.json.example'],
      url='https://github.com/jj4jj/gsapp',
)

