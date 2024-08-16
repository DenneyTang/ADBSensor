
# ADB Sensor for Home Assistant

## 简介
ADB Sensor 是一个用于 Home Assistant 的自定义组件，它允许用户通过 ADB (Android Debug Bridge) 命令监控 Android TV 或其他 Android 设备上的状态。主要作用是使用adb命令获取安卓设备的一些状态，用于联动。之所以不是通过安装Home Assistant agent获取安卓设备的传感器，完全是为了省电，不想装多余的APP。

## 应用场景

### 智能家居自动化
   当您的智能手机连接到蓝牙音箱(如Sonos Era 30)时,自动调整家中的灯光和温度设置,创造舒适的观影环境
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

## 功能特点
- 通过 ADB 命令实时监控 Android 设备上的设备状态
- 支持多个设备和多个关键词的监控
- 可自定义扫描间隔
- 提供设备在线/离线状态以及每个监控设备的连接状态

## 安装方法
1. 将 `adb_sensor` 文件夹复制到您的 Home Assistant 配置目录下的 `custom_components` 文件夹中。
2. 重启 Home Assistant。

## 配置方法
在 `configuration.yaml` 文件中添加以下配置：

```yaml
sensor:
  - platform: adb_sensor
    sensors:
      - name: "ADB Sensor 1"
        entity_id: media_player.android_tv_1
        scan_interval: 120
        adb_commands
          - command: "dumpsys input | grep -iE '{grep_keywords}' | sed 's/\x1b[[0-9;]*m//g'"
            keywords:
               'YOUR KEYWORDS1 YOU WANA TO GREP IN ADB_Command': 'YOUR KEYWORDS1'S NAME YOU WANA SHOW IN Attributes'
               'YOUR KEYWORDS2 YOU WANA TO GREP IN ADB_Command': 'YOUR KEYWORDS2'S NAME YOU WANA SHOW IN Attributes'
          - command: "dumpsys bluetooth_manager | grep -iE '{grep_keywords}'"
            keywords:
               'YOUR KEYWORDS3 YOU WANA TO GREP IN ADB_Command': 'YOUR KEYWORDS3'S NAME YOU WANA SHOW IN Attributes'

      - name: "Mate30Pro_ADBSensor"
        entity_id: media_player.android_tv
        scan_interval: 30
        adb_commands:
          - command: "dumpsys input | grep -iE '{grep_keywords}' | sed 's/\x1b[[0-9;]*m//g'"
            keywords:
              'UniqueId:7': 'WatchGT2'
          - command: "dumpsys media_session | sed -n '/QQMusicMediaSession.*/,/state=PlaybackState/p' | grep 'state=PlaybackState.*{grep_keywords}' | grep -o 'state=PlaybackState.*' | sed 's/\x1b[[0-9;]*m//g'"
            keywords:
              'state=3': 'QQMusic'


```

## 配置选项说明
name: 传感器的名称

entity_id: 要监控的 Android TV 或 Android 设备的实体 ID，需要你提前在homeassistant的集成中将Android设备添加后，获取该entity_id。

scan_interval: 扫描间隔（秒）

command: 要执行的 ADB 命令模板：其中”{grep_keywords}“变量需要保留用于检索关键字；其中"sed 's/\x1b[[0-9;]*m//g"建议保留用于去除多余的字体颜色特殊字符确保grep命中准确。其他内容可以依据自己情况编写查询命令。

keywords: 要监控的关键词和对应的关键字名称。可以同时监控多个关键字，格式为：‘待搜索的关键字’: '检索后给这个关键字一个关键字显示到属性中供后续调用'。'YOUR KEYWORDS1 YOU WANA TO GREP IN ADB_Command': 'YOUR KEYWORDS1'S NAME YOU WANA SHOW IN Attributes'

## 使用方法
配置完成后，Home Assistant 将自动创建对应的传感器实体。您可以在 Home Assistant 的仪表板中添加这些传感器，或在自动化中使用它们。

传感器状态将显示为 "online" 或 "offline"，表示 Android 设备的连接状态。每个监控的蓝牙设备的状态将显示在传感器的属性中。

## 注意事项
确保您的 Android 设备已启用 ADB 调试，并且 Home Assistant 能够成功连接到该设备。
ADB 命令的执行可能会对设备性能产生轻微影响，请根据需要调整扫描间隔。
