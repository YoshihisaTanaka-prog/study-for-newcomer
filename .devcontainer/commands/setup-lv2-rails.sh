#!/usr/bin/env bash
set -u

app_dir="/workspaces/lv2-rails"

if [ ! -f "$app_dir/Gemfile" ]; then
  echo "lv2-rails Gemfile was not found. Skipping bundle install."
  exit 0
fi

cd "$app_dir" || exit 0

bundle config set path vendor/bundle

echo "bundle pass was set."
