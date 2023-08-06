"""Cookie implementation based on Paste's AuthTicket for crypto-cookie package
"""
__author__ = "@philipkershaw"
__date__ = "09/07/15"
__copyright__ = "(C) 2015 Science and Technology Facilities Council"
__license__ = "BSD - see LICENSE file in top-level directory"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'

import time as time_mod
try:
    from http.cookies import SimpleCookie
except ImportError:
    from Cookie import SimpleCookie

from six import string_types
from six.moves.urllib.parse import quote, unquote

from .encoding import Encoder
from .exceptions import BadTicket


class SecureCookie(object):
    '''This class represents an authentication token. The structure is based
    on AuthTicket from paste.auth.auth_tkt (https://pypi.org/project/Paste/).
    '''
    
    def __init__(self, secret, userid, ip, tokens=(), user_data='',
                 time=None, cookie_name='auth_tkt', secure=False):
        
        self.secret = secret
        self.userid = userid
        self.ip = ip
        if not isinstance(tokens, string_types):
            tokens = ','.join(tokens)
        self.tokens = tokens
        self.user_data = user_data
        if time is None:
            self.time = time_mod.time()
        else:
            self.time = time
        self.cookie_name = cookie_name
        self.secure = secure
    
    def digest(self):
        '''Don't calculate a digest because this is done as an independent step
        following encryption of the cookie
        '''
        return ''
    
    @classmethod
    def parse_ticket(cls, secret, ticket, ip, session):
        '''Parse cookie and check its signature.
        
        :var secret: shared secret used between multiple trusted peers to 
        verify signature of cookie
        :var ticket: signed cookie content
        :var ip: originating client IP address - extracted from X Forwarded
        or Remote address iterms in HTTP header
        :var session: AuthKit session object content
        :return: tuple of parsed cookie content
        '''
        if session is not None:
            if 'authkit.cookie.user' not in session:
                raise BadTicket('No authkit.cookie.user key exists in the '
                                'session')
            if 'authkit.cookie.user_data' not in session:
                raise BadTicket('No authkit.cookie.user_data key exists in the '
                                'session')

        decrypted_ticket = Encoder().decode_msg(ticket, secret)
        
        try:
            timestamp = int(decrypted_ticket[:8], 16)
            
        except ValueError as e:
            raise BadTicket('Timestamp is not a hex integer: %s' % e)
            
        try:
            userid, data = decrypted_ticket[8:].split('!', 1)
            
        except ValueError:
            raise BadTicket('userid is not followed by !')
        
        userid = unquote(userid)
        if '!' in data:
            tokens, user_data = data.split('!', 1)
            tokens = tokens.split(',')
        else:
            tokens = []
            user_data = data
        
        return timestamp, userid, tokens, user_data
    
    def cookie_value(self):
        """Extend cookie_value method to enable encryption, encoding and signing 
        of encrypted cipher text
        
        :return: signed and encrypted cookie encoded as hexadecimal string
        """
        cookie_val = '%s%08x%s!' % (self.digest(), int(self.time), quote(self.userid))
        if self.tokens:
            cookie_val += self.tokens + '!'
        cookie_val += self.user_data
        
        encoded_cookie_val = Encoder().encode_msg(cookie_val, self.secret)
        
        return encoded_cookie_val
    
    def cookie(self):
        c = SimpleCookie()
        c[self.cookie_name] = self.cookie_value().encode('base64').strip().replace('\n', '')
        c[self.cookie_name]['path'] = '/'
        if self.secure:
            c[self.cookie_name]['secure'] = 'true'
        return c
