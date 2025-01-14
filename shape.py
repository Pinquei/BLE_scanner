import sqlite3
from flask import Flask, jsonify
import time
import requests
import threading
import csv
import json

app = Flask(__name__)

# Dictionary to store data for each Raspberry Pi
raspberry_data = {}
update_interval = 15  # 更新数据的时间间隔，单位为秒

raspberry_ip_mapping = {
    4: '192.168.50.132',
    5: '192.168.50.201',
    6: '192.168.50.235'
}

# Dictionary to store beacon mapping to Raspberry Pi
beacon_raspberry_mapping = {}  # 初始化为空字典
temp_mac_data={}
problem=[]

# Load beacon mapping from 'beacon_id.csv' file
with open('beacon_id.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        if len(row) == 2:
            beacon_number, mac_address = int(row[0]), row[1]
            beacon_raspberry_mapping[beacon_number] = mac_address


def update_raspberry_data():
    raspberry_data={}
    global temp_mac_data
    while True:
        mac_data={}
        for raspberry_id, ip_address in raspberry_ip_mapping.items():
            try:
                # 向樹莓派发送请求获取数据
                response = requests.get(f'http://{ip_address}:8080/count')
                if response.status_code == 200:
                    data = response.json()
                    raspberry_data[raspberry_id] = data
                    temp_mac_data[raspberry_id]=data
                    # 保留具有最大信号强度的记录
                    for key, values in raspberry_data.items():
                        for mac, signal_strength in values.items():
                            if mac not in mac_data:
                                mac_data[mac] = {}
                            mac_data[mac][key] = signal_strength
                else:
                    print(f"Failed to update data for Raspberry Pi {raspberry_id}")

            except Exception as e:
                print("")
                # print(f"Error updating data for Raspberry Pi {raspberry_id}")
                # for mac, signal_strength in temp_mac_data[raspberry_id].items():
                #     if mac not in mac_data:
                #         mac_data[mac] = {}
                #     mac_data[mac][raspberry_id] = signal_strength*1.2
                #     temp_mac_data[raspberry_id][mac]=signal_strength*1.2
        # 在这里进行beacon与mac的映射
        beacon_raspberry_result = {}
        for mac, signal_data in mac_data.items():
            if len(signal_data) > 1:
                max_key = max(signal_data, key=signal_data.get)
                for key in signal_data.keys():
                    if key != max_key:
                        try:
                            raspberry_data[key].pop(mac)
                        except:
                            temp_mac_data={}

        for beacon_number, mac_address in beacon_raspberry_mapping.items():
            found = False
            for raspberry_id, data in raspberry_data.items():
                if mac_address in data:
                    beacon_raspberry_result[beacon_number] = raspberry_id
                    found = True
                    break
            if not found:
                beacon_raspberry_result[beacon_number] = 0

        # 将映射结果写入CSV文件
        with open('beacon_raspberry_mapping.csv', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for beacon_number, raspberry_id in beacon_raspberry_result.items():
                csv_writer.writerow([beacon_number, raspberry_id])
        print(beacon_raspberry_result)
        raspberry_data={}
        time.sleep(update_interval)


if __name__ == '__main__':

    update_thread = threading.Thread(target=update_raspberry_data)
    update_thread.daemon = True
    update_thread.start()

    app.run(debug=False, host='0.0.0.0', port=5000)
