-- World without metals: no ores on Nauvis, rocks give limestone, vanilla recipes/technologies hidden.
local P = "cozy-"

-- 1) No ores, coal, oil or uranium on Nauvis.
local REMOVED = { "iron-ore", "copper-ore", "stone", "coal", "uranium-ore", "crude-oil" }
local nauvis = data.raw.planet and data.raw.planet["nauvis"]
if nauvis and nauvis.map_gen_settings then
  local mgs = nauvis.map_gen_settings
  for _, name in ipairs(REMOVED) do
    if mgs.autoplace_controls then mgs.autoplace_controls[name] = nil end
    local ent = mgs.autoplace_settings and mgs.autoplace_settings.entity and mgs.autoplace_settings.entity.settings
    if ent then ent[name] = nil end
  end
end
-- Map presets may reference the removed controls.
for _, preset_set in pairs(data.raw["map-gen-presets"] or {}) do
  for _, preset in pairs(preset_set) do
    if type(preset) == "table" and preset.basic_settings and preset.basic_settings.autoplace_controls then
      for _, name in ipairs(REMOVED) do preset.basic_settings.autoplace_controls[name] = nil end
    end
  end
end

-- 2) Rocks give limestone instead of stone/coal/ore.
local ROCK_ITEMS = { ["stone"] = true, ["coal"] = true, ["iron-ore"] = true, ["copper-ore"] = true, ["uranium-ore"] = true }
for _, e in pairs(data.raw["simple-entity"]) do
  local m = e.minable
  if m then
    if m.result and ROCK_ITEMS[m.result] then
      m.results = { { type = "item", name = P .. "limestone", amount = m.count or 1 } }
      m.result, m.count = nil, nil
    elseif m.results then
      for _, r in pairs(m.results) do
        if ROCK_ITEMS[r.name] then r.name = P .. "limestone" end
      end
    end
  end
end

-- 3) Hide vanilla recipes and technologies we don't use.
local keep = COZY_KEEP_RECIPES or {}
for name, r in pairs(data.raw.recipe) do
  if not keep[name] and string.sub(name, 1, #P) ~= P then
    r.enabled = false
    r.hidden = true
  end
end
for name, t in pairs(data.raw.technology) do
  if string.sub(name, 1, #P) ~= P then
    t.enabled = false
    t.hidden = true
  end
end
