import requests
import ScanUtility
import bluetooth._bluetooth as bluez
from collections import defaultdict
import time
from time import sleep

# Set bluetooth device. Default 0.
dev_id = 0
try:
    sock = bluez.hci_open_dev(dev_id)
    print("\n *** Looking for BLE Beacons ***\n")
    print("\n *** CTRL-C to Cancel ***\n")
except:
    print("Error accessing bluetooth")

ScanUtility.hci_enable_le_scan(sock)

mac_address_count = defaultdict(int)

RASPBERRY_ID = 1  # Replace with the Raspberry Pi's ID
WEB_APP_URL = f"http://10.0.1.100:5000/update/2"

mac_last_seen = {}  # Store the last seen time of each MAC address
zero=1
last_mac_address_count={}
post_interval=5
last_post_time=8
try:

    while True:
        returnedList = ScanUtility.parse_events(sock, 10)
        current_time = time.time()
        for mac_address, last_seen_time in list(mac_last_seen.items()):
            if current_time - last_seen_time > 30:
                del mac_address_count[mac_address]
                del mac_last_seen[mac_address]
                
            
        #print("return", returnedList)


        for item in returnedList:
            mac_address = item["macAddress"]
            mac_address_count[mac_address] = item["rssi"]
            mac_last_seen[mac_address] = current_time  # Update last seen time
            #print(mac_address_count)
        # Send updated data to the web app
        
        if mac_address_count != last_mac_address_count:
            if mac_address_count=={}:
               zero+=1
			
            #print(mac_address_count,zero,last_mac_address_count)

			#print(mac_address_count, last_mac_address_count)
            if mac_address_count=={}:
                print("empty")
                requests.post(WEB_APP_URL, json=mac_address_count)

            elif mac_address_count!={} and current_time-last_post_time>=5:
                print("change")
                last_post_time=current_time
                requests.post(WEB_APP_URL, json=mac_address_count)
			    
        last_mac_address_count=dict(mac_address_count)
            
except KeyboardInterrupt:
    pass
