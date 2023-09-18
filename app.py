import sqlite3
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import time
app = Flask(__name__)
# Create a SQLite database and connect to it
conn = sqlite3.connect('raspberry_data.db')

conn.execute('''CREATE TABLE IF NOT EXISTS mac_tracking
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                mac TEXT,
                location INTEGER,
                appearance_time DATETIME,
                disappearance_time DATETIME)''')
conn.close()

# Dictionary to store data for each Raspberry Pi
raspberry_data = {}
last_time = time.time()
@app.route('/')
def index():
    return render_template('index.html', raspberry_data=raspberry_data)



@app.route('/update/<int:raspberry_id>', methods=['POST'])
def update_data(raspberry_id):
    global raspberry_data, last_time
    data = request.get_json()
    # print(data,raspberry_id)
    raspberry_data[raspberry_id] = data

    mac_data = {}
    for key, values in raspberry_data.items():
        for mac, signal_strength in values.items():
            if mac not in mac_data:
                mac_data[mac] = {}
            mac_data[mac][key] = signal_strength

    # 刪除重複的MAC資料，保留訊號強度較大的資料
    for mac, signal_data in mac_data.items():
        if len(signal_data) > 1:
            max_key = max(signal_data, key=signal_data.get)
            for key in signal_data.keys():
                if key != max_key:
                    raspberry_data[key].pop(mac)
                    # print(raspberry_data)
        

    return jsonify(success=True)


@app.route('/data/<int:raspberry_id>')
def get_data(raspberry_id):
    print("raspberry_data",raspberry_data)
    conn = sqlite3.connect('raspberry_data.db')
    cursor = conn.cursor()

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    now_time=time.time()
    for location, mac_data in raspberry_data.items():
        for mac, strength in mac_data.items():
            # 檢查資料庫是否已經有這個mac資料
            cursor = conn.execute("SELECT * FROM mac_tracking WHERE mac = ? ORDER BY rowid DESC LIMIT 1", (mac,))
            existing_data = cursor.fetchone()
            print('existing_data_test',existing_data)
            if existing_data:
                print(existing_data)
                # 如果mac的location有變化，更新disappearance_time
                if existing_data[2] != location:
                    conn.execute(
                        "UPDATE mac_tracking SET disappearance_time = ? WHERE mac = ? AND disappearance_time IS NULL",
                        (current_time, mac))
                    #print('update')
                    conn.commit()
                    insert_data = (mac, location, current_time, None)
                    conn.execute(
                        "INSERT INTO mac_tracking (mac, location, appearance_time, disappearance_time) VALUES (?, ?, ?, ?)",
                        insert_data)
                    #print('insert')
                    last_time=time.time()
                    conn.commit()
                elif existing_data[4] != None:
                    insert_data = (mac, location, current_time, None)
                    conn.execute(
                        "INSERT INTO mac_tracking (mac, location, appearance_time, disappearance_time) VALUES (?, ?, ?, ?)",
                        insert_data)
                    print('insert')
                        
            else:
                # 新增一筆新的資料
                insert_data = (mac, location, current_time, None)
                conn.execute(
                    "INSERT INTO mac_tracking (mac, location, appearance_time, disappearance_time) VALUES (?, ?, ?, ?)",
                    insert_data)
                #print('insertblblblba')
                last_time=time.time()
                conn.commit()

    # 檢查是否有mac在新的一筆dict中消失了
    cursor = conn.execute("SELECT mac FROM mac_tracking WHERE disappearance_time IS NULL")
    existing_macs = set(row[0] for row in cursor.fetchall())

    for mac in existing_macs:
        if mac not in {mac for mac_data in raspberry_data.values() for mac in mac_data.keys()}:
            # mac在新的一筆dict中消失，補充disappearance_time
            conn.execute("UPDATE mac_tracking SET disappearance_time = ? WHERE mac = ? AND disappearance_time IS NULL",
                        (current_time, mac))
            print('update')
            conn.commit()

        # Commit the changes and close the database connection
    conn.commit()
    conn.close()

    return jsonify(raspberry_data.get(raspberry_id, {}))
    
@app.route('/database')
def get_database():
    conn = sqlite3.connect('raspberry_data.db')
    cursor = conn.cursor()
    cursor = conn.execute("SELECT * FROM mac_tracking")
    existing_data = cursor.fetchall()
    #print(existing_data)
    return jsonify(existing_data)
    


if __name__ == '__main__':
    from gevent import pywsgi
    last_time=time.time()
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    server.serve_forever()
    # app.run(debug=True, host='0.0.0.0',port=5000)
