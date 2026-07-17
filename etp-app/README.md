# ETP — Sistema de Planificación de Producción

Production planning web application for ETP spa workshop (maestranza).

Built with: Next.js 16, TypeScript, Tailwind CSS v4, shadcn/ui, Prisma 7, React Hook Form + Zod, xlsx.

---

## Running Locally (SQLite + mocked auth)

No Supabase account required. Uses SQLite and a mocked user.

```bash
# 1. Install dependencies
npm install

# 2. Run the database migration (creates prisma/dev.db)
npx prisma migrate dev --name init

# 3. Start the dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

You will see a **"Entrar como dev@etp.cl"** button — click it, no password needed.

> **Node.js 20+ is required.** If your system has an older version, install via fnm:
> ```bash
> curl -L https://github.com/Schniz/fnm/releases/latest/download/fnm-macos.zip -o /tmp/fnm.zip
> unzip -o /tmp/fnm.zip -d ~/bin && chmod +x ~/bin/fnm
> eval "$(~/bin/fnm env --shell bash)" && ~/bin/fnm install 22 && ~/bin/fnm use 22
> ```
> Then run the commands above normally.

---

## Environment Variables

`.env.local` is pre-configured for local development (already in the repo):

```
DATABASE_URL="file:./dev.db"
DEV_AUTH="true"
NEXT_PUBLIC_SUPABASE_URL="https://placeholder.supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="placeholder-anon-key"
```

For production, copy `.env.example` and fill in real values. See the comments in that file for a full description of every variable.

### Access control — two independent mechanisms

| Mechanism | What it controls | Where it lives |
|---|---|---|
| `ADMIN_EMAIL_EXCEPTIONS` | Who can **register and log in** (bypasses corporate domain check) | Hardcoded in `src/lib/validations.ts` |
| `ADMIN_EMAILS` | Who has **administrator permissions** (`user.isAdmin`) | Environment variable |

These are completely independent. Being in `ADMIN_EMAIL_EXCEPTIONS` does not grant admin permissions. Being in `ADMIN_EMAILS` does not bypass the domain check. A user can appear in both, neither, or only one of the two lists.

---

## Connecting to Supabase (Production)

1. Create a project at [supabase.com](https://supabase.com).
2. Go to **Settings → API** and copy:
   - `Project URL` → `NEXT_PUBLIC_SUPABASE_URL`
   - `anon public` key → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
3. Go to **Settings → Database → Connection string**:
   - **Transaction pooler** URI → `DATABASE_URL` (append `?pgbouncer=true&connection_limit=1`)
   - **Direct connection** URI → `DIRECT_URL` (used for migrations)
4. Enable **Email auth** in **Authentication → Providers**.
5. In `.env.local`: set `DEV_AUTH=""` (empty string disables mock auth) and fill in Supabase vars.
6. In `prisma/schema.prisma`: change `provider` from `"sqlite"` to `"postgresql"`.
7. Run migrations using the direct URL:
   ```bash
   DATABASE_URL="<direct-connection-url>" npx prisma migrate dev --name init
   ```

---

## Dev vs Production

| | Local | Production |
|---|---|---|
| Database | SQLite (`prisma/dev.db`) | Supabase PostgreSQL |
| Auth | Mock cookie (`dev-session`) | Supabase Auth |
| `DEV_AUTH` | `"true"` | `""` or unset |
| Schema provider | `sqlite` | `postgresql` |

---

## Scripts

```bash
npm run dev              # Start dev server → http://localhost:3000
npm run build            # Production build
npm run start            # Start production server
npm run lint             # ESLint

npx prisma migrate dev   # Run pending migrations
npx prisma studio        # Open Prisma visual DB explorer
npx prisma generate      # Regenerate Prisma client after schema changes
```

---

## Project Structure

```
src/
├── actions/
│   ├── auth.ts               # login / signup / logout / devLogin
│   └── sales-planning.ts     # CRUD + FIFO sync to optimized table
├── app/
│   ├── api/export/route.ts   # GET → Excel download
│   ├── auth/login/page.tsx
│   ├── layout.tsx
│   └── page.tsx              # Main dashboard
├── components/
│   ├── auth/auth-form.tsx    # Dev login card + Supabase form
│   └── planning/
│       ├── planning-form.tsx  # Create / edit form (RHF + Zod)
│       ├── planning-table.tsx # Filterable table with edit / delete
│       └── export-button.tsx
├── lib/
│   ├── auth.ts               # getUser() — dev cookie OR Supabase
│   ├── prisma.ts             # Prisma singleton
│   ├── supabase/             # client / server / middleware helpers
│   └── validations.ts        # Zod schema
├── middleware.ts              # Auth guard
└── types/index.ts

prisma/
├── schema.prisma             # SalesPlanning + SalesPlanningOptimized
├── migrations/               # SQL migrations
└── dev.db                    # SQLite file (local only — add to .gitignore)
```

---

## Deployment to Vercel

All `.env*` files are gitignored — no environment file is uploaded to Vercel automatically. Every variable must be set manually in **Settings → Environment Variables**.

1. Push the repository to GitHub.
2. Import at [vercel.com](https://vercel.com).
3. Add the following variables under **Settings → Environment Variables**:

| Variable | Required | Notes |
|---|---|---|
| `DATABASE_URL` | Yes | Transaction pooler URL (pgbouncer) |
| `NEXT_PUBLIC_SUPABASE_URL` | Yes | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | Supabase anon/public key |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Server-side only — enables user management |
| `ADMIN_EMAILS` | Yes | Comma-separated list of admin emails. Controls `user.isAdmin`. Independent of `ADMIN_EMAIL_EXCEPTIONS` |
| `ALLOW_PUBLIC_REGISTER` | Recommended | Set to `"false"` to disable self-registration |
| `PLANNER_SERVICE_URL` | If using planner | URL of the planning microservice |
| `PLANNER_SERVICE_TOKEN` | If using planner | Bearer token for the planning microservice |
| `TZ` | Recommended | Set to `America/Santiago` |
| `DEV_AUTH` | No | Must be absent or empty in production |

4. Deploy — Vercel runs `npm run build` automatically.
