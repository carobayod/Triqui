function RawBlock(el)
  if el.format == "tex" and el.text:match("^\\newpage") then
    return {}
  end
end