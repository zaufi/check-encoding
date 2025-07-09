<!--
SPDX-FileCopyrightText: 2025 Alex Turbov <zaufi@pm.me>
SPDX-License-Identifier: CC0-1.0
-->

# What is This

A CLI tool to check file encoding compliance. Supports UTF-8 by default and
can validate against any Python-supported codec. Also lists all available
encoding aliases. The tool aimed to be a `pre-commit` hook.

## Using with `pre-commit`

To check that every committed file is encoded in UTF-8 you can use
`check-encoding` as a [`pre-commit`](https://pre-commit.com/) hook.  Add the
following snippet to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/zaufi/check-encoding
    rev: v0.1  # Use the appropriate released version
    hooks:
      - id: check-encoding
        args: ["--encoding", "utf-8"]
```

After adding the configuration run `pre-commit install` once to activate the
hook. It will then prevent commits that contain files not encoded in UTF-8.
