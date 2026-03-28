# gstack-listen

> gstack has eyes (`/browse`) but no ears. This adds `/listen` — real-time system audio capture via PipeWire/PulseAudio for Linux environments.

A [gstack](https://github.com/garrytan/gstack) skill for capturing system audio on Linux.

## Quick start

```bash
python3 capture.py          # 5 seconds -> captured.wav
python3 capture.py 10       # 10 seconds -> captured.wav
python3 capture.py 5 out.wav
```

## How it works

`capture.py` auto-detects the audio backend:

| Environment | Backend | Tool | Status |
|---|---|---|---|
| Ubuntu 24.04+ | PipeWire | `pw-record` | Tested |
| WSL2 Ubuntu | PulseAudio | `parec` | Tested |
| Older Ubuntu / Debian | PulseAudio | `parec` | Supported |

## Test results

**PipeWire (Ubuntu 24.04 Live, real hardware):**
```
PipeWire 1.0.5
Server Name: PulseAudio (on PipeWire 1.0.5)
Captured: 574,032 bytes (5 seconds)
```

**PulseAudio (WSL2 Ubuntu 24.04):**
```
Server Name: pulseaudio
Default Sink: RDPSink, 44100Hz
Captured: 892,628 bytes (5 seconds)
```

## Requirements

- Linux (Ubuntu 24.04 recommended)
- Python 3.6+
- PipeWire (`pw-record`) or PulseAudio (`parec`, `pactl`)

## License

MIT
