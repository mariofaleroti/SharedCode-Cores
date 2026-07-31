# Operaciones en segundo plano — GuiCore 1.1

`GuiTaskRunner` ejecuta lógica fuera del hilo de interfaz y entrega todos los
callbacks mediante `root.after`, dentro del hilo propietario de Tk.

## Worker

```python
def worker(context: TaskContext):
    for index in range(1, 101):
        context.report_progress(index, 100)
        context.sleep(0.02)
    return {"processed": 100}
```

El worker puede usar:

```text
context.report_progress(...)
context.report_indeterminate(...)
context.check_cancelled()
context.sleep(...)
context.is_cancelled
```

No debe acceder a widgets Tk/CustomTkinter.

## Integración con GuiAppWindow

```python
runner = app.start_task(
    worker,
    task_key="scan",
    start_message="Preparando...",
    success_message="Finalizado",
    cancellable=True,
    disable_while_running=(run_button,),
    on_success=handle_result,
    on_error=handle_error,
)
```

`start_task` integra automáticamente:

- `ProgressPanel` determinado o indeterminado;
- botón de cancelación cooperativa;
- mensajes terminales;
- bloqueo y restauración de controles;
- protección contra una segunda tarea con el mismo `task_key`;
- cancelación defensiva al cerrar la ventana.

## Uso directo

```python
runner = GuiTaskRunner(root)
runner.start(
    worker,
    on_progress=update_view,
    on_finished=finish_view,
)
```

## Resultados

```text
TaskProgress
TaskError
TaskResult
CancellationToken
TaskContext
TaskCancelledError
```

Estados:

```text
idle
running
cancelling
completed
failed
cancelled
```

## Seguridad de hilo

La cola interna es la única vía de comunicación desde el worker. El worker no
programa callbacks Tk y no recibe referencias a widgets. El polling, los
callbacks, el progreso y la restauración de controles ocurren en el hilo
propietario de `GuiTaskRunner`.

## Throttling

`progress_interval_seconds` limita la frecuencia de eventos emitidos desde el
worker. Además, el polling conserva únicamente el progreso más reciente de cada
ciclo, evitando saturar la interfaz.
