#!/usr/bin/python3
# -*- encoding:utf-8 -*-

import socket
import numpy as np
import binascii
import codecs
import struct
import ctypes
import sys
import time
import scipy
from scipy import sparse
import matplotlib
import datetime
# matplotlib.use('Agg')
# from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy
import scipy.spatial.distance
# import scipy.stats.signaltonoise
from scipy.spatial.distance import pdist
from sklearn.metrics.pairwise import cosine_similarity
# import seaborn as sns
# import Fast5File

# import logging


CHIP = '43455c0'     #wifi chip (possible values 4339, 4358<nexus 6p>, 43455c0<raspberrypi>,4366c0)
BW = 20
NFFT = BW*3.2



def socket_csi():
    
    """
        parameter:
        -channel 6
        -BW 20
        -package len 274
        -[0 1 2 3 ] magic bytes 0x11111111              4
        -[4 5 6 7 8 9 ] source mac addr                 6
        -[10 11 ] sequence number                       2
        -[12 13 ] <core and spatial number>             2
        -[14 15 ]  chanspec    channel/BW                2
        -[16 17 ] chip version                          2
        -[18 274 ]  real data                          256

 
    """
    #1 0100  0000 0001  0001 1000  0001 0011

    #10100               11000       10011

    udp_socket = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) 
    udp_socket.bind(("", 5500))
    global count
    count = 0
    print('[===============START===============]')

    # plt interactive 
    plt.ion()
    # plt.rcParams['figure.figsize'] = (10, 10)
    # plt.rcParams['font.sans-serif'] = ['SimHei']
    # plt.rcParams['axes.unicode_mius'] = False
    # plt.rcParams['lines.linewidth'] = 1
    
    global compare_list
    compare_list = []

    global var_list_7
    var_list_7 = []

    global var_list_5
    var_list_5 = []

    global var_list_3 
    var_list_3 = []

    global var_list_2
    var_list_2 = []

    compare_value =np.arange(100)
    global fig 
    global ax
    fig ,ax = plt.subplots()
    while 1:
        data, addr  = udp_socket.recvfrom(1024)
        np_data = np.frombuffer(data,dtype=np.int16,offset=18)
        # print("np_data",np_data)
        print('-----------------')
        magic_bytes  = []
        source_mac = []
        sequence_number = []
        core_spatial_number = []
        chan_spec = []
        chip_version = []
        real_data = []
        if len(data) != 274:
            continue
        # magic_bytes = [x for x in data[:4]]
        # print("magic_bytes:", magic_bytes, [hex(x) for x in magic_bytes])
        # source_mac = [x for x in data[4:10]]
        # print("source_mac:",source_mac,[hex(x) for x in source_mac])
        # sequence_number = [x for x in data[10:12]]
        # print("sequence_number:",sequence_number, [hex(x) for x in sequence_number])
        # core_spatial_number = [x for x in data[12:14]]
        # print("core_spatial_number:",core_spatial_number)
        # chanspec = [x for x in data[14:16]]
        # print("chanspec:",chanspec)
        # chip_version = [x for x in data[16:18]]
        # print("chip_version",chip_version)
        # real_data = [x for x in data[18:]]
        # print("real_data:",real_data,len(real_data))
        
        count += 1 
        # if count >= 200:
        #     break
        
        treat_one_package(np_data,count)


        #control package number 
        
        
    udp_socket.close()
    plt.ioff()
    plt.show()

def treat_one_package(data,count):
    # data is a list
    # step
    # data是256个字节的16进制数转换成10进制的数
    # 1.将这256个数按照四个字节一组转化成int32的类型，总共有64维
    # print("开始计算")
    # print(data)
    csi_data = data
    # csi_data = np.array(data,dtype = np.int16)
    # treated_csi = np.array(len(data)/2)
    # treated_csi = np.zeros(shape=(0,128))
    # lists = []
    # # print(treated_csi)
    # # csi_data.byteswap(True)
    # for i in range(0,len(csi_data),2):
    #     # print(csi_data[i],csi_data[i+1])
    #     bytes_2_val = binascii.b2a_hex(csi_data[i:i+1])
    #     tt = little_2_big(bytes_2_val)
    #     # print(tt)
    #     lists.append(tt)
    #     # np.append(treated_csi, tt)
    # # print(csi_data)
    # print('xxxx')
    # print(treated_csi)


    # 计算出复数值
    treated_csi = csi_data
    # print(treated_csi)
    reshape_csi = np.reshape(treated_csi, (64,2))
    # print(reshape_csi)
    complex_lists = []
    for j in range(len(reshape_csi)):
        # print(reshape_csi[j][0],reshape_csi[j][1])
        complex_csi = complex(float(reshape_csi[j][0]),float(reshape_csi[j][1]))
        complex_lists.append(complex_csi)
    complex_csi_array = np.array(complex_lists)
    reshape_csi_array = np.reshape(complex_csi_array,(1,64))
    # print(complex_csi_array)
    # print("complex_csi_array")
    pre_plot(reshape_csi_array,count)



def pre_plot(csi,count):
    # print('-------------------')
    # print('pre_plot')

    # csi_freqs = np.fft.fftfreq(csi)
    csi_fft = np.fft.fftshift(csi)
    # print("csi fft")
    # print(csi_fft)


    # calculate the magnitude

    # mangnitude 代表形状分量(phase)每一部分的比重
    csi_magnitude = np.absolute(csi_fft)
    csi_magnitude = np.reshape(csi_magnitude,(64,))
    # print(csi_magnitude)

    # calculate phase 
    csi_angle = np.angle(csi_fft)
    # print(csi_angle)
    csi_phase = np.rad2deg(csi_angle)
    csi_phase = np.reshape(csi_phase,(64,))
    # print(csi_phase)
    x = np.arange(-32,32)
    x_var = np.arange(1000)
    # 第一个子图，幅度图
    plt.clf()
    plt.suptitle('Channel State Information By Nexnon')

    plt.subplot(2,1,1)
    plt.plot(x,csi_magnitude)
    # plt.title('Magnitude graph')
    plt.xlabel('subcarrier')
    plt.ylabel('magnitude')
    # plt.ylim((0,2000))
    plt.grid()


    # 画出第二个子图，相位图
    plt.subplot(2,1,2)
    plt.plot(x, csi_phase)
    # plt.title('Phase graph')
    plt.xlabel('subcarrier')
    plt.ylabel('phase')
    plt.grid()
    # plt.subplots_adjust(wspace =0, hspace = 0.6)


    # 画出第三个子图
    # plt.subplot(3,1,3)

    # csi_snr = signaltonoise(csi_fft)
    # plt.plot(x, csi_snr)
    # plt.xlabel('subcarrier')
    # plt.ylabel('SNR')
    # plt.grid()


    # calculate the similarity 
    # c1 = csi_angle
    # c2 = csi_angle
    # compare_list.append(c1)

    # print("count:",count)
    # if count >=2:
    #     c = cosine_similarity(compare_list[count-2],compare_list[count-1])
    #     print("calculate",c[0][0])
    #     save(str(c[0][0]),flag='similarity')
    # else:
    #     print(count,"不能比较")
    # print("len compare_list:",len(compare_list))
    

    # 求出一段的方差 然后置[]为空
    # if len(compare_list)%7 == 0:
    #     arr_var = np.var(compare_list[count-6:count-1])
    #     var_list_7.append(arr_var)
    #     print("方差7为:",str(arr_var))
    #     # save(str(arr_var),flag='var')
    # if len(compare_list)%5 == 0:
    #     arr_var = np.var(compare_list[count-6:count-1])
    #     var_list_5.append(arr_var)
    #     print("方差5为:",str(arr_var))

    # if len(compare_list)%3 == 0:
    #     arr_var = np.var(compare_list[count-6:count-1])
    #     var_list_3.append(arr_var)
    #     print("方差3为:",str(arr_var))

    # if len(compare_list)%2 == 0:
    #     arr_var = np.var(compare_list[count-6:count-1])
    #     var_list_2.append(arr_var)
    #     print("方差为:",str(arr_var))

        # count = 0


    # 画出方差的图
    # plt.subplot(3,2,3)
    # x_len = len(var_list_7)
    # x_list7 = np.arange(x_len) 
    # plt.plot(x_list7, var_list_7)
    # # plt.title('Phase graph')
    # plt.xlabel('times')
    # plt.ylabel('var7')
    # plt.grid()
   

    # plt.subplot(3,2,4)
    # x_len = len(var_list_5)
    # x_list5 = np.arange(x_len) 
    # plt.plot(x_list5, var_list_5)
    # # plt.title('Phase graph')
    # plt.xlabel('times')
    # plt.ylabel('var5')
    # plt.grid()


    # plt.subplot(3,2,5)
    # x_len = len(var_list_3)
    # x_list3 = np.arange(x_len) 
    # plt.plot(x_list3, var_list_3)
    # # plt.title('Phase graph')
    # plt.xlabel('times')
    # plt.ylabel('var3')
    # plt.grid()
    
    
    # plt.subplot(3,2,6)
    # x_len = len(var_list_2)
    # x_list = np.arange(x_len) 
    # plt.plot(x_list, var_list_2)
    # # plt.title('Phase graph')
    # plt.xlabel('times')
    # plt.ylabel('var')
    # plt.grid()   

    plt.pause(0.00001)



def little_2_big(hex_str):

    # print(hex_str)
    # print(type(hex_str))
    int_big = int(hex_str,16) # 16进制的大端转换为Int
    # print(int_big)
    int_little = int_big.to_bytes(2, byteorder="little",signed=True)    # int 大端转换为Int小端
    # print(int_little)
    hex_little = binascii.b2a_hex(int_little)    # int 小端的转换为16进制
    converted_int = int(hex_little,16)
    # print("hex_little",hex_little)
    # print("converted_int", converted_int)
    signed_int = ctypes.c_int16(converted_int).value
    # print("signed {} hex_little {} converted_int {}".format(signed_int,hex_little, converted_int))
    return signed_int

    # int16_convert = hex_little
    # print(int16_convert)

    # x = hex_str
    # y = chr((x >> 16) & 0xFF) + chr((x >> 8) & 0xFF) + chr(x & 0xFF)
    # print(y)



def save(data,flag):
    if flag == 'similarity':
        file_path = '/home/pi/similarity1.txt'
    elif flag == 'var':
        file_path = '/home/pi/var1.txt'
    else:
        pass    
    with open(file_path,'a+') as fw:
        fw.write(data + '++' + datetime.datetime.now().strftime("%b %d %Y %H:%M:%S") + '\n')



if __name__ == "__main__":
    socket_csi()






