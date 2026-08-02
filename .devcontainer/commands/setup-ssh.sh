#!/usr/bin/env bash
set -u

host_ssh_dir="/home/vscode/.ssh"
target_ssh_dir="/root/.ssh"

if [ ! -d "$host_ssh_dir" ]; then
  echo "Host SSH directory is not mounted. Skipping SSH setup."
  exit 0
fi

mkdir -p "$target_ssh_dir"
cp -a "$host_ssh_dir"/. "$target_ssh_dir"/ 2>/dev/null || true

find "$target_ssh_dir" -type f -exec sed -i 's/\r$//' {} \;

chown -R root:root "$target_ssh_dir"
chmod 700 "$target_ssh_dir"

find "$target_ssh_dir" -type f -name "*.pub" -exec chmod 644 {} \;
find "$target_ssh_dir" -type f -name "known_hosts*" -exec chmod 644 {} \;
find "$target_ssh_dir" -type f -name "config" -exec chmod 600 {} \;

find "$target_ssh_dir" -type f \
  ! -name "*.pub" \
  ! -name "known_hosts*" \
  ! -name "config" \
  -exec chmod 600 {} \;

echo "SSH files copied into the container with safe permissions."
