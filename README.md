# Epson EH-LS12000 for Home Assistant

Custom Home Assistant integration for Epson EH-LS12000 projectors.

## Installation with HACS

1. In HACS, open **Integrations**.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add this GitHub repository URL.
4. Select category **Integration**.
5. Install **Epson EH-LS12000** and restart Home Assistant.

## Features

- Power and HDMI source selection through a media player entity.
- Sensors for ESC/VP21 values: power, source, mute, OSD, color mode, aspect, light source mode, brightness level, lamp, and lens shift.
- Switches for A/V mute and on-screen display.
- Select entities for source, color mode, aspect, and light source mode.
- Number entity for custom light source brightness level.
- Buttons for lens shift, lens centering, and recall of projector/lens memories.
- Raw ESC/VP21 services for commands supported by the projector firmware.

Enable the Epson Web API in the projector network menu before configuring the integration.
