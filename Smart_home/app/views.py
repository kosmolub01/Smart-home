from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Devices
from .mqtt_manager import *
from .chatbot import *

broker_ip = "192.168.1.105"

"""Starting page. User can:
- see table of active devices, 
- assign localization to them, 
- interact with Chatbot."""
def index(request):
    # Create MqttManager object, so retrieving active devices is possible.
    manager = MqttManager(broker_ip)

    # Get list of active devices (it's a list of tuples) from MQTT Manager.
    active_devices = manager.get_devices_list()

    print("active devices", active_devices)

    # Get list of devices from server-side DB.
    devices = Devices.objects.all()

    # List of currently connected devices. Devices present on that list are not going to be deleted with server-side DB update.
    current_devices = []

    # Assign to every device, so devices have ordinal number.
    number = 1

    # Compare devices from MQTT Manager and devices from server-side DB.
    # Update server-side DB with new devices. Update server-side DB already present devices (field 'value').
    # The whole point of it is to update the table of devices, seen by the user, and also to remember assigned localizations of devices.
    for active_device in active_devices:
        # Retrieve the device based on mac and device_id.
        obj, created = Devices.objects.get_or_create(mac = active_device[1], device_id = active_device[2],
                                                     defaults={#'pk' : number,
                                                               'name' : active_device[0],
                                                               'mac': active_device[1],
                                                               'device_id': active_device[2],
                                                               'type': active_device[3],
                                                               'value': active_device[4]})

        # If the device is already present in the server-side DB, then update only 'value' field.
        if not created:
            #obj.pk = number
            obj.value = active_device[4]

        current_devices.append(obj)

        number = number + 1

    print("current_devices", current_devices)

    # Update server-side DB.
    Devices.objects.all().delete()
    print("after delete ", Devices.objects.all())
    for device in current_devices:
        device.save()

    # Pass list of connected devices to HTML.
    context = {'devices_list': current_devices}
    return render(request, 'app/index.html', context)

"""Assigning  localization page."""
def assign_localization(request):
    # Get list of devices from server-side DB, so user can choose to which device assign location.
    devices = Devices.objects.all()
    print("in assign_localization devices", devices)
    context = {'devices_list': devices}
    return render(request, 'app/assign_localization.html', context)

"""Save assigned localizations in the DB."""
def save_assigned_localizations(request):
    localizations = request.GET.get('localizations', '').split(',')
    
    devices = Devices.objects.all()

    i = 0

    for device in devices:
        print("localization: ", localizations[i])
        device.localization = localizations[i]
        device.save()
        i = i + 1

    return HttpResponse(status=200)

"""Handle message passed to the Chatbot."""
def message_to_the_chatbot(request):
    # Get the value of the 'message' parameter from the GET request.
    message = request.GET.get('message')  

    # Create a response with parameter.
    response = HttpResponse(status=200)

    # Init Chatbot with the list of tuples (device, locations). Make sure the device has assigned localization.
    devices = Devices.objects.values('name', 'localization')
    # Transform list of dictonairies into list of tuples.
    devices = [(device['name'], device['localization']) for device in devices]
    # Init Chatbot
    chatbot = Chatbot(devices)

    # Send message to Chatbot.
    chatbot_response = chatbot.send_message(message)

    # Detect what Chatbot returned. 
    # If it is a list with command info, react accordingly (pass command to MQTT manager, display 'Command was sent.').
    # If it is regular string, just display it.
    if type(chatbot_response) is list:

        print('chatbot_response is list')

        #Get the device.
        device = Devices.objects.get(name=chatbot_response[1], localization=chatbot_response[2])

        # Check what kind of command was sent by user.
        if chatbot_response[0] == 'value':
            # User wants to check value of the device. 
            # Create response.
            chatbot_response = 'Value of ' + device.name + ' in ' + device.localization + ': ' + device.value + '.'
        else:
            # User wants to set the value of the device.
            # Create MqttManager object, so passing command to the device is possible.
            manager = MqttManager(broker_ip) 
            # Distinguish whether user wants to set particular value or only turn on / off the device.
            if chatbot_response[0] == 'set to':
                # Set to particular value.
                print(device.mac, device.device_id, chatbot_response[3], 'set to')
                manager.set_value(device.mac, device.device_id, chatbot_response[3])
            else:
                # Turn on / off etc.
                print('Turn on / off')
                manager.set_value(device.mac, device.device_id, chatbot_response[0])
            
            chatbot_response = 'Command was sent.'

    # Set parameter in the response headers.
    response['chatbot_response'] = chatbot_response 

    # Set the response content
    response.content = 'Response Content'

    return response

"""Update the table content."""
def update_the_table_content(request):
    # Create MqttManager object, so retrieving active devices is possible.
    manager = MqttManager(broker_ip)

    # Get list of active devices (it's a list of tuples) from MQTT Manager.
    active_devices = manager.get_devices_list()

    print("active devices", active_devices)

    # Get list of devices from server-side DB.
    devices = Devices.objects.all()

    # List of currently connected devices. Devices present on that list are not going to be deleted with server-side DB update.
    current_devices = []

    # Assign to every device, so devices have ordinal number.
    number = 1

    # Compare devices from MQTT Manager and devices from server-side DB.
    # Update server-side DB with new devices. Update server-side DB already present devices (field 'value').
    # The whole point of it is to update the table of devices, seen by the user, and also to remember assigned localizations of devices.
    for active_device in active_devices:
        # Retrieve the device based on mac and device_id.
        obj, created = Devices.objects.get_or_create(mac = active_device[1], device_id = active_device[2],
                                                     defaults={#'pk' : number,
                                                               'name' : active_device[0],
                                                               'mac': active_device[1],
                                                               'device_id': active_device[2],
                                                               'type': active_device[3],
                                                               'value': active_device[4]})

        # If the device is already present in the server-side DB, then update only 'value' field.
        if not created:
            #obj.pk = number
            obj.value = active_device[4]

        current_devices.append(obj)

        number = number + 1

    print("current_devices", current_devices)

    # Generate HTML table with current devices.
    table = '<tbody>'

    # Device ordinal number within the table.
    device_ordinal_number = 1

    # Update server-side DB and table.
    Devices.objects.all().delete()
    print("after delete ", Devices.objects.all())
    for device in current_devices:
        device.save()
        table += """<tr>
                        <td>""" + str(device_ordinal_number) + """</td>
                        <td>""" + device.name + """</td>
                        <td>""" + device.mac  +"""</td>
                        <td>""" + str(device.device_id)  +"""</td>
                        <td>""" + device.localization +"""</td>
                        <td>""" + device.type + """</td>
                        <td>""" + device.value + """</td>
                    </tr>"""
        
        device_ordinal_number += 1

    table += '</tbody>'

    print(table)

    # Create a response with parameter.
    response = HttpResponse(table)

    return response