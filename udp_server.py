"""A server that handles a connection with an OpenBCI board and serves that
data over both a UDP socket server and a WebSocket server.

Requires:
  - pyserial
  - asyncio
  - websockets
"""

import json
import socket
from recordclass import recordclass
import tests
import struct

class UDPServer():

  def __init__(self, ip='localhost', port=8888):
    self.ip = ip
    self.port = port
    self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # print(ip,port)
    
  def activate(self):
    if len(self.args) > 0:
      self.ip = self.args[0]
    if len(self.args) > 1:
      self.port = int(self.args[1])
    
    # init network
    self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  def __call__(self, sample): 
    self.send_data(json.dumps(sample.channel_data))
    
  def send_data(self, data, type):

    if type is (None or 'raw_data'):                                 #default = raw data
      print('original data (data return obj: ', data)
      data = data.raw_data
      print('raw data portion', data)
    elif type is 'fft_data':                
      data = self.data.fft_data

    #MAKE DATA INTO A BYTE-LIKE OBJECT
    packer = struct.Struct('s s s s s s s s')
    packed_data = packer.pack(*data)
    self.server.sendto(data, (self.ip, self.port))



  def receive_data(self,data,type):
    self.send_data(data, type)

  def deactivate(self):
    self.server.close();
