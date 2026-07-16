# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Workshop (maestranza) production planning web app for ETP spa. Phase 1 is an MVP focused on data entry, CRUD, and historical visualization — with architecture designed to support a future optimization engine (CP-SAT / finite capacity heuristic).

## Tech Stack

- **Next.js** (App Router) + **TypeScript** — full-stack, no separate backend
- **Supabase** — PostgreSQL database + Auth (email/password)
- **Prisma** — ORM for database access
- **Tailwind CSS** + **shadcn/ui** — styling and components
- **React Hook Form** + **Zod** — form handling and validation
- **Vercel** — deployment target

## Commands

```bash
npm run dev        # Start development server
npm run build      # Production build
npm run lint       # ESLint
npx prisma migrate dev   # Run DB migrations
npx prisma studio        # Open Prisma visual DB explorer
npx prisma generate      # Regenerate Prisma client after schema changes
```

## Architecture

### Data Model

Primary table: `sales_planning`

Business fields: `ot`, `clte_interno`, `cliente`, `codigo_plazo`, `equipo`, `modelo_capacidad`, `camion`, `modelo`, `vin`, `llegada`, `entrega`, `venta`, `color_eq`, `oc`, `factura`, `proximo_a_entrega`, `cotizacion`, `correo`, `patente`, `neumatico_de_repuesto`, `n_recepcion`, `color_cabina`, `atraso`, `prioridad`

Audit fields: `id`, `created_at`, `updated_at`, `created_by` (Supabase user ID), `updated_by` (Supabase user ID)

Future table: `sales_planning_optimized` — stores FIFO-ordered output for Excel export (Phase 1: no optimization, just ordered by `llegada`).

### API Routes (Next.js App Router)

All data access goes through `/app/api/` route handlers. Supabase Auth session is validated server-side on every request. `created_by`/`updated_by` are set from the authenticated user's ID — never from client input.

### Authentication Flow

Supabase Auth handles registration, login, and session management. Use Supabase server client (with cookie-based session) in Server Components and route handlers. Never expose service role key to the client.

### Excel Export

The export endpoint reads from `sales_planning_optimized` and generates an `.xlsx` file using **openpyxl** (Python via API route or a dedicated script) or a Node.js XLSX library. Refer to `.claude/skills/xlsx/SKILL.md` for spreadsheet generation conventions — key rule: **use Excel formulas, not hardcoded computed values**.

## Key Design Constraints

- The `codigo_plazo` field drives future capacity planning — preserve it accurately; it maps to process time data in `/data/`.
- Historical table must display records in **insertion order** (`created_at ASC`).
- All mutations must record `created_by`/`updated_by` using the authenticated Supabase user ID.
- The optimization module is **out of scope for Phase 1** — do not add scheduling or capacity logic now, but keep the schema extensible.

## `/data` Folder

Contains reference Excel/CSV files for future optimization:
- `procesos.xlsx` — process definitions
- `Tiempo_trabajos.xlsx` — process durations
- `Maestro_producto.xlsx` — product master
- `Programación Equipos.csv` — equipment scheduling data
- `Info Planificación Equipos.xlsx` — planning reference

These are read-only reference files; do not modify them.

## Skills

Active skills in `.claude/skills/`:
- **frontend-design** — UI/component generation: commit to a bold, intentional aesthetic; avoid generic AI defaults (Inter font, purple gradients, cookie-cutter layouts).
- **backend-development** — API design, auth, DB patterns, security (OWASP Top 10).
- **xlsx** — Excel file creation/editing: use formulas over hardcoded values; run `scripts/recalc.py` after any formula changes; deliver zero formula errors.
