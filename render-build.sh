#!/bin/bash
set -e
apt-get update
apt-get install -y firefox-esr
GECKODRIVER_VERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep "tag_name" | sed -E 's/.*"([^"]+)".*/\1/')
wget "https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz"
tar -xzf "geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz"
mv geckodriver /usr/local/bin/
chmod +x /usr/local/bin/geckodriver
rm "geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz"
