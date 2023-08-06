'''
    Module:
        Conf

    Description:
        This is a sub-component of Genie that Configures topology through Python object
        attributes, featuring a common object structure. These object's structures
        means that they are compatible with all operating systems and Management
        Interfaces (such as CLI/Yang/REST, etc.)

'''

# metadata
__version__ = '3.0.2'
__author__ = 'Cisco Systems Inc.'
__contact__ = ['pyats-support@cisco.com', 'pyats-support-ext@cisco.com']
__copyright__ = 'Copyright (c) 2018, Cisco Systems Inc.'

from .main import Genie
