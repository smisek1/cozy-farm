-- Grown buildings: the recipe gives a sprout; a planted sprout grows into the building (scripts/growth.lua).
-- Mining the grown building gives the sprout back.
local common = require("prototypes.common")
local P = common.P
local GROWN = require("scripts.grown_list")

local KINDS = { "assembling-machine", "lab", "burner-generator", "furnace" }
local function find(name)
  for _, kind in ipairs(KINDS) do
    if data.raw[kind] and data.raw[kind][name] then return data.raw[kind][name] end
  end
end

local renamed = {}
for short, seconds in pairs(GROWN) do
  local name = P .. short
  local e = find(name)
  local item = data.raw.item[name]
  assert(e and item, "grown building not found: " .. name)
  local sprout_name = name .. "-sprout"
  renamed[name] = sprout_name

  local icons = table.deepcopy(item.icons or { { icon = item.icon, icon_size = 64 } })
  icons[#icons + 1] = { icon = common.icon("seedling"), icon_size = 64, scale = 0.3, shift = { -8, -8 } }

  local w = e.collision_box[2][1] - e.collision_box[1][1]
  local size = math.ceil(w)
  local sprout = {
    type = "simple-entity-with-owner",
    name = sprout_name,
    icons = icons,
    flags = { "placeable-neutral", "placeable-player", "player-creation" },
    minable = { mining_time = 0.3, result = sprout_name },
    max_health = 100,
    collision_box = table.deepcopy(e.collision_box),
    selection_box = table.deepcopy(e.selection_box),
    render_layer = "object",
    picture = {
      filename = common.G .. "entity/building-sprout.png",
      width = 128, height = 128, scale = size / 4,
    },
    map_color = { 0.4, 0.6, 0.3 },
  }

  local sprout_item = table.deepcopy(item)
  sprout_item.name = sprout_name
  sprout_item.icon = nil
  sprout_item.icons = icons
  sprout_item.place_result = sprout_name
  sprout_item.localised_name = { "cozy-farm.sprout", { "entity-name." .. name } }
  sprout_item.localised_description = { "cozy-farm.sprout-description", { "entity-name." .. name }, tostring(seconds) }

  -- The adult building is placed (by blueprints) and mined as the sprout item.
  e.minable.result = sprout_name
  e.placeable_by = { item = sprout_name, count = 1 }
  e.next_upgrade = nil
  e.fast_replaceable_group = nil

  data.raw.item[name] = nil
  data:extend({ sprout, sprout_item })
end

-- Recipes now produce / use sprouts instead of the adult items.
for _, r in pairs(data.raw.recipe) do
  for _, list in ipairs({ r.ingredients or {}, r.results or {} }) do
    for _, x in pairs(list) do
      if renamed[x.name] then x.name = renamed[x.name] end
    end
  end
  if r.main_product and renamed[r.main_product] then r.main_product = renamed[r.main_product] end
end
