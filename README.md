# gstack-listen

> gstack has eyes (`/browse`) but no ears. This adds `/listen` — real-time system audio capture via PipeWire/PulseAudio for Linux environments.

A [gstack](https://github.com/garrytan/gstack) skill for capturing system audio on Linux.

## Quick start

```
python3 capture.py          # 5 seconds -> captured.wav
python3 capture.py 10       # 10 seconds -> captured.wav
python3 capture.py 5 out.wav
```

## How it works

`capture.py` auto-detects the audio backend:

| Environment | Backend | Tool | Status |
|---|---|---|---|
| Ubuntu 24.04+ | PipeWire | `pw-record --target` | Verified |
| Older Ubuntu / Debian | PulseAudio | `parec` | Supported |

> **Note:** WSL2 is not supported. RDPSink cannot capture Windows system audio.

## Test results

**PipeWire (Ubuntu 24.04, real hardware):**

```
PipeWire 1.0.5
Server Name: PulseAudio (on PipeWire 1.0.5)
pw-record --target 50 → captured and verified with audio playback
```

## Requirements

- Linux (Ubuntu 24.04 recommended)
- Python 3.6+
- PipeWire (`pw-record`) or PulseAudio (`parec`, `pactl`)

## License

MIT
