from setuptools import setup, find_packages
import os

version = '2.0'

setup(name='optilux.theme',
      version=version,
      description="Theme for the Optilux website",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Rob Gietema',
      author_email='rob@fourdigits.nl',
      url='http://optilux-cinemas.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['optilux'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.theming',
          'plone.app.themingplugins',
      ],
      extras_require={
          'test': ['plone.app.testing',]
      },
#     entry_points="""
#     # -*- Entry points: -*-
#     
#     [z3c.autoinclude.plugin]
#     target = plone
#     """,
# uncomment these to re-enable support for Paster local commands
#     setup_requires=["PasteScript"],
#     paster_plugins=["ZopeSkel"],
      )
