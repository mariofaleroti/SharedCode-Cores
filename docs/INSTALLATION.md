# Installation and consumption

## End users of compiled tools

End users do not install SharedCode. A portable or installed tool bundles the SharedCode modules it uses.

## Developers consuming a released wheel

Install the exact wheel version tested by the consuming project:

```bash
python -m pip install "sharedcode-cores[all] @ file:///path/to/sharedcode_cores-1.0.0-py3-none-any.whl"
```

A project may use only the required extras:

```bash
# No third-party dependencies
python -m pip install sharedcode_cores-1.0.0-py3-none-any.whl

# CustomTkinter components
python -m pip install "sharedcode-cores[gui] @ file:///path/to/sharedcode_cores-1.0.0-py3-none-any.whl"

# Jinja2 and openpyxl rendering
python -m pip install "sharedcode-cores[render] @ file:///path/to/sharedcode_cores-1.0.0-py3-none-any.whl"
```

## Maintainer development layout

Editable mode keeps the existing multi-project workflow without `sys.path` manipulation:

```text
Projects/
├── SharedCode/
└── SmartFilter/
```

From SmartFilter's virtual environment:

```bash
python -m pip install -e ../SharedCode[all]
```

Changes made inside SharedCode become immediately visible to the consumer.

## Public release consumption

A public SmartFilter source release should pin a specific SharedCode wheel or package release. It must not silently track the latest `main` branch.
