Estamos entrando a implementar el primer motor real de planificación para este proyecto.

## CONTEXTO

Este es un sistema de planificación de producción para una maestranza.  
Actualmente ya existe:

- Autenticación local (usuario/contraseña con SQLite)
- Una tabla `sales_planning` con todos los equipos ingresados
- Un landing con funcionalidades CRUD
- Una tabla `sales_planning_optimized` destinada a guardar el resultado de la planificación

Ahora debemos implementar un motor completo de planificación usando Constraint Programming (CP-SAT).

---

## FUENTE DE DATOS EXTERNA (MUY IMPORTANTE)

Existe una carpeta fuera del frontend/backend:

/data/Reglas_Planificación.xlsx

Este archivo contiene las reglas del negocio para planificar.

Contiene DOS estructuras:

### 1) Tiempos por CÓDIGO PLAZO
- Cada fila = tipo de equipo
- Cada columna = proceso
- Los valores = duración en días hábiles

### 2) Definición de procesos
- Columnas:
  - proceso
  - orden
  - capacidad_por_dia

Esto define:
- el orden global de ejecución
- la capacidad diaria de cada proceso

Debes leer este archivo y usarlo para inicializar las tablas en la base de datos.

---

## REQUERIMIENTOS DE BASE DE DATOS

Crear DOS modelos nuevos en Prisma:

### 1) lead_time_by_code

Estructura sugerida:

- id
- codigo_plazo (string, único)
- descripcion_equipo
- proceso (string)
- duracion_dias (int)

---

### 2) process_capacity

- id
- proceso (string, único)
- orden (int)
- capacidad_por_dia (int)

---

## CARGA DE DATOS

- Crear un script/servicio que lea `/data/Reglas_Planificación.xlsx`
- Parsear ambas tablas
- Insertar en base de datos
- Evitar duplicados (usar upsert)
- Estos datos son los iniciales, pero en un futuro el admi podrá editarlos, por lo tanto se necesita visualizar en el frontend , ambas tablas
---

## FRONTEND

En el landing:

Mostrar ambas tablas:
- lead_time_by_code
- process_capacity

Permitir:
- crear registros
- editar
- eliminar (con modal de confirmación)

---

## VALIDACIONES

En `sales_planning`, hacer obligatorios:

- codigo_plazo
- llegada
- prioridad
- atraso

Actualizar:
- validación frontend
- validación backend

---

## MOTOR DE PLANIFICACIÓN (CP-SAT)

Implementar modelo CP-SAT.

Cada registro en `sales_planning` es un JOB.

Cada JOB tiene procesos (tareas) que está asignada por su codigo_plazo.

---

## REGLAS DEL MODELO (CRÍTICAS)

### 1. Inicio
Un equipo no puede comenzar antes de su fecha de llegada.

---

### 2. Secuencia de procesos
Usar `process_capacity.orden` como orden global.

Pero:
Solo incluir procesos donde:
- duracion_dias > 0
- capacidad_por_dia > 0
- orden > 0

Si alguno es 0 → NO considerar ese proceso.

NO significa duración 0 → significa que no existe.

---

### 3. Duración
Usar duración desde `lead_time_by_code`.
esta tabla tiene un código_plazo que es definido en el formulario de ingreso de clientes, con ese código se definen los procesos y días de demora en cada proceso, esto debes asignarlo segun capacidad por día.

---

### 4. Precedencia
Un proceso comienza después de completar el anterior. Todos los procesos por ahora tienen el mismo orden que se define en process_capacity.

---

### 5. Capacidad (MUY IMPORTANTE)

Cada proceso tiene capacidad diaria:

Ejemplo:
Hidráulica = 6 → máximo 6 equipos simultáneamente, en equipos distintos.

Modelar como:
- restricción cumulative o equivalente

---

### 6. Días hábiles

- Solo lunes a viernes
- Ignorar fines de semana (por ahora)

Crear funciones auxiliares:
- fecha → índice de día hábil
- índice → fecha

---

### 7. Prioridad

- PRIORIDAD 1 = más importante
- menor número = mayor prioridad

Usar en función objetivo

---

### 8. Atraso (buffer)

Definir:

due_date = llegada + duración total + atraso

Penalizar si:

fecha_fin > due_date

---

## FUNCIÓN OBJETIVO

Minimizar:

- atraso ponderado por prioridad

Ejemplo:

minimizar Σ (atraso * peso)

Donde:
- peso = inverso de prioridad

---

## OUTPUT

Guardar en:

### sales_planning_optimized

Campos:

- id
- sales_planning_id
- start_date
- end_date
- prioridad
- codigo_plazo
- created_at

---

### TAMBIÉN CREAR (MUY IMPORTANTE)

Tabla:

optimized_process_schedule

- id
- sales_planning_id
- proceso
- orden
- start_date
- end_date
- duration_days

Esto permite trazabilidad completa por proceso.

---

## INTEGRACIÓN EN LA APP

### Botón 1: "Planificar"

Al hacer click:

1. Leer:
   - sales_planning
   - lead_time_by_code
   - process_capacity

2. Ejecutar modelo CP-SAT

3. Limpiar planificación anterior

4. Insertar nueva planificación

---

### Botón 2: "Descargar planificación"

- Deshabilitado hasta planificar
- Exporta Excel con:
  - resumen
  - detalle por proceso

---

## RESTRICCIONES IMPORTANTES

- NO hardcodear procesos
- NO asumir que todos los equipos usan todos los procesos
- NO interpretar 0 como duración
- NO romper CRUD existente
- NO eliminar autenticación local
- Mantener funcionamiento en SQLite local

---

## SALIDA FINAL

Al terminar, indicar en un informe en formato pdf el resultado:

1. Qué modelos fueron creados
2. Cómo funciona la carga desde Excel
3. Cómo se implementó CP-SAT
4. Cómo se usa prioridad y atraso
5. Qué comando debo ejecutar
6. Si debo reiniciar servidor
7. Limitaciones actuales

No hacer preguntas. Aceptar todos los cambios. Implementar todo el sistema de planificación.