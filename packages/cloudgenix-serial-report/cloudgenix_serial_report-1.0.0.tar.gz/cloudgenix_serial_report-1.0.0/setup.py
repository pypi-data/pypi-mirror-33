from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(name='cloudgenix_serial_report',
      version='1.0.0',
      description='Utility to dump all CloudGenix network serial information to an .XLSX file.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/ebob9/cloudgenix_serial_report',
      author='Aaron Edwards',
      author_email='cloudgenix_serial_report@ebob9.com',
      license='MIT',
      install_requires=[
            'cloudgenix >= 5.0.1b1',
            'cloudgenix_idname >= 1.2.0',
            'openpyxl >= 2.5.4'
      ],
      packages=['cloudgenix_serial_report'],
      entry_points={
            'console_scripts': [
                  'serial_report = cloudgenix_serial_report:go',
                  ]
      },
      classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
      ]
      )
