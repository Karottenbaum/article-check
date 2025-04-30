#!/bin/bash

# Abbrechen bei Fehlern
set -e

# Systempakete aktualisieren
apt-get update

# Firefox ESR installieren (stabile Version)
apt-get install -y firefox-esr

# Neueste Geckodriver-Version abrufen
GECKODRIVER_VERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest \
  | grep '"tag_name":' \
  | sed -E 's/.*"([^"]+)".*/\1/')

# Geckodriver herunterladen und installieren
wget "https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz"
tar -xzf "geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz"
mv geckodriver /usr/local/bin/
chmod +x /usr/local/bin/geckodriver

# Bereinigen
rm "geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz"