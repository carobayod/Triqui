-- Convert the "Recomendación final" blockquote into a highlighted blue box
-- in LaTeX, keeping it as a normal blockquote in other formats.
local function flatten(t)
  local out = {}
  for _, v in ipairs(t) do
    if type(v) == "table" and v.t then
      out[#out + 1] = v
    elseif type(v) == "table" then
      for _, w in ipairs(v) do out[#out + 1] = w end
    else
      out[#out + 1] = v
    end
  end
  return out
end

function BlockQuote(el)
  local s = pandoc.utils.stringify(el)
  if s:match("Recomendaci") and s:match("final") then
    local open = pandoc.RawBlock("latex",
      "\\begin{center}\\begin{tcolorbox}[colback=coverblue!10, colframe=coverblue, arc=3mm, boxsep=12pt, left=14pt, right=14pt, top=12pt, bottom=12pt, width=0.92\\textwidth]\n")
    local close = pandoc.RawBlock("latex",
      "\n\\end{tcolorbox}\\end{center}")
    return { open, el, close }
  end
end