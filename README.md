# rocketLab

Detector Data Broadcast (VIM-BCAST) 
            & 
First Order Data over Parallel Out (VIM-PARLL)

Running the software:
    By default, the software will launch automatically when the board boots up.
    The software is launched using `sudo crontab -e`.

    The devices are expecting to be on a local area network in the neighborhood
    of 192.168.1.1/24. Development was done on a network in 172.16.0.1/20.

    The two devices are called VIM-BCAST and VIM-PARLL:
    
    VIM-BCAST: Receives the detector data packets over unicast UDP and 
                resends them to the broadcast address.
        - IP:   192.168.1.100 (172.16.1.125)
        - MAC:  C8:63:14:70:3E:A7
    
    VIM-PARLL: Receives the zero-order data packets over broadcast UDP and
                converts them to parallel data, sent to the RIO.
        - IP:     192.168.1.200 (172.16.1.126)
        - MAC:    C8:63:14:70:3E:99