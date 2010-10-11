import unittest2 as unittest

from plone.testing.z2 import Browser

from optilux.cinemacontent.testing import OPTILUX_CINEMACONTENT_FUNCTIONAL_TESTING

class TestEnquiryForm(unittest.TestCase):

    layer = OPTILUX_CINEMACONTENT_FUNCTIONAL_TESTING

    def test_email_validation_error(self):
        app = self.layer['app']
        portal = self.layer['portal']
        
        browser = Browser(app)
        browser.handleErrors = False
        
        # Open form
        browser.open("%s/@@make-an-enquiry" % portal.absolute_url())
        
        # Fill in the form 
        browser.getControl(name=u"form.widgets.subject").value = u"Hello"
        browser.getControl(name=u"form.widgets.name").value = u"John Smith"
        browser.getControl(name=u"form.widgets.emailAddress").value = u"invalid"
        browser.getControl(name=u"form.widgets.message").value = u"test"
        
        # Submit
        browser.getControl(u"Send").click()
        
        self.assertTrue(u"Invalid email address" in browser.contents)
        
    def test_send_mail(self):
        app = self.layer['app']
        portal = self.layer['portal']
        
        # Set up a target address
        portal._setPropValue('email_from_address', "admin@example.com")
        
        # Commit the transaction so the test browser sees our changes
        import transaction; transaction.commit()
        
        # Submit the form
        
        browser = Browser(app)
        browser.handleErrors = False
        
        # Open form
        browser.open("%s/@@make-an-enquiry" % portal.absolute_url())
        
        # Fill in the form 
        browser.getControl(name=u"form.widgets.subject").value = u"Hello"
        browser.getControl(name=u"form.widgets.name").value = u"John Smith"
        browser.getControl(name=u"form.widgets.emailAddress").value = u"test@example.com"
        browser.getControl(name=u"form.widgets.message").value = u"test"
        
        # Submit
        browser.getControl(u"Send").click()
        
        # We should be back at the front page
        self.assertEqual(browser.url, portal.absolute_url())
