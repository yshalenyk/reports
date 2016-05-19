#!/usr/bin/bash

comm -12 <( sort $1 ) <( sort $2 ) | head -n -1 | cut -f1 -d","
