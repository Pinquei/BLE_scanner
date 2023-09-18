import ScanUtility
import bluetooth._bluetooth as bluez
from collections import defaultdict

# Set bluetooth device. Default 0.
dev_id = 0
try:
    sock = bluez.hci_open_dev(dev_id)
    print("\n *** Looking for BLE Beacons ***\n")
    print("\n *** CTRL-C to Cancel ***\n")
except:
    print("Error accessing bluetooth")

ScanUtility.hci_enable_le_scan(sock)

mac_address_count = defaultdict(int)  # Dictionary to store macAddress and its count

try:
    while True:
        returnedList = ScanUtility.parse_events(sock, 10)
        for item in returnedList:
            mac_address = item["macAddress"]
            mac_address_count[mac_address] += 1  # Increment the count for each appearance
            print(f"MacAddress: {mac_address}, Count: {mac_address_count[mac_address]}")
except KeyboardInterrupt:
    pass
