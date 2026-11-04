-- Crops: seed item -> plant entity (grows on garden soil) -> harvest (crop + chance of seeds back).
local common = require("prototypes.common")
local P, G = common.P, common.G

local minutes = 60 * 60

-- name, growth (min), yield, seeds back on harvest (probability), seeds per crop (seed recipe), heal when eaten
local crops = {
  { name = "carrot",  growth = 2,   yield = 2, seed_chance = 0.5, seeds_from = { 1, 3 }, heal = 10, color = { 0.95, 0.54, 0.12 } },
  { name = "potato",  growth = 3,   yield = 3, seed_chance = 0.5, seeds_from = { 1, 2 }, heal = 10, color = { 0.63, 0.48, 0.27 } },
  { name = "wheat",   growth = 2.5, yield = 3, seed_chance = 0.5, seeds_from = { 2, 3 }, heal = nil, color = { 0.88, 0.72, 0.24 } },
  { name = "tomato",  growth = 4,   yield = 3, seed_chance = 0.5, seeds_from = { 1, 3 }, heal = 15, color = { 0.9, 0.22, 0.21 } },
  { name = "pumpkin", growth = 6,   yield = 1, seed_chance = 0.5, seeds_from = { 1, 5 }, heal = 25, color = { 0.88, 0.48, 0.09 } },
  { name = "flax",    growth = 2.5, yield = 3, seed_chance = 0.5, seeds_from = { 1, 2 }, heal = nil, color = { 0.44, 0.66, 0.86 } },
}

local sprite_shift = { 0, -0.3 }

for i, c in ipairs(crops) do
  local order = string.char(96 + i)
  local seed = P .. c.name .. "-seeds"
  local plant = P .. c.name .. "-plant"

  local crop_item = c.heal
    and common.item(c.name, "crops", order, 50, { type = "capsule", capsule_action = common.food_action(c.heal) })
    or common.item(c.name, "crops", order, 50)

  data:extend({
    crop_item,
    common.item(c.name .. "-seeds", "seeds", order, 100, { plant_result = plant, place_result = plant }),
    {
      type = "plant",
      name = plant,
      icon = common.icon(c.name),
      icon_size = 64,
      localised_name = { "item-name." .. P .. c.name },
      flags = { "placeable-neutral", "breaths-air" },
      minable = {
        mining_time = 0.3,
        results = {
          { type = "item", name = P .. c.name, amount = c.yield },
          { type = "item", name = seed, amount = 1, independent_probability = c.seed_chance },
        },
      },
      growth_ticks = math.floor(c.growth * minutes),
      max_health = 20,
      collision_box = { { -0.3, -0.3 }, { 0.3, 0.3 } },
      selection_box = { { -0.5, -0.9 }, { 0.5, 0.5 } },
      subgroup = "cozy-farm-crops",
      order = "z-" .. order,
      pictures = {
        { filename = G .. "entity/" .. c.name .. "-plant.png", width = 64, height = 64, scale = 0.5, shift = sprite_shift },
      },
      tile_buildability_rules = {
        { area = { { -0.25, -0.25 }, { 0.25, 0.25 } }, required_tiles = { layers = { cozy_garden_soil = true } }, remove_on_collision = true },
      },
      autoplace = {
        probability_expression = 0,
        -- Plants only grow on garden soil (also used by towers to show the plots).
        tile_restriction = { "cozy-garden-soil" },
      },
      agricultural_tower_tint = {
        primary = { r = c.color[1], g = c.color[2], b = c.color[3], a = 1 },
        secondary = { r = 0.45, g = 0.7, b = 0.3, a = 1 },
      },
      map_color = { r = c.color[1], g = c.color[2], b = c.color[3], a = 0.6 },
      emissions_per_second = { pollution = -0.0005 },
    },
    common.recipe(c.name .. "-seeds", "crafting", 1,
      { { c.name, c.seeds_from[1] } }, { { c.name .. "-seeds", c.seeds_from[2] } },
      { subgroup = "cozy-farm-seeds", order = order }),
  })
end
