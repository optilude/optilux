from plone.z3cform import layout

from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

from optilux.cinemacontent.interfaces import IOptiluxSettings
from optilux.cinemacontent import CinemaMessageFactory as _

class OptiluxControlPanelForm(RegistryEditForm):
    schema = IOptiluxSettings
    
    label = _(u"Optilux control panel")
    
OptiluxControlPanelView = layout.wrap_form(OptiluxControlPanelForm, ControlPanelFormWrapper)
