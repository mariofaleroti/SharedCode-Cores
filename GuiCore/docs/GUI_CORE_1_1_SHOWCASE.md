# Showcase oficial de GuiCore 1.1

`examples/guicore_1_1_showcase.py` es la aplicación neutral de integración del
contrato GuiCore 1.1.

## Ejecución

```powershell
.\.venv\Scripts\python.exe `
  .\GuiCore\examples\guicore_1_1_showcase.py
```

Modo de preferencias explícito:

```powershell
.\.venv\Scripts\python.exe `
  .\GuiCore\examples\guicore_1_1_showcase.py `
  --preferences basic
```

Valores válidos:

```text
none
basic
advanced
```

## Componentes demostrados

- perfil `compact`;
- sidebar desplazable;
- acciones primarias fijas;
- footer de dos columnas;
- controles compactos;
- combo con acción auxiliar;
- métricas y tooltips;
- tabla ordenable;
- tarjeta plegable;
- tabla clave/valor;
- progreso determinado;
- cancelación cooperativa;
- bloqueo temporal de controles;
- preferencias `none`, `basic` y `advanced`.

La demo no contiene lógica de un producto concreto. Sus datos son simulados y
su objetivo es verificar que todos los componentes conviven bajo una única
aplicación.
