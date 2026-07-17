/**
 * TEMPORARY diagnostic endpoint — DELETE after diagnosis is complete.
 * GET /api/plan/diagnose
 *
 * Checks, in order:
 *  1. Whether PLANNER_SERVICE_URL is configured in this environment.
 *  2. Whether Railway /health responds (no auth required).
 *  3. Whether Railway /run responds (with full stdout/stderr).
 */
import { NextResponse } from "next/server";
import { getUser } from "@/lib/auth";

export async function GET() {
  const user = await getUser();
  if (!user) return NextResponse.json({ error: "No autenticado" }, { status: 401 });
  if (!user.isAdmin) return NextResponse.json({ error: "No autorizado" }, { status: 403 });

  const serviceUrl   = process.env.PLANNER_SERVICE_URL?.replace(/\/$/, "") ?? null;
  const serviceToken = process.env.PLANNER_SERVICE_TOKEN ?? "";

  const report: Record<string, unknown> = {
    step1_env: {
      PLANNER_SERVICE_URL_set:   serviceUrl !== null,
      PLANNER_SERVICE_URL_value: serviceUrl
        ? serviceUrl.replace(/\/\/[^@]*@/, "//***@")  // redact credentials if any
        : "(not set)",
      PLANNER_SERVICE_TOKEN_set: serviceToken.length > 0,
      PLANNER_SERVICE_TOKEN_len: serviceToken.length,
    },
  };

  if (!serviceUrl) {
    report.conclusion =
      "PLANNER_SERVICE_URL no está configurada en este entorno. " +
      "El API route intentaría ejecutar python3 localmente, lo cual falla en Vercel. " +
      "Configura PLANNER_SERVICE_URL en las variables de entorno de Vercel.";
    return NextResponse.json(report);
  }

  // Step 2: Railway /health (no auth)
  try {
    const healthRes = await fetch(`${serviceUrl}/health`, {
      signal: AbortSignal.timeout(10_000),
    });
    const healthBody = await healthRes.text();
    let healthJson: unknown;
    try { healthJson = JSON.parse(healthBody); } catch { healthJson = healthBody; }
    report.step2_health = {
      status: healthRes.status,
      ok:     healthRes.ok,
      body:   healthJson,
    };
  } catch (e: unknown) {
    report.step2_health = {
      error: e instanceof Error ? e.message : String(e),
    };
    report.conclusion = "Railway /health no responde. El servicio puede estar caído o la URL es incorrecta.";
    return NextResponse.json(report);
  }

  // Step 3: Railway /run (with auth) — full response
  try {
    const runRes = await fetch(`${serviceUrl}/run`, {
      method:  "POST",
      headers: {
        "Authorization": `Bearer ${serviceToken}`,
        "Content-Type":  "application/json",
      },
      signal: AbortSignal.timeout(130_000),
    });
    const runBody = await runRes.text();
    let runJson: unknown;
    try { runJson = JSON.parse(runBody); } catch { runJson = runBody; }
    report.step3_run = {
      status:   runRes.status,
      ok:       runRes.ok,
      body:     runJson,
    };
    if (!runRes.ok) {
      report.conclusion = `Railway /run respondió HTTP ${runRes.status}. Ver step3_run.body para detalle.`;
    } else {
      report.conclusion = "Railway /run respondió OK. Ver step3_run.body para stdout/stderr del planner.";
    }
  } catch (e: unknown) {
    report.step3_run = {
      error: e instanceof Error ? e.message : String(e),
    };
    report.conclusion = "Fetch a Railway /run lanzó excepción. Ver step3_run.error.";
  }

  return NextResponse.json(report, { status: 200 });
}
