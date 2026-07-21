# Toolkit Render Templates

Este directorio contiene las plantillas Jinja usadas por Toolkit IT para generar reportes HTML.

La idea principal es separar responsabilidades para evitar duplicar codigo y preparar el camino para un reporte completo reutilizando secciones internas.

## Estructura esperada

```text
templates/
├─ base.html.j2
├─ report_base.html.j2
├─ hardware_report.html.j2
├─ network_report.html.j2
├─ software_report.html.j2
├─ extras_report.html.j2
├─ full_report.html.j2
│
├─ components/
│  ├─ usage_bar.html.j2
│  ├─ diagnostics.html.j2
│  ├─ errors.html.j2
│  └─ summary_card.html.j2
│
└─ report_sections/
   ├─ hardware_content.html.j2
   ├─ network_content.html.j2
   ├─ software_content.html.j2
   └─ extras_content.html.j2
```

## Objetivo de esta estructura

La estructura busca que cada archivo tenga una responsabilidad clara.

El objetivo no es crear componentes por todo, sino separar lo que realmente aporta valor.

La idea final es que:

```text
Reportes individuales
    usan una base comun
    usan componentes reutilizables
    usan secciones internas

Full report
    usa la misma base comun
    reutiliza las mismas secciones internas
```

De esta forma evitamos:

```text
- duplicar HTML
- copiar reportes completos dentro de otro reporte
- mezclar estilos generales con estilos especificos
- romper reportes individuales al crear el reporte completo
```

## Niveles de plantillas

La arquitectura se divide en cuatro niveles:

```text
Nivel 1: Base general
Nivel 2: Base de reportes
Nivel 3: Reportes individuales
Nivel 4: Secciones internas y componentes
```

---

## 1. base.html.j2

Plantilla base general.

Responsabilidad:

```text
- Crear la estructura HTML general
- Definir head, body y main
- Definir CSS global basico
- Exponer bloques reutilizables
```

No debe saber nada de reportes.

No debe contener:

```text
- Encabezado de reporte
- Diagnosticos
- Resumen
- Tablas de hardware
- Tablas de red
- Tablas de software
- Tablas de extras
```

Ejemplo conceptual:

```jinja2
<!DOCTYPE html>
<html lang="{% block html_lang %}es{% endblock %}">
<head>
    <title>{% block title %}Toolkit IT{% endblock %}</title>

    <style>
        /* CSS global */

        {% block styles %}{% endblock %}
    </style>
</head>

<body>
    <main class="{% block main_class %}page{% endblock %}">
        {% block page_content %}{% endblock %}
    </main>
</body>
</html>
```

Regla:

```text
base.html.j2 no debe depender de ningun reporte especifico.
```

---

## 2. report_base.html.j2

Plantilla base para reportes.

Hereda de:

```jinja2
{% extends "base.html.j2" %}
```

Responsabilidad:

```text
- Crear encabezado comun de reportes
- Crear footer comun de reportes
- Definir estilos comunes de reportes
- Exponer el bloque content
- Exponer el bloque report_styles para estilos propios de cada reporte
```

No debe contener datos especificos de:

```text
- hardware
- red
- software
- extras
```

Ejemplo conceptual:

```jinja2
{% extends "base.html.j2" %}

{% block title %}
    {% block report_page_title %}Toolkit IT Report{% endblock %}
{% endblock %}

{% block styles %}
    /* CSS comun de reportes */

    {% block report_styles %}{% endblock %}
{% endblock %}

{% block page_content %}
    <header class="report-bar">
        ...
    </header>

    {% block content %}{% endblock %}

    <footer class="footer">
        ...
    </footer>
{% endblock %}
```

Regla:

```text
report_base.html.j2 define el marco comun de todos los reportes.
```

---

## 3. Reportes individuales

Ejemplos:

```text
hardware_report.html.j2
network_report.html.j2
software_report.html.j2
extras_report.html.j2
```

Estos archivos son envoltorios.

Responsabilidad:

```text
- Heredar de report_base.html.j2
- Definir titulo de pagina
- Definir titulo visible del reporte
- Definir estilos propios del reporte
- Incluir el contenido interno desde report_sections
```

No deben contener todo el cuerpo del reporte si ya existe una seccion interna reutilizable.

Ejemplo de network_report.html.j2:

```jinja2
{#
    network_report.html.j2

    Envoltorio del reporte individual de red.
#}

{% extends "report_base.html.j2" %}

{% block report_page_title %}Reporte de Red - Toolkit IT{% endblock %}

{% block report_title %}
    {{ meta.tool_name | default("Toolkit IT") }} - Reporte de Red
{% endblock %}

{% block report_styles %}
    .network-panel-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 18px;
    }

    .network-wide-panel {
        grid-column: 1 / -1;
    }

    @media (max-width: 900px) {
        .network-panel-grid {
            grid-template-columns: 1fr;
        }
    }
{% endblock %}

{% block content %}
    {% include "report_sections/network_content.html.j2" %}
{% endblock %}
```

Regla:

```text
El reporte individual pone el marco especifico.
El archivo content pone el cuerpo reutilizable.
```

---

## 4. report_sections

Carpeta esperada:

```text
templates/report_sections/
```

Archivos esperados:

```text
hardware_content.html.j2
network_content.html.j2
software_content.html.j2
extras_content.html.j2
```

Responsabilidad:

```text
- Contener solo el HTML interno del reporte
- Poder ser usado por un reporte individual
- Poder ser usado por full_report.html.j2
```

No deben contener:

```jinja2
{% extends "report_base.html.j2" %}
```

No deben contener:

```jinja2
{% block report_page_title %}
```

No deben contener:

```jinja2
{% block report_title %}
```

No deben contener:

```jinja2
{% block report_styles %}
```

No deben contener:

```jinja2
{% block content %}
```

Solo deben contener lo que antes estaba dentro de:

```jinja2
{% block content %}
    ...
{% endblock %}
```

pero sin copiar las lineas del block.

Ejemplo de network_content.html.j2:

```jinja2
{#
    network_content.html.j2

    Contenido interno del reporte de red.

    Este archivo no hereda de ninguna plantilla base.
    Este archivo no define titulo, encabezado ni pie de pagina.

    Solo contiene el HTML interno que puede ser reutilizado por:
    - network_report.html.j2
    - full_report.html.j2
#}

{% import "components/summary_card.html.j2" as summary_card %}

<div class="overview-grid">
    ...
</div>

{% include "components/errors.html.j2" %}

<section class="section" id="network-section">
    ...
</section>
```

Regla:

```text
report_sections contiene cuerpos reutilizables, no paginas completas.
```

---

## 5. components

Carpeta esperada:

```text
templates/components/
```

Archivos actuales:

```text
usage_bar.html.j2
diagnostics.html.j2
errors.html.j2
summary_card.html.j2
```

Responsabilidad:

```text
- Evitar repetir bloques visuales
- Mantener piezas comunes en un solo lugar
- Ser usados por reportes individuales
- Ser usados por report_sections
- Ser usados por full_report cuando corresponda
```

Regla importante:

```text
Un componente debe aportar valor real.
No todo debe convertirse en componente.
```

Ejemplos de componentes que si aportan valor:

```text
usage_bar.html.j2
    barra de uso reutilizable

diagnostics.html.j2
    tabla de diagnosticos reutilizable

errors.html.j2
    bloque de errores reutilizable

summary_card.html.j2
    tarjeta de resumen reutilizable
```

Ejemplo de componente que no necesariamente aporta valor:

```text
section_title.html.j2
```

Motivo:

```text
Si cada titulo tiene un icono distinto y solo se reemplaza un h2 simple,
puede agregar mas complejidad que valor.
```

---

## Como separar un reporte individual

Ejemplo usando network_report.html.j2.

### Paso 1

Crear la carpeta si no existe:

```text
templates/report_sections/
```

### Paso 2

Crear:

```text
templates/report_sections/network_content.html.j2
```

### Paso 3

Abrir:

```text
templates/network_report.html.j2
```

Buscar:

```jinja2
{% block content %}
```

### Paso 4

Mover todo lo que esta dentro de ese bloque hasta antes de:

```jinja2
{% endblock %}
```

Importante:

```text
No copiar la linea {% block content %}
No copiar la linea {% endblock %}
```

### Paso 5

Pegar ese contenido en:

```text
templates/report_sections/network_content.html.j2
```

### Paso 6

Si el contenido usa summary_card, agregar arriba del content:

```jinja2
{% import "components/summary_card.html.j2" as summary_card %}
```

### Paso 7

Dejar network_report.html.j2 como envoltorio:

```jinja2
{% block content %}
    {% include "report_sections/network_content.html.j2" %}
{% endblock %}
```

### Paso 8

Renderizar y verificar que el HTML final no cambie visualmente.

### Paso 9

Hacer commit.

---

## Orden recomendado para separar reportes

No empezar por hardware, porque es el mas grande y complejo.

Orden recomendado:

```text
1. network_content.html.j2
2. extras_content.html.j2
3. software_content.html.j2
4. hardware_content.html.j2
```

Motivo:

```text
Red y extras son mas simples.
Hardware tiene mas logica visual y mas detalles.
```

---

## Full report

El reporte completo no debe pegar HTML final ya renderizado.

No hacer esto:

```text
hardware_report.html completo dentro de full_report.html
network_report.html completo dentro de full_report.html
software_report.html completo dentro de full_report.html
extras_report.html completo dentro de full_report.html
```

Eso seria incorrecto porque cada reporte individual ya trae:

```text
- estructura HTML
- encabezado
- footer
- estilos
- bloques propios
```

La forma correcta es reutilizar secciones internas:

```jinja2
{#
    full_report.html.j2

    Envoltorio del reporte completo.

    Este archivo incluye las secciones internas de cada reporte.
    No debe pegar HTML final ya renderizado.
#}

{% extends "report_base.html.j2" %}

{% block report_page_title %}Reporte Completo - Toolkit IT{% endblock %}

{% block report_title %}
    {{ meta.tool_name | default("Toolkit IT") }} - Reporte Completo
{% endblock %}

{% block content %}

    {% include "report_sections/hardware_content.html.j2" %}

    {% include "report_sections/network_content.html.j2" %}

    {% include "report_sections/software_content.html.j2" %}

    {% include "report_sections/extras_content.html.j2" %}

{% endblock %}
```

---

## Nota importante sobre el JSON del full report

El full_report puede necesitar adaptar variables si el JSON viene anidado.

Ejemplo posible:

```text
reports.hardware
reports.network
reports.software
reports.system_extras
```

Los reportes individuales normalmente esperan variables como:

```text
meta
summary
data
diagnostics
errors
```

Pero en un full_report, cada seccion podria venir dentro de su propio bloque.

Ejemplo:

```text
reports.hardware.meta
reports.hardware.summary
reports.hardware.data
reports.hardware.diagnostics
reports.hardware.errors

reports.network.meta
reports.network.summary
reports.network.data
reports.network.diagnostics
reports.network.errors
```

En ese caso, antes de incluir cada seccion habra que preparar variables.

Ejemplo conceptual:

```jinja2
{% set meta = reports.hardware.meta %}
{% set summary = reports.hardware.summary %}
{% set data = reports.hardware.data %}
{% set diagnostics = reports.hardware.diagnostics %}
{% set errors = reports.hardware.errors %}

{% include "report_sections/hardware_content.html.j2" %}
```

Luego para red:

```jinja2
{% set meta = reports.network.meta %}
{% set summary = reports.network.summary %}
{% set data = reports.network.data %}
{% set diagnostics = reports.network.diagnostics %}
{% set errors = reports.network.errors %}

{% include "report_sections/network_content.html.j2" %}
```

Esto se debe validar con el JSON real del full_report.

---

## Router de render-engine.py

El archivo:

```text
render-engine.py
```

debe mapear cada report_type al template correcto.

Ejemplo:

```python
template_map = {
    "hardware": "hardware_report.html.j2",
    "network": "network_report.html.j2",
    "software": "software_report.html.j2",
    "software_reports": "software_report.html.j2",
    "extras": "extras_report.html.j2",
    "system_extras": "extras_report.html.j2",
    "system_extras_reports": "extras_report.html.j2",
    "full_report": "full_report.html.j2"
}
```

Regla:

```text
El JSON decide el tipo de reporte mediante meta.report_type.
render-engine.py decide que template usar.
```

---

## Render en modo desarrollo

En desarrollo se usa Python y Jinja directamente.

Ejemplo:

```powershell
.\.venv\Scripts\python.exe .\render-engine.py --input "C:\ruta\hardware_report.json" --output "C:\ruta\hardware_report.html"
```

Motivo:

```text
Permite modificar templates sin recompilar exe.
Es mas rapido para iterar.
Es mejor mientras los reportes siguen cambiando.
```

---

## Render portable futuro

La prueba portable con PyInstaller ya fue validada.

La idea futura es compilar:

```text
render-engine.py
```

como:

```text
render-engine.exe
```

Esto permite ejecutar el render en equipos sin Python ni Jinja instalados.

Pero durante desarrollo no conviene depender del exe, porque cada cambio de plantilla puede obligar a recompilar o copiar templates.

Decision actual:

```text
Desarrollo diario:
    Python + Jinja + templates editables

Portable futuro:
    render-engine.exe cuando los reportes esten mas estables
```

---

## Reglas de estilo

### Comentarios

Los comentarios dentro de archivos de codigo deben estar en espanol neutro pero sin tildes ni letra especial.

Usar:

```text
Contenido interno del reporte de red.
Este archivo no define titulo, encabezado ni pie de pagina.
```

Evitar:

```text
Contenido interno del reporte de red.
Este archivo no define título, encabezado ni pie de página.
```

### Idioma visible

Los textos visibles para el usuario deben estar en espanol.

Ejemplos:

```text
Resumen
Diagnosticos
Red
Hardware
Software
Extras
Adaptadores activos
Configuraciones IP
Recursos compartidos
Unidades logicas
```

### Componentes

No crear componentes si no reducen complejidad.

Antes de crear un componente preguntar:

```text
Esto reduce repeticion real?
Esto mejora lectura?
Esto se reutilizara en mas de un reporte?
Esto evita errores?
```

Si la respuesta es no, mantener HTML directo.

---

## Regla principal

```text
base.html.j2
    HTML general

report_base.html.j2
    Marco comun de reportes

*_report.html.j2
    Envoltorio de reporte individual

report_sections/*_content.html.j2
    Cuerpo reutilizable del reporte

components/*.html.j2
    Piezas visuales reutilizables
```

---

## Decision tecnica

El reporte completo debe construirse reutilizando secciones internas.

No se debe crear desde cero duplicando todo.

No se debe unir HTML final ya renderizado.

La convergencia correcta es:

```text
Reportes individuales
    usan report_sections

Reporte completo
    usa las mismas report_sections
```

---

## Plan de trabajo recomendado

```text
1. Mantener reportes individuales funcionando.
2. Crear carpeta report_sections.
3. Extraer primero network_content.
4. Probar render de network_report.
5. Extraer extras_content.
6. Probar render de extras_report.
7. Extraer software_content.
8. Probar render de software_report.
9. Extraer hardware_content.
10. Probar render de hardware_report.
11. Revisar JSON real de full_report.
12. Crear full_report.html.j2 usando las secciones internas.
13. Probar full_report.
14. Ajustar variables si el JSON viene anidado.
15. Hacer commit final.
```

---

## Commit recomendado luego de separar secciones

```bash
git status
git add external/python/render-engine/templates/
git add external/python/render-engine/render-engine.py
git commit -m "Prepare reusable report sections"
```

---

## Estado actual esperado

Los reportes individuales deben seguir funcionando antes de tocar full_report.

Reportes esperados:

```text
hardware_report.html.j2
network_report.html.j2
software_report.html.j2
extras_report.html.j2
```

El siguiente objetivo no es embellecer.

El siguiente objetivo es preparar:

```text
report_sections/
```

para que el full_report pueda reutilizar el mismo contenido.