# PlatformCore portable path resolution contract

## `resolve=True`

This is the normal runtime mode. Context variables and the final path are
resolved against the active host filesystem.

## `resolve=False`

This is the portable composition mode:

- caller-provided context paths are not physically resolved;
- no current drive is attached to foreign-platform rooted paths;
- relative values are composed with `base_dir` without filesystem access;
- token expansion remains deterministic for Windows/Linux tests and config
  migration tools.

## Rooted paths on Windows

A Windows `Path` created from `/home/tester` has a root but no drive.
`Path.is_absolute()` therefore returns `False`, even though the value must not be
treated as relative for portable composition.

PlatformCore recognizes either:

```python
candidate.is_absolute() or bool(candidate.root)
```

before deciding whether to prepend `base_dir`.

## Runtime recommendation

Consumers should normally omit `platform_name` and use the active host.
Cross-platform simulations should pass the intended platform and
`resolve=False`.
