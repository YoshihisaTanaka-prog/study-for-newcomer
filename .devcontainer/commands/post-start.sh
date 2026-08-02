#!/usr/bin/env bash
set -u

/commands/setup-ssh.sh || true &
/commands/start-postgres.sh || true &
wait || true
