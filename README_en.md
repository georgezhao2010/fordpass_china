# FordPass China

[简体中文](https://github.com/georgezhao2010/fordpass_china/blob/main/README.md) | English

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

The Ford FordPass integration components for Home Assistant.

If your Ford vehicles could access via FordPass App, This component allow you control your vehicle or get vehicle details in Home Assistant.
To use this component, you need a FordPass account, if you do not have one, register one in FordPass App.

**attention: This compontent can be used inside china mainland only**

# Features

This component supports more vehicle details than officially FordPass App.

## Remote controls
- Start/stop vehicle
- Lock/unlock vehicle

## Vehicle details
- Last know GPS coordinates
- Fuel level
- Odometer
- Distance to empty
- Oil Life
- Ignition status
- Doors status
- Windows status
- Tires Pressure
- Battery health and voltage

# Installtion
Use HACS and Install as a custom repository, or or copy all files in `custom_components/fordpass_china` from [Latest Release](https://github.com/georgezhao2010/fordpass_china/releases/latest) to your `<Home Assistant config folder>/custom_components/fordpass_china` in Home Assistant manually. Restart HomeAssistant.

# Configuration
Add FordPass China component in Home Assistant integrations page, and enter your FordPass username and password.


