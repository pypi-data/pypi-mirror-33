from setuptools import setup

setup(name='limetree',
      version='0.1',
      description='Async HTTP/2 web framework',
      author='Adam Hopkins',
      author_email='admhpkns@gmail.com',
      license='MIT',
      packages=['src'],
      zip_safe=False,
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Framework :: Trio',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ])
