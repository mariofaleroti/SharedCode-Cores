# Auditoría de documentación y portabilidad

## Objetivo

Revisar que SharedCode explique claramente:

```text
- para qué sirve cada core;
- qué no debe hacer cada core;
- qué partes son portables;
- qué partes son específicas de Windows/Linux;
- dónde deben vivir las diferencias de sistema operativo.
```

## Resultado

Se agregaron documentos centrales para que la información no quede dispersa:

```text
docs/CORE_RESPONSIBILITIES.md
docs/PORTABILITY_WINDOWS_LINUX.md
docs/OS_SPECIFIC_BOUNDARIES.md
README.md raíz actualizado
docs/README.md actualizado
```

## Hallazgos principales

```text
1. La mayoría de los cores son portables o neutrales.
2. PlatformCore concentra correctamente las diferencias Windows/Linux nuevas.
3. GuiCore ya documenta iconos centralizados, pero se agregó referencia desde la documentación general.
4. Hay scripts PowerShell/.cmd que son Windows-only; se documentan como auxiliares, no como core portable.
5. RenderCore tiene scripts y manifest actuales orientados a Windows; queda documentado como punto futuro para entry_by_platform y scripts .sh.
6. Los ejemplos con rutas C:\ deben tratarse como ejemplos Windows, no como regla universal.
```

## Estado recomendado

```text
ShareCode puede considerarse documentado como base portable Windows/Linux inicial.
No hace falta tocar SmartFilter para este corte.
Próximo paso sugerido: congelar esta documentación y luego decidir packaging Windows/Linux.
```
