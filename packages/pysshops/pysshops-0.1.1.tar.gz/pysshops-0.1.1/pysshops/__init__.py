__author__ = 'Lorenzo Gaggini'
__email__ = 'lg@lgaggini.net'
__url__ = 'https://github.com/lgaggini/pysshops'
__version__ = '0.1.1'

from .pysshops import SshOps

from .pysshops import SshCommandBlockingException
from .pysshops import SshNetworkException

__all__ = [
        'SshOps',
        'SshCommandBlockingException',
        'SshNetworkException',
     ]
