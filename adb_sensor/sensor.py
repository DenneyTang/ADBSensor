"""Support for ADB Sensor."""
from __future__ import annotations

import logging
import asyncio
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.const import CONF_NAME, CONF_ENTITY_ID, CONF_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

CONF_ADB_COMMAND = "adb_command"
CONF_KEYWORDS = "keywords"

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """设置 ADB Sensor 平台。"""
    sensors = []

    for sensor_config in config.get("sensors", []):
        name = sensor_config.get(CONF_NAME)
        entity_id = sensor_config.get(CONF_ENTITY_ID)
        scan_interval = sensor_config.get(CONF_SCAN_INTERVAL)
        adb_command = sensor_config.get(CONF_ADB_COMMAND)
        keywords = sensor_config.get(CONF_KEYWORDS, {})

        # 处理更新间隔
        if isinstance(scan_interval, timedelta):
            update_interval = scan_interval
        elif scan_interval is not None:
            try:
                update_interval = timedelta(seconds=float(scan_interval))
            except ValueError:
                _LOGGER.error(f"无效的 scan_interval 值 {name}: {scan_interval}。使用默认值 120 秒。")
                update_interval = timedelta(seconds=120)
        else:
            update_interval = timedelta(seconds=120)

        if not adb_command:
            _LOGGER.error(f"{name} 的配置中未指定 ADB 命令模板。")
            continue

        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name=f"adb_sensor_{name}",
            update_method=lambda e_id=entity_id, kw=keywords, cmd=adb_command: update_adb_sensor(hass, e_id, kw, cmd),
            update_interval=update_interval,
        )

        # 首次更新数据
        await coordinator.async_config_entry_first_refresh()

        sensor = ADBSensor(coordinator, name, entity_id, keywords)
        sensors.append(sensor)

        # 设置对 Android TV 实体状态变化的监听
        async_track_state_change_event(hass, [entity_id], sensor.async_state_changed)

    async_add_entities(sensors)

async def update_adb_sensor(hass, entity_id, keywords, adb_command_template):
    """更新 ADB 传感器的状态。"""
    try:
        state = hass.states.get(entity_id)
        attributes = {"state": str(state)}

        if state:
            if state.state in ['unavailable', 'unknown']:
                return 'offline', attributes
            
            grep_keywords = '|'.join(f'{keyword.strip()}' for keyword in keywords.keys())
            attributes["debug_keywords"] = str(keywords.keys())
            command = f"{adb_command_template}".format(grep_keywords=grep_keywords)

            _LOGGER.debug(f"构建的 ADB 命令: {command}")
            attributes['debug_command'] = command

            # 执行 ADB 命令
            await hass.services.async_call(
                'androidtv', 'adb_command', 
                {'entity_id': entity_id, 'command': command}
            )

            # 等待命令执行完成
            await asyncio.sleep(2)

            # 重新获取实体状态
            updated_state = hass.states.get(entity_id)
            if updated_state:
                adb_response = updated_state.attributes.get('adb_response', '').lower()
                attributes['adb_response'] = adb_response

                for keyword, device_name in keywords.items():
                    if keyword.lower() in adb_response:
                        attributes[device_name] = 'on'
                    else:
                        attributes[device_name] = 'off'

                return 'online', attributes
            else:
                return 'offline', {"error": "ADB 命令执行后无法获取更新状态"}
        else:
            return 'offline', {"error": "未找到设备状态"}
    except Exception as e:
        _LOGGER.error(f"更新 ADB 传感器时出错: {e}")
        return 'offline', {"error": str(e)}

class ADBSensor(CoordinatorEntity, SensorEntity):
    """ADB 传感器类。"""

    def __init__(self, coordinator, name, entity_id, keywords):
        """初始化 ADB 传感器。"""
        super().__init__(coordinator)
        self._name = name
        self._entity_id = entity_id
        self._keywords = keywords
        self._attr_unique_id = f"adb_sensor_{entity_id}_{name}"
        self._attr_device_class = SensorDeviceClass.ENUM

    @property
    def name(self):
        """返回传感器的名称。"""
        return self._name

    @property
    def state(self):
        """返回传感器的状态。"""
        return self.coordinator.data[0] if self.coordinator.data else None

    @property
    def extra_state_attributes(self):
        """返回传感器的额外属性。"""
        return self.coordinator.data[1] if self.coordinator.data else {}

    @callback
    def async_state_changed(self, event):
        """处理 Android TV 状态变化。"""
        _LOGGER.debug(f"Android TV 状态变化 {self._name}: {event.data.get('new_state')}")
        self.coordinator.async_request_refresh()