# Copyright (c) 2016 System Level Solutions Pvt Ltd
#
# All rights reserved.
# The License is available at
#    http://www.slscorp.com/licence
#
# Contributors:
#    Nilesh Vora - initial API and implementation

"""
This is client module for Yalgaar Server. This module contains API for
connecting with Yalgaar server.
"""

import client as mqtt

import sys
import random
import string
import json
import time
import re

from encrypt import AESCipher

#Supported AES Types
AES_TYPES = [128, 192, 256]
BLOCK_SIZE = {128:16, 192:24, 256:32}

#Yalgaar error codes
YALGAAR_ERR_SUCCESS = 0
YALGAAR_ERR_CLIENT_ID_NULL = 101
YALGAAR_ERR_INVALID_CLIENT_ID = 102
YALGAAR_ERR_INVALID_CLIENT_KEY = 103
YALGAAR_ERR_INVALID_UUID = 104
YALGAAR_ERR_CLIENT_KEY_INACTIVE = 105
YALGAAR_ERR_SSL_DISABLED = 106
YALGAAR_ERR_LIMIT_EXCEEDED = 107
YALGAAR_ERR_SUB_INVALID_CHANNEL = 108
YALGAAR_ERR_SUB_KEY_NOT_MATCH = 109
YALGAAR_ERR_SUB_MULTIPLE_CH_NOT_ALLOWED = 110
YALGAAR_ERR_SUB_NAME_NOT_SUPPORTED = 111
YALGAAR_ERR_NO_STORAGE = 112
YALGAAR_ERR_NO_PRESENCE = 113
YALGAAR_ERR_NOT_SUBSCRIBED = 114
YALGAAR_ERR_PUB_MSG_NULL = 115
YALGAAR_ERR_PUB_INVALID_CHANNEL = 116
YALGAAR_ERR_PUB_KEY_NOT_MATCH = 117
YALGAAR_ERR_PUB_CNT_LIMIT_EXCEEDED = 118
YALGAAR_ERR_PUB_SIZE_LIMIT_EXCEEDED = 119
YALGAAR_ERR_PUB_NAME_NOT_SUPPORTED = 120
YALGAAR_ERR_UNSUB_INVALID_CHANNEL = 121
YALGAAR_ERR_UNSUB_KEY_NOT_MATCH = 122
YALGAAR_ERR_UNSUB_NAME_NOT_SUPPORTED = 123
YALGARR_ERR_SUBCRIPTION_NOT_ALLOWED = 125
YALGARR_ERR_PUBLISH_NOT_ALLOWED = 126

# Yalgaar error strings
error_strings = {YALGAAR_ERR_SUCCESS:'Connection successful', YALGAAR_ERR_CLIENT_ID_NULL:'ClientId should not be null', YALGAAR_ERR_INVALID_CLIENT_ID:'Invalid ClientId', YALGAAR_ERR_INVALID_CLIENT_KEY:'Invalid ClientKey.ClientKey is not registered', YALGAAR_ERR_INVALID_UUID:'Invalid Uuid.Only alpha numeric,hyphens,@,underscore allowed and maximum length must be 50.', YALGAAR_ERR_CLIENT_KEY_INACTIVE:'ClientKey is not active', YALGAAR_ERR_SSL_DISABLED:'SSL is not enable.', YALGAAR_ERR_LIMIT_EXCEEDED:'The maximum connection limit has been reached.', YALGAAR_ERR_SUB_INVALID_CHANNEL:'Invalid subscribe channel.', YALGAAR_ERR_SUB_KEY_NOT_MATCH:'Invalid subscribe channel.ClientKey does not match.', YALGAAR_ERR_SUB_MULTIPLE_CH_NOT_ALLOWED:'Multiple subscribe channels are not allowed. Multiplexing is not enable.', YALGAAR_ERR_SUB_NAME_NOT_SUPPORTED:'Invalid subscribe channel.Only alpha numeric,hyphens,@,underscore allowed and maximum length must be 50.', YALGAAR_ERR_NO_STORAGE:'Storage is not enable.', YALGAAR_ERR_NO_PRESENCE:'Presence is not enable.', YALGAAR_ERR_NOT_SUBSCRIBED:'Entered history channel has not been subscribed.', YALGAAR_ERR_PUB_MSG_NULL:'Message can not be null.', YALGAAR_ERR_PUB_INVALID_CHANNEL:'Invalid publish channel.', YALGAAR_ERR_PUB_KEY_NOT_MATCH:'Invalid publish channel.ClientKey does not match.', YALGAAR_ERR_PUB_CNT_LIMIT_EXCEEDED:'Message count exceeds maximum limit.', YALGAAR_ERR_PUB_SIZE_LIMIT_EXCEEDED:'Message size exceeds maximum limit.', YALGAAR_ERR_PUB_NAME_NOT_SUPPORTED:'Invalid publish channel.Only alpha numeric,hyphens,@,underscore allowed and maximum length must be 50.', YALGAAR_ERR_UNSUB_INVALID_CHANNEL:'Invalid UnSubscribe channel.', YALGAAR_ERR_UNSUB_KEY_NOT_MATCH:'Invalid UnSubscribe channel.ClientKey does not match.', YALGAAR_ERR_UNSUB_NAME_NOT_SUPPORTED:'Invalid UnSubscribe channel.Only alpha numeric,hyphens,@,underscore allowed and maximum length must be 50.', YALGARR_ERR_SUBCRIPTION_NOT_ALLOWED:'Subscribe is disabled for this UUID.', YALGARR_ERR_PUBLISH_NOT_ALLOWED:'Publish is disabled for this UUID.'}

class Yalgaar:
    """
    This is a main class of Yalgaar framework and can be used 
    to create connection with Yalgaar server and subsrice and
    publish on yalgaar channel with Client Key provided.
    """
    def __init__(self, url="api.yalgaar.io", port=1883, keepalive=60):
        """@url is the url of yalgaar server by default.
           @port is the port number of the yalgaar server when ssl is not used
           @keepalive: Maximum period in seconds between communications with the
            broker. If no other messages are being exchanged, this controls the
            rate at which the client will send ping messages to the broker.
        """
        self.__url = url
        self.__port = port
        self.__keepalive = keepalive
        self.__shouldEncrypt = False
        self.__shouldDecrypt = False
    
    def handle_error(self, code):
        """@code Error code given by yalgaar server
        """
        if code in error_strings.keys():
            if self.__connect_cb is not None:
                self.__connect_cb(code, error_strings[code])

    def Encrypt(self, plain_text):
        """This is a encryption method used this Yalgaar SDK to encrypt the @plain_text
        """
        try:
            from Crypto.Cipher import AES
        except ImportError:
            print ('Install Crypto module in order to use Cryptography')
        o = AESCipher(self.__aesKey)
        enc_text = o.encrypt(str(plain_text))
        return enc_text
        
    def Decrypt(self, enc_text):
        """This is a decryption method used this Yalgaar SDK to decrypt the @enc_text
        """
        try:
            from Crypto.Cipher import AES
        except ImportError:
            print('Install Crypto module in order to use Cryptography')
        o = AESCipher(self.__aesKey)
        plain_text = o.decrypt(enc_text)
        return plain_text
    
    def on_connect(self, __client, userdata, flags, rc):
        """This is callback function for Yalgaar server connection
        """
        #print("Result Code: " + str(rc))
        self.handle_error(rc)
    
    def on_message(self, __client, userdata, msg):
        """This is callback function when there is a message from yalgaar server
        """
        #print(msg.topic + " " + str(msg.payload))
        parent_topic = msg.topic.split("$")
        #print("len: " + str(len(parent_topic)))
        if len(parent_topic) == 1:
            try:
                decoded = json.loads(msg.payload.decode())
                #print("JSON parsing example: ", decoded['uuid'])
                #print("JSON parsing example: ", decoded['isPresence'])
                if decoded['uuid'] != str(self.__uuid) and decoded['isPresence']:
                    if self.__on_presense is not None:
                        self.__on_presense(str(msg.payload))
                elif decoded['uuid'] == str(self.__uuid) and decoded['isPresence']:
                    pass
            except ValueError:
                """
                    If received message is not json message, then it will come here
                """
                if self.__shouldDecrypt == True:
                    try:
                        revd_msg = self.Decrypt(msg.payload.decode())
                    except ValueError:
                        print('Msg can not be decrypted. Considering as Normal')
                        revd_msg = msg.payload.decode()
                else:
                    revd_msg = msg.payload.decode()
                if self.__on_message is not None:
                    self.__on_message(msg.topic, revd_msg)
                return
        elif len(parent_topic) == 3:
            parse_topic = parent_topic[2]
            #print("Parse topic: " + parse_topic)
            if parse_topic == 'history':
                if self.__on_history is not None:
                    self.__on_history(msg.payload.decode())
            elif parse_topic == 'channels':
                if self.__on_channelList is not None:
                    self.__on_channelList(msg.payload.decode())
            elif parse_topic == 'users':
                if self.__on_userList_cb is not None:
                    self.__on_userList_cb(msg.payload.decode())

    def on_publish(self, __client, userdata, msg):
        """This is callback function when message is published from this framework
        """
        pass
    
    def on_disconnect(self, __client, obj, rc):
        """This is callback function when disconnected from yalgaar server
        """
        print("Disconnected with result code " + str(rc));
        self.handle_error(rc)

    def on_subscribe(self, __client, obj, mid, granted_qos):
        """This is callback function when you are successfully subscribe to channel
        """
        #print("Subscribed: " + str(mid) + " " + str(granted_qos))
        for code in granted_qos:
            if self.__on_sub_err is not None:
                if code in error_strings.keys():
                    if code != 0:
                        self.__on_sub_err(error_strings[code])
                    else:
                        print("Subscribed successfully")
    
    def on_unsubscribe(self, __client, userdata, mid):
        """This is callback function when you are successfully unsubscribe to channel
        """
        print("UnSubscribed: " + str(mid))
    
    def generateUuid(self, len):
        """This method generates random id with [A-Za-z0-9_@-] regex
        """
        return ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase + '-' + '_' + '@') for _ in range(len))
        
    def yalgaarConnect(self, clientKey, isSecure, connect_cb = None, uuid = None, aesType = None, aesKey = None):
        """ This method will be used to connect to the yalgaar server
            @clientKey is the registered client for Yalgaar server
            @isSecure is True if connection is secured by TLS
            @connect_cb is callback given by user to know the status
            @uuid is random id given by user. If None given then one will be generated
            @aesType is 128,192 or 256 bit encryption types
            @aesKey is secret key used by AES encryption
        """
        self.__connect_cb = connect_cb
        
        if clientKey is None or isinstance(clientKey, str) == False:
            self.handle_error(YALGAAR_ERR_INVALID_CLIENT_KEY)
        
        if aesType is not None and aesKey is not None:
            try:
                from Crypto.Cipher import AES
            except ImportError:
                raise ImportError('Install Crypto module in order to use cryptography.')

            if aesType in AES_TYPES:
                self.__aesType = aesType
            else:
                raise NameError('AES type must be 128, 192 or 256')
                
            if len(aesKey) is not aesType // 8:
                raise NameError('AES type does not match with AES key.')
            self.__aesKey = aesKey
            self.__shouldEncrypt = True
            self.__shouldDecrypt = True
            
            
        self.__isSecure = isSecure
        self.__clientKey = clientKey
        
        if uuid is None:
            uuid = self.generateUuid(3)
        
        self.__uuid = uuid
        if self.__uuid is None:
            self.handle_error(YALGAAR_ERR_INVALID_UUID)
            
        client_id = str(clientKey) + '/' + uuid
        if client_id is None:
            self.handle_error(YALGAAR_ERR_CLIENT_ID_NULL)
            
        self.__client = mqtt.Client(client_id)
        self.__client.on_connect = self.on_connect
        self.__client.on_disconnect = self.on_disconnect
        self.__client.on_message = self.on_message
        self.__client.on_publish = self.on_publish
        self.__client.on_subscribe = self.on_subscribe
        self.__client.on_unsubscribe = self.on_unsubscribe
        if isSecure is True:
            self.__client.tls_set("api_yalgaar_io.pem")
            self.__port = 8883
        self.__client.connect(self.__url, self.__port, self.__keepalive)        
    
    def handle_subscribe_error(self, code):
        if self.__on_sub_err is not None:
            self.__on_sub_err(error_strings[code])
    
    def yalgaarSubscribe(self, channel, message_cb = None, presense_cb = None, err_cb = None):
        """This method will be used to subscribe to channel on yalgaar server
           @channel is the channel to which user wants to subscribe
           @message_cb is callback when there is any message on this channel
           @presense_cb is callback to capture the presense of other user on same channel
           @err_cb is callback to capture the error event
            
        """
        subscribe_list = []
        self.__on_message = message_cb
        self.__on_presense = presense_cb
        self.__on_sub_err = err_cb
        
        if self.__clientKey is None:
            self.handle_error(YALGAAR_ERR_CLIENT_ID_NULL)
        
        if type(channel) is str:
            if channel is None:
                self.handle_subscribe_error(YALGAAR_ERR_SUB_INVALID_CHANNEL)
            subscribe_list.append(channel)
        elif type(channel) is list:
            for name in channel:
                if type(name) is not str:
                    self.handle_subscribe_error(YALGAAR_ERR_SUB_INVALID_CHANNEL)
                subscribe_list.append(name)
        else:
            self.handle_subscribe_error(YALGAAR_ERR_SUB_NAME_NOT_SUPPORTED)
        
        for ch in subscribe_list:
            if re.match("^[A-Za-z0-9_@-]*$", ch) is None:
                self.handle_subscribe_error(YALGAAR_ERR_SUB_NAME_NOT_SUPPORTED)
            channel_id = self.__clientKey + '/' + ch
            #print('Subscribing to ' + channel_id)
            rc = self.__client.subscribe(channel_id)

    def yalgaarUnSubscribe(self, channel):
        """This method will be used to unsubscribe from channel
        @channel is the channel to which user wants to unsubscribe
        """
        unsubscribe_list = []
        if self.__clientKey is None:
            self.handle_error(YALGAAR_ERR_CLIENT_ID_NULL)
            
        if type(channel) is str:
            if channel is None:
                self.handle_error(YALGAAR_ERR_UNSUB_INVALID_CHANNEL)
            unsubscribe_list.append(channel)
        elif type(channel) is list:
            for name in channel:
                if type(name) is not str:
                    self.handle_error(YALGAAR_ERR_UNSUB_NAME_NOT_SUPPORTED)
                unsubscribe_list.append(name)
        else:
            self.handle_error(YALGAAR_ERR_UNSUB_NAME_NOT_SUPPORTED)
        
        for ch in unsubscribe_list:
            if re.match("^[A-Za-z0-9_@-]*$", ch) is None:
                self.handle_error(YALGAAR_ERR_UNSUB_NAME_NOT_SUPPORTED)
            channel_id = self.__clientKey + '/' + ch
            #print('UnSubscribing from ' + channel_id)
            try:
                self.__client.unsubscribe(channel_id)
            except ValueError as e:
                print(str(e))
        
    def yalgaarPublish(self, channel, message):
        """This method will be used to publish message on given channel
        @channel is the channel on which user wants to publish
        @message is message in string format
        """
        if self.__clientKey is None or channel is None:
            self.handle_error(YALGAAR_ERR_PUB_INVALID_CHANNEL)
        if re.match("^[A-Za-z0-9_@-]*$", channel) is None:
            self.handle_error(YALGAAR_ERR_PUB_NAME_NOT_SUPPORTED)
        channel_id = self.__clientKey + '/' + channel
        #print("Publishing on " + channel_id)
        if self.__shouldEncrypt == True:
            send_text = self.Encrypt(message)
        else:
            send_text = message
        self.__client.publish(channel_id, send_text)
    
    def yalgaarHistory(self, channel, count, history_cb = None, err_cb = None):
        """This method will be used to capture the history message on the given channel
        @channel is the channel from which user wants to capture history events
        @count is the number of history message to be collected
        @history_cb is callback to call when all message are capture
        @err_cb is callback to capture the error event
        """
        if self.__clientKey is None or channel is None:
            if err_cb is not None:
                err_cb(error_strings[YALGAAR_ERR_SUB_INVALID_CHANNEL])
        if re.match("^[A-Za-z0-9_@-]*$", str(self.__uuid)) is None:
            if err_cb is not None:
                err_cb(error_strings[YALGAAR_ERR_INVALID_UUID])
        if re.match("^[A-Za-z0-9_@-]*$", channel) is None or type(channel) is not str:
            if err_cb is not None:
                err_cb(error_strings[YALGAAR_ERR_SUB_NAME_NOT_SUPPORTED])
        channel_id = self.__clientKey + '/' + str(self.__uuid) + '/' + channel + '$' + str(count) + '$history'
        self.__on_history = history_cb
        self.__on_sub_err = err_cb
        #print('Getting history from ' + channel_id)
        self.__client.subscribe(channel_id)
    
    def yalgaarChannelList(self, uuid, channelList_cb = None, err_cb = None):
        """This method will be used to get the list of channels used by given uuid
        @uuid is UUID used to get the list of channels accosiated with itself
        @channelList_cb is callback function when response is recevied
        @err_cb is callback to capture the error event
        """
        if uuid is None:
            if err_cb is not None:
                err_cb("Uuid should not be null")
        if self.__clientKey is None:
            if err_cb is not None:
                err_cb(error_strings[YALGAAR_ERR_SUB_INVALID_CHANNEL])
        if re.match("^[A-Za-z0-9_@-]*$", uuid) is None:
            if err_cb is not None:
                err_cb(error_strings[YALGAAR_ERR_INVALID_UUID])
        channel_id = self.__clientKey + '/' + str(self.__uuid) + '/' + uuid + '$0$channels'
        self.__on_channelList = channelList_cb
        self.__on_sub_err = err_cb
        #print('Getting channel list from ' + channel_id)
        self.__client.subscribe(channel_id)

    def yalgaarUserList(self, channel, userList_cb = None, err_cb = None):
        """This method will be used to get the list of used subscribed to given channel
        @channel is channel used to get the users on it
        @userList_cb is callback function when response is received
        @err_cb is callback to capture the error event
        """
        if self.__clientKey is None:
            self.handle_error(YALGAAR_ERR_SUB_INVALID_CHANNEL)
        if re.match("^[A-Za-z0-9_@-]*$", str(self.__uuid)) is None:
            self.handle_error(YALGAAR_ERR_INVALID_UUID)
        if re.match("^[A-Za-z0-9_@-]*$", channel) is None or type(channel) is not str:
            self.handle_error(YALGAAR_ERR_SUB_NAME_NOT_SUPPORTED)
        channel_id = self.__clientKey + '/' + str(self.__uuid) + '/' + channel + '$0$users'
        self.__on_userList_cb = userList_cb
        self.__on_sub_err = err_cb
        #print(channel_id)
        self.__client.subscribe(channel_id)
        
    def looping(self):
        """Process the network events.
        Return 0 on success otherwise >0.
        """
        rc = self.__client.loop()
        if rc != 0:
            self.handle_error(rc)
        return rc
        
    def loop_forever(self):
        """This will process the network event 
           in continous loop.
        """
        self.__client.loop_forever()
        
    def loop(self):
        """This will process the network event when called.
        """
        self.__client.loop()