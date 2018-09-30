#!/bin/bash

filename="game/assets/karte-madarice.svg"
destination="game/assets/cards"
dpi=150

# Directory
mkdir -p $destination

# Herc
for id in herc-7 herc-8 herc-9 herc-10 herc-decko herc-dama herc-kralj herc-as
do
    inkscape --export-id=$id --export-png=$destination/$id.png --export-dpi=$dpi $filename
done

# Pik
for id in pik-7 pik-8 pik-9 pik-10 pik-decko pik-dama pik-kralj pik-as
do
    inkscape --export-id=$id --export-png=$destination/$id.png --export-dpi=$dpi $filename
done

# Karo
for id in karo-7 karo-8 karo-9 karo-10 karo-decko karo-dama karo-kralj karo-as
do
    inkscape --export-id=$id --export-png=$destination/$id.png --export-dpi=$dpi $filename
done

# Tref
for id in tref-7 tref-8 tref-9 tref-10 tref-decko tref-dama tref-kralj tref-as
do
    inkscape --export-id=$id --export-png=$destination/$id.png --export-dpi=$dpi $filename
done
