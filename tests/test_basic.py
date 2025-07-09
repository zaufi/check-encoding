# SPDX-FileCopyrightText: 2025 Alex Turbov <zaufi@pm.me>
# SPDX-License-Identifier: GPL-3.0-or-later

from check_encoding import cli


def test_cli_runs(monkeypatch):
    monkeypatch.setattr("sys.argv", ["check-encoding", "--list-encodings"])
    try:
        cli.main()
    except SystemExit as e:
        assert e.code == 0
