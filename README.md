# Smart Home
Smart Home is a web app, that combined with auxiliary software and proper devices provides smart home functionalities.


## Table of Contents
* [General Info](#general-information)
* [Features](#features)
* [Screenshots](#screenshots)
* [Project Components](#project-components)
* [Technologies Used To Implement Core Features](#technologies-used-to-implement-core-features)
* [Typical Scenario](#typical-scenario)
* [Project Status](#project-status)
* [Upcoming Features](#upcoming-features)
* [TODO](#todo)


## General Information
<div style="text-align: justify"> The idea behind this project is to provide smart home software with documentation that will allow anybody to use it. You can create smart home devices that can be monitored and controlled with the web app.
 </div>


## Features
- You can monitor sensors and control actuators using chatbot
- You can assign localization of your devices


## Screenshots
![image](https://github.com/kosmolub01/cwiczenia-z-gitem/assets/72302279/07739a90-ca0b-4ba0-9259-824b7f1c31fa)
![image](https://github.com/kosmolub01/cwiczenia-z-gitem/assets/72302279/7d9ceab3-507c-4ba6-a687-8106ed850a77)
![image](https://github.com/kosmolub01/cwiczenia-z-gitem/assets/72302279/2cefb99f-9e50-4c58-8a8f-ab8640bc1de6)


## Project Components
![image](https://github.com/kosmolub01/cwiczenia-z-gitem/assets/72302279/19860b0e-23a1-445b-9fd0-a1da8ee0f3ce)

This project contains source code of the web app, Chatbot and MQTT Manager. The only additional software that you need to set up is Python with required packages and the MQTT broker.


## Technologies Used To Implement Core Features
- Django
- Eclipse Mosquitto
- Natural Language Toolkit 
- SQLite
- NodeMCU

## Typical Scenario
1. Run the MQTT broker.
2. Run the Django server.
3. Connect your devices to the local network of the broker and the Django server.
4. Monitor and control your devices using the web app.


## Project Status
Project is: _in progress_.


## Upcoming Features
- Split the table to separate active and inactive devices
- Deleting inactive devices only on user command
- Timestamp of last update for every device
- Add colours to indicate how long ago there was an update
- Highlight devices without localization
- Generate graphs of devices values


## TODO
Add documentation with examples explaining how to create devices that can be connected to the web app.


