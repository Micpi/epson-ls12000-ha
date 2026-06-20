# Epson EH-LS12000 for Home Assistant

Custom integration for Epson EH-LS12000 projectors using ESC/VP21 over TCP or the Epson Web API endpoint.

## Features

- Media player: power and HDMI source selection.
- Sensors: raw/queryable ESC/VP21 values for power, source, mute, color mode, aspect, light source mode, light level, lamp, and lens shift values.
- Switches: A/V mute and on-screen display.
- Selects: source, color mode, aspect, light source mode.
- Number: custom light source brightness level.
- Buttons: lens shift nudges, lens shift reset, recall lens memories 1-10, recall projector memories 1-10.
- Services: `epson_ls12000.send_command`, `epson_ls12000.query_command`, and `epson_ls12000.set_command` for any ESC/VP21 command accepted by the projector firmware.

For most EH-LS12000 installations, use connection type `tcp` with port `3629`.
This mode performs the Epson ESC/VP.net handshake before sending ESC/VP21 commands.
Use connection type `web_api` with port `80` only when the projector Web API is enabled and supported by your firmware.
