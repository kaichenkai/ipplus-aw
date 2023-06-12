# encoding: utf-8

import json
import logging
import os

from piratebay.lib import awdb

AWDB_CONFIG = {
    'ipip_v4_cn': os.getenv('AW_DB_CN', '/data/awdb/ipv4_cn.awdb'),
    'ipip_v4_en': os.getenv('AW_DB_EN', '/data/awdb/ipv4_en.awdb'),
    'ipip_country': os.getenv('COUNTRY_FILE', '/data/ipip/country.json')
}


class AiwenInfos(object):
    def __init__(self):
        self.lat = ""
        self.lon = ""
        self.latbd = ""
        self.lonbd = ""
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
        self.district_cn_name = ""
        self.district_en_name = ""
        self.isp_en = ""
        self.isp_cn = ""
        self.idc = ""
        self.asn = ""
        self.zipcode = ""  # 邮编
        self.timezone = ""  # 时区
        self.owner_en = ""  # IP 拥有者名
        self.owner_cn = ""  # IP 拥有者名
        self.radius = None
        self.accuracy_en = ""
        self.accuracy_cn = ""
        self.scene_en = ""
        self.scene_cn = ""
        self.usertype_en = ""
        self.usertype_cn = ""
        self.user_en = ""
        self.user_cn = ""

    def get_continent_code_from_name(self):

        continent_mapping = {"Asia": "AP",
                             "Africa": "AF",
                             "Europe": "EU",
                             "South America": "LA",
                             "North American": "NA",
                             "Australia": "OA",
                             "Antarctica": "AQ"}
        if self.continent_en_name in continent_mapping:
            self.continent_code = continent_mapping[self.continent_en_name]
        else:
            self.continent_code = None

    def unify_city_info(self):
        city_mapping = {
            u"Hongkong": u"Hong Kong",
            u"\u4e2d\u56fd\u9999\u6e2f": u"\u9999\u6e2f"
        }

        if self.city_en_name in city_mapping:
            self.city_en_name = city_mapping[self.city_en_name]
        if self.city_cn_name in city_mapping:
            self.city_cn_name = city_mapping[self.city_cn_name]
        if self.subd_en_name in city_mapping:
            self.subd_en_name = city_mapping[self.subd_en_name]
        if self.subd_cn_name in city_mapping:
            self.subd_cn_name = city_mapping[self.subd_cn_name]

    def correct_politics(self):
        if self.country_code in ("TW", "MO", "HK"):
            self.country_code = "CN"
        if self.country_cn_name in [u"台湾", u"澳门", u"香港"]:
            self.country_cn_name = u"中国"
        if self.country_en_name.lower() in ['taiwan', 'macao', 'macau', 'hongkong']:
            self.country_en_name = "China"


class GetAiwen(object):
    def __init__(self, en_db_v4=AWDB_CONFIG['ipip_v4_en'],
                 cn_db_v4=AWDB_CONFIG['ipip_v4_cn'],
                 COUNTRY_FILE=AWDB_CONFIG['ipip_country']):

        self.en_reader = awdb.open_database(en_db_v4)
        self.cn_reader = awdb.open_database(cn_db_v4)
        self.country_list = []
        try:
            with open(COUNTRY_FILE) as f:
                country_dict = json.loads(f.read())
                self.country_list = country_dict["country"]
        except Exception as e:
            logging.warn("Failed to read country list err_info:{}".format(e))

    def _make_geoinfo(self):
        geoinfo = {
            "city": {
                "geoname_id": None,
                "names": {"cn": "", "en": ""}
            },
            "country": {
                "geoname_id": None,
                "code": None,
                "names": {"cn": "", "en": ""}
            },
            "isp": {
                "en": "",
                "cn": ""
            },
            "asn": [],
            "subdivisions": {
                "geoname_id": None,
                "code": None,
                "names": {"cn": "", "en": ""}
            },
            "location": {
                "lat": "",
                "lon": "",
            },
            "location_bd": {
                "lat": "",
                "lon": "",
            },

            "organization": {
                "en": "",
                "cn": ""
            },
            "aso": "",
            "base_station": "",
            "idc": "",
            "zipcode": "",
            "timezone": "",
            "owner": "",
            "continent": {
                "geoname_id": None,
                "code": "",
                "names": {"cn": "", "en": ""}
            },
            "radius": None,
            "district": {
                "geoname_id": None,
                "code": None,
                "names": {
                    "cn": "",
                    "en": ""
                }
            },
            "accuracy": {"en": "", "cn": ""},
            "scene": {"en": "", "cn": ""},
            "usertype": {"en": "", "cn": ""},
            "user": {"en": "", "cn": ""}
        }
        return geoinfo

    def default(self, obj):
        if not obj:
            return ""
        if isinstance(obj, bytes):
            return obj.decode('utf8')
        return obj

    def get_aiweninfo_from_ip(self, ip):
        aw_info = AiwenInfos()
        en_result, en_prefix_len = self.en_reader.get_with_prefix_len(ip)
        cn_result, cn_prefix_len = self.cn_reader.get_with_prefix_len(ip)

        if cn_result.get('multiAreas'):
            cn_area_info = cn_result['multiAreas'][0]
            aw_info.subd_cn_name = self.default(cn_area_info.get("prov"))
            aw_info.city_cn_name = self.default(cn_area_info.get("city"))
            aw_info.district_cn_name = self.default(cn_area_info.get("district"))
            aw_info.lon = cn_area_info.get("lngwgs")
            aw_info.lat = cn_area_info.get("latwgs")
            aw_info.lonbd = cn_area_info.get("lngbd")
            aw_info.latbd = cn_area_info.get("latbd")
            aw_info.radius = self.default(cn_area_info.get("radius"))
        if en_result.get('multiAreas'):
            en_area_info = en_result['multiAreas'][0]
            aw_info.subd_en_name = self.default(en_area_info.get("prov"))
            aw_info.city_en_name = self.default(en_area_info.get("city"))
            aw_info.district_en_name = self.default(en_area_info.get("district"))
        aw_info.accuracy_cn = self.default(cn_result.get("accuracy"))
        aw_info.accuracy_en = self.default(en_result.get("accuracy"))
        aw_info.scene_cn = self.default(cn_result.get("scene"))
        aw_info.scene_en = self.default(en_result.get("scene"))
        aw_info.usertype_cn = self.default(cn_result.get("user_type"))
        aw_info.usertype_en = self.default(en_result.get("user_type"))
        aw_info.user_cn = self.default(cn_result.get("user"))
        aw_info.user_en = self.default(en_result.get("user"))

        aw_info.isp_en = self.default(en_result.get("isp"))
        aw_info.isp_cn = self.default(cn_result.get("isp"))
        aw_info.asn = self.default(en_result.get("asnumber"))
        aw_info.zipcode = self.default(cn_result.get("zipcode"))
        aw_info.timezone = self.default(cn_result.get("timezone"))
        aw_info.owner_en = self.default(en_result.get("owner"))
        aw_info.owner_cn = self.default(cn_result.get("owner"))
        aw_info.country_code = self.default(en_result.get("areacode"))

        aw_info.country_cn_name = self.default(cn_result.get("country"))
        aw_info.country_en_name = self.default(en_result.get("country"))

        aw_info.continent_cn_name = self.default(cn_result.get("continent"))
        aw_info.continent_en_name = self.default(en_result.get("continent"))

        aw_info.get_continent_code_from_name()
        aw_info.unify_city_info()
        aw_info.correct_politics()
        return aw_info

    def get_aiwen(self, ip):
        geoinfo = self._make_geoinfo()
        aiwen_info = self.get_aiweninfo_from_ip(ip)
        if aiwen_info is None:
            return None

        self.valid_localtion(geoinfo, aiwen_info)

        if self.country_list and aiwen_info.country_cn_name not in self.country_list:
            geoinfo["country"]["names"]["en"] = "Unknown"
            geoinfo["country"]["names"]["cn"] = "Unknown"
            geoinfo["country"]["geoname_id"] = None
            geoinfo["country"]["code"] = None

            geoinfo["subdivisions"]["names"]["en"] = "Unknown"
            geoinfo["subdivisions"]["names"]["cn"] = "Unknown"

            geoinfo["city"]["names"]["en"] = "Unknown"
            geoinfo["city"]["names"]["cn"] = "Unknown"

            geoinfo["continent"]["names"]["en"] = "Unknown"
            geoinfo["continent"]["names"]["cn"] = "Unknown"
            geoinfo["continent"]["code"] = None
        else:
            geoinfo["continent"]["names"]["en"] = aiwen_info.continent_en_name
            geoinfo["continent"]["names"]["cn"] = aiwen_info.continent_cn_name
            geoinfo["continent"]["code"] = aiwen_info.continent_code

            geoinfo["country"]["names"]["en"] = aiwen_info.country_en_name
            geoinfo["country"]["names"]["cn"] = aiwen_info.country_cn_name
            geoinfo["country"]["geoname_id"] = None
            geoinfo["country"]["code"] = aiwen_info.country_code

            geoinfo["subdivisions"]["names"]["en"] = aiwen_info.subd_en_name
            geoinfo["subdivisions"]["names"]["cn"] = aiwen_info.subd_cn_name

            geoinfo["city"]["names"]["en"] = aiwen_info.city_en_name
            geoinfo["city"]["names"]["cn"] = aiwen_info.city_cn_name

            if aiwen_info.subd_cn_name in self.country_list:
                geoinfo["subdivisions"]["names"]["en"] = "Unknown"
                geoinfo["subdivisions"]["names"]["cn"] = "Unknown"

        geoinfo["district"]["names"]["en"] = aiwen_info.district_en_name
        geoinfo["district"]["names"]["cn"] = aiwen_info.district_cn_name

        geoinfo["accuracy"]["en"] = aiwen_info.accuracy_en
        geoinfo["accuracy"]["cn"] = aiwen_info.accuracy_cn
        geoinfo["scene"]["en"] = aiwen_info.scene_en
        geoinfo["scene"]["cn"] = aiwen_info.scene_cn
        geoinfo["usertype"]["en"] = aiwen_info.usertype_en
        geoinfo["usertype"]["cn"] = aiwen_info.usertype_cn
        geoinfo["user"]["en"] = aiwen_info.user_en
        geoinfo["user"]["cn"] = aiwen_info.user_cn
        geoinfo['radius'] = aiwen_info.radius
        geoinfo['isp']["cn"] = aiwen_info.isp_cn
        geoinfo['isp']["en"] = aiwen_info.isp_en
        geoinfo["asn"] = aiwen_info.asn
        geoinfo["zipcode"] = aiwen_info.zipcode
        geoinfo["timezone"] = aiwen_info.timezone
        geoinfo["organization"]["en"] = aiwen_info.owner_en
        geoinfo["organization"]["cn"] = aiwen_info.owner_cn

        return geoinfo

    def valid_localtion(self, geoinfo, aiwen_info):
        try:
            geoinfo["location"]["lon"] = float(aiwen_info.lon)
            geoinfo["location"]["lat"] = float(aiwen_info.lat)
        except (ValueError, TypeError) as e:
            geoinfo.pop("location")

        try:
            geoinfo["location_bd"]["lon"] = float(aiwen_info.lonbd)
            geoinfo["location_bd"]["lat"] = float(aiwen_info.latbd)
        except (ValueError, TypeError) as e:
            geoinfo.pop("location_bd")


if __name__ == '__main__':
    ipip = GetAiwen()
    print(ipip.get_aiwen("2a01:53c0:ffe6::f"))
