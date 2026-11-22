#!/usr/bin/env bash
# Одноразовая подготовка свежего Ubuntu-сервера: Docker + открытые порты 80/443.
set -euo pipefail

sudo apt-get update
sudo apt-get install -y unzip curl
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"

# На образах Oracle Ubuntu входящие порты закрыты правилами iptables.
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y iptables-persistent
sudo netfilter-persistent save

echo "Готово. Выйдите и зайдите по SSH заново, чтобы применилась группа docker."
