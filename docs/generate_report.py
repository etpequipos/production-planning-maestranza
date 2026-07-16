#!/usr/bin/env python3
"""
Generate professional PDF report for ETP Maestranza production planning system.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import datetime

# ── Color palette ──────────────────────────────────────────────────────────────
AMBER_DARK   = HexColor("#78350F")   # amber-900
AMBER_MED    = HexColor("#92400E")   # amber-800
AMBER_LIGHT  = HexColor("#FEF3C7")   # amber-50
AMBER_ACCENT = HexColor("#F59E0B")   # amber-400
GRAY_DARK    = HexColor("#1C1917")   # stone-900
GRAY_MED     = HexColor("#44403C")   # stone-700
GRAY_LIGHT   = HexColor("#F5F5F4")   # stone-100
GRAY_BORDER  = HexColor("#D6D3D1")   # stone-300
WHITE        = colors.white
BLACK        = colors.black

OUTPUT_PATH = "/Users/cami/Documents/Proyecto Producción ETP spa/Informe_Motor_Planificacion_ETP.pdf"

# ── Page layout ────────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
MARGIN_L = 2.2 * cm
MARGIN_R = 2.2 * cm
MARGIN_T = 2.5 * cm
MARGIN_B = 2.5 * cm
BODY_W   = PAGE_W - MARGIN_L - MARGIN_R


# ── Header / Footer ────────────────────────────────────────────────────────────
class HeaderFooterCanvas(canvas.Canvas):
    """Adds page-level header stripe and footer to every page except the cover."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._page_counter = 0

    def showPage(self):
        self._page_counter += 1
        self._draw_page_decorations()
        super().showPage()

    def save(self):
        super().save()

    def _draw_page_decorations(self):
        if self._page_counter == 1:
            return  # cover page — no header/footer

        w, h = A4

        # Top accent bar
        self.setFillColor(AMBER_MED)
        self.rect(0, h - 14*mm, w, 14*mm, fill=1, stroke=0)

        # Header text
        self.setFillColor(WHITE)
        self.setFont("Helvetica-Bold", 8)
        self.drawString(MARGIN_L, h - 9*mm, "INFORME TÉCNICO — Motor de Planificación CP-SAT")
        self.setFont("Helvetica", 7)
        self.drawRightString(w - MARGIN_R, h - 9*mm, "ETP Maestranza  |  Versión 1.0")

        # Bottom footer
        self.setFillColor(GRAY_LIGHT)
        self.rect(0, 0, w, 11*mm, fill=1, stroke=0)

        # Footer separator line
        self.setStrokeColor(AMBER_ACCENT)
        self.setLineWidth(0.8)
        self.line(MARGIN_L, 11*mm, w - MARGIN_R, 11*mm)

        # Footer text
        self.setFillColor(GRAY_MED)
        self.setFont("Helvetica", 7)
        self.drawString(MARGIN_L, 4*mm, "ETP Maestranza — Confidencial")
        self.drawCentredString(w / 2, 4*mm, "19 de abril de 2026")
        self.setFont("Helvetica-Bold", 7)
        self.drawRightString(w - MARGIN_R, 4*mm, f"Página {self._page_counter - 1}")


# ── Styles ─────────────────────────────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()

    styles = {}

    styles["cover_title"] = ParagraphStyle(
        "cover_title",
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=32,
        textColor=WHITE,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    styles["cover_subtitle"] = ParagraphStyle(
        "cover_subtitle",
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        textColor=AMBER_LIGHT,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    styles["cover_meta"] = ParagraphStyle(
        "cover_meta",
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=HexColor("#FDE68A"),
        alignment=TA_CENTER,
    )
    styles["section_header"] = ParagraphStyle(
        "section_header",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=WHITE,
        spaceAfter=0,
        spaceBefore=0,
        leftIndent=6,
    )
    styles["subsection_header"] = ParagraphStyle(
        "subsection_header",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=AMBER_DARK,
        spaceBefore=10,
        spaceAfter=4,
    )
    styles["body"] = ParagraphStyle(
        "body",
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=GRAY_DARK,
        spaceBefore=2,
        spaceAfter=2,
        alignment=TA_JUSTIFY,
    )
    styles["bullet"] = ParagraphStyle(
        "bullet",
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=GRAY_DARK,
        leftIndent=14,
        bulletIndent=4,
        spaceBefore=1,
        spaceAfter=1,
    )
    styles["code"] = ParagraphStyle(
        "code",
        fontName="Courier",
        fontSize=8.5,
        leading=12,
        textColor=GRAY_DARK,
        backColor=GRAY_LIGHT,
        leftIndent=10,
        rightIndent=10,
        spaceBefore=2,
        spaceAfter=2,
    )
    styles["code_comment"] = ParagraphStyle(
        "code_comment",
        fontName="Courier-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=HexColor("#6B7280"),
        backColor=GRAY_LIGHT,
        leftIndent=10,
        rightIndent=10,
        spaceBefore=0,
        spaceAfter=0,
    )
    styles["table_header"] = ParagraphStyle(
        "table_header",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=WHITE,
        alignment=TA_CENTER,
    )
    styles["table_cell"] = ParagraphStyle(
        "table_cell",
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=GRAY_DARK,
    )
    styles["table_cell_center"] = ParagraphStyle(
        "table_cell_center",
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=GRAY_DARK,
        alignment=TA_CENTER,
    )
    styles["field_name"] = ParagraphStyle(
        "field_name",
        fontName="Courier-Bold",
        fontSize=8.5,
        leading=12,
        textColor=AMBER_DARK,
    )
    styles["caption"] = ParagraphStyle(
        "caption",
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=GRAY_MED,
        alignment=TA_CENTER,
        spaceBefore=2,
        spaceAfter=6,
    )

    return styles


# ── Helper flowables ────────────────────────────────────────────────────────────
def section_header(number, title, styles):
    """Returns a colored section header block."""
    text = f"  {number}.  {title}"
    p = Paragraph(text, styles["section_header"])
    tbl = Table([[p]], colWidths=[BODY_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AMBER_MED),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("ROUNDEDCORNERS", [3]),
    ]))
    return [Spacer(1, 10), tbl, Spacer(1, 6)]


def subsection(title, styles):
    return [Paragraph(title, styles["subsection_header"])]


def bullet_item(text, styles):
    return Paragraph(f"• {text}", styles["bullet"])


def hr():
    return HRFlowable(width=BODY_W, thickness=0.5, color=GRAY_BORDER, spaceAfter=4, spaceBefore=4)


def code_block(lines, styles):
    items = []
    for line in lines:
        if line.startswith("#"):
            items.append(Paragraph(line, styles["code_comment"]))
        else:
            items.append(Paragraph(line if line else " ", styles["code"]))
    return items


def field_table(rows, styles):
    """
    rows: list of (field_name, type_and_description)
    """
    data = [[
        Paragraph("Campo", styles["table_header"]),
        Paragraph("Tipo / Descripción", styles["table_header"]),
    ]]
    for fname, fdesc in rows:
        data.append([
            Paragraph(fname, styles["field_name"]),
            Paragraph(fdesc, styles["table_cell"]),
        ])

    col_widths = [BODY_W * 0.30, BODY_W * 0.70]
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        # Header row
        ("BACKGROUND",    (0, 0), (-1, 0), AMBER_MED),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("TOPPADDING",    (0, 0), (-1, 0), 5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        # Data rows alternating
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GRAY_LIGHT]),
        ("TOPPADDING",    (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        # Grid
        ("GRID",          (0, 0), (-1, -1), 0.4, GRAY_BORDER),
        ("LINEBELOW",     (0, 0), (-1, 0), 1.2, AMBER_ACCENT),
    ]))
    return [tbl, Spacer(1, 6)]


def process_table(rows, styles):
    """
    Tabla de procesos: orden, proceso, capacidad
    """
    data = [[
        Paragraph("Orden", styles["table_header"]),
        Paragraph("Proceso", styles["table_header"]),
        Paragraph("Cap./día", styles["table_header"]),
    ]]
    for orden, proceso, cap in rows:
        data.append([
            Paragraph(str(orden), styles["table_cell_center"]),
            Paragraph(proceso, styles["table_cell"]),
            Paragraph(str(cap), styles["table_cell_center"]),
        ])

    col_widths = [BODY_W * 0.15, BODY_W * 0.60, BODY_W * 0.25]
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), AMBER_MED),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GRAY_LIGHT]),
        ("GRID",          (0, 0), (-1, -1), 0.4, GRAY_BORDER),
        ("LINEBELOW",     (0, 0), (-1, 0), 1.2, AMBER_ACCENT),
        ("ALIGN",         (0, 0), (0, -1), "CENTER"),
        ("ALIGN",         (2, 0), (2, -1), "CENTER"),
    ]))
    return [tbl, Spacer(1, 6)]


# ── Cover page ─────────────────────────────────────────────────────────────────
def cover_page(styles):
    """Returns a list of flowables that form the cover page."""

    class CoverBackground(Flowable):
        def draw(self):
            c = self.canv
            w, h = A4

            # Full-page dark background
            c.setFillColor(AMBER_DARK)
            c.rect(0, 0, w, h, fill=1, stroke=0)

            # Top geometric accent
            c.setFillColor(AMBER_MED)
            c.rect(0, h - 5*cm, w, 5*cm, fill=1, stroke=0)

            # Diagonal accent strip
            c.setFillColor(HexColor("#451A03"))  # amber-950
            p = c.beginPath()
            p.moveTo(0, h - 5*cm)
            p.lineTo(w, h - 5*cm)
            p.lineTo(w, h - 7*cm)
            p.lineTo(0, h - 5.5*cm)
            p.close()
            c.drawPath(p, fill=1, stroke=0)

            # Bottom strip
            c.setFillColor(HexColor("#451A03"))
            c.rect(0, 0, w, 3*cm, fill=1, stroke=0)

            # Amber accent line
            c.setFillColor(AMBER_ACCENT)
            c.rect(MARGIN_L, h - 5.2*cm - 3*mm, w - MARGIN_L - MARGIN_R, 3*mm, fill=1, stroke=0)

            # Logo placeholder box
            logo_w, logo_h = 5*cm, 2*cm
            logo_x = (w - logo_w) / 2
            logo_y = h - 3.8*cm
            c.setFillColor(AMBER_ACCENT)
            c.roundRect(logo_x, logo_y, logo_w, logo_h, 4*mm, fill=1, stroke=0)
            c.setFillColor(AMBER_DARK)
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(w / 2, logo_y + 0.6*cm, "ETP")

        def wrap(self, availWidth, availHeight):
            return (0, 0)

    elements = []
    elements.append(CoverBackground())

    # Vertical spacing to push title into center area
    elements.append(Spacer(1, 6.5*cm))

    elements.append(Paragraph(
        "INFORME TÉCNICO",
        styles["cover_meta"]
    ))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(
        "Motor de Planificación CP-SAT",
        styles["cover_title"]
    ))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(
        "ETP Maestranza",
        styles["cover_subtitle"]
    ))
    elements.append(Spacer(1, 1.2*cm))

    # Horizontal rule
    elements.append(HRFlowable(
        width=BODY_W * 0.5,
        thickness=1.5,
        color=AMBER_ACCENT,
        spaceAfter=1*cm,
        spaceBefore=0,
        hAlign="CENTER",
    ))

    # Meta info table
    meta_data = [
        ["Fecha", "19 de abril de 2026"],
        ["Versión", "1.0 — MVP Fase 1"],
        ["Clasificación", "Confidencial"],
        ["Proyecto", "Sistema de Planificación de Producción"],
    ]
    meta_style = ParagraphStyle(
        "meta_label",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=AMBER_ACCENT,
    )
    meta_val_style = ParagraphStyle(
        "meta_val",
        fontName="Helvetica",
        fontSize=9,
        textColor=WHITE,
    )
    meta_rows = [
        [Paragraph(k, meta_style), Paragraph(v, meta_val_style)]
        for k, v in meta_data
    ]
    meta_tbl = Table(meta_rows, colWidths=[BODY_W * 0.35, BODY_W * 0.65])
    meta_tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.3, HexColor("#92400E")),
    ]))
    elements.append(meta_tbl)

    elements.append(PageBreak())
    return elements


# ── Section 1: Database Models ─────────────────────────────────────────────────
def section1(styles):
    items = []
    items += section_header("1", "Modelos Creados en Base de Datos", styles)

    items.append(Paragraph(
        "Se crearon cuatro modelos Prisma en la base de datos SQLite (dev.db) del proyecto etp-app. "
        "Estos modelos conforman la capa de datos del motor de planificación y almacenan las reglas "
        "de producción, las restricciones de capacidad y los resultados del planificador.",
        styles["body"]
    ))
    items.append(Spacer(1, 6))

    # ── LeadTimeByCode ──────────────────────────────────────────────────────────
    items += subsection("1.1  LeadTimeByCode  (tabla: lead_time_by_code)", styles)
    items += field_table([
        ("id",               "TEXT — Clave primaria (CUID)"),
        ("codigo_plazo",     "TEXT — Tipo de equipo, valores 1 a 17"),
        ("descripcion_equipo","TEXT — Descripción legible del equipo"),
        ("proceso",          "TEXT — Nombre del proceso productivo"),
        ("duracion_dias",    "INTEGER — Días hábiles requeridos por el proceso"),
    ], styles)
    items += [
        bullet_item("Restricción de unicidad compuesta: <b>(codigo_plazo, proceso)</b>", styles),
        bullet_item("Registros cargados: <b>187</b>  (17 tipos de equipo × 11 procesos)", styles),
        Spacer(1, 4),
    ]

    # ── ProcessCapacity ─────────────────────────────────────────────────────────
    items += subsection("1.2  ProcessCapacity  (tabla: process_capacity)", styles)
    items += field_table([
        ("id",                "TEXT — Clave primaria (CUID)"),
        ("proceso",           "TEXT — Nombre del proceso (UNIQUE)"),
        ("orden",             "INTEGER — Orden global de ejecución"),
        ("capacidad_por_dia", "INTEGER — Equipos simultáneos máximos por día"),
    ], styles)
    items += [
        bullet_item("Registros cargados: <b>11 procesos</b>", styles),
        Spacer(1, 4),
    ]

    # ── OptimizedProcessSchedule ────────────────────────────────────────────────
    items += subsection("1.3  OptimizedProcessSchedule  (tabla: optimized_process_schedule)", styles)
    items += field_table([
        ("id",               "TEXT — Clave primaria (CUID)"),
        ("sales_planning_id","TEXT — FK → sales_planning (registro de equipo)"),
        ("proceso",          "TEXT — Nombre del proceso"),
        ("orden",            "INTEGER — Orden de ejecución"),
        ("start_date",       "DATETIME — Fecha/hora de inicio del proceso"),
        ("end_date",         "DATETIME — Fecha/hora de fin del proceso"),
        ("duration_days",    "INTEGER — Duración en días hábiles"),
    ], styles)
    items += [
        bullet_item("Permite trazabilidad completa: cada equipo tiene un registro por proceso.", styles),
        Spacer(1, 4),
    ]

    # ── SalesPlanningOptimized ──────────────────────────────────────────────────
    items += subsection("1.4  SalesPlanningOptimized  (tabla: sales_planning_optimized) — actualizado", styles)
    items += field_table([
        ("start_date",   "DATETIME — Inicio del job completo (primer proceso)"),
        ("end_date",     "DATETIME — Fin del job completo (último proceso)"),
        ("prioridad",    "INTEGER — Prioridad del equipo (1–10)"),
        ("codigo_plazo", "TEXT — Tipo de equipo (referencia a lead times)"),
    ], styles)
    items += [
        bullet_item("Campos añadidos en esta versión al modelo existente.", styles),
        bullet_item("Almacena el resultado <i>agregado por equipo</i> (inicio/fin del job completo).", styles),
        Spacer(1, 4),
    ]

    return items


# ── Section 2: Seed Script ─────────────────────────────────────────────────────
def section2(styles):
    items = []
    items += section_header("2", "Carga desde Excel (seed_rules.py)", styles)

    items.append(Paragraph(
        "El script <b>scripts/seed_rules.py</b> lee el archivo Excel de reglas de planificación y carga "
        "los datos en la base de datos mediante UPSERT, garantizando idempotencia en ejecuciones repetidas.",
        styles["body"]
    ))
    items.append(Spacer(1, 4))
    items += [
        bullet_item("Archivo fuente: <b>data/Reglas_Planificación.xlsx</b>", styles),
        bullet_item("Conexión directa a SQLite: <b>etp-app/dev.db</b>", styles),
        Spacer(1, 6),
    ]

    items += subsection("Hojas leídas", styles)
    items += [
        bullet_item(
            "<b>CÓDIGO PLAZO Y DEMORAS EN DÍAS</b> — 17 tipos de equipo × 11 procesos = 187 registros en lead_time_by_code",
            styles
        ),
        bullet_item(
            "<b>CAPACIDAD POR PROCESO</b> — 11 procesos con orden y capacidad diaria en process_capacity",
            styles
        ),
        Spacer(1, 8),
    ]

    items += subsection("Procesos cargados", styles)
    process_rows = [
        (1,  "INGENIERÍA",          2),
        (2,  "CORTE",               3),
        (3,  "PLEGADO",             2),
        (4,  "ARMADO",              2),
        (5,  "REMATE",              2),
        (7,  "MONTAJE",             3),
        (8,  "HIDRÁULICA",          6),
        (10, "PINTURA",             2),
        (11, "TERMINACIONES",       2),
        (12, "CONTROL DE CALIDAD",  1),
        (0,  "INSPECCIÓN",          "0  (excluido del planificador)"),
    ]
    items += process_table(process_rows, styles)
    items.append(Paragraph(
        "Tabla 1. Procesos productivos: orden de ejecución y capacidad máxima diaria.",
        styles["caption"]
    ))

    return items


# ── Section 3: CP-SAT Engine ───────────────────────────────────────────────────
def section3(styles):
    items = []
    items += section_header("3", "Motor CP-SAT  (scripts/planner.py)", styles)

    items.append(Paragraph(
        "El planificador utiliza la biblioteca <b>Google OR-Tools CP-SAT</b> (ortools v9.15), "
        "un solver de programación con restricciones orientado a problemas de scheduling industrial. "
        "El modelo formulado es un <i>Job-Shop con recursos compartidos</i> y función objetivo de "
        "minimización de tardanza ponderada.",
        styles["body"]
    ))
    items.append(Spacer(1, 6))

    # ── Variables ───────────────────────────────────────────────────────────────
    items += subsection("3.1  Variables de decisión", styles)
    items += code_block([
        "start[j][p]    ∈  [llegada_day, HORIZON]   # día hábil de inicio de tarea",
        "end[j][p]      =  start[j][p] + duration[j][p]",
        "interval[j][p] =  IntervalVar(start, duration, end)",
    ], styles)
    items.append(Spacer(1, 6))

    # ── Constraints ─────────────────────────────────────────────────────────────
    items += subsection("3.2  Restricciones", styles)
    items += [
        bullet_item(
            "<b>No-earlier-than:</b>  start[j][0] ≥ workday(llegada[j])  — "
            "ningún proceso puede iniciar antes de la fecha de llegada del equipo.",
            styles
        ),
        bullet_item(
            "<b>Precedencia:</b>  start[j][p] ≥ end[j][p-1]  para p &gt; 0  — "
            "cada proceso debe esperar la finalización del anterior.",
            styles
        ),
        bullet_item(
            "<b>Capacidad (Cumulative):</b>  Σ demand[j][p] ≤ capacidad_por_dia[p]  "
            "en todo momento  — no se supera la capacidad simultánea de ningún proceso.",
            styles
        ),
        Spacer(1, 4),
    ]

    items += subsection("3.3  Filtros de proceso", styles)
    items.append(Paragraph(
        "Un proceso es excluido del modelo si se cumple alguna de las siguientes condiciones:",
        styles["body"]
    ))
    items += [
        bullet_item("duracion_dias = 0 para ese tipo de equipo, O", styles),
        bullet_item("capacidad_por_dia = 0, O", styles),
        bullet_item("orden = 0  (e.g. INSPECCIÓN)", styles),
        Spacer(1, 6),
    ]

    # ── Objective ───────────────────────────────────────────────────────────────
    items += subsection("3.4  Función objetivo", styles)
    items.append(Paragraph(
        "Minimizar la <b>tardanza total ponderada por prioridad</b>:",
        styles["body"]
    ))
    items += code_block([
        "min  Σ_j  ( tardanza[j] × peso[j] )",
        "",
        "# donde:",
        "tardanza[j]  =  max( 0,  end[j][last] − due_date[j] )",
        "due_date[j]  =  llegada[j] + Σ duraciones[j] + atraso[j]",
        "peso[j]      =  100 ÷ prioridad[j]",
        "               # prioridad 1 → peso 100  |  prioridad 5 → peso 20",
    ], styles)
    items.append(Spacer(1, 6))

    # ── Solver config ───────────────────────────────────────────────────────────
    items += subsection("3.5  Configuración del solver", styles)
    items += [
        bullet_item("Tiempo límite: <b>30 segundos</b>", styles),
        bullet_item("Workers paralelos: <b>4</b>", styles),
        Spacer(1, 6),
    ]

    # ── Working days ────────────────────────────────────────────────────────────
    items += subsection("3.6  Días hábiles", styles)
    items += [
        bullet_item("Solo <b>lunes a viernes</b>. Sábado y domingo excluidos automáticamente.", styles),
        bullet_item("Sin feriados en esta fase (Fase 1).", styles),
        bullet_item(
            "Referencia: lunes al inicio o antes de la fecha mínima de llegada del lote.",
            styles
        ),
        bullet_item(
            "Conversión date → workday: cuenta días Mon–Fri entre referencia y fecha.",
            styles
        ),
        bullet_item(
            "Conversión workday → date: avanza días hábiles desde la referencia.",
            styles
        ),
        Spacer(1, 4),
    ]

    return items


# ── Section 4: Priority and Delay ─────────────────────────────────────────────
def section4(styles):
    items = []
    items += section_header("4", "Uso de Prioridad y Atraso", styles)

    # ── Prioridad ───────────────────────────────────────────────────────────────
    items += subsection("4.1  Prioridad", styles)
    items += [
        bullet_item("Escala <b>1–10</b>  (1 = más urgente, 10 = menos urgente).", styles),
        bullet_item("Campo <b>OBLIGATORIO</b> desde esta versión del sistema.", styles),
        bullet_item("Usado como peso en la función objetivo:  <b>peso = 100 ÷ prioridad</b>", styles),
        bullet_item("Un equipo P1 tiene <b>10×</b> más peso que uno P10.", styles),
        Spacer(1, 6),
    ]

    # ── Atraso ──────────────────────────────────────────────────────────────────
    items += subsection("4.2  Atraso (buffer)", styles)
    items += [
        bullet_item("Días hábiles de margen tolerados después de la duración nominal.", styles),
        bullet_item("Campo <b>OBLIGATORIO</b>  (valor 0 = sin tolerancia de atraso).", styles),
        bullet_item(
            "due_date = llegada + Σ duración_procesos + atraso", styles
        ),
        bullet_item("La tardanza se penaliza sólo si  fin &gt; due_date.", styles),
        Spacer(1, 6),
    ]

    # ── Campos obligatorios ─────────────────────────────────────────────────────
    items += subsection("4.3  Campos obligatorios en el formulario", styles)
    items += field_table([
        ("codigo_plazo", "Define los procesos y duraciones del equipo (1–17)"),
        ("llegada",      "Fecha de llegada — restricción no-earlier-than del primer proceso"),
        ("prioridad",    "Escala 1–10 — peso en la función objetivo"),
        ("atraso",       "Días hábiles de buffer (≥ 0, valor 0 = sin tolerancia)"),
    ], styles)

    return items


# ── Section 5: Commands ────────────────────────────────────────────────────────
def section5(styles):
    items = []
    items += section_header("5", "Comandos a Ejecutar", styles)

    items += subsection("5.1  Setup inicial (solo primera vez)", styles)
    items += code_block([
        "# Instalar dependencias Python",
        "pip3 install ortools openpyxl",
        "",
        "# Cargar reglas desde Excel",
        "python3 scripts/seed_rules.py",
    ], styles)
    items.append(Spacer(1, 6))

    items += subsection("5.2  Servidor de desarrollo", styles)
    items += code_block([
        "cd etp-app",
        "npm run dev",
        "# Abrir: http://localhost:3000",
    ], styles)
    items.append(Spacer(1, 6))

    items += subsection("5.3  Prisma (si se modifican modelos)", styles)
    items += code_block([
        "# Usar Node.js v22 (requerido por Prisma 7)",
        'export PATH="$HOME/.local/share/fnm/node-versions/v22.22.2/installation/bin:$PATH"',
        "npx prisma generate",
    ], styles)
    items.append(Spacer(1, 6))

    items += subsection("5.4  Re-cargar reglas de planificación", styles)
    items += code_block([
        "python3 scripts/seed_rules.py [ruta_db_opcional]",
    ], styles)
    items.append(Spacer(1, 6))

    items += subsection("5.5  Planificar manualmente (sin UI)", styles)
    items += code_block([
        "python3 scripts/planner.py [ruta_db_opcional]",
    ], styles)
    items.append(Spacer(1, 6))

    return items


# ── Section 6: Server Restart ──────────────────────────────────────────────────
def section6(styles):
    items = []
    items += section_header("6", "Reinicio del Servidor", styles)

    items.append(Paragraph(
        "Es necesario reiniciar el servidor Next.js después de cualquier cambio en el schema "
        "de Prisma o regeneración del cliente.",
        styles["body"]
    ))
    items.append(Spacer(1, 4))
    items += [
        bullet_item("La migración de schema se aplica directamente al SQLite.", styles),
        bullet_item("El cliente Prisma debe ser regenerado con <b>npx prisma generate</b>.", styles),
        bullet_item("El build de producción debe verificarse sin errores antes del deploy.", styles),
        Spacer(1, 6),
    ]
    items += subsection("Comando de reinicio", styles)
    items += code_block([
        "cd etp-app && npm run dev",
    ], styles)
    items.append(Spacer(1, 4))

    return items


# ── Section 7: Limitations ────────────────────────────────────────────────────
def section7(styles):
    items = []
    items += section_header("7", "Limitaciones Actuales", styles)

    items.append(Paragraph(
        "Las siguientes limitaciones son conocidas en la Fase 1 (MVP). "
        "Serán abordadas en fases posteriores del proyecto.",
        styles["body"]
    ))
    items.append(Spacer(1, 6))

    limitations = [
        (
            "Sin feriados",
            "Solo se excluyen sábados y domingos. No se consideran feriados chilenos ni días de parada "
            "programada. Impacto: las fechas planificadas pueden no coincidir con el calendario real."
        ),
        (
            "Sin talleres / recursos específicos",
            "El modelo asume que un equipo ocupa 1 unidad de capacidad por proceso. No hay modelado "
            "de operarios específicos ni máquinas individuales."
        ),
        (
            "Capacidad diaria vs. simultáneo",
            "La restricción Cumulative modela días laborales como intervalos enteros. Un equipo con "
            "duración = 2 ocupa 2 slots consecutivos."
        ),
        (
            "Procesamiento síncrono",
            "El botón \"Planificar\" bloquea la UI hasta que el solver termina (máx. 30 s). "
            "Para flotas grandes se recomienda implementar un job asíncrono (queue + polling)."
        ),
        (
            "Sin replanificación incremental",
            "Cada ejecución limpia el plan anterior completo. No es posible fijar tareas ya iniciadas "
            "y replanificar solo las pendientes."
        ),
        (
            "Sin mantenimiento de equipos",
            "No se modela tiempo muerto de proceso entre equipos (setup time, limpieza, calibración)."
        ),
        (
            "Node.js v22 requerido para Prisma 7",
            "La versión del sistema (v18) no es compatible. Se debe usar fnm con v22.22.2 para todas "
            "las operaciones Prisma (generate, migrate, studio)."
        ),
        (
            "Datos de prueba — migración manual",
            "La migración se aplicó manualmente para preservar los registros existentes. "
            "En producción utilizar <b>npx prisma migrate deploy</b>."
        ),
    ]

    # Build numbered limitation table
    data = [[
        Paragraph("#", styles["table_header"]),
        Paragraph("Limitación", styles["table_header"]),
        Paragraph("Descripción", styles["table_header"]),
    ]]
    for i, (title, desc) in enumerate(limitations, 1):
        data.append([
            Paragraph(str(i), styles["table_cell_center"]),
            Paragraph(f"<b>{title}</b>", styles["table_cell"]),
            Paragraph(desc, styles["table_cell"]),
        ])

    col_widths = [BODY_W * 0.06, BODY_W * 0.27, BODY_W * 0.67]
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), AMBER_MED),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GRAY_LIGHT]),
        ("GRID",          (0, 0), (-1, -1), 0.4, GRAY_BORDER),
        ("LINEBELOW",     (0, 0), (-1, 0), 1.2, AMBER_ACCENT),
        ("ALIGN",         (0, 0), (0, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    items.append(tbl)
    items.append(Spacer(1, 6))

    return items


# ── Build document ─────────────────────────────────────────────────────────────
def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=MARGIN_L,
        rightMargin=MARGIN_R,
        topMargin=MARGIN_T + 14*mm,   # extra for header bar on body pages
        bottomMargin=MARGIN_B + 11*mm, # extra for footer bar
        title="Informe Técnico — Motor de Planificación CP-SAT",
        author="ETP Maestranza",
        subject="Sistema de Planificación de Producción — Fase 1 MVP",
    )

    styles = build_styles()

    story = []
    story += cover_page(styles)
    story += section1(styles)
    story += section2(styles)
    story += section3(styles)
    story += section4(styles)
    story += section5(styles)
    story += section6(styles)
    story += section7(styles)

    # Final spacer
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width=BODY_W, thickness=0.8, color=AMBER_ACCENT))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "— Fin del informe —",
        ParagraphStyle(
            "end",
            fontName="Helvetica-Oblique",
            fontSize=9,
            textColor=GRAY_MED,
            alignment=TA_CENTER,
        )
    ))

    doc.build(story, canvasmaker=HeaderFooterCanvas)
    print(f"PDF generado exitosamente: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()
