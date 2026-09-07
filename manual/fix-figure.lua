-- Convert pandoc Figure blocks into non-floating LaTeX figures
-- ([H] placement) so they stay exactly in place in the text.
function Figure(el)
  local src, width, alt
  local function walk(blk)
    if blk.t == "Image" then
      src = blk.src
      width = blk.attributes["width"]
      alt = pandoc.utils.stringify(blk.alt or {})
      return true
    elseif blk.content then
      for _, b in ipairs(blk.content) do
        if walk(b) then return true end
      end
    end
  end
  for _, b in ipairs(el.content) do
    walk(b)
  end
  if not src then return nil end
  -- Convert width percent (e.g. "42%") to a fraction of linewidth
  local w = width and width:match("^%s*([%d%.]+)%s*%%%s*$")
  if w then
    w = (tonumber(w) / 100)
    w = string.format("%.2f", w) .. "\\linewidth"
  else
    w = "1.0\\linewidth"
  end
  local caption = pandoc.utils.stringify(el.caption)
  return pandoc.RawBlock("latex",
    "\\begin{figure}[H]\n\\centering\n" ..
    "\\includegraphics[width=" .. w .. ",height=\\textheight,keepaspectratio,alt={" ..
    (alt or "") .. "}]{" .. src .. "}\n" ..
    "\\caption{" .. caption .. "}\n" ..
    "\\end{figure}")
end