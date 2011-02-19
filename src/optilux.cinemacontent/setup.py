from setuptools import setup, find_packages
import os

version = '2.0'

setup(name='optilux.cinemacontent',
      version=version,
      description="Content types for the Optilux Cinemas project",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='optilux content',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://optilux-cinemas.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['optilux'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
          'plone.app.dexterity [grok]',
          'plone.app.referenceablebehavior',
          'plone.app.relationfield',
          'plone.namedfile [blobs]', # makes sure we get blob support
          'archetypes.schemaextender',
          'plone.app.registry',
          'plone.app.z3cform',
          'zope.annotation',
          'z3c.saconfig',
          'MySQL-python',
          'five.globalrequest',
          'collective.beaker',
      ],
      extras_require={
          'test': ['plone.app.testing',]
      },
#      entry_points="""
#      # -*- Entry points: -*-
#
#      [z3c.autoinclude.plugin]
#      target = plone
#      """,
## uncomment these to re-enable support for Paster local commands
#     setup_requires=["PasteScript"],
#     paster_plugins=["ZopeSkel"],
      )
