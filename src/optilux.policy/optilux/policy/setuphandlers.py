from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.setuphandlers import DEFAULT_POLICIES

def setupGroups(portal):
    acl_users = getToolByName(portal, 'acl_users')
    if not acl_users.searchGroups(name='Staff'):
        gtool = getToolByName(portal, 'portal_groups')
        gtool.addGroup('Staff', roles=['StaffMember'])

def setVersionedTypes(portal):
    portal_repository = getToolByName(portal, 'portal_repository')
    
    versionableTypes = list(portal_repository.getVersionableContentTypes())
    for typeId in ('Film', 'Cinema', 'Promotion',):
        if typeId not in versionableTypes:
            versionableTypes.append(typeId)
            # Add default versioning policies to the versioned type
            for policyId in DEFAULT_POLICIES:
                portal_repository.addPolicyForContentType(typeId, policyId)
    portal_repository.setVersionableContentTypes(versionableTypes)

def importVarious(context):
    """Miscellanous steps import handle
    """
    
    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a 
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.
    
    if context.readDataFile('optilux.policy-various.txt') is None:
        return
    
    portal = context.getSite()
    
    setupGroups(portal)
    setVersionedTypes(portal)
