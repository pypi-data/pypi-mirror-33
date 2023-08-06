"""Signature module for crypto-cookie package
"""
__author__ = "@philipkershaw"
__date__ = "09/07/15"
__copyright__ = "(C) 2015 Science and Technology Facilities Council"
__license__ = "BSD - see LICENSE file in top-level directory"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
import hmac
import hashlib


class VerificationError(Exception):
    """Raise if signature verification failed"""
    
    
class Signature(object):
    """Class for handling HMAC signature of messages"""
    DEFAULT_HASH_ALGORITHM = hashlib.sha256
    
    def __init__(self, hash_algorithm=DEFAULT_HASH_ALGORITHM):
        '''Set hash algorithm and encoding method'''
        self.hash_algorithm = hash_algorithm
        
    def sign(self, msg, key):
        """Calculate digest for input message using the given key"""
        signature = hmac.new(key, msg, self.hash_algorithm)
        digest = signature.digest()

        return digest

    def verify_signature(self, msg, digest, key):
        """Verify digest for input message"""
        calculated_digest = self.sign(msg, key)
        
        if calculated_digest != digest:
            raise VerificationError("Signature verification failed: "
                                    "the calculated digest (%r) doesn't "
                                    "match the input value %r" % 
                                    (calculated_digest, digest))