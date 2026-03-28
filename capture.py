#!/usr/bin/env python3
"""
gstack /listen — System audio capture for Linux.
Supports PipeWire (pw-record) and PulseAudio (parec) with auto-detection.
"""

import subprocess
import sys
import os
import signal
import time


def detect_audio_backend():
    """Detect whether PipeWire or PulseAudio is running."""
    try:
        result = subprocess.run(
            ["pw-cli", "info", "0"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            return "pipewire"
    except FileNotFoundError:
        pass
    except subprocess.TimeoutExpired:
        pass

    try:
        result = subprocess.run(
            ["pactl", "info"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            if "PipeWire" in result.stdout:
                return "pipewire"
            return "pulseaudio"
    except FileNotFoundError:
        pass
    except subprocess.TimeoutExpired:
        pass

    return None


def get_monitor_source():
    """Find the monitor source for PulseAudio capture."""
    try:
        result = subprocess.run(
            ["pactl", "list", "short", "sources"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if ".monitor" in line:
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        return parts[1]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def capture_pipewire(output_file, duration):
    """Capture audio using pw-record."""
    print("Backend: PipeWire (pw-record)")
    print("Capturing {} seconds -> {}".format(duration, output_file))

    proc = subprocess.Popen(["pw-record", output_file])

    try:
        time.sleep(duration)
    except KeyboardInterrupt:
        pass

    proc.send_signal(signal.SIGINT)
    proc.wait(timeout=5)

    size = os.path.getsize(output_file)
    print("Captured {} -> {} bytes".format(output_file, size))

    if size <= 44:
        print("WARNING: Only WAV header captured. No audio was playing.")
        return False
    return True


def capture_pulseaudio(output_file, duration, monitor_source):
    """Capture audio using parec."""
    print("Backend: PulseAudio (parec)")
    print("Monitor source: {}".format(monitor_source))
    print("Capturing {} seconds -> {}".format(duration, output_file))

    proc = subprocess.Popen([
        "parec",
        "--format=s16le",
        "--rate=44100",
        "--channels=2",
        "-d", monitor_source,
        "--file-format=wav",
        output_file
    ])

    try:
        time.sleep(duration)
    except KeyboardInterrupt:
        pass

    proc.send_signal(signal.SIGINT)
    proc.wait(timeout=5)

    size = os.path.getsize(output_file)
    print("Captured {} -> {} bytes".format(output_file, size))

    if size <= 44:
        print("WARNING: Only WAV header captured. No audio was playing.")
        return False
    return True


def main():
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    output_file = sys.argv[2] if len(sys.argv) > 2 else "captured.wav"

    backend = detect_audio_backend()

    if backend is None:
        print("ERROR: No audio backend found. Install PipeWire or PulseAudio.")
        sys.exit(1)

    if backend == "pipewire":
        capture_pipewire(output_file, duration)
    elif backend == "pulseaudio":
        monitor = get_monitor_source()
        if monitor is None:
            print("ERROR: No monitor source found.")
            sys.exit(1)
        capture_pulseaudio(output_file, duration, monitor)


if __name__ == "__main__":
    main()
