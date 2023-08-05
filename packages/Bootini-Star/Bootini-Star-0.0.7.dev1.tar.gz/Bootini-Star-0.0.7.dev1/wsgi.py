"""
Launch module for Bootini Star. This allows BS to be run in the NGINX Unit
dynamic application server.
"""
__author__ = 'Ralph Seichter'

from bootini_star import app as application

if __name__ == "__main__":
    application.run()
