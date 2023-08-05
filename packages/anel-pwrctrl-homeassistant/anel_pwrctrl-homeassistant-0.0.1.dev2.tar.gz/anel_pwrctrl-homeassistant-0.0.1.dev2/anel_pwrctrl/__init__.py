#!/usr/bin/env python

import socket
import time
from base64 import b64encode
from socket import AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST


class Switch:
    def __init__(self, device, idx, label, state):
        self.device = device
        self.idx = idx
        self.label = label
        self.state = state

    def on(self):
        self.device.write('Sw_on{idx}'.format(idx=self.idx))
        self.device.update()

    def off(self):
        self.device.write('Sw_off{idx}'.format(idx=self.idx))
        self.device.update()

    def get_index(self):
        return self.idx

    def get_state(self):
        return self.state


class Device:
    switches = {}

    def __init__(self, master, label, ip_addr, read_port, write_port, auth):
        self.master = master
        self.host = ip_addr
        self.port_read = read_port
        self.port_write = write_port
        self.auth = auth

        self.label = label

    def update_switch(self, idx, label, state):
        if idx not in self.switches:
            self.switches[idx] = Switch(device=self, idx=idx, label=label, state=state)
        else:
            self.switches[idx].label = label
            self.switches[idx].state = state

    def update(self):
        self.master.query(ip_addr=self.host,
                          read_port=self.port_read,
                          write_port=self.port_write)

    def print(self):
        print("{name}<{ip}> {auth}".format(name=self.label, ip=self.host, auth=self.auth))

        for switch in self.switches.values():
            print(" - {}: {} ({})".format(switch.idx, switch.state, switch.label))

    def write(self, payload):
        data = "{payload}{auth}".format(payload=payload, auth=self.auth).encode('latin1')
        print('= payload "{payload}" to {host}'.format(payload=data, host=self.host))

        sock = socket.socket(AF_INET, SOCK_DGRAM)
        sock.sendto(data, (self.host, self.port_write))
        sock.close()

    def read(self):
        pass

    def on(self, idx):
        self.switches[idx].on()

    def off(self, idx):
        self.switches[idx].off()

    def test(self):
        print("Testing device {label} ({addr})".format(label=self.label, addr=self.host))
        for switch in self.switches:
            print("+ Sw{} on".format(switch.idx))
            switch.on()
            time.sleep(2)
            print("+ Sw{} off".format(switch.idx))
            switch.off()


class DeviceMaster:
    def __init__(self, username, password, read_port, write_port):
        self.auth = b64encode("{}{}".format(username, password).encode('ascii')).decode('latin1')
        self.read_port = read_port
        self.write_port = write_port
        self.devices = {}

    def query(self, ip_addr=None, read_port=None, write_port=None):
        if read_port is None:
            read_port = self.read_port
        if write_port is None:
            write_port = self.write_port

        sock = socket.socket(family=AF_INET, type=SOCK_DGRAM)
        sock.bind(('0.0.0.0', read_port))

        query = "wer da?".encode('latin1')

        if ip_addr is None:
            sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            sock.sendto(query, ('255.255.255.255', write_port))
            sock.settimeout(2.0)
        else:
            sock.sendto(query, (ip_addr, write_port))
            sock.settimeout(0.5)

        while True:
            try:
                buffer, address = sock.recvfrom(1024)
            except socket.timeout:
                break

            # ['NET-PwrCtrl', 'PWR-GARTEN', '192.168.178.189', '255.255.255.0', '192.168.178.1', '0.4.163.16.4.23', 'Nr.1,0', 'Nr.2,0', 'Nr.3,0', 'Nr.4,0', 'Nr.5,0', 'Nr.6,0', 'Nr.7,0', 'Nr.8,0', '0', '80', 'IO-1,0,0', 'IO-2,0,0', 'IO-3,0,0', 'IO-4,0,0', 'IO-5,0,0', 'IO-6,0,0', 'IO-7,0,0', 'IO-8,0,0', '27.4°C', 'NET-PWRCTRL_06.0', 'h', 'n']
            bits = buffer[:-2].decode('latin1').split(':')

            ip_addr = bits[2]

            if ip_addr not in self.devices:
                self.devices[ip_addr] = Device(master=self, label=bits[1],
                                               ip_addr=bits[2], read_port=read_port, write_port=write_port,
                                               auth=self.auth)

            # update states for already existings devices
            ip_addr = self.devices[ip_addr]
            for idx, sw in enumerate(bits[6:14]):
                label, state = sw.split(',', 1)
                ip_addr.update_switch(idx=idx + 1,
                                      label=label.encode('latin1').decode('utf-8'),
                                      state=int(state))

        sock.close()
