#!/bin/bash

# Script to restore monitor brightness
ddcutil --bus=14 setvcp 10 100
ddcutil --bus=15 setvcp 10 100
