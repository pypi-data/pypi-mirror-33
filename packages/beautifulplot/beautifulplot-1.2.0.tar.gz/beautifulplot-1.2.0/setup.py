from setuptools import setup

setup(name='beautifulplot',
      version='1.2.0',
      description='Make beautiful plot and statistical analysis effortless.',
      url='https://git.benjamin-gallois.fr/bgallois/BeautifulPlot',
      author='Benjamin Gallois',
      author_email='benjamin.gallois@upmc.fr',
      license='GNU GENERAL PUBLIC LICENSE',
      packages=['beautifulplot'],
      install_requires=[
          'matplotlib', 'numpy', 'scipy'
      ],
      zip_safe=False)
