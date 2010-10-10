"""Definition of the FilmFolder content type. See cinemafolder.py for more
explanation on the statements below.
"""

from zope.interface import implements

from Products.Archetypes import atapi

from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from optilux.cinemacontent.interfaces import IFilmFolder
from optilux.cinemacontent.config import PROJECTNAME

FilmFolderSchema = folder.ATFolderSchema.copy()

finalizeATCTSchema(FilmFolderSchema, folderish=True, moveDiscussion=False)

class FilmFolder(folder.ATFolder):
    """Contains multiple films.
    """
    implements(IFilmFolder)
    
    schema = FilmFolderSchema

atapi.registerType(FilmFolder, PROJECTNAME)
