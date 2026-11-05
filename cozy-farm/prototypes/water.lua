-- Late game on water: plant oil, algae farm, reed filter, lotus reactor and the synthetic genome
-- (science pack 4). Water buildings stand directly on water tiles (like the offshore pump).
local common = require("prototypes.common")
local P = common.P

data:extend({
  { type = "recipe-category", name = "cozy-algae" },
  { type = "recipe-category", name = "cozy-reed" },
})

-- Collide only with objects (not with water), and require water under the whole building.
local function on_water(e)
  e.collision_mask = { layers = { object = true, train = true, is_object = true, is_lower_object = true } }
  local b = e.collision_box
  e.tile_buildability_rules = {
    { area = { { b[1][1], b[1][2] }, { b[2][1], b[2][2] } },
      required_tiles = { layers = { water_tile = true } }, colliding_tiles = { layers = {} }, remove_on_collision = true },
  }
end

local function electric(e, usage)
  e.energy_source = { type = "electric", usage_priority = "secondary-input" }
  e.energy_usage = usage
end

-- Algae farm: algae from sunlight and water, nothing else needed.
local algae_farm, algae_farm_item = common.machine("assembling-machine", "assembling-machine-2", "algae-farm",
  { badge = "algae", tint = { 0.55, 0.95, 0.6 }, categories = { "cozy-algae" }, speed = 1, order = "j-a" })
algae_farm.fluid_boxes = nil
electric(algae_farm, "100kW")
on_water(algae_farm)

-- Reed filter: reeds filter lime and sugar out of the water (renewable limestone once rocks run out).
local reed, reed_item = common.machine("assembling-machine", "chemical-plant", "reed-filter",
  { badge = "reed", tint = { 0.8, 0.95, 0.55 }, categories = { "cozy-reed" }, speed = 1, order = "j-b" })
reed.fluid_boxes = nil
electric(reed, "100kW")
on_water(reed)

-- Lotus reactor: a big floating lotus burning food (best: plant oil) into network energy.
local nuclear = data.raw.reactor["nuclear-reactor"]
local LOTUS = { 1, 0.7, 0.85 }
local anim = table.deepcopy(nuclear.picture)
common.tint_graphics(anim, LOTUS)
local lotus = {
  type = "burner-generator",
  name = P .. "lotus-reactor",
  icons = common.badged(nuclear.icon, "lotus", LOTUS),
  flags = { "placeable-neutral", "player-creation" },
  minable = { mining_time = 0.5, result = P .. "lotus-reactor" },
  max_health = 500,
  corpse = nuclear.corpse,
  dying_explosion = nuclear.dying_explosion,
  collision_box = table.deepcopy(nuclear.collision_box),
  selection_box = table.deepcopy(nuclear.selection_box),
  max_power_output = "1.5MW",
  animation = anim,
  burner = common.fed_energy(),
  energy_source = { type = "electric", usage_priority = "secondary-output" },
  open_sound = nuclear.open_sound,
  close_sound = nuclear.close_sound,
  working_sound = nuclear.working_sound,
}
on_water(lotus)
local lotus_item = common.item("lotus-reactor", "buildings", "j-c", 10, { place_result = lotus.name })
lotus_item.icon = nil
lotus_item.icons = lotus.icons

-- Science pack 4
local genome = common.item("synthetic-genome", "science", "d", 200)
genome.type = "tool"
genome.durability = 1
table.insert(data.raw.lab[P .. "sequencer"].inputs, P .. "synthetic-genome")

local DIGEST = { subgroup = "cozy-farm-materials", enabled = false, allow_productivity = true }

data:extend({
  algae_farm, algae_farm_item, reed, reed_item, lotus, lotus_item, genome,
  common.item("plant-oil", "materials", "l", 100, { fuel_categories = { "cozy-food" }, fuel_value = "8MJ" }),
  common.item("algae", "materials", "m", 100),

  -- Oil
  common.recipe("plant-oil-from-seeds", "cozy-digest", 6, { { "flax-seeds", 4 } }, { { "plant-oil", 1 } },
    { subgroup = "cozy-farm-materials", order = "l-a", enabled = false, allow_productivity = true }),
  common.recipe("plant-oil-from-algae", "cozy-digest", 6, { { "algae", 3 } }, { { "plant-oil", 1 }, { "sugar", 1 } },
    { subgroup = "cozy-farm-materials", order = "l-b", enabled = false, allow_productivity = true, main_product = P .. "plant-oil" }),

  -- Water buildings' own recipes (no ingredients: water and sun)
  common.recipe("algae", "cozy-algae", 8, {}, { { "algae", 3 } }, { enabled = false }),
  common.recipe("limestone-from-reeds", "cozy-reed", 10, {}, { { "limestone", 3 } }, { enabled = false }),
  common.recipe("sugar-from-reeds", "cozy-reed", 10, {}, { { "sugar", 2 } }, { enabled = false }),

  common.recipe("synthetic-genome", "cozy-ant", 20,
    { { "crispr-kit", 1 }, { "algae", 2 }, { "plant-oil", 1 }, { "nerve-tissue", 2 } }, { { "synthetic-genome", 1 } },
    { enabled = false }),

  -- Buildings
  common.recipe("algae-farm", "crafting", 5, { { "plank", 10 }, { "resin", 10 }, { "flax-fiber", 10 }, { "nerve-tissue", 2 } },
    { { "algae-farm", 1 } }, { enabled = false }),
  common.recipe("reed-filter", "crafting", 5, { { "plank", 10 }, { "biocement", 10 }, { "flax-fiber", 20 } },
    { { "reed-filter", 1 } }, { enabled = false }),
  common.recipe("lotus-reactor", "crafting", 15,
    { { "biocement", 50 }, { "chitin", 20 }, { "nerve-tissue", 20 }, { "resin", 20 }, { "synthetic-genome", 5 } },
    { { "lotus-reactor", 1 } }, { enabled = false }),
})

-- Existing digester recipes can get productivity from synthetic enzymes.
local ENZYME_RECIPES = { "resin", "biocement", "sugar-from-potato", "sugar-from-wheat", "plant-oil-from-seeds", "plant-oil-from-algae" }
local enzyme_effects = {}
for _, r in ipairs(ENZYME_RECIPES) do
  data.raw.recipe[P .. r].allow_productivity = true
  enzyme_effects[#enzyme_effects + 1] = { type = "change-recipe-productivity", recipe = P .. r, change = 0.2 }
end

-- Technologies --------------------------------------------------------------------------

local function tech(name, icon, unlocks, prereqs, count, packs, order)
  local effects, pre, ings = {}, {}, {}
  for _, r in ipairs(unlocks) do effects[#effects + 1] = { type = "unlock-recipe", recipe = P .. r } end
  for _, p in ipairs(prereqs) do pre[#pre + 1] = P .. p end
  for _, p in ipairs(packs) do ings[#ings + 1] = { P .. p, 1 } end
  return {
    type = "technology", name = P .. name, icon = icon, icon_size = 64,
    effects = effects, prerequisites = pre, order = "z-cozy-" .. order,
    unit = { count = count, ingredients = ings, time = 30 },
  }
end
local DNA3 = { "dna-sample", "genome-sequence", "crispr-kit" }
local DNA4 = { "dna-sample", "genome-sequence", "crispr-kit", "synthetic-genome" }

local enzymes = tech("synthetic-enzymes", common.icon("synthetic-genome"), {}, { "synthetic-genome" }, 200, DNA4, "q")
enzymes.effects = enzyme_effects

data:extend({
  tech("plant-oil", common.icon("plant-oil"), { "plant-oil-from-seeds" }, { "crispr" }, 75, DNA3, "m"),
  tech("water-buildings", common.icon("algae"),
    { "algae-farm", "algae", "plant-oil-from-algae", "reed-filter", "limestone-from-reeds", "sugar-from-reeds" },
    { "plant-oil" }, 100, DNA3, "n"),
  tech("synthetic-genome", common.icon("synthetic-genome"), { "synthetic-genome" },
    { "water-buildings", "ant-workshop-3" }, 150, DNA3, "o"),
  tech("lotus-reactor", common.icon("lotus"), { "lotus-reactor" }, { "synthetic-genome" }, 200, DNA4, "p"),
  enzymes,
})
