# Author: Jared Frees
# Testing: ssh -p 2222 127.0.0.1
"""
SSH server that accepts connections and immediately closes them to
protect against users trying to break in. This program reads the first line
of the SSH connection to get the client SSH version and logs the version.
This is a low interaction, passive honeypot which means it does not give
the attacker any real access to the computer system, it simply allows a connection
and then closes it so the attacker does not think they actually broke into
an SSH system.
"""

import socket
import sys
import time
import os
import threading
from common.common import HoneypotBaseServer

def log(address, data):
  sep = '-' * 50
  with open('./ssh/logs/ssh.log', 'a') as file:
    file.write('Time: {}\nAddress: {}:{}\nClient SSH Version: {}\n'.format(time.ctime(), address[0], address[1], data))
    file.write(sep + '\n')

class SshServer(HoneypotBaseServer):
  def __init__(self):
    HoneypotBaseServer.__init__(self, 'SSH')

  def handle_ssh_connection(self, client_sock, client_addr):
    client_version = client_sock.recv(1024).decode('ascii').rstrip()
    print('SSH connection with address:', client_addr)
    log(client_addr, client_version)
    client_sock.close()
    
  def listen_for_connections(self, sock):
    while True:
      client_sock, client_addr = sock.accept()
      threading.Thread(target=self.handle_ssh_connection, args=[client_sock, client_addr], daemon=True).start()
        
  # Opens tcp port and listens for connections
  def run_pot(self):
    host = ''
    port = 2222
    print("Starting SSH honeypot on port ", port, "...", sep='')
    try:
      # Bind socket to port and accept connections from 100 clients max
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      sock.bind((host, port))
      sock.listen(100)
      self.is_running = True
      print('SSH server started, listening for SSH connections')
      # Multithreaded
      threading.Thread(target=self.listen_for_connections, args=[sock], daemon=True).start()
    except Exception as e:
          print('ERROR: SSH socket failed on port', port, 'with error:', e)
          sys.exit(1)

def main():
  try:
    server = SshServer()
    server.run_pot()
  except KeyboardInterrupt:
    print('Closing SSH server...')
    sys.exit(1)

if __name__ == '__main__':
  main()
