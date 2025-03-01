# Wiser Home Assistant Integration v3.4.3

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![downloads](https://shields.io/github/downloads/asantaga/wiserHomeAssistantPlatform/latest/total?style=for-the-badge)](https://github.com/asantaga/wiserHomeAssistantPlatform)
[![version](https://shields.io/github/v/release/asantaga/wiserHomeAssistantPlatform?style=for-the-badge)](https://github.com/asantaga/wiserHomeAssistantPlatform)

This repository contains a Home Assistant integration for the awesome Drayton Wiser Heating solution.  This integration works locally with your wiser hub and does not rely on the cloud.

It also supports some European versions of the Wiser Hub under the Schneider Electric brand, including support for lights and blinds.

For the latest version of the Wiser Home Assistant Platform please install via HACS. If you want bleeding edge then checkout the dev branch, or look out for beta releases via HACS. Depending on what you choose you may need to use the Manual Code Installation as described in the Wiki.

**This integration requires a minimum HA version of 2024.2.**

Detailed information about this integration has now been moved to our [Wiki pages](https://github.com/asantaga/wiserHomeAssistantPlatform/wiki)

For more information checkout the AMAZING community thread available on
[https://community.home-assistant.io/t/drayton-wiser-home-assistant-integration/80965](https://community.home-assistant.io/t/drayton-wiser-home-assistant-integration/80965)

## What's New in 3.4?

- Added support for v2 hub
- Added PowerTagE support

## Change log

- v3.4.3
  - Fixed Warning error in logs caused by new HA2024.2 requirement to explicity support Turn On/Off for climate entities (issue [#435](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/435))
  - Bump api to v1.5.7 to fix issue setting lower target temp when in passive mode


- v3.4.2
  - Reverted to using aiohttp for communication and resolved issues caused by HA2023.12
  - Bumped api to v1.5.5
  - Fixed issue where hub communication would error due to command characters in payload (issue [#418](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/418))
  - Updated schedule card to allow hiding of hot water schedule (issue [#415](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/415))
  - Included version in card resources to improve updating of new versions
  - Added more v2 hub features and attributes
  - Improved error handling/logging when hub offline and command is issued

- v3.4.1
  - Corrected error deleting schedule
  - Handle space at end of secret key and prevent error (issue [#409](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/409))
  - Updated schedule card to v1.3.2 - fixed some UI bugs, added ability to hide info and assignments via config (issue [#404](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/404))

- v3.4.0beta
  - Fixed issue in HA 2023.12 with errors reading hub
  - Add PowerTagE support (v2 hub)
  - Add tilt functions for shutters (v2 hub)
  - Fixed issue whereby non ASCII chars are removed in device/room names - issues #396

- v3.3.11
  - Add check for overrides to prevent turning off away modewhen selecting cancel overrides when none exist (Wiser hub bug)
  - Correct sensor device class and native values to fix history not displaying issue in HA 2023.11

- v3.3.10
  - bump api to v1.3.8 to fix passive mode error if room trv/roomstat goes offline
  - make battery sensor unavailable if no battery info provided by hub (previously showed 0%)
  - add uptime and last reset reason to Hub signal sensor
  - make LTS sensors normal sensors instead of diagnostic sensors so they show in Area card - issue #381
  - save schedule service will now create directory for file if it doesn't exist
  - correct relative modulation level magnitude

- v3.3.9
  - bump api to v1.3.5 to fix warning regarding async not awaited on extra config

- v3.3.8
  - Fix extra key issue preventing loading on HA 2023.8.0 and above

- v3.3.7
  - Fix issue with zigbee card unable to save layout in stack card
  - Updated libraries for schedule card to fix security vulnerabilities
  - Fix colours missing on on/off schedule in schedule card
  - Minor UI improvements in schedule card

- v3.3.6
  - Improved Zigbee network card

- v3.3.5
  - Fix for eroneous current temp if lost signal with TRV - issue #369
  - Reduced log error level for failed update form hub to warning

A full change log can be seen on our wiki [here](https://github.com/asantaga/wiserHomeAssistantPlatform/wiki/Full-Change-Log)
