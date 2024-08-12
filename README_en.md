# ADB Sensor for Home Assistant

## Introduction
ADB Sensor is a custom component for Home Assistant that allows users to monitor the status of Android TV or other Android devices through ADB (Android Debug Bridge) commands. The main function is to obtain some status of Android devices using adb commands for linkage. The reason for not obtaining the sensors of Android devices by installing the Home Assistant agent is entirely for power saving and not wanting to install redundant APPs.

## Application Scenarios

### Smart Home Automation
When your smartphone connects to a Bluetooth speaker (such as Sonos Era 30), automatically adjust the lighting and temperature settings at home to create a comfortable viewing environment
```yaml
automation:
  - trigger:
      platform: state
      entity_id: sensor.adb_sensor_1
      to: 'online'
  - condition:
      condition: template
      value_template: "{{ state_attr('sensor.adb_sensor_1', 'Sonos Era 30') == 'connected' }}"
  - action:
      - service: light.turn_on
        entity_id: light.living_room
        data:
          brightness: 30
      - service: climate.set_temperature
        entity_id: climate.living_room
        data:
          temperature: 22
``` 

## Features
- Real-time monitoring of device status on Android devices through ADB commands
- Support for monitoring multiple devices and multiple keywords
- Customizable scan intervals
- Provide device online/offline status and connection status of each monitored device

## Installation Method
1. Copy the `adb_sensor` folder to the `custom_components` folder in your Home Assistant configuration directory.
2. Restart Home Assistant.

## Configuration Method
Add the following configuration in the `configuration.yaml` file:

```yaml
sensor:
  - platform: adb_sensor
    sensors:
      - name: "ADB Sensor 1"
        entity_id: media_player.android_tv_1
        scan_interval: 120
        adb_command: "dumpsys input | grep -iE '{grep_keywords}' | sed 's/\x1b[[0-9;]*m//g'"
        keywords:
          'YOUR KEYWORDS1 YOU WANA TO GREP IN ADB_Command': 'YOUR KEYWORDS1'S NAME YOU WANA SHOW IN Attributes'
          'YOUR KEYWORDS2 YOU WANA TO GREP IN ADB_Command': 'YOUR KEYWORDS2'S NAME YOU WANA SHOW IN Attributes'
      - name: "ADB Sensor 2"
        entity_id: media_player.android_tv_2
        scan_interval: 180
        adb_command: "dumpsys bluetooth_manager | grep -iE '{grep_keywords}'"
        keywords:
          'YOUR KEYWORDS1 YOU WANA TO GREP IN ADB_Command': 'YOUR KEYWORDS1'S NAME YOU WANA SHOW IN Attributes'
```

## Configuration Option Explanations
name: The name of the sensor

entity_id: The entity ID of the Android TV or Android device to be monitored. You need to add the Android device in the integration of homeassistant in advance to obtain this entity_id.

scan_interval: Scan interval (seconds)

adb_command: The ADB command template to be executed: The "{grep_keywords}" variable needs to be retained for keyword retrieval; The "sed 's/\x1b[[0-9;]*m//g" is recommended to be retained to remove excess font color special characters to ensure accurate grep hits. Other contents can be written as query commands according to your own situation.

keywords: The keywords to be monitored and the corresponding keyword names. Multiple keywords can be monitored at the same time. The format is: 'Keyword to be searched': 'A keyword name given to this keyword after retrieval for subsequent calls'. 'YOUR KEYWORDS1 YOU WANA TO GREP IN ADB_Command': 'YOUR KEYWORDS1'S NAME YOU WANA SHOW IN Attributes'

## Usage Method
After configuration, Home Assistant will automatically create the corresponding sensor entities. You can add these sensors in the dashboard of Home Assistant or use them in automations.

The sensor status will be displayed as "online" or "offline", indicating the connection status of the Android device. The status of each monitored Bluetooth device will be displayed in the attributes of the sensor.

## Notes
Ensure that ADB debugging is enabled on your Android device and that Home Assistant can successfully connect to the device.
The execution of ADB commands may have a slight impact on device performance. Please adjust the scan interval as needed. 
