# ZEOS-V2

ZEOS is a minimal operating system for IoT devices based on micropython

## Features
- [x] File System
- [x] WiFi Drivers
- [x] TCP
- [ ] MQTT
- [x] Simple RPC Implementation
- [x] Device Drivers
- [x] Concurrency, Multitasking and Process Scheduling
- [x] Memory Manager
- [x] Python Shell
- [x] Device Config
- [ ] Cron Jobs
- [ ] OTA Firmware Update
- [x] Python Shell
- [x] Simple Access Control

## Run
1. Install MicroPython [rshell](https://github.com/dhylands/rshell)
```bash
pip3 install rshell
```

2. Upload ZEOS File System on Target Device Using Helper Script **scripts/init_fs.py**
```bash
# init_fs.py <module_name> [ul: update lib | (sl): skip lib]
init_fs.py switch ul
```
