from zope.interface import Interface

class IOptiluxTheme(Interface):
    """Marker interface that defines a ZTK browser layer. We can reference
    this in the 'layer' attribute of ZCML <browser:* /> directives to ensure
    the relevant registration only takes effect when this theme is installed.
    
    The browser layer is installed via the browserlayer.xml GenericSetup
    import step.
    """
