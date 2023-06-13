from django.shortcuts import render
from django.http import HttpResponse
from .models import Devices
from .mqtt_manager import *

broker_ip = "192.168.0.250"

"""Starting page. User can:
- see table of active devices, 
- assign localization to them, 
- interact with Chatbot."""
def index(request):
    # Create mqtt_manager object, so retrieving active devices is possible.
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
    # pass active devices so user can choose to which device assign location
    return render(request, 'app/assign_localization.html')

