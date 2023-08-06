__author__ = "@williamtucker"
__date__ = "30/05/18"
__copyright__ = "(C) 2015 Science and Technology Facilities Council"
__license__ = "BSD - see LICENSE file in top-level directory"
__contact__ = "william.tucker@stfc.ac.uk"
__revision__ = '$Id$'


class BadTicket(Exception):
    """Exception raised when a ticket can't be parsed."""
    pass
