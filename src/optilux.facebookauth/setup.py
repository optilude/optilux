from setuptools import setup, find_packages
import os

version = '2.0'

setup(name='optilux.facebookauth',
      version=version,
      description="Facebook authentication for Optilux Cinemas",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['optilux'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.interface',
          'zope.publisher',
          'zope.i18nmessageid',
          'five.globalrequest',
          'collective.beaker',
          'Products.PluggableAuthService',
          'Products.PlonePAS',
          'Products.statusmessages',
      ],
      extras_require={
          'test': ['plone.app.testing',]
      },
      # entry_points="""
      # # -*- Entry points: -*-
      # 
      # [z3c.autoinclude.plugin]
      # target = plone
      # """,
      # setup_requires=["PasteScript"],
      # paster_plugins=["ZopeSkel"],
      )
