#!/bin/bash
# sendet alle 30s ein HDMI-CEC “on” an den TV (addr 0)
while true; do
  echo "on 0" | cec-client -s -d 1 >/dev/null 2>&1
  sleep 30
done
