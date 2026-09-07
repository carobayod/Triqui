-- Envuelve los blockquotes de CONSEJO y BUG ALERT en marcos
-- decorados (tcolorbox) cuando se genera LaTeX/PDF.
-- En otros formatos los deja como blockquote normal.

local function is_latex()
  return FORMAT == "latex" or FORMAT == "beamer"
end

function BlockQuote(el)
  if not is_latex() then return nil end
  local s = pandoc.utils.stringify(el)

  local kind
  if s:match("BUG ALERT") then
    kind = "bug"
  elseif s:match("CONSEJO") then
    kind = "consejo"
  else
    return nil
  end

  local col, bg
  if kind == "consejo" then
    col, bg = "consejocolor", "consejobg"
  else
    col, bg = "bugcolor", "bugbg"
  end

  local open = pandoc.RawBlock("latex",
    "\\begin{center}\\begin{tcolorbox}[colback=" .. bg .. ", colframe=" .. col ..
    ", arc=2.5mm, boxrule=1pt, boxsep=10pt, left=12pt, right=12pt, top=10pt, bottom=10pt, width=0.95\\textwidth]\n")
  local close = pandoc.RawBlock("latex",
    "\n\\end{tcolorbox}\\end{center}")
  return { open, el, close }
end