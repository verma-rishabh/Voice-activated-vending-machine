## snips-app-kiosk-py
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/snipsco/snips-app-relay-switch/blob/master/LICENSE)

Action code for the ***kiosk*** bundle. It uses matrix creator on Raspberry Pi.

## Usage
***```"Hey snips, I would like to order a burger"```***

***```"I am allergic to peanuts"```***

## Installation

### Install with assistant
1. Create a Snips account ***[here](https://console.snips.ai/?ref=Qr4Gq17mkPk)***
2. Create an English assistant in ***[Snips console](https://console.snips.ai/)***
3. Add APP ***Kiosk*** (Available soon)
4. Deploy assistant by ***[Sam](https://snips.gitbook.io/documentation/console/deploy-your-assistant)***
5. (On Pi) Add permission to `_snips-skill` user to access gpio: `sudo usermod -a -G i2c,spi,gpio,audio _snips-skills`
6. (On Pi) Restart snips-skill-server: `sudo systemctl restart snips-skill-server`
7. Have fun ***;-)***

### Install only action
```
sam install actions -g https://github.com/verma-rishabh/snips-app-kiosk-py
```
## Configuration

### MQTT

| Config | Description | Value | Default |
| --- | --- | --- | --- |
| `mqtt_host` | MQTT host name | `<ip address>`/`<hostname>` | `localhost` |
| `mqtt_port` | MQTT port number | `<mqtt port>` | `1883` |

> ***To make satellite work correctly, please change here***

### Device Info

| Config | Description | Value | Default |
| --- | --- | --- | --- |
| `site_id` | Snips device ID | Refering to the actual `snips.toml` | `default` |

> ***To make satellite work correctly, please change here***




## Copyright

This library is as Open Source software. See [LICENSE](https://github.com/verma-rishabh/snips-app-kiosk-py/blob/master/LICENSE) for more information.
