function Str(el)
  local s = el.text
    :gsub('\227\132\128', '')   -- ⚠️ (con selector)
    :gsub('\226\154\160', '')   -- ⚠
    :gsub('\239\184\143', '')   -- U+FE0F selector de variación emoji
    :gsub('\240\159\143\134', '') -- 🏆
    :gsub('\240\159\146\161', '') -- 💡
    :gsub('\240\159\167\160', '') -- 🧠
    :gsub('\240\159\142\175', '') -- 🎯
  if s ~= el.text then
    el.text = s
    return el
  end
end