# BLE iBeacon 掃描器 - iBeacon 和 Eddystone 信標

一個使用 Raspberry Pi 和 Python 掃描 iBeacon 和 Eddystone BLE 信標的簡單專案。

## iBeacon
UUID、Major、Minor、Mac 地址和 RSSI

## Eddystone
UID - 查找：命名空間 ID 和實例 ID。

URL - 查找：URL 和 URL 前綴。

EID - 查找（詳細信息即將推出）。

TLM - 查找（詳細信息即將推出）。



這是一個演示：

![](BLEBeaconDemo.gif)

## Getting Started

您需要下載 bluez 以獲取藍牙數據。

```
sudo apt-get update
sudo apt-get install python-pip python-dev ipython
```
```
sudo apt-get install bluetooth libbluetooth-dev
sudo pip install pybluez
```
另外，為了檢測 BLE 設備，您需要啟用實驗性功能。請按照以下步驟操作：

1. Go to directory

```
cd /lib/systemd/system
```
2. Edit a file
```
sudo vim bluetooth.service
```
Add ```--experimental``` after  ```ExecStart=/usr/local/libexec/bluetooth/bluetoothd```
So it lookes like this: 
```
ExecStart=/usr/local/libexec/bluetooth/bluetoothd --experimental
```

3. Save and exit vim
Shift + Colon, then type ```wq!``` - to write and quit.

4. Restart daemon
```
sudo systemctl daemon-reload
```
5. Restart bluetooth
```
sudo systemctl restart bluetooth
```

## Quick Start

Download files.

Go to directory
```
cd Desktop/BLE-Beacon-Scanner
```
Run
```
python BeaconScanner.py
```
Note that this does not work with Python 3 yet... we are working on it!

## Running the tests

Once the app is running you should see any iBeacon and Eddystone devices in the vicinity - The RSSI will update if an iBeacon moves.

## Deployment

I DON'T recommend that you use this in a live project - it is merely a proof of concept.

## Future Development

- UriBeacon support
- Versatility
- Beacon type selection

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE
