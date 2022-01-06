import random
import time

from pythonosc import udp_client


ip = "127.0.0.1"
port = 57121

client = udp_client.SimpleUDPClient(ip, port)

for x in range(10):
  client.send_message("/testAddress", random.random())
  time.sleep(1)