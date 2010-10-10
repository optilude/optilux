"""Define a browser view for the Promotion content type. In the FTI 
configured in profiles/default/types/*.xml, this is being set as the default
view of that content type.
"""

from zope.publisher.browser import BrowserView

from optilux.cinemacontent.interfaces import IBannerProvider

class PromotionView(BrowserView):
    """Default view of a promotion
    """
        
    def bannerTag(self):
        bannerProvider = IBannerProvider(self.context)
        return bannerProvider.tag
