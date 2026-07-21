# ReleaseCore

ReleaseCore es un core compartido para preparar carpetas de release de forma controlada.

Su objetivo no es compilar ejecutables ni reemplazar PyInstaller. Su objetivo es copiar archivos,
limpiar destinos, excluir contenido de desarrollo y devolver un resultado estructurado del paquete generado.

## Rol dentro de SharedCode

```text
ReleaseCore prepara entregables.
Cada herramienta decide qué archivos necesita.
Toolkit consume herramientas ya estables por manifest.
```

## Principios

```text
- neutral
- sin dependencia de Toolkit
- sin dependencia de herramientas concretas
- sin ejecutar comandos externos
- sin compilar
- sin inventar reglas de negocio
```

## Validaciones

```bash
python -m compileall .
python -m unittest discover -s tests -v
```
