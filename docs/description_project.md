# Project Description

## 1. Business Context and Objective

This project aims to build a web application for a workshop (maestranza) planning system. The goal is not only to capture data but to create the operational foundation for a future production planning optimization engine.

In this first phase, the focus is on:
- Centralizing client/equipment data
- Visualizing full historical records
- Tracking user actions (create/update)
- Preparing the architecture for future optimization

The optimization module is NOT included in this phase but must be considered in the design.

---

## 2. Scope (MVP)

Included:
- User registration and login
- Manual data entry (form)
- Full historical table view
- Edit and delete records
- User traceability
- Landing page with form + table
- Excel export of planning data (non-optimized)

Excluded:
- Optimization engine
- Scheduling logic
- Capacity constraints
- Simulation

---

## 3. Data Model

### Main Table: sales_planning

Business fields:
- ot
- clte_interno
- cliente
- codigo_plazo
- equipo
- modelo_capacidad
- camion
- modelo
- vin
- llegada
- entrega
- venta
- color_eq
- oc
- factura
- proximo_a_entrega
- cotizacion
- correo
- patente
- neumatico_de_repuesto
- n_recepcion
- color_cabina
- atraso
- prioridad

Technical fields:
- id (primary key)
- created_at
- updated_at
- created_by
- updated_by

---

### Future Table: sales_planning_optimized

Purpose:
- Store final planning output
- Serve as Excel export source

Phase 1 behavior:
- Ordered by arrival date (FIFO)
- No optimization logic applied

---

## 4. Frontend Requirements

The landing page must include:
- Authentication (login/register)
- Data entry form
- Historical table (sales_planning)
- Filters and search
- Edit/delete actions
- Excel download button (from sales_planning_optimized)

The historical table must display records in insertion order.

---

## 5. Authentication

Use Supabase Auth:
- User registration
- Login
- Session management

Store user ID in:
- created_by
- updated_by

---

## 6. Functional Rules

Users can:
- Create records
- View all records
- Edit records
- Delete records

System must:
- Validate inputs
- Maintain consistency
- Track changes

---

## 7. Tech Stack

- Next.js (Frontend + Backend)
- TypeScript
- Supabase (PostgreSQL + Auth)
- Prisma (ORM)
- Tailwind CSS
- shadcn/ui
- React Hook Form
- Zod
- Vercel (deploy)

Architecture:
- Full-stack unified app
- No separate backend

---

## 8. Backend Logic

Must include:
- Authentication
- Full CRUD
- Audit tracking
- Excel export

Prepared for:
- Future planning engine integration

---

## 9. Future Planning Dependencies

Optimization will depend on:
- codigo_plazo (capacity usage)
- process order
- daily capacity per process

Data will be provided in:
- /data folder (future implementation)

---

## 10. Future Vision

Planned evolution:

1. Finite capacity heuristic
2. Constraint Programming (CP-SAT)
3. Discrete event simulation

---

## 11. Best Practices

Follow project skills:
- backend-development
- frontend-design
- xlsx

Code must be:
- modular
- typed
- scalable
- clean

---

## 12. Expected Deliverables

- Full project setup
- Supabase integration
- Auth system
- Database schema
- CRUD UI
- Excel export
- Documentation
