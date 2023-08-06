"""
A python module to get information from Untappd.
This code is released under the terms of the MIT license. See the LICENSE
file for more details.
"""
import requests

__version__ = '0.0.3'

class Untappd:
    """This class is used to get information from Untappd."""
    BASE_URL = 'https://api.untappd.com/v4/'

    def __init__(self):
        """Initialize"""

    def get_last_activity(self, api_id, secret, username):
        """Get the last activity for the spesified user"""
        auth = '?client_id=' + api_id + '&client_secret=' + secret
        fetchurl = self.BASE_URL + 'user/checkins/' + username + auth
        try:
            get_last_activity = requests.get(fetchurl, timeout=2).json()
        except:
            activity = None
        else:
            activity = get_last_activity['response']['checkins']['items'][0]
            return activity

    def get_info(self, api_id, secret, username):
        """Get information for the spesified user"""
        auth = '?client_id=' + api_id + '&client_secret=' + secret
        fetchurl = self.BASE_URL + 'user/info/' + username + auth
        try:
            get_info = requests.get(fetchurl, timeout=2).json()
        except:
            userinfo = None
        else:
            userinfo = get_info['response']['user']
            return userinfo

    def get_wishlist(self, api_id, secret, username):
        """Get information for the spesified user"""
        auth = '?client_id=' + api_id + '&client_secret=' + secret
        fetchurl = self.BASE_URL + 'user/wishlist/' + username + auth
        try:
            get_wishlist = requests.get(fetchurl, timeout=2).json()
        except:
            wishlist = None
        else:
            wishlist = get_wishlist['response']['beers']['items']
            return wishlist
