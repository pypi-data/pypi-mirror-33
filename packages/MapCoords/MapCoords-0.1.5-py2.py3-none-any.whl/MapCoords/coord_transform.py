# ！/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/6/21 11:46
# @Author   : Run (18817363043@163.com)
# @File     : coord_transform.py
# @Software : PyCharm

"""
【坐标转换】
常用的几种坐标系间经纬度的相互转换
加密：wgs84 -> gcj02, gcj02 -> bd09
解密：gcj02 -> wgs84, bd09 -> gcj02
由于加密过程中的一些函数不存在反函数，所以解密的过程不存在解析解，只能用数值逼近的方式估计数值解，当迭代的次数趋于无穷时，数值解收敛到真实值
wgs84 -> bd09 和 bd09 -> wgs84 这两种转换分两步进行

【问题】
1. python中浮点数的存储，机器精度，python内置浮点数和numpy中的区别

【更新】
1. 问题：
        当传入坐标小数点后超过6位后，解密时难以收敛至1e-7的精度。
   解决方案：
        传入参数先从小数点6位后做截断，并设置最大迭代次数为100
2. 使得array系列函数的传参及返回结果更为灵活、智能

【笔记】
1. round()和np.round()对小数做截断后，由于浮点数存储的原因，并不保证仅剩截断的位数
2. 使用decorator会影响到函数的文档，必须要运行一次函数，才可以通过`?`或者help查看函数文档
"""

import math
import numpy as np


COORD_TRANSFORM_a = 6378245  # 半长轴
COORD_TRANSFORM_ee = 0.00669342162296594323  # 椭球偏心率的平方
COORD_TRANSFORM_delta = 1e-7  # 解密时的精度
COORD_TRANSFORM_max_loop = 100  # 解密时的最大迭代次数


def out_of_China(lgt, lat):
    """
    粗略地判断该坐标点是否在国内（只有国内的坐标需要偏移）
    注意：这里只是以BoundingBox进行了粗略的判断，并不是严格地以我国边境线
    这样的思路对国内坐标转换是确定无误的，但是对于BoundingBox和边境线相夹区域是不确定其正确性的

    :param args: WGS84坐标系的经纬度（注意：经度在前，纬度在后）
    :return: 不在国内返回True，在国内返回False
    """

    return not ((73.66 < lgt < 135.05) and (3.86 < lat < 53.55))


def rectify_input_point(func):
    """
    整理输入的参数的格式
    point系列函数

    :param func:
    :return:
    """

    def dec(*args):
        dec.__doc__ = func.__doc__

        if len(args) == 1:
            if len(args[0]) == 2:
                lgt, lat = args[0]
            else:
                raise Exception("输入有误：{0}".format(args))
        elif len(args) == 2:
            lgt, lat = args
        else:
            raise Exception("输入有误：{0}".format(args))
        return func(lgt, lat)

    return dec


def rectify_input_array(func):
    """
    整理输入的参数的格式
    array系列函数
    :param func:
    :return:
    """

    def dec(*args):
        dec.__doc__ = func.__doc__

        if len(args) == 1:
            arr = np.array(args[0])
            if len(arr.shape) == 2 and arr.shape[1] == 2:
                lgts, lats = zip(*args[0])
            else:
                raise Exception("输入有误：{0}".format(args))
        elif len(args) == 2:
            lgts, lats = args
        else:
            raise Exception("输入有误：{0}".format(args))

        lgt_arr, lat_arr = func(lgts, lats)

        if len(args) == 1:
            return [[lgt_arr[i], lat_arr[i]] for i in range(len(lgt_arr))]
        else:
            return lgt_arr, lat_arr

    return dec


@rectify_input_point
def wgs84_to_gcj02_point(lgt, lat):
    """
    单点的坐标转换
    WGS84(原始的GPS经纬度坐标)  ->  GCJ02(火星坐标系)
    :param args: WGS84坐标系的经纬度（注意：保证经度在前，纬度在后，任意数据格式均可）
    :return:
        [lgt, lat] （即 [GCJ02坐标系的经度, GCJ02坐标系的纬度]）
        数据类型 [float, float]
    """

    a = COORD_TRANSFORM_a  # 半长轴
    ee = COORD_TRANSFORM_ee  # 椭球偏心率的平方

    def _transform_lgt(lgt, lat):
        ret = 300.0 + lgt + 2.0 * lat + 0.1 * lgt * lgt + 0.1 * lgt * lat + 0.1 * math.sqrt(abs(lgt))
        ret += (20.0 * math.sin(6.0 * lgt * math.pi) + 20.0 * np.sin(2.0 * lgt * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lgt * math.pi) + 40.0 * math.sin(lgt / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lgt / 12.0 * math.pi) + 300.0 * math.sin(lgt / 30.0 * math.pi)) * 2.0 / 3.0
        return ret

    def _transform_lat(lgt, lat):
        ret = -100 + 2 * lgt + 3 * lat + 0.2 * lat * lat + 0.1 * lgt * lat + 0.2 * math.sqrt(abs(lgt))
        ret += (20.0 * math.sin(6.0 * lgt * math.pi) + 20.0 * math.sin(2.0 * lgt * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * math.pi) + 40.0 * math.sin(lat / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * math.pi) + 320 * math.sin(lat * math.pi / 30.0)) * 2.0 / 3.0
        return ret

    if out_of_China(lgt, lat): return [lgt, lat]

    dLgt = _transform_lgt(lgt - 105, lat - 35)
    dLat = _transform_lat(lgt - 105, lat - 35)
    radLat = lat * math.pi / 180
    magic = math.sin(radLat)
    magic = 1 - ee * magic * magic
    sqrtMagic = math.sqrt(magic)
    dLgt = (dLgt * 180) / (a / sqrtMagic * math.cos(radLat) * math.pi)
    dLat = (dLat * 180) / ((a * (1 - ee)) / (magic * sqrtMagic) * math.pi)
    lgt, lat = round(lgt + dLgt, 6), round(lat + dLat, 6)

    return [lgt, lat]


@rectify_input_point
def gcj02_to_bd09_point(lgt, lat):
    """
    单点的坐标转换
    GCJ02(火星坐标系)  ->  BD-09(百度坐标系)
    :param args: GCJ02坐标系的经纬度（注意：保证经度在前，纬度在后，任意数据格式均可）
    :return:
        [lgt, lat] （即 [BD09坐标系的经度, BD09坐标系的纬度]）
        数据类型 [float, float]
    """

    x_pi = math.pi * 3000 / 180
    z = math.sqrt(lgt * lgt + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lgt) + 0.000003 * math.cos(lgt * x_pi)
    lgt = round(z * math.cos(theta) + 0.0065, 6)
    lat = round(z * math.sin(theta) + 0.006, 6)

    return [lgt, lat]


@rectify_input_point
def wgs84_to_bd09_point(lgt, lat):
    """
    单点的坐标转换
    WGS84(原始的GPS经纬度坐标)  ->  BD-09(百度坐标系)
    :param args: WGS84坐标系的经纬度（注意：保证经度在前，纬度在后，任意数据格式均可）
    :return:
        [lgt, lat] （即 [BD-09坐标系的经度, BD-09坐标系的纬度]）
        数据类型 [float, float]

    :param lgt:
    :param lat:
    :return:
    """
    return gcj02_to_bd09_point(wgs84_to_gcj02_point(lgt, lat))


@rectify_input_point
def gcj02_to_wgs84_point(gcj_lgt, gcj_lat):
    """
    单点的坐标转换
    GCJ02(火星坐标系)  ->  WGS84(原始的GPS经纬度坐标)
    :param args: GCJ02坐标系的经纬度（注意：保证经度在前，纬度在后，任意数据格式均可）
    :return:
        [lgt, lat] （即 [WGS84坐标系的经度, WGS84坐标系的纬度]）
        数据类型 [float, float]
    """

    delta = COORD_TRANSFORM_delta
    max_loop = COORD_TRANSFORM_max_loop

    gcj_lgt, gcj_lat = round(gcj_lgt, 6), round(gcj_lat, 6)

    lgt, lat = gcj_lgt, gcj_lat
    mglgt, mglat = wgs84_to_gcj02_point(lgt, lat)
    delta1, delta2 = gcj_lgt - mglgt, gcj_lat - mglat
    loop = 0
    while (abs(delta1) > delta or abs(delta2) > delta) and loop < max_loop:
        lgt += delta1
        lat += delta2
        mglgt, mglat = wgs84_to_gcj02_point(lgt, lat)
        delta1, delta2 = gcj_lgt - mglgt, gcj_lat - mglat
        loop += 1

    return [round(lgt, 6), round(lat, 6)]


@rectify_input_point
def bd09_to_gcj02_point(bd_lgt, bd_lat):
    """
    单点的坐标转换
    BD-09(百度坐标系)  ->  GCJ02(火星坐标系)
    :param args: BD-09坐标系的经纬度（注意：保证经度在前，纬度在后，任意数据格式均可）
    :return:
        [lgt, lat] （即 [gcj02坐标系的经度, gcj02坐标系的纬度]）
        数据类型 [float, float]
    """

    delta = COORD_TRANSFORM_delta
    max_loop = COORD_TRANSFORM_max_loop

    bd_lgt, bd_lat = round(bd_lgt, 6), round(bd_lat, 6)

    lgt, lat = bd_lgt, bd_lat
    mglgt, mglat = gcj02_to_bd09_point(lgt, lat)
    delta1, delta2 = bd_lgt - mglgt, bd_lat - mglat
    loop = 0
    while (abs(delta1) > delta or abs(delta2) > delta) and loop < max_loop:
        lgt += delta1
        lat += delta2
        mglgt, mglat = gcj02_to_bd09_point(lgt, lat)
        delta1, delta2 = bd_lgt - mglgt, bd_lat - mglat
        loop += 1

    return [round(lgt, 6), round(lat, 6)]


@rectify_input_point
def bd09_to_wgs84_point(lgt, lat):
    """
    单点的坐标转换
    BD-09(百度坐标系)  ->  WGS84(原始的GPS经纬度坐标)
    :param args: BD-09坐标系的经纬度（注意：保证经度在前，纬度在后，任意数据格式均可）
    :return:
        [lgt, lat] （即 [WGS84坐标系的经度, WGS84坐标系的纬度]）
        数据类型 [float, float]
    :param lgt:
    :param lat:
    :return:
    """
    return gcj02_to_wgs84_point(bd09_to_gcj02_point(lgt, lat))


@rectify_input_array
def wgs84_to_gcj02_array(lgt_arr, lat_arr):
    """
    一列点的坐标转换
    WGS84(原始的GPS经纬度坐标)  ->  GCJ02(火星坐标系)
    注意：
        1. 由于业务场景主要是在国内，所以批量进行坐标转换时不再进行国内的判断
    :param args: 如果传入参数为lgt_arr, lat_arr，则返回也是该形式；
                 如果传入参数形式类似[[lgt1, lat1], [lgt2, lat2], ...]，则返回也是该形式
    :return:
    """

    a = COORD_TRANSFORM_a  # 卫星椭球坐标投影到平面地图坐标系的投影因子
    ee = COORD_TRANSFORM_ee  # 椭球的偏心率

    def _transform_lgt_arr(lgt_arr, lat_arr):
        ret = 300 + lgt_arr + 2 * lat_arr + 0.1 * lgt_arr * lgt_arr + 0.1 * lgt_arr * lat_arr + 0.1 * np.sqrt(
            abs(lgt_arr))
        ret += (20 * np.sin(6 * lgt_arr * np.pi) + 20 * np.sin(2 * lgt_arr * np.pi)) * 2 / 3
        ret += (20 * np.sin(lgt_arr * np.pi) + 40 * np.sin(lgt_arr / 3 * np.pi)) * 2 / 3
        ret += (150 * np.sin(lgt_arr / 12 * np.pi) + 300 * np.sin(lgt_arr / 30 * np.pi)) * 2 / 3
        return ret

    def _transform_lat_arr(lgt_arr, lat_arr):
        ret = -100 + 2 * lgt_arr + 3 * lat_arr + 0.2 * lat_arr * lat_arr + 0.1 * lgt_arr * lat_arr + 0.2 * np.sqrt(
            abs(lgt_arr))
        ret += (20 * np.sin(6 * lgt_arr * np.pi) + 20 * np.sin(2.0 * lgt_arr * np.pi)) * 2 / 3
        ret += (20 * np.sin(lat_arr * np.pi) + 40 * np.sin(lat_arr / 3 * np.pi)) * 2 / 3
        ret += (160 * np.sin(lat_arr / 12 * np.pi) + 320 * np.sin(lat_arr * np.pi / 30)) * 2 / 3
        return ret

    lgt_arr, lat_arr = np.array(lgt_arr), np.array(lat_arr)
    dLgt_arr = _transform_lgt_arr(lgt_arr - 105, lat_arr - 35)
    dLat_arr = _transform_lat_arr(lgt_arr - 105, lat_arr - 35)
    radLat_arr = lat_arr * np.pi / 180
    magic = np.sin(radLat_arr)
    magic = 1 - ee * magic * magic
    sqrtMagic = np.sqrt(magic)
    dLgt_arr = (dLgt_arr * 180) / (a / sqrtMagic * np.cos(radLat_arr) * np.pi)
    dLat_arr = (dLat_arr * 180) / ((a * (1 - ee)) / (magic * sqrtMagic) * np.pi)
    lgt_arr = np.round(lgt_arr + dLgt_arr, 6)
    lat_arr = np.round(lat_arr + dLat_arr, 6)

    return lgt_arr, lat_arr


@rectify_input_array
def gcj02_to_bd09_array(lgt_arr, lat_arr):
    """
    一列点的坐标转换
    GCJ02(火星坐标系)  ->  BD-09(百度坐标系)
    注意：
        1. 由于业务场景主要是在国内，所以批量进行坐标转换时不再进行国内的判断
    :param args: 如果传入参数为lgt_arr, lat_arr，则返回也是该形式；
                 如果传入参数形式类似[[lgt1, lat1], [lgt2, lat2], ...]，则返回也是该形式
    :return:
    """

    lgt_arr, lat_arr = np.array(lgt_arr), np.array(lat_arr)
    x_pi = np.pi * 3000 / 180
    z = np.sqrt(lgt_arr ** 2 + lat_arr ** 2) + 0.00002 * np.sin(lat_arr * x_pi)
    theta = np.arctan2(lat_arr, lgt_arr) + 0.000003 * np.cos(lgt_arr * x_pi)
    lgt_arr = np.round(z * np.cos(theta) + 0.0065, 6)
    lat_arr = np.round(z * np.sin(theta) + 0.006, 6)

    return lgt_arr, lat_arr


@rectify_input_array
def wgs84_to_bd09_array(lgt_arr, lat_arr):
    """
    一列点的坐标转换
    WGS84(原始的GPS经纬度坐标)  ->  BD-09(百度坐标系)
    注意：
        1. 由于业务场景主要是在国内，所以批量进行坐标转换时不再进行国内的判断
    :param args: 如果传入参数为lgt_arr, lat_arr，则返回也是该形式；
                 如果传入参数形式类似[[lgt1, lat1], [lgt2, lat2], ...]，则返回也是该形式
    :return:
    """
    return gcj02_to_bd09_array(*wgs84_to_gcj02_array(lgt_arr, lat_arr))


@rectify_input_array
def gcj02_to_wgs84_array(lgt_arr, lat_arr):
    """
    一列点的坐标转换
    GCJ02(火星坐标系)  ->  WGS84(原始的GPS经纬度坐标)
    注意：
        1. 由于业务场景主要是在国内，所以批量进行坐标转换时不再进行国内的判断
    :param args: 如果传入参数为lgt_arr, lat_arr，则返回也是该形式；
                 如果传入参数形式类似[[lgt1, lat1], [lgt2, lat2], ...]，则返回也是该形式
    :return:
    """

    delta = COORD_TRANSFORM_delta
    max_loop = COORD_TRANSFORM_max_loop

    lgt_arr, lat_arr = np.round(np.array(lgt_arr), 6), np.round(np.array(lat_arr), 6)
    gcj_lgt_arr, gcj_lat_arr = lgt_arr.copy(), lat_arr.copy()
    mglgt_arr, mglat_arr = wgs84_to_gcj02_array(lgt_arr, lat_arr)
    delta1_arr, delta2_arr = gcj_lgt_arr - mglgt_arr, gcj_lat_arr - mglat_arr
    loop = 0
    while ((abs(delta1_arr) > delta).any() or (abs(delta2_arr) > delta).any()) and loop < max_loop:
        lgt_arr += delta1_arr
        lat_arr += delta2_arr
        mglgt_arr, mglat_arr = wgs84_to_gcj02_array(lgt_arr, lat_arr)
        delta1_arr, delta2_arr = gcj_lgt_arr - mglgt_arr, gcj_lat_arr - mglat_arr
        loop += 1

    return np.round(lgt_arr, 6), np.round(lat_arr, 6)


@rectify_input_array
def bd09_to_gcj02_array(lgt_arr, lat_arr):
    """
    一列点的坐标转换
    BD-09(百度坐标系)  ->  GCJ02(火星坐标系)
    注意：
        1. 由于业务场景主要是在国内，所以批量进行坐标转换时不再进行国内的判断
    :param args: 如果传入参数为lgt_arr, lat_arr，则返回也是该形式；
                 如果传入参数形式类似[[lgt1, lat1], [lgt2, lat2], ...]，则返回也是该形式
    :return:
    """

    delta = COORD_TRANSFORM_delta
    max_loop = COORD_TRANSFORM_max_loop

    lgt_arr, lat_arr = np.round(np.array(lgt_arr), 6), np.round(np.array(lat_arr), 6)
    bd_lgt_arr, bd_lat_arr = lgt_arr.copy(), lat_arr.copy()
    mglgt_arr, mglat_arr = gcj02_to_bd09_array(lgt_arr, lat_arr)
    delta1_arr, delta2_arr = bd_lgt_arr - mglgt_arr, bd_lat_arr - mglat_arr
    loop = 0
    while ((abs(delta1_arr) > delta).any() or (abs(delta2_arr) > delta).any()) and loop < max_loop:
        lgt_arr += delta1_arr
        lat_arr += delta2_arr
        mglgt_arr, mglat_arr = gcj02_to_bd09_array(lgt_arr, lat_arr)
        delta1_arr, delta2_arr = bd_lgt_arr - mglgt_arr, bd_lat_arr - mglat_arr
        loop += 1

    return np.round(lgt_arr, 6), np.round(lat_arr, 6)


@rectify_input_array
def bd09_to_wgs84_array(lgt_arr, lat_arr):
    """
    一列点的坐标转换
    BD-09(百度坐标系)  ->  WGS84(原始的GPS经纬度坐标)
    注意：
        1. 由于业务场景主要是在国内，所以批量进行坐标转换时不再进行国内的判断
    :param args: 如果传入参数为lgt_arr, lat_arr，则返回也是该形式；
                 如果传入参数形式类似[[lgt1, lat1], [lgt2, lat2], ...]，则返回也是该形式
    :return:
    """
    return gcj02_to_wgs84_array(*bd09_to_gcj02_array(lgt_arr, lat_arr))


if __name__ == '__main__':
    # 测试wgs84_to_gcj02_point，对比高德api的结果：http://lbs.amap.com/api/webservice/guide/api/convert
    print(wgs84_to_gcj02_point(116.481499, 39.990475))  # [116.487586, 39.991754]
    print(wgs84_to_gcj02_point([116.481499, 39.990475]))  # [116.487586, 39.991754]
    print(wgs84_to_gcj02_point((116.481499, 39.990475)))  # [116.487586, 39.991754]
    print(wgs84_to_gcj02_point(np.array([116.481499, 39.990475])))  # [116.487586, 39.991754]
    print(wgs84_to_gcj02_point(140, 60))  # [140, 60]

    # 测试gcj02_to_bd09_point
    print()
    print(gcj02_to_bd09_point(116.487586, 39.991754))  # [116.49412, 39.997716]
    print(gcj02_to_bd09_point([116.487586, 39.991754]))  # [116.49412, 39.997716]
    print(gcj02_to_bd09_point((116.487586, 39.991754)))  # [116.49412, 39.997716]
    print(gcj02_to_bd09_point(np.array([116.487586, 39.991754])))  # [116.49412, 39.997716]

    # 测试wgs84_to_bd09_point
    print()
    print(wgs84_to_bd09_point(116.481499, 39.990475))  # [116.49412, 39.997716]
    print(wgs84_to_bd09_point([116.481499, 39.990475]))  # [116.49412, 39.997716]
    print(wgs84_to_bd09_point((116.481499, 39.990475)))  # [116.49412, 39.997716]
    print(wgs84_to_bd09_point(np.array([116.481499, 39.990475])))  # [116.49412, 39.997716]

    # 测试gcj02_to_wgs84_point
    print()
    print(gcj02_to_wgs84_point(116.487586, 39.991754))  # [116.481499, 39.990475]
    print(gcj02_to_wgs84_point([116.487586, 39.991754]))  # [116.481499, 39.990475]
    print(gcj02_to_wgs84_point((116.487586, 39.991754)))  # [116.481499, 39.990475]
    print(gcj02_to_wgs84_point(np.array([116.487586, 39.991754])))  # [116.481499, 39.990475]

    # 测试bd09_to_gcj02_point
    print()
    print(bd09_to_gcj02_point(116.49412, 39.997716))  # [116.487586, 39.991754]
    print(bd09_to_gcj02_point([116.49412, 39.997716]))  # [116.487586, 39.991754]
    print(bd09_to_gcj02_point((116.49412, 39.997716)))  # [116.487586, 39.991754]
    print(bd09_to_gcj02_point(np.array([116.49412, 39.997716])))  # [116.487586, 39.991754]

    # 测试bd09_to_wgs84_point
    print()
    print(bd09_to_wgs84_point(116.49412, 39.997716))  # [116.481499, 39.990475]
    print(bd09_to_wgs84_point([116.49412, 39.997716]))  # [116.481499, 39.990475]
    print(bd09_to_wgs84_point((116.49412, 39.997716)))  # [116.481499, 39.990475]
    print(bd09_to_wgs84_point(np.array([116.49412, 39.997716])))  # [116.481499, 39.990475]

    # 测试wgs84_to_gcj02_array
    print()
    print(wgs84_to_gcj02_array(np.array([116.481499, 116.481499, 116.481499]),
                               np.array([39.990475, 39.990475, 39.990475])))
    print(wgs84_to_gcj02_array([116.481499, 116.481499, 116.481499],
                               [39.990475, 39.990475, 39.990475]))
    print(wgs84_to_gcj02_array([[116.481499, 39.990475], [116.481499, 39.990475], [116.481499, 39.990475]]))

    # 测试gcj02_to_bd09_array
    print()
    print(gcj02_to_bd09_array(np.array([116.487586, 116.487586, 116.487586]),
                              np.array([39.991754, 39.991754, 39.991754])))
    print(gcj02_to_bd09_array([116.487586, 116.487586, 116.487586],
                              [39.991754, 39.991754, 39.991754]))
    print(gcj02_to_bd09_array([[116.487586, 39.991754], [116.487586, 39.991754], [116.487586, 39.991754]]))

    # 测试wgs84_to_bd09_array
    print()
    print(wgs84_to_bd09_array(np.array([116.481499, 116.481499, 116.481499]),
                              np.array([39.990475, 39.990475, 39.990475])))
    print(wgs84_to_bd09_array([116.481499, 116.481499, 116.481499],
                              [39.990475, 39.990475, 39.990475]))
    print(wgs84_to_bd09_array([[116.481499, 39.990475], [116.481499, 39.990475], [116.481499, 39.990475]]))

    # 测试gcj02_to_wgs84_array
    print()
    print(gcj02_to_wgs84_array(np.array([116.487586, 116.487586, 116.487586]),
                               np.array([39.991754, 39.991754, 39.991754])))
    print(gcj02_to_wgs84_array([116.487586, 116.487586, 116.487586],
                               [39.991754, 39.991754, 39.991754]))
    print(gcj02_to_wgs84_array([[116.487586, 39.991754], [116.487586, 39.991754], [116.487586, 39.991754]]))

    # 测试bd09_to_gcj02_array
    print()
    print(bd09_to_gcj02_array(np.array([116.49412, 116.49412, 116.49412]),
                              np.array([39.997716, 39.997716, 39.997716])))
    print(bd09_to_gcj02_array([116.49412, 116.49412, 116.49412],
                              [39.997716, 39.997716, 39.997716]))
    print(bd09_to_gcj02_array([[116.49412, 39.997716], [116.49412, 39.997716], [116.49412, 39.997716]]))

    # 测试bd09_to_wgs84_array
    print()
    print(bd09_to_wgs84_array(np.array([116.49412, 116.49412, 116.49412]),
                              np.array([39.997716, 39.997716, 39.997716])))
    print(bd09_to_wgs84_array([116.49412, 116.49412, 116.49412],
                              [39.997716, 39.997716, 39.997716]))
    print(bd09_to_wgs84_array([[116.49412, 39.997716], [116.49412, 39.997716], [116.49412, 39.997716]]))

