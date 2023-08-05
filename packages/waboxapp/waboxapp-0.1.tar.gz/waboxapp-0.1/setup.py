from setuptools import setup, find_packages
setup(
        name='waboxapp',
        packages=find_packages(),
        scripts=["bin/waboxapp"],
        version='0.1',
        description='Waboxapp library for accessing waboxapp.com api',
        author='Cristiano W. Araujo',
        author_email='cristianowerneraraujo@gmail.com',
        url='https://github.com/cristianowa/waboxapp',
        download_url='https://github.com/cristianowa/waboxapp/archive/0.1.zip',
        keywords=['whatsup', 'waboxapp', 'instant message'],
        classifiers=[],
     )
