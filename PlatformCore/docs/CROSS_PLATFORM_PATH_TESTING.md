# PlatformCore cross-platform path testing

PlatformCore returns the active host's concrete `pathlib.Path` type.

## Portable expansion tests

Tests that simulate a foreign platform, such as Linux while running on Windows,
must use `resolve=False`. This validates:

- portable-token substitution;
- relative-path composition;
- platform-specific directory selection;

without asking the host operating system to physically resolve a foreign path.

## Physical resolution tests

`resolve=True` is tested separately with a temporary directory on the active
host. This validates actual filesystem resolution without mixing Windows and
POSIX path semantics.

## Native path representation

Path separators are host-native. Tests compare `Path` objects rather than
requiring a literal `/` or `\` string.
