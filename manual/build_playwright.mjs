#!/usr/bin/env node
/**
 * Genera los PDF del libro con Chromium (Playwright) para comparar visualmente
 * con los de WeasyPrint que produce templates_canva/build_canva.py.
 *
 * NO modifica ni sustituye el pipeline de WeasyPrint: solo lee el mismo HTML.
 * El HTML se genera importando build_canva.py, de modo que la comparacion
 * entre motores es justa (mismo HTML byte a byte, solo cambia el renderizador).
 *
 * Uso:  node build_playwright.mjs [A|B|C ...]      (por defecto: A B C)
 */
import { chromium } from "./playwright/node_modules/playwright/index.mjs";
import { execFileSync } from "node:child_process";
import { writeFileSync, readFileSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const MANUAL = HERE;
const TEMPLATES = resolve(HERE, "templates_canva");
const TMP = "/tmp/opencode";

// ---------- 1. HTML: idéntico al que consume WeasyPrint ----------
// Se reutiliza build_canva.pandoc_body() y add_line_numbers() para no duplicar
// la cadena de pandoc ni los regex. Solo lectura: no se toca el original.
function htmlFromCanva() {
  const py = `
import sys, json
sys.path.insert(0, ${JSON.stringify(TEMPLATES)})
import build_canva as bc
nav, content = bc.pandoc_body()
print(json.dumps({"nav": nav, "body": bc.add_line_numbers(content)}))
`;
  const out = execFileSync("python3", ["-c", py], {
    cwd: MANUAL,
    encoding: "utf-8",
    maxBuffer: 64 * 1024 * 1024,
  });
  return JSON.parse(out);
}

// ---------- 2. CSS: solo lo que Chromium no resuelve solo ----------
// target-counter(attr(href), page) devuelve "none" en Chromium. Se sustituye
// por attr(data-pg), que rellena la segunda pasada con la pagina real.
// El resto del CSS (margin boxes, counter(page), @page cover) funciona nativo.
const CSS_CHROMIUM = `
/* --- ajuste Chromium: ver build_playwright.mjs --- */
nav#TOC a::after { content: attr(data-pg); color: #64748B; }
`;

function buildHtml(theme, nav, body) {
  const css =
    readFileSync(resolve(TEMPLATES, "css_base.css"), "utf-8") +
    readFileSync(resolve(TEMPLATES, `css_${theme}.css`), "utf-8") +
    CSS_CHROMIUM;
  const cover = readFileSync(resolve(TEMPLATES, `portada_${theme}.html`), "utf-8");
  return `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Libro Chromium ${theme}</title>
<style>
${css}
</style>
</head>
<body>
${cover}
${nav}
${body}
</body>
</html>`;
}

// ---------- 3. Marcadores invisibles + segunda pasada ----------
// Chromium no resuelve target-counter, asi que se averigua la pagina de cada
// titulo por bruto: se antepone una marca invisible a cada titulo, se
// renderiza, y pdftotext dice en que pagina quedo cada marca.
//
// La marca va EN FLUJO dentro del h1 (no position:absolute): una caja absoluta
// antes de un salto de pagina aterriza en la pagina ANTERIOR a su titulo, y
// el indice queda corrido una pagina. En flujo, pdftotext la devuelve en la
// pagina correcta. Ademas no debe llevar espacios, porque pdftotext puede
// partirla en varios fragmentos.
const INJECT_MARKS = (prefix) => {
  const links = [...document.querySelectorAll('nav#TOC a[href^="#"]')];
  const ids = [...new Set(links.map((a) => decodeURIComponent(a.getAttribute("href").slice(1))))];
  const map = {};
  let i = 0;
  for (const id of ids) {
    const el = document.getElementById(id);
    if (!el) continue;
    const mark = `ZZM${prefix}${String(i).padStart(4, "0")}ZZ`;
    map[mark] = id;
    const span = document.createElement("span");
    span.className = "__tocmark";
    span.textContent = mark;
    span.style.cssText = "font-size:1px;line-height:0;color:transparent;white-space:nowrap;";
    el.insertBefore(span, el.firstChild);
    i++;
  }
  return map;
};

const FILL_PAGES = (pageOfId) => {
  let n = 0;
  for (const a of document.querySelectorAll('nav#TOC a[href^="#"]')) {
    const id = decodeURIComponent(a.getAttribute("href").slice(1));
    if (pageOfId[id] != null) a.setAttribute("data-pg", String(pageOfId[id]));
    n++;
  }
  // las marcas se dejan: son invisibles (1px, transparentes) y quitarlas
  // cambiaria el flujo y con ello la paginacion que acabamos de medir.
  return n;
};

// Lee en que pagina quedo cada marcador. Quita todo espacio antes de buscar:
// pdftotext introduce saltos dentro de la marca segun como cuts el PDF.
function pagesFromPdf(pdf) {
  const info = execFileSync("pdfinfo", [pdf], { encoding: "utf-8" });
  const pages = Number(/Pages:\s+(\d+)/.exec(info)[1]);
  const found = {};
  for (let p = 1; p <= pages; p++) {
    const txt = execFileSync("pdftotext", ["-f", String(p), "-l", String(p), pdf, "-"], {
      encoding: "utf-8",
      maxBuffer: 32 * 1024 * 1024,
    });
    for (const m of txt.matchAll(/ZZM[A-Z0-9]*\d{4}ZZ/g)) {
      if (!(m[0] in found)) found[m[0]] = p;
    }
  }
  return { pages, found };
}

// ---------- 4. Build de un tema ----------
async function build(theme, browser) {
  const { nav, body } = htmlFromCanva();
  const html = buildHtml(theme, nav, body);
  const htmlPath = `${TMP}/libro_chromium_${theme}.html`;
  writeFileSync(htmlPath, html);

  const page = await browser.newPage();
  await page.setContent(html, { waitUntil: "load" });
  // Las fuentes son locales del sistema, pero hay que esperar a que esten
  // listas: si no, Chromium mide el texto con la fuente de reserva y las
  // paginas salen mal.
  await page.evaluate(() => document.fonts.ready);

  // --- pasada 1: descubrir paginas ---
  const markMap = await page.evaluate(INJECT_MARKS, `T${theme}`);
  const probe = `${TMP}/probe_${theme}.pdf`;
  await page.pdf({
    path: probe,
    preferCSSPageSize: true,
    printBackground: true,
  });

  const { pages, found } = pagesFromPdf(probe);
  const pageOfId = {};
  for (const [mark, id] of Object.entries(markMap)) {
    if (found[mark] != null) pageOfId[id] = found[mark];
  }
  const hits = Object.keys(pageOfId).length;
  const total = Object.keys(markMap).length;

  // --- pasada 2: numeros reales en el indice ---
  const nLinks = await page.evaluate(FILL_PAGES, pageOfId);
  const out = resolve(MANUAL, `Libro_Aprende_Java_Triqui_Chromium_${theme}.pdf`);
  await page.pdf({
    path: out,
    preferCSSPageSize: true,
    printBackground: true,
  });
  await page.close();

  const bytes = readFileSync(out).length;
  const notas = [];
  if (hits < total) notas.push(`INDICE INCOMPLETO: ${total - hits}/${total} titulos sin pagina`);
  console.log(
    `OK ${theme}: ${readFileSync(out).length} bytes, ${pages} paginas, ` +
      `indice ${hits}/${total} titulos con numero (${nLinks} enlaces)`
  );
  for (const n of notas) console.log(`   AVISO ${theme}: ${n}`);
  return { theme, out, pages, hits, total };
}

// ---------- main ----------
const themes = process.argv.slice(2).filter((a) => /^[ABC]$/.test(a));
const lista = themes.length ? themes : ["A", "B", "C"];

for (const t of ["A", "B", "C"]) {
  if (!existsSync(resolve(TEMPLATES, `css_${t}.css`))) {
    console.error(`FALLO: falta templates_canva/css_${t}.css`);
    process.exit(1);
  }
}

const browser = await chromium.launch();
try {
  const res = [];
  for (const t of lista) res.push(await build(t, browser));
  console.log("");
  for (const r of res) console.log(`  ${r.theme}: ${r.pages} paginas, indice ${r.hits}/${r.total}`);
} finally {
  await browser.close();
}
