# mise-prune-system

A small, preview-first helper for reclaiming unused versions from mise's
system-wide installs directory. It is intended as a temporary companion to
mise's built-in `mise prune`, which does not currently prune shared/system
install roots.

The helper is deliberately Linux-only for now. It lists all installed versions,
uses mise's tracked configuration sources to protect referenced versions, and
checks `/proc` for running processes that refer to an install, then delegates removals to
`mise uninstall` with `MISE_INSTALLS_DIR` pointed at the system install root.
It does not remove files directly.

## Usage

From this checkout:

```sh
mise ioweb-prune-system
```

This is a preview. To remove the listed versions, pass `--apply`; the helper
prompts before making changes:

```sh
sudo -H mise ioweb-prune-system --apply
```

Use `--yes` with `--apply` only in an explicitly reviewed automation run. The
helper refuses to apply changes unless it runs as root and can complete its
process scan.

The system root defaults to `/usr/local/share/mise`, or
`$MISE_SYSTEM_DATA_DIR` if set. Override it with `--system-data-dir` when mise
uses a non-default location. The installs directory is `<system-data-dir>/installs`.

## Candidate rules

- Only installed versions whose reported install path is inside the selected
  system installs directory are considered.
- Versions associated with tracked config sources, active in the current mise
  environment, or referenced by a running process are kept.
- If mise output is invalid, a candidate path is ambiguous, or process
  inspection is incomplete, the helper stops or keeps the affected versions.
- Every removal goes through `mise uninstall` with the system installs root
  selected as mise's primary installs directory.

The first release has no migration or path-inference mode for installs that
mise cannot identify. Review the preview before applying it, especially on
hosts with custom shared install roots.

## Install as a mise task

The repository includes a `mise.toml` task named `ioweb-prune-system`. When
this checkout is loaded by mise, its task can be invoked as
`mise ioweb-prune-system`. To make it available from other directories, add the
same task definition to a global or system mise config, with `run` pointing at
the installed helper path.
