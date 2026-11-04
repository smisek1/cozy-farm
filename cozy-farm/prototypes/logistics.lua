-- Vanilla logistics, reskinned as living things and made from bio materials.
local common = require("prototypes.common")
local P = common.P

local ROOT = { 0.72, 0.88, 0.55 }   -- greenish tint for root belts
local VINE = { 0.6, 0.95, 0.5 }

local function ing(list)
  local out = {}
  for _, i in ipairs(list) do out[#out + 1] = common.ing(i[1], i[2]) end
  return out
end

local function reskin(kind, name, tint, recipe_ings, count, enabled)
  local e = data.raw[kind][name]
  common.tint_graphics(e, tint)
  e.icons = { { icon = e.icon, icon_size = e.icon_size or 64, tint = tint } }
  local item = data.raw.item[name]
  if item then item.icons = e.icons end
  local r = data.raw.recipe[name]
  r.ingredients = ing(recipe_ings)
  r.results = { { type = "item", name = name, amount = count or 1 } }
  r.enabled = enabled ~= false
  r.energy_required = r.energy_required or 0.5
end

reskin("transport-belt", "transport-belt", ROOT, { { "plank", 1 }, { "flax-fiber", 1 } }, 2)
reskin("underground-belt", "underground-belt", ROOT, { { "plank", 10 }, { "transport-belt", 5 } }, 2)
reskin("splitter", "splitter", ROOT, { { "plank", 5 }, { "flax-fiber", 5 }, { "transport-belt", 4 } }, 1)

-- Burner inserter = tendril; it eats like other living buildings.
local tendril = data.raw.inserter["burner-inserter"]
reskin("inserter", "burner-inserter", VINE, { { "plank", 2 }, { "flax-fiber", 1 } }, 1)
tendril.energy_source = common.fed_energy()
tendril.energy_source.fuel_inventory_size = 1
tendril.energy_source.burner_usage = "food"
tendril.energy_source.emissions_per_minute = nil

data.raw.recipe["wooden-chest"].enabled = true

-- Lab = genetic lab (becomes the DNA sequencer later). Eats for now.
local lab = data.raw.lab["lab"]
lab.energy_source = common.fed_energy()
lab.inputs = { P .. "farm-pack" }
local lab_recipe = data.raw.recipe["lab"]
lab_recipe.ingredients = ing({ { "plank", 10 }, { "flax-fiber", 10 }, { "biocement", 5 } })
lab_recipe.enabled = true

-- Agricultural tower = forest tower (plants trees for wood). Unlocked with the garden tower.
local forest = data.raw["agricultural-tower"]["agricultural-tower"]
forest.energy_source = common.fed_energy()
local forest_recipe = data.raw.recipe["agricultural-tower"]
forest_recipe.ingredients = ing({ { "plank", 20 }, { "flax-fiber", 10 }, { "resin", 10 }, { "biocement", 5 } })
forest_recipe.enabled = false

-- Recipes that stay available from vanilla (everything else gets hidden in data-final-fixes).
COZY_KEEP_RECIPES = {
  ["transport-belt"] = true, ["underground-belt"] = true, ["splitter"] = true,
  ["burner-inserter"] = true, ["wooden-chest"] = true, ["lab"] = true, ["agricultural-tower"] = true,
}
