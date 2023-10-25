# Rocket Group - OAxFORTIS
## Detector Data Broadcast (VIM-BCAST) & Zero Order Data over Parallel Out (VIM-PARLL)
### Running the software:

By default, the software will launch automatically when the board boots up. The software is launched using `sudo crontab -e`.

The devices are expecting to be on a local area network in the neighborhood of 192.168.1.1/24. Development was done on a network in 172.16.0.1/20. Use Network Manager (nmcli) to change IP addresses/networks/etc.

The two devices are SBCs from Khadas called the VIM2, with the hostnames __VIM-BCAST__ and __VIM-PARLL__:

---

#### __VIM-BCAST__
Receives the detector data packets over unicast UDP and  resends them to the broadcast address. 

__IP Address__: 192.168.1.100 (172.16.1.125) \
__MAC Address__: C8:63:14:70:3E:A7
    
---

#### __VIM-PARLL__: 
Receives the zero-order data packets over broadcast UDP and converts them to parallel data, sent to the RIO.

__IP Address__: 192.168.1.200 (172.16.1.126)\
__MAC Address__: C8:63:14:70:3E:99