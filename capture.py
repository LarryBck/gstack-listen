#!/usr/bin/env python3
"""
gstack /listen — System audio capture for Linux.
Supports PipeWire (pw-record) and PulseAudio (parec) with auto-detection.

Tested on:
- Ubuntu 24.04 native (PipeWire) — VERIFIED with real audio playback
- Native Linux with PulseAudio — Supported

NOTE: WSL2 is NOT supported. RDPSink cannot capture Windows system audio.
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


def get_running_sink_id():
    """Find the RUNNING sink ID for PipeWire capture."""
    try:
        result = subprocess.run(
            ["pactl", "list", "short", "sinks"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if "RUNNING" in line:
                    parts = line.split("\t")
                    if len(parts) >= 1:
                        return parts[0].strip()
            # No RUNNING sink, try first available
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) >= 1:
                        return parts[0].strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
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
            # Prefer RUNNING or IDLE monitor
            for state in ["RUNNING", "IDLE"]:
                for line in result.stdout.strip().split("\n"):
                    if ".monitor" in line and state in line:
                        parts = line.split("\t")
                        if len(parts) >= 2:
                            return parts[1]
            # Fallback: any monitor
            for line in result.stdout.strip().split("\n"):
                if ".monitor" in line:
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        return parts[1]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def capture_pipewire(output_file, duration):
    """Capture audio using pw-record with --target sink_id."""
    sink_id = get_running_sink_id()
    if sink_id is None:
        print("ERROR: No sink found for PipeWire capture.")
        return False

    print("Backend: PipeWire (pw-record --target {})".format(sink_id))
    print("Capturing {} seconds -> {}".format(duration, output_file))

    proc = subprocess.Popen(["pw-record", "--target", sink_id, output_file])
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
    """Capture audio using parec with monitor source."""
    print("Backend: PulseAudio (parec)")
    print("Monitor source: {}".format(monitor_source))
    print("Capturing {} seconds -> {}".format(duration, output_file))

    proc = subprocess.Popen([
        "parec",
        "--format=s16le",
        "--rate=48000",
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
        success = capture_pipewire(output_file, duration)
    elif backend == "pulseaudio":
        monitor = get_monitor_source()
        if monitor is None:
            print("ERROR: No monitor source found.")
            sys.exit(1)
        success = capture_pulseaudio(output_file, duration, monitor)

    if success:
        print("SUCCESS: Audio captured. Play with: aplay {}".format(output_file))
    else:
        print("FAILED: No audio captured. Make sure audio is playing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
