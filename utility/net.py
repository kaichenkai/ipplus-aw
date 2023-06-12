import logging
from pathlib import Path

import pyasn


from config.constants import IPASN_FILE, AS_NAMES_FILE

logger = logging.getLogger(__name__)


class LazyASN(object):
    """
    Lazy loading asndb file
    """

    def __init__(self, ipasn_file, as_names_file=None):
        assert Path(ipasn_file).exists()
        if as_names_file:
            assert Path(as_names_file).exists()
        self._db = None
        self.ipasn_file = ipasn_file
        self.as_names_file = as_names_file

    @property
    def db(self):
        if self._db is None:
            print('loading asn file')
            self._db = pyasn.pyasn(self.ipasn_file, self.as_names_file)
        return self._db

    def lookup(self, ip):
        as_number, cidr = lazy_asn.db.lookup(ip)
        as_name = lazy_asn.db.get_as_name(as_number)
        return as_number, as_name, cidr


lazy_asn = LazyASN(ipasn_file=IPASN_FILE,
                   as_names_file=AS_NAMES_FILE)
