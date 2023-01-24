#!/bin/bash

source venv/bin/activate
cd ..
python draft_space.py
cd scripts
deactivate
