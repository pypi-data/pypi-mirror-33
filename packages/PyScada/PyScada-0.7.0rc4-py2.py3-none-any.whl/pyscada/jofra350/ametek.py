# -*- coding: utf-8 -*-
"""
Lib to communicate with a Ametek RTC Temperture Calibrator

15-Mrz-2017
Martin Schröder

History:

22-Feb-2017  MS created Class

"""
from __future__ import unicode_literals

import socket
from signal import signal, SIGPIPE, SIG_DFL
import xml.etree.ElementTree
import time
import logging

logger = logging.getLogger(__name__)


signal(SIGPIPE, SIG_DFL)


def parse_live_sensors_response(node):
    """
    parse the data from a input source of the calibrator
    """
    out = dict(Node=node.tag, InputType=None, InputValue=None, TemperatureValue=None, StabilityTolerance=None,
               StabilityRequiredSeconds=None, StabilitySecondsLeft=None, SetFollows=None)

    inp = node.find('Input')
    if inp is None:
        return out
    if 'InputType' in inp.attrib:
        out['InputType'] = inp.attrib['InputType']
    # InputValue
    input_value = inp.find('InputValue')
    if input_value is not None:
        if input_value.attrib['val'] != 'NaN':
            out['InputValue'] = float(input_value.attrib['val'])

    # TemperatureValue
    temp_value = inp.find('TemperatureValue')
    if temp_value is not None:
        if temp_value.attrib['val'] != 'NaN':
            out['TemperatureValue'] = float(temp_value.attrib['val'])
    # Stability
    stab = node.find('Stability')
    if stab is None:
        return out
    # StabilityTolerance
    tolerance_value = stab.find('StabilityTolerance')
    if tolerance_value is not None:
        if tolerance_value.attrib['val'] != 'NaN':
            out['StabilityTolerance'] = float(tolerance_value.attrib['val'])
    # StabilityRequiredSeconds
    req_seconds_value = stab.find('RequiredSeconds')
    if req_seconds_value is not None:
        out['StabilityRequiredSeconds'] = float(req_seconds_value.text)
    # StabilitySecondsLeft
    seconds_value = stab.find('Seconds')
    if seconds_value is not None:
        if seconds_value.attrib['val'] != 'NaN':
            out['StabilitySecondsLeft'] = float(seconds_value.attrib['val'])
    # SetFollows
    set_follows = node.find('SetFollows')
    if set_follows is not None:
        if set_follows.text.lower() == 'false':
            out['SetFollows'] = False
        elif set_follows.text.lower() == 'true':
            out['SetFollows'] = True

    return out


def parse_calibrator_device_response(node):
    """
    parse the calibrator device info telegram
    """
    out = {'Serial': None,
           'ModelId': None,
           'EnableReferenceInputBoardFailed': None,
           'EnableSensorInputBoardFailed': None,
           'IsReferenceInputBoardCalibrated': None,
           'IsSensorInputBoardCalibrated': None}

    for key in out.keys():
        node_value = node.find(key)
        if node_value is not None:
            out[key] = node_value.text

    out['Node'] = node.tag
    return out


def parse_calibration_info_response(node):
    """
    parse the data from a input source of the calibrator
    """
    return {'Node': node.tag, 'Date': node.text}


class Jofra350:
    def __init__(self, tcp_ip='127.0.0.1', tcp_port=17001, timeout=2):
        """

        """
        self.tcp_ip = tcp_ip
        self.tcp_port = tcp_port
        self.sock = None
        self.telegram_raw = None
        self.telegram_header = None
        self.telegram_xml = None
        self.timeout = timeout

    def connect(self):
        """
        Connect to the Device
        """
        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            try:
                self.sock.connect((self.tcp_ip, self.tcp_port))
            except:
                self.sock.close()
                return False
            return True
        return False

    def disconnect(self):
        """
        close connection to the device
        """
        if self.sock is not None:
            self.sock.close()
            self.sock = None
            return True
        return False

    def get_sensor_data(self, seq=1):
        """
        query the live sensor data


        """
        return self.get_request(request_type='SensorManager.LiveSensors', seq=seq)

    def get_device_info(self, seq=1):
        """
        query the device info
        """
        return self.get_request(request_type='CalibratorManager.CalibratorDevice', seq=seq)

    def get_calibration_info(self, seq=1):
        """
        query the calibration date
        """
        return self.get_request(request_type='CalibratorManager.CalibrationDate', seq=seq)

    def get_request(self, request_type, seq=1, retries=3):
        """
        build a get request ,query date and return the parsed response
        """
        request_str = self.request(request_type=request_type, telegram_type='get-request', seq=seq)
        result = False
        retry = 0
        while retry < retries and result is False:
            # open a connection to the Server
            if self.sock is None:
                if not self.connect():
                    return False

            # send the telegram
            try:
                self.sock.sendall(request_str)
            except socket.error as msg:
                # print(msg)
                retry += 1
                # parse the data
                self.disconnect()
                continue

            try:
                # recive the telegram
                # end_of_message = '</%s>'%request_type.split('.')[-1]
                # self.telegram_raw = ''
                # loops = 0
                # while  len(self.telegram_raw) < 3600 and loops < 15:
                #     self.telegram_raw += self.sock.recv(254) # todo check len
                #     loops += 1
                #     if len(self.telegram_raw) >= len(end_of_message):
                #         # check if message is complet
                #         if self.telegram_raw[-len(end_of_message)::] == self.telegram_raw:
                #             break

                self.telegram_raw = self.sock.recv(2506)  # todo check len
            except socket.timeout:
                print('timed out')
                retry += 1
                # parse the data
                self.disconnect()
                time.sleep(0.5)
                continue
            except socket.error as msg:
                print(msg)
                retry += 1
                # parse the data
                self.disconnect()
                time.sleep(0.5)
                continue

            self.disconnect()
            retry += 1
            # parse the data
            result = self.parse_telegram()
            if result is False:
                time.sleep(0.5)
        return result

    def parse_telegram(self):
        """
        parse the telegram data, split into header and xml, check the length
        """

        # split the data
        try:
            (self.telegram_header, self.telegram_xml) = self.telegram_raw.split('\r\n\r\n')
        except:
            return False
        try:
            telegram_length = None
            for item in self.telegram_header.split('\r\n'):
                (field, value) = item.split(':')
                if field == 'Length':
                    telegram_length = int(value)
        except:
            return False

        if telegram_length is None:
            return False
        if len(self.telegram_xml) != telegram_length:
            return False
        xml_doc = xml.etree.ElementTree.fromstring(self.telegram_xml)

        output = {}
        for item in xml_doc.getchildren():
            if item.tag == 'ProtocolVersion':
                output['ProtocolVersion'] = item.text
            elif item.tag == 'TelegramType':
                output['TelegramType'] = item.text
            elif item.tag == 'Value':
                # select parser
                if xml_doc.tag == 'LiveSensors':
                    for node in item.getchildren():
                        data = parse_live_sensors_response(node)
                        output[data['InputType']] = data
                    return output
                elif xml_doc.tag == 'CalibratorDevice':
                    output['Value'] = parse_calibrator_device_response(item)
                elif xml_doc.tag == 'CalibrationDate':
                    output['Value'] = parse_calibration_info_response(item)
                else:
                    return output

        return output

    def request(self, request_type='SensorManager.LiveSensors', telegram_type='get-request', seq=1, protocol_version=1,
                version='1.0.1691.0'):
        """
        build a request

        """

        request_telegram_type = request_type.split('.')[-1]

        request_xml = '<?xml version="1.0"?>\r\n'
        request_xml += '<%s xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" Seq="%d">\r\n' % (
            request_telegram_type, 0)
        request_xml += '  <ProtocolVersion>%d</ProtocolVersion>\r\n' % protocol_version
        request_xml += '  <TelegramType>%s</TelegramType>\r\n</%s>' % (telegram_type, request_telegram_type)

        request_header = 'Length:%d\r\nVersion:%s\r\n' % (len(request_xml), version)
        request_header += 'Type:Ametek.Jofra350.Communication.Telegrams.JCAPI.%s\r\n' % request_type
        request_header += 'Seq:%d\r\n\r\n' % seq

        return request_header + request_xml
