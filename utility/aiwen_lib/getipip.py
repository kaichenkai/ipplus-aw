# encoding: utf-8

import json
import os

import ipdb
from tornado.log import app_log

# -------------------------------------------  ipip config start   --------------------------------------------
IPIP_CONFIG = {
    'ipip_v4_cn': os.getenv('CITY_DB_CN', '/data/ipip/ipv4_cn.ipdb'),
    'ipip_v4_en': os.getenv('CITY_DB_EN', '/data/ipip/ipv4_en.ipdb'),
    'ipip_country': os.getenv('COUNTRY_FILE', '/data/ipip/country.json')
}

# -------------------------------------------  ipip config end   --------------------------------------------


class IpipInfos:
    def __init__(self):
        self.lat = ""
        self.lon = ""
        self.country_code = ""
        self.country_cn_name = ""
        self.country_en_name = ""
        self.subd_cn_name = ""
        self.subd_en_name = ""
        self.city_cn_name = ""
        self.city_en_name = ""
        self.continent_code = ""
        self.continent_cn_name = ""
        self.continent_en_name = ""
        self.isp = ""
        self.organization = ""
        self.organization_CN = ""
        self.idc = ""
        self.base_station = ""

    def get_continent_name_from_code(self):
        continent_mapping = {"AP": ["Asia", u"亚洲"],
                             "AF": ["Africa", u"非洲"],
                             "EU": ["Europe", u"欧洲"],
                             "LA": ["South America", u"南美洲"],
                             "NA": ["North American", u"北美洲"],
                             "OA": ["Australia", u"大洋洲"],
                             "AQ": ["Antarctica", u"南极洲"]}
        if self.continent_code in continent_mapping:
            self.continent_cn_name = continent_mapping[self.continent_code][1]
            self.continent_en_name = continent_mapping[self.continent_code][0]
        else:
            self.continent_cn_name = None
            self.continent_en_name = None


class GetIpip(object):
    # def __init__(self, city_db="/data/ipip/mydata4vipday4.ipdb"):
    def __init__(self, city_db_en=IPIP_CONFIG['ipip_v4_en'],
                 city_db_cn=IPIP_CONFIG['ipip_v4_cn'],
                 COUNTRY_FILE=IPIP_CONFIG['ipip_country']):
        self.ipip_db_en = ipdb.City(city_db_en)
        self.ipip_db_cn = ipdb.City(city_db_cn)

        try:
            with open(COUNTRY_FILE) as f:
                country_dict = json.loads(f.read())
                self.country_list = country_dict["country"]
        except Exception as e:
            app_log("Failed to read country list err_info: %s", e)

    def get_ipipinfo_from_ip(self, ip):
        ipip_info = IpipInfos()
        en_result = self.ipip_db_en.find_map(ip, "EN")
        cn_result = self.ipip_db_cn.find_map(ip, "CN")
        # print('cn_result:',cn_result)
        ipip_info.lat = en_result["latitude"]
        ipip_info.lon = en_result["longitude"]
        ipip_info.country_code = en_result["country_code"]
        if ipip_info.country_code in ("TW", "MO", "HK"):
            ipip_info.country_code = "CN"
        if ipip_info.country_code == "CN":
            ipip_info.country_cn_name = u"中国"
            ipip_info.city_en_name = "China"
        ipip_info.country_cn_name = cn_result["country_name"]
        ipip_info.country_en_name = en_result["country_name"]
        ipip_info.subd_cn_name = cn_result["region_name"]
        ipip_info.subd_en_name = en_result["region_name"]
        ipip_info.city_cn_name = cn_result["city_name"]
        ipip_info.city_en_name = en_result["city_name"]
        ipip_info.isp = en_result["isp_domain"]
        ipip_info.continent_code = en_result["continent_code"]
        ipip_info.organization = en_result["owner_domain"]
        ipip_info.organization_CN = cn_result["owner_domain"]
        if ipip_info.organization == "":
            ipip_info.organization = ipip_info.organization_CN

        ipip_info.base_station = en_result["base_station"]
        ipip_info.idc = en_result["idc"]
        ipip_info.asn = None
        if eval(en_result['asn_info']):
            try:
                ipip_info.asn = eval(en_result['asn_info'])[0]['asn']
            except Exception as e:
                app_log('get asn error: %s', e)
        ipip_info.get_continent_name_from_code()

        return ipip_info

    def get_ipip(self, ip):
        if ip is None:
            return None
        ipip_info = self.get_ipipinfo_from_ip(ip)
        geoinfo = {"country": {"names": {}, "code": None},
                   "subdivisions": {"names": {}},
                   "city": {"names": {}},
                   "continent": {"names": {}},
                   "location": {'lon': None, 'lat': None},
                   "organization": None,
                   "organization_CN": None,
                   "aso": None,
                   "asn": None}

        try:
            float(ipip_info.lat)
            float(ipip_info.lon)

            geoinfo["location"]["lon"] = ipip_info.lon
            geoinfo["location"]["lat"] = ipip_info.lat

        except ValueError:
            app_log.info("Invalid response from IPIP for ip: %s,lat:%s,lon:%s", ip, ipip_info.lat, ipip_info.lon)

        geoinfo['base_station'] = ipip_info.base_station
        geoinfo['idc'] = ipip_info.idc
        if self.country_list and ipip_info.country_cn_name not in self.country_list:
            return geoinfo

        geoinfo['PoweredBy'] = "IPIP"

        geoinfo["country"] = {
            'names': {
                "en": ipip_info.country_en_name,
                "zh-CN": ipip_info.country_cn_name
            },
            # "geoname_id":None,
            "code": ipip_info.country_code,
        }
        geoinfo["subdivisions"] = {
            'names': {
                "en": ipip_info.subd_en_name,
                "zh-CN": ipip_info.subd_cn_name
            },
            # "geoname_id":None,
            "code": None,
        }
        geoinfo["city"] = {
            'names': {
                "en": ipip_info.city_en_name,
                "zh-CN": ipip_info.city_cn_name
            },
            # "geoname_id":None,
        }

        geoinfo["continent"] = {
            'names': {
                "en": ipip_info.continent_en_name,
                "zh-CN": ipip_info.continent_cn_name
            },
            # "geoname_id":None,
            "code": ipip_info.continent_code,
        }

        if ipip_info.organization:
            geoinfo["organization"] = ipip_info.organization
            geoinfo["organization_CN"] = ipip_info.organization_CN

        geoinfo['isp'] = ipip_info.isp
        return geoinfo

if __name__ == '__main__':
    ipip = GetIpip()
    print(ipip.get_ipip("206.197.187.10"))
    # print(ipip.get_ipip("117.36.0.189"))
    # print(ipip.get_ipip("1.244.42.177"))
    # print(ipip.get_ipip("64.71.39.113"))
