import environ

env = environ.Env()


class CacheKey:
    """Redis 缓存的 key常量"""

    view = 'view:%s'  # 缓存查询view

    # exit_addresses = 'exit_addresses'  # 缓存出口地址数据

# awdb file path
AWDB_FILE_PATH = env('AWDB_FILE_PATH', default='/data/ipplus/IP_ultimate_cn_2023M06_multi_BD09_WGS84.awdb')
#
# For ASN Lookup
IPASN_FILE = env('IPASN_FILE', default='/data/ipplus/ipasn_20200927.dat')
AS_NAMES_FILE = env('AS_NAMES_FILE', default='/data/ipplus/asnames.json')
