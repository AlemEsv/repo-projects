# Ejercicios (WIP)

### Ejercicio 1: Crear un Epic y vincular historias de usuario

1. Crea un nuevo Epic en tu Kanban board llamado "Gestión de Contadores".

	![](assets/images/Pasted%20image%2020250514173045.png)

2. Vincula las historias de usuario existentes, como "Need a service that has a counter", "Must allow multiple counters", y "Counters can be reset" a este Epic.

	`Need a service that has a counter`
	
	![](assets/images/Pasted%20image%2020250514173223.png)

	`Must allow multiple counters`
	
	![](assets/images/Pasted%20image%2020250514173306.png)

	`Counters can be reset`
	
	![](assets/images/Pasted%20image%2020250514173411.png)

	`Generate counter usage reports` (Nueva historia de usuario)

	![](assets/images/Pasted%20image%2020250514175420.png)

### Ejercicio 2: Uso avanzado de etiquetas (labels) para priorización y estado

a. **Creación de etiquetas(labels) de prioridad.**

En proyectos dentro de Github es necesario tener un control sobre qué problemas abordará el equipo en un periodo cercano de tiempo a comparación de otras actividades.

Algunas de estas marca son las siguientes:

![alt](assets/images/labels.png)

Para este proyecto habrá 3 tipos de prioridad para abordar de manera eficiente cada reto propuesto en esta actividad.

![alt](assets/images/labels-priority.png)

b. **Asignación de etiquetas a historias de usuario**

Se mide la prioridad de los issues que estén en **Product Backlog** para tener una mayor concideración a la hora de abordarlos.

![alt](assets/images/product-backlog.png)

Luego se reagrupan, y se colocan las etiquetas para definir su prioridad en base a lo pedido en la actividad.

![alt](assets/images/labels-priority-2.png)

c. **Creación de etiquetas adicionales**

Para un mayor control se consideran etiquetas que verificarán si algún **intengrante** tiene problemas para resolver los **issues** y/o se quiera tener apuntado el avance de los **issues**.

![alt](assets/images/labels-control.png)

Teniendo completado la información de los estados de cada **issue** para facilitar la gestión del flujo de trabajo.

![alt](assets/images/labels-control-2.png)

### Ejercicio 3: Automatización de Kanban board con GitHub Actions

### Ejercicio 4: Seguimiento de tiempo y esfuerzo usando GitHub Projects

### Ejercicio 5: Refinamiento de backlog basado en comentarios de los stakeholders

Se ha visto comentarios de stakeholders que piden necesitan una funcionalidad para poder exportar los datos del contador a CSV, por lo que se creará un nuevo **issue** que aborde dicha funcionalidad.

![alt](assets/images/data-CSV.png)

Para mayor detalle en la visualización de los criterios de aceptación:

```gherkin
Scenario: Export a single counter to CSV
Given the user is viewing the details of the counter
When the user clicks "Export to CSV"
Then a CSV file is downloaded

Scenario: Export all counters to CSV
Given the user has multiple counters
When the user clicks "Export All to CSV"
Then a CSV file is downloaded

Scenario: Export with no counters
Given the user has no counters in the system
When the user attempts to export counters to CSV
Then the system shows a message: "No counters to export"
```

Luego se le colocan los labels de alta prioridad y se denota que estará listo para entrár al sprint.

![alt](assets/images/labels-CSV.png)

### Ejercicio 6: Análisis del flujo de trabajo usando el Kanban board
