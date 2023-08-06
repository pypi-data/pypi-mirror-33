from setuptools import setup

setup(name='lera',
      version='0.2.2',
      description='A journal for your ML experiments. It has lightweight visualization and can store images, sounds, files, models, source code',
      url='https://lera.ai',
      author='Ilya Ovdin',
      author_email='iovdin@lera.ai',
      license='Apache License 2.0',
      entry_points = {
        'console_scripts': ['lera=lera:main'],
      },
      install_requires = [
        'requests', 'numpy', 'pillow'
      ],
      packages=['lera'],
      zip_safe=False)
