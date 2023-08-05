# coding=utf-8
import requests
import re

from pydawn.string_utils import gen_md5

import matplotlib
from matplotlib.collections import PatchCollection
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import time
import os
import numpy as np
import sys
from peewee import *
import urllib


reload(sys)
sys.setdefaultencoding('utf-8')

location_cache = "location_cache.txt"
base_dir = os.path.dirname(__file__).replace("\\", "/")
font = FontProperties(fname="%s/fonts/simsun.ttc" % base_dir, size=14)

db = SqliteDatabase('locations.db')


def refine_address(address):
    address = address.encode("utf-8").lower()
    pattern = re.compile("\s+")
    return pattern.sub(" ", address).strip()


class BaseModel(Model):
    class Meta:
        database = db


class Address(BaseModel):
    address = CharField(unique=True)
    address_md5 = CharField(unique=True)
    longitude = FloatField()
    latitude = FloatField()


def insert_address(address, longitude, latitude):
    address = refine_address(address)
    md5 = gen_md5(address)
    try:
        address_object = Address.get(Address.address_md5 == md5)
        if address_object.longitude is None:
            address_object.longitude = float(longitude)
            address_object.latitude = float(latitude)
            address_object.save()
    except:
        address_object = Address.create(address=address,
                                        address_md5=md5,
                                        longitude=float(longitude),
                                        latitude=float(latitude))

        address_object.save()


def get_cached_coordinate(address):
    address = refine_address(address)
    md5 = gen_md5(address)
    try:
        address_object = Address.get(Address.address_md5 == md5)
        if address_object.longitude is not None:
            return address_object.longitude, address_object.latitude
    except:
        pass

    return None, None


def init_address_db():
    db.connect()
    db.create_tables([Address])


def get_coordinate(location):
    if len(location) > 84:
        print "location over size"
        return None, None
    url_format = "http://api.map.baidu.com/geocoder/v2/?output=json&ak=SjDhGSaC0GTQfhL7ezS9Qb0MoTWk49hO&address=%s"
    url = url_format % location
    response = requests.get(url, timeout=8)
    answer = response.json()
    try:
        x, y = answer['result']['location']['lng'], answer['result']['location']['lat']
        print "get coordinate for %s(%s,%s)" % (location, x, y)
        return x, y
    except:
        print 'query location %s fail, %s' % (location, answer)
        return None, None


def get_coordinate2(location):
    url_format = "http://restapi.amap.com/v3/geocode/geo?key=ea2b07318489822d536cf4d90c436522&address=%s"
    url = url_format % location
    response = requests.get(url)
    answer = response.json()
    print answer


def get_coordinate4(location):
    url = "https://maps.googleapis.com/maps/api/geocode/json?"
    params = {"address": location,
              "key":"AIzaSyAwJl7gHh3baTqIqoBAE0XNnCZD_My63LY"}
    url = url + urllib.urlencode(params)
    try:
        response = requests.get(url)
        answer = response.json()
        location = answer["results"][0]["geometry"]["location"]
        print "get:", location['lng'], location['lat']
        return location['lng'], location['lat']
    except:
        return None, None

def get_coordinates(location_list_file, host="g"):
    for line in open(location_list_file):
        address = refine_address(line)
        longitude, latitude = get_cached_coordinate(address)
        if longitude is None:
            if host == "g":
                longitude, latitude = get_coordinate4(address)
            else:
                longitude, latitude = get_coordinate(address)
            if longitude is not None:
                insert_address(address, longitude, latitude)


if __name__ == '__main__':
    init_address_db()
    #draw_cn_map("author_location_cn.txt")
    '''
    for line in open("location_cache_refine.txt"):
        address = line.split("|")[0]
        longitude = line.split("|")[1].split(" ")[0]
        latitude = line.split("|")[1].split(" ")[1]
        insert_address(address, longitude, latitude)
    '''

    #str = "van godewijckstraat 30  netherlands"
    #refine_cache()
    #get_coordinates("author_location_en.txt")
    # draw_world_map("author_location_en.txt")
    get_coordinate4("VAN GODEWIJCKSTRAAT 30, 3311 GZ DORDRECHT, NETHERLANDS")
