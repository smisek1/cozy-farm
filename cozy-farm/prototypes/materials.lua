-- Basic living materials that replace metals, stone and fuel, plus the digester that makes them.
local common = require("prototypes.common")
local P = common.P

data:extend({
  { type = "fuel-category", name = "cozy-food" },
  { type = "recipe-category", name = "cozy-digest" },
  { type = "item-subgroup", name = "cozy-farm-materials", group = "cozy-farm", order = "b-a" },
})

local function mat(name, order, stack, extra)
  return common.item(name, "materials", order, stack or 100, extra)
end

-- Digester: a living stomach (Gleba biochamber) that breaks biomass down.
local base = data.raw["assembling-machine"]["biochamber"]
local digester = table.deepcopy(base)
digester.name = P .. "digester"
digester.icon = nil
digester.icons = common.badged(base.icon, "digester-badge")
digester.minable = { mining_time = 0.3, result = P .. "digester" }
digester.crafting_categories = { "cozy-digest" }
digester.crafting_speed = 1
digester.energy_source = common.fed_energy()
digester.energy_usage = "100kW"
digester.heating_energy = nil
digester.surface_conditions = nil
digester.module_slots = 0
digester.allowed_effects = nil
digester.next_upgrade = nil
digester.fast_replaceable_group = nil
digester.effect_receiver = nil
local digester_item = common.item("digester", "buildings", "c-a", 20, { place_result = P .. "digester" })
digester_item.icon = nil
digester_item.icons = digester.icons

local function digest(name, time, ingredients, results, order)
  return common.recipe(name, "cozy-digest", time, ingredients, results, { subgroup = "cozy-farm-materials", order = order })
end

data:extend({
  digester, digester_item,

  mat("plank", "a"),
  mat("flax-fiber", "b"),
  mat("resin", "c"),
  mat("limestone", "d"),
  mat("biocement", "e"),
  mat("sugar", "f", 100, { fuel_categories = { "cozy-food" }, fuel_value = "4MJ" }),

  -- Hand-craftable basics
  common.recipe("plank", "crafting", 0.5, { { "wood", 1 } }, { { "plank", 2 } }),
  common.recipe("flax-fiber", "crafting", 1, { { "flax", 1 } }, { { "flax-fiber", 2 } }),
  common.recipe("tree-seed", "crafting", 1, { { "wood", 2 } }, { { "tree-seed", 1 } },
    { subgroup = "cozy-farm-seeds", order = "z" }),
  common.recipe("digester", "crafting", 3, { { "plank", 10 }, { "flax-fiber", 5 }, { "limestone", 10 } }, { { "digester", 1 } }),

  -- Digester
  digest("resin", 3, { { "wood", 4 } }, { { "resin", 1 } }, "c"),
  digest("biocement", 4, { { "limestone", 2 }, { "hay", 1 } }, { { "biocement", 2 } }, "e"),
  digest("sugar-from-potato", 4, { { "potato", 2 } }, { { "sugar", 1 } }, "f-a"),
  digest("sugar-from-wheat", 4, { { "wheat", 3 } }, { { "sugar", 1 } }, "f-b"),
})
