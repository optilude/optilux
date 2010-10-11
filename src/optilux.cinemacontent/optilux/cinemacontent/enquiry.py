import re

from five import grok
from plone.directives import form

from zope.interface import Interface
from zope.interface import Invalid
from zope import schema

from z3c.form import field, button

from Products.statusmessages.interfaces import IStatusMessage

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from optilux.cinemacontent import CinemaMessageFactory as _

checkEmail = re.compile(r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)*[a-zA-Z]{2,4}").match
def validateEmail(value):
    if not checkEmail(value):
        raise Invalid(_(u"Invalid email address"))
    return True
    
MESSAGE_TEMPLATE = """\
Enquiry from: %(name)s <%(emailAddress)s>

%(message)s
"""

class IEnquiryForm(Interface):
    """Define the fields of our form
    """
    
    subject = schema.TextLine(
            title=_(u"Subject"),
        )
    
    name = schema.TextLine(
            title=_(u"Your name"),
        )
    
    emailAddress = schema.ASCIILine(
            title=_(u"Your email address"),
            description=_(u"We will use this to contact you if you request it"),
            constraint=validateEmail
        )
    
    message = schema.Text(
            title=_(u"Message"),
            description=_(u"Please keep to 1,000 characters"),
            max_length=1000
        )

class EnquiryForm(form.Form):
    """The enquiry form
    """
    
    grok.context(ISiteRoot)
    grok.name('make-an-enquiry')
    grok.require('zope2.View')
    
    fields = field.Fields(IEnquiryForm)
    
    label = _(u"Make an enquiry")
    description = _(u"Got a question or comment? Please submit it using the form below!")
    
    ignoreContext = True
    
    # Hide the editable border and tabs
    def update(self):
        self.request.set('disable_border', True)
        return super(EnquiryForm, self).update()
    
    @button.buttonAndHandler(_(u"Send"))
    def sendMail(self, action):
        """Send the email to the site administrator and redirect to the
        front page, showing a status message to say the message was received.
        """
        
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        
        mailhost = getToolByName(self.context, 'MailHost')
        urltool = getToolByName(self.context, 'portal_url')
        
        portal = urltool.getPortalObject()

        # Construct and send a message
        toAddress = portal.getProperty('email_from_address')
        source = "%s <%s>" % (data['name'], data['emailAddress'])
        subject = data['subject']
        message = MESSAGE_TEMPLATE % data

        mailhost.send(message, mto=toAddress, mfrom=str(source), subject=subject)
        
        # Issue a status message
        confirm = _(u"Thank you! Your enquiry has been received and we will respond as soon as possible")
        IStatusMessage(self.request).add(confirm, type='info')
        
        # Redirect to the portal front page. Return an empty string as the
        # page body - we are redirecting anyway!
        self.request.response.redirect(portal.absolute_url())
        return ''
    
    @button.buttonAndHandler(_(u"Cancel"))
    def cancelForm(self, action):
        
        urltool = getToolByName(self.context, 'portal_url')
        portal = urltool.getPortalObject()
        
        # Redirect to the portal front page. Return an empty string as the
        # page body - we are redirecting anyway!
        self.request.response.redirect(portal.absolute_url())
        return u''
