# coding=utf-8
import requests
import re

from geopy import Nominatim
from pydawn.string_utils import gen_md5

from pydawn.file_utils import open_file_in_utf8
import matplotlib
from matplotlib.collections import PatchCollection
from matplotlib.font_manager import FontProperties
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import time
import os
import numpy as np
import sys
from peewee import *
import urllib
from pydawn.sqlite_utils import sqlite_get_db, sqlite_excute

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


def get_coordinate3(location):
    geolocator = Nominatim()
    try:
        loc = geolocator.geocode(location, timeout=20)
        print "get_coordinates3: %s(%s,%s)" % (location, loc.longitude, loc.latitude)
        return loc.longitude, loc.latitude
    except:
        return None, None


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


def draw_cn_map(location_file):
    fig = plt.figure(figsize=(16, 8))
    m = Basemap(llcrnrlon=77, llcrnrlat=14, urcrnrlon=140, urcrnrlat=51, projection='lcc', lat_1=33, lat_2=45, lon_0=100)
    m.drawcoastlines()
    m.drawcountries(linewidth=1.5)

    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)

    ax = plt.gca()
    #ax.spines['top'].set_visible(False)
    #ax.spines['bottom'].set_visible(False)
    #ax.spines['left'].set_visible(False)
    #ax.spines['right'].set_visible(False)

    #plt.axis('off')

    base_dir = os.path.dirname(__file__).replace("\\", "/")
    m.readshapefile('%s/CHN_adm_shp/CHN_adm1' % base_dir, 'states', drawbounds=True)
    ax = plt.gca()
    for nshape, seg in enumerate(m.states):
        poly = Polygon(seg, facecolor='#96CDCD')
        ax.add_patch(poly)

    m.readshapefile('%s/TWN_adm_shp/TWN_adm0' % base_dir, 'taiwan', drawbounds=True)
    for nshape, seg in enumerate(m.taiwan):
        poly = Polygon(seg, facecolor='#96CDCD')
        ax.add_patch(poly)

    for line in open(location_file):
        location = re.split(",\s;", line)[0]
        location = location.replace(";", "").strip()

        longitude, latitude = get_cached_coordinate(location)
        if longitude is None:
            continue

        x, y = m(longitude, latitude)
        m.plot(x, y, marker='o', color='r', markersize=3, alpha=0.8, zorder=10)

    province = []
    for shapedict in m.states_info:
        statename = shapedict['NL_NAME_1']
        p = statename.split('|')
        if len(p) > 1:
            s = p[1]
        else:
            s = p[0]

        if s not in province:
            province.append(s)

    for shapedict in m.taiwan_info:
        s = shapedict['NAME_CHINE']
        if s not in province:
            province.append(s)

    province.append(u"黑龙江")
    font = FontProperties(fname="%s/fonts/simsun.ttc" % base_dir, size=14)
    for pro in province:
        print "pro", pro
        try:
            if pro == u"海南" or pro == u"河南":
                pro = pro + u"省"

            longitude, latitude = get_cached_coordinate(pro)
            if longitude is None:
                continue

            x, y = m(longitude, latitude)
            plt.text(x, y, pro, fontsize=8, color='#000000', zorder=100, fontproperties=font)
            print "add text %s" % pro
        except:
            pass

    start_x, start_y = m(127.500830295, 50.2506900907)
    end_x, end_y = m(98.4999883215, 25.2799781235)
    plt.plot([start_x, end_x], [start_y, end_y], color="g", linestyle='--', linewidth=3)
    fig.savefig("cn_map.jpg", format='jpg', dpi=300, pad_inches=0)
    plt.show()


def draw_label(x, y, width, height, ax, color, text):
    rect_pos = np.zeros(shape=(4, 2))
    rect_pos[0][0] = x
    rect_pos[0][1] = y

    rect_pos[1][0] = x
    rect_pos[1][1] = y - height

    rect_pos[2][0] = x + width
    rect_pos[2][1] = y - height

    rect_pos[3][0] = x + width
    rect_pos[3][1] = y

    patches = []
    polygon = Polygon(rect_pos, True)
    patches.append(polygon)
    p = PatchCollection(patches, cmap=matplotlib.cm.jet, alpha=0.4, facecolors=color, edgecolors="#000000")
    ax.add_collection(p)

    text_margin = 10000
    top_margin = 1000
    plt.text(x+width+text_margin, y-top_margin, text, fontsize=14, color='#000000', zorder=100, fontproperties=font, ha='left', va="top")


def draw_cities(city_list, save_path):

    coords = []
    for city in city_list:
        print repr(city)
        x, y = location_coord[city]
        coords.append((x, y))

    padding = 0.05
    llcrnrlon = min(coords,key=lambda x:x[0])[0] * (1-padding)
    urcrnrlon = max(coords, key=lambda x: x[0])[0] * (1+padding)
    llcrnrlat = min(coords, key=lambda x: x[1])[1] * (1-padding)
    urcrnrlat = max(coords, key=lambda x: x[1])[1] * (1+padding)

    mid_lon = (llcrnrlon+urcrnrlon) / 2
    mid_lat = (llcrnrlat+urcrnrlat) / 2

    show_label = True
    start = time.clock()

    plt.figure(figsize=(20, 20))
    m = Basemap(llcrnrlon=llcrnrlon, urcrnrlon=urcrnrlon, llcrnrlat=llcrnrlat, urcrnrlat=urcrnrlat, projection='lcc', lon_0=mid_lon, lat_0=mid_lat)

    m.readshapefile("CHN_adm_shp\\CHN_adm2", 'states', drawbounds=False)
    m.drawcoastlines(color="w", zorder=-1)

    ax = plt.gca()
    # ax.spines['top'].set_visible(False)
    # ax.spines['bottom'].set_visible(False)
    # ax.spines['left'].set_visible(False)
    # ax.spines['right'].set_visible(False)


    color1 = "#ffff00"
    color2 = "#def9de"
    color3 = "#bbfbba"
    color4 = "#9eeb1a"
    color5 = "#00FF00"

    for info, shp in zip(m.states_info, m.states):
        province = info['NAME_1']
        city = info['NAME_2']
        city_name = info["NL_NAME_2"].split("|")[0].encode("utf-8")
        if city_name in city_list:
            color = 'g'
            poly = Polygon(shp, facecolor=color, edgecolor='#000000', lw=1)
            ax.add_patch(poly)

            if show_label:
                x, y = location_coord[city_name]
                x, y = m(x, y)
                # print city_name, x, y
                city_name = city_name.replace(u"襄樊", u"襄阳")
                plt.text(x, y, city_name, fontsize=10, color='#000000', zorder=100, fontproperties=font, ha='center')

    # draw arrow
    '''
    x, y = location_coord["arrow"]
    x, y = m(x, y)
    plt.text(x, y, "N", fontsize=14, color='#000000', zorder=100, fontproperties=font, ha='center')

    x_offset = 25000
    y_offset = 70000
    height = 50000

    left_angle = np.zeros(shape=(3, 2))
    left_angle[0][0] = x
    left_angle[0][1] = y

    left_angle[1][0] = x - x_offset
    left_angle[1][1] = y - y_offset

    left_angle[2][0] = x
    left_angle[2][1] = y - height

    left_patches = []
    left_polygon = Polygon(left_angle, True)
    left_patches.append(left_polygon)

    left_p = PatchCollection(left_patches, cmap=matplotlib.cm.jet, alpha=0.4, facecolors="#000000",
                             edgecolors="#000000")
    ax.add_collection(left_p)

    right_angle = np.zeros(shape=(3, 2))
    right_angle[0][0] = x
    right_angle[0][1] = y

    right_angle[1][0] = x + x_offset
    right_angle[1][1] = y - y_offset

    right_angle[2][0] = x
    right_angle[2][1] = y - height

    right_patches = []
    right_polygon = Polygon(right_angle, True, color="w")
    right_patches.append(right_polygon)

    right_p = PatchCollection(right_patches, cmap=matplotlib.cm.jet, alpha=0.4, facecolors="w", edgecolors="#000000")
    ax.add_collection(right_p)

    # draw label
    width = 50000
    height = 20000
    location = location_coord["label"]
    x = float(location.split(",")[0])
    y = float(location.split(",")[1])
    x, y = m(x, y)

    margin = 10000
    draw_label(x, y, width, height, ax, color1, "<0.2")
    draw_label(x, y - (height + margin), width, height, ax, color2, "0.2～0.4")
    draw_label(x, y - (height + margin) * 2, width, height, ax, color3, "0.4～0.6")
    draw_label(x, y - (height + margin) * 3, width, height, ax, color4, "0.6～0.8")
    draw_label(x, y - (height + margin) * 4, width, height, ax, color5, ">0.8")
    '''

    end = time.clock()
    print(end - start)
    plt.savefig(save_path)
    plt.show()


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


def draw_world_map(location_list_file):
    fig = plt.figure(figsize=(20, 10))
    world_map = Basemap(projection='cyl')
    world_map.drawmapboundary()
    world_map.drawcountries(linewidth=0.25)
    world_map.fillcontinents(color='lightgray', zorder=1)

    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)

    # draw country name first
    country_list = "country.csv"
    get_coordinates(country_list)

    for line in open(country_list):
        country = line.strip()

        longitude, latitude = get_cached_coordinate(country)
        if longitude is None:
            continue

        x, y = world_map(longitude, latitude)
        plt.text(x, y, country, fontsize=6, color='#8B8378', zorder=100)

    for line in open(location_list_file):
        address = refine_address(line)
        longitude, latitude = get_cached_coordinate(address)
        if longitude is None:
            continue
        x, y = world_map(longitude, latitude)
        world_map.plot(x, y, marker='o', markersize=7, color='Red', alpha=0.3, zorder=10)

    fig.savefig("world_map.jpg", format='jpg', dpi=300, pad_inches=0)
    plt.show()


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
    get_coordinates4("VAN GODEWIJCKSTRAAT 30, 3311 GZ DORDRECHT, NETHERLANDS")
