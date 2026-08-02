#!/usr/bin/env bash
set -u

/commands/setup-ssh.sh || true &
/commands/start-postgres.sh || true &
/commands/setup-lv2-rails.sh || true &
wait || true
