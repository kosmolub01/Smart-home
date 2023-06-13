import paho.mqtt.client as mqtt
import sqlite3
from datetime import datetime, timedelta

# Name of DB file.
db_file = "connected_devices.db"

# Exceptions classes.
class ConnectionToMqttBrokerException(Exception):
   def __init__(self):
      pass

   def __str__(self):
      message = "MQTT Manager could not connect to the broker."
      return message
   
class DbSetUpException(Exception):
   def __init__(self):
      pass

   def __str__(self):
      message = "MQTT Manager could not set up the DB."
      return message
   
class DbUpdateException(Exception):
   def __init__(self):
      pass

   def __str__(self):
      message = "MQTT Manager could not update the DB."
      return message
   
class DbReadException(Exception):
   def __init__(self):
      pass

   def __str__(self):
      message = "MQTT Manager could not read from the DB."
      return message
   
# Callback function for when a connection is established with the broker.
def on_connect(client, userdata, flags, rc):
    if rc != 0:
        raise ConnectionToMqttBrokerException

    # Subscribe to the topics of interest.
    client.subscribe("mqtt_manager")

# Callback function for when a message is received. 
# If message was on 'mqtt_manager' topic, then update the DB.
# TODO 
# - Is there message filtering required, so only messages with valid syntax are passed thru? 
def on_message(client, userdata, msg):
    if msg.topic == "mqtt_manager":
        msg_elements = msg.payload.decode().split(';')

        try:
            # Connect to the database.
            conn = sqlite3.connect(db_file)

            # Create a cursor.
            cursor = conn.cursor()

            # Get the current timestamp.
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            msg_elements.append(current_time)
            msg_elements.append(msg_elements[1])
            msg_elements.append(msg_elements[2])

            # If message comes from sensor device.
            if msg_elements[3] == "Sensor":
                #print("Sensor")
                sql_update_table = """UPDATE connected_sensors SET name=?, mac=?, device_id=?, 
                            type=?, value=?, timestamp=? WHERE mac=? AND device_id=?"""
                
                sql_insert = """INSERT INTO connected_sensors (name, mac, device_id, 
                            type, value, timestamp) VALUES (?, ?, ?, ?, ?, ?)"""
                
            # If message comes from actuator device.
            elif msg_elements[3] == "Actuator": 
                
                #print("Actuator")
                sql_update_table = """UPDATE connected_actuators SET name=?, mac=?, device_id=?, 
                            type=?, value=?, value_to_set_topic=?, timestamp=? WHERE mac=? AND device_id=?"""
                    
                sql_insert = """INSERT INTO connected_actuators (name, mac, device_id, 
                            type, value, value_to_set_topic, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)"""

            # Execute the update statement.

            cursor.execute(sql_update_table, msg_elements)

            # Check if the update affected any rows.
            if cursor.rowcount == 0:
    
                # Remove last two elements from the list (mac and device_id)
                del msg_elements[-2:]

                # Execute the insert statement.

                cursor.execute(sql_insert, msg_elements)

            conn.commit()
 
            # Close the cursor and the database connection.
            cursor.close()
            conn.close()
        except:
            raise DbUpdateException

    #print(f"Received message '{msg.payload.decode()}' on topic '{msg.topic}'")
        

class MqttManager:
    def __init__(self, broker_ip, broker_port=1883, keepalive=60):
        self._set_up_the_db()
        self._set_up_mqtt_client()
        self._connect_to_the_broker(broker_ip, broker_port, keepalive)

    # Get list (list of tuples) of active devices (sensors and actuators).
    # For each device its name, mac, device id, value and type are returned.
    def get_devices_list(self):
        self._remove_inactive_devices_form_db(20)
        
        try:
            # Connect to the database.
            conn = sqlite3.connect(db_file)

            # Create a cursor.
            cursor = conn.cursor()

            # Select all rows from a table
            cursor.execute('SELECT name, mac, device_id, type, value FROM connected_sensors')

            # Fetch all rows as a list of tuples
            sensors = cursor.fetchall()

            # Select all rows from a table
            cursor.execute('SELECT name, mac, device_id, type, value FROM connected_actuators')

            # Fetch all rows as a list of tuples
            actuators = cursor.fetchall()

            devices = sensors + actuators

            # Close the cursor and the database connection.
            cursor.close()
            conn.close()
        except:
            raise DbReadException
        
        return devices
    
    # Set device value. Raises an error for incorrect parameters.
    def set_value(self, mac, device_id, value):
        # Make sure the device is the actuator (so setting value makes sense).
        try:
            # Connect to the database.
            conn = sqlite3.connect(db_file)

            # Create a cursor.
            cursor = conn.cursor()

            # Select.
            cursor.execute('SELECT value_to_set_topic FROM connected_actuators WHERE mac=? AND device_id=?', (mac, device_id))

            # Fetch the topic name.
            topic = cursor.fetchone()[0]

            # Send message in given topic
            self.client.publish(topic, str(value))

            # Close the cursor and the database connection.
            cursor.close()
            conn.close()
        except:
            raise DbReadException

    # Connects to the broker. Blocks until connection is established.
    def _connect_to_the_broker(self, broker_ip, broker_port, keepalive):
        try:
            self.client.connect(broker_ip, broker_port, keepalive)
        except:
            # 'from None' suppresses exceptions inside exception
            raise ConnectionToMqttBrokerException from None

        # Start the network loop to handle incoming messages (it is also needed for connecting to the broker).
        self.client.loop_start()

        # Wait for client to connect to the broker.
        while not self.client.is_connected():
            pass

    def _set_up_mqtt_client(self):
        # Create an MQTT client instance (MqttManager acts as a MQTT client).
        self.client = mqtt.Client()

        # Set up the callback functions.
        self.client.on_connect = on_connect
        self.client.on_message = on_message
    
    # In case there is no DB or table, it creates them.
    def _set_up_the_db(self):
        
        try:
            # Connect to the database.
            conn = sqlite3.connect(db_file)

            # Create a cursor.
            cursor = conn.cursor()

            # Create sensors table.
            sql_create_table = """ CREATE TABLE IF NOT EXISTS connected_sensors (
                                            id integer PRIMARY KEY AUTOINCREMENT,
                                            name text NOT NULL,
                                            mac text,
                                            device_id integer,
                                            type text,
                                            value text,
                                            timestamp DATE DEFAULT (datetime('now','localtime'))
                                        ); """

            cursor.execute(sql_create_table)

            # Create actuators table.
            sql_create_table = """ CREATE TABLE IF NOT EXISTS connected_actuators (
                                            id integer PRIMARY KEY AUTOINCREMENT,
                                            name text NOT NULL,
                                            mac text,
                                            device_id integer,
                                            type text,
                                            value text,
                                            value_to_set_topic text,
                                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                        ); """

            cursor.execute(sql_create_table)

            """sql_drop_table = " DROP TABLE connected_devices; "

            cursor.execute(sql_drop_table)"""

            # Close the cursor and the database connection.
            cursor.close()
            conn.close()
        except:
            raise DbSetUpException
    
    # Removes inactive devices form DB. 
    # Devices inactive for longer than 'max_time_of_inactivity' (in seconds) are removed.
    def _remove_inactive_devices_form_db(self, max_time_of_inactivity):
        try:
            # Connect to the database.
            conn = sqlite3.connect(db_file)

            # Create a cursor.
            cursor = conn.cursor()

            # Define the timestamp threshold for deleting old records.
            timestamp_threshold = datetime.now() - timedelta(seconds=max_time_of_inactivity)

            # Execute the DELETE statement.
            sql_delete = "DELETE FROM connected_sensors WHERE timestamp < ?"
            cursor.execute(sql_delete, (timestamp_threshold,))

            sql_delete = "DELETE FROM connected_actuators WHERE timestamp < ?"
            cursor.execute(sql_delete, (timestamp_threshold,))

            conn.commit()
 
            # Close the cursor and the database connection.
            cursor.close()
            conn.close()
        except:
            raise DbUpdateException







