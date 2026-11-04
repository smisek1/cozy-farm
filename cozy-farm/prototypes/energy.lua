-- Mycelium network: the electric network as a living fungal web.
-- Leaves (solar) and fermentation chambers (burn sugar) feed it, starch tubers store it,
-- fungal nodes (poles) carry it. Big buildings switch from eating to the network.
local common = require("prototypes.common")
local P = common.P

local FUNGUS = { 0.95, 0.85, 0.7 }
local LEAF = { 0.55, 1, 0.45 }
local TUBER = { 0.95, 0.8, 0.55 }

local function ing(list)
  local out = {}
  for _, i in ipairs(list) do out[#out + 1] = common.ing(i[1], i[2]) end
  return out
end

--- Reskins a vanilla entity + item, sets its recipe and keeps it locked behind a technology.
local function reskin(kind, name, tint, ingredients, count)
  local e = data.raw[kind][name]
  if tint then
    common.tint_graphics(e, tint)
    e.icons = { { icon = e.icon, icon_size = e.icon_size or 64, tint = tint } }
    if data.raw.item[name] then data.raw.item[name].icons = e.icons end
  end
  local r = data.raw.recipe[name]
  r.ingredients = ing(ingredients)
  r.results = { { type = "item", name = name, amount = count or 1 } }
  r.enabled = false
  COZY_KEEP_RECIPES[name] = true
  return e
end

reskin("electric-pole", "small-electric-pole", FUNGUS, { { "plank", 1 }, { "flax-fiber", 1 } }, 2)
reskin("electric-pole", "medium-electric-pole", FUNGUS, { { "plank", 2 }, { "silk", 2 }, { "biocement", 1 } }, 1)
reskin("solar-panel", "solar-panel", LEAF, { { "plank", 5 }, { "flax-fiber", 10 }, { "resin", 5 }, { "biocement", 2 } }, 1)
reskin("accumulator", "accumulator", TUBER, { { "plank", 5 }, { "sugar", 10 }, { "biocement", 5 } }, 1)

-- Fermentation chamber: burns sugar (or hay) into network energy.
local biochamber = data.raw["assembling-machine"]["biochamber"]
local anim = table.deepcopy(biochamber.graphics_set.animation)
common.tint_graphics(anim, { 1, 0.85, 0.45 })
local burner = common.fed_energy()
burner.effectivity = 1
local chamber = {
  type = "burner-generator",
  name = P .. "fermentation-chamber",
  icons = common.badged(biochamber.icon, "sugar", { 1, 0.85, 0.45 }),
  flags = { "placeable-neutral", "player-creation" },
  minable = { mining_time = 0.5, result = P .. "fermentation-chamber" },
  max_health = 300,
  corpse = biochamber.corpse,
  dying_explosion = biochamber.dying_explosion,
  collision_box = table.deepcopy(biochamber.collision_box),
  selection_box = table.deepcopy(biochamber.selection_box),
  max_power_output = "300kW",
  animation = anim,
  perceived_performance = { minimum = 0.25, performance_to_activity_rate = 2.0 },
  burner = burner,
  energy_source = { type = "electric", usage_priority = "secondary-output" },
  open_sound = biochamber.open_sound,
  close_sound = biochamber.close_sound,
  working_sound = biochamber.working_sound,
}
local chamber_item = common.item("fermentation-chamber", "buildings", "i-a", 20, { place_result = chamber.name })
chamber_item.icon = nil
chamber_item.icons = chamber.icons

data:extend({
  chamber, chamber_item,
  common.recipe("fermentation-chamber", "crafting", 5, { { "plank", 10 }, { "biocement", 10 }, { "resin", 5 } },
    { { "fermentation-chamber", 1 } }, { enabled = false }),
})

-- Big buildings run on the network instead of eating.
local function electric(e, usage)
  e.energy_source = { type = "electric", usage_priority = "secondary-input" }
  if usage then e.energy_usage = usage end
end
electric(data.raw.lab[P .. "sequencer"], "150kW")
electric(data.raw["assembling-machine"][P .. "ant-workshop-2"], "150kW")
electric(data.raw["agricultural-tower"][P .. "garden-tower"])
electric(data.raw["agricultural-tower"]["agricultural-tower"])
