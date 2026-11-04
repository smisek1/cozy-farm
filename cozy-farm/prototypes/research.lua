-- Research = DNA sequencing. Science packs, labs, insect factories and the technology tree.
local common = require("prototypes.common")
local P = common.P

data:extend({
  { type = "item-subgroup", name = "cozy-farm-science", group = "cozy-farm", order = "h" },
  { type = "recipe-category", name = "cozy-ant" },
  { type = "recipe-category", name = "cozy-spin" },
})

local function pack(name, order)
  local item = common.item(name, "science", order, 200)
  item.type = "tool"
  item.durability = 1
  return item
end

-- Buildings -------------------------------------------------------------------------------

local AMBER = { 1, 0.82, 0.55 }
local ant1, ant1_item = common.machine("assembling-machine", "assembling-machine-1", "ant-workshop-1",
  { badge = "ant", tint = AMBER, categories = { "crafting", "cozy-ant" }, speed = 0.5, usage = "75kW",
    order = "g-a", replace_group = "cozy-ant-workshop" })
ant1.next_upgrade = P .. "ant-workshop-2"
local ant2, ant2_item = common.machine("assembling-machine", "assembling-machine-2", "ant-workshop-2",
  { badge = "ant", tint = { 0.95, 0.65, 0.4 }, categories = { "crafting", "cozy-ant" }, speed = 0.75, usage = "100kW",
    order = "g-b", replace_group = "cozy-ant-workshop" })
local spinner, spinner_item = common.machine("assembling-machine", "centrifuge", "spider-spinner",
  { badge = "spider", tint = { 0.85, 0.85, 1 }, categories = { "cozy-spin" }, speed = 1, usage = "75kW", order = "g-c" })

-- Sequencer: the Space Age biolab, eating like everything else.
local biolab = data.raw.lab["biolab"]
local sequencer = table.deepcopy(biolab)
sequencer.name = P .. "sequencer"
sequencer.icon = nil
sequencer.icons = common.badged(biolab.icon, "genome-sequence")
sequencer.minable = { mining_time = 0.5, result = P .. "sequencer" }
sequencer.energy_source = common.fed_energy()
sequencer.energy_usage = "100kW"
sequencer.inputs = { P .. "dna-sample", P .. "genome-sequence" }
sequencer.module_slots = 0
sequencer.allowed_effects = nil
sequencer.effect_receiver = nil
sequencer.surface_conditions = nil
sequencer.researching_speed = 2
sequencer.next_upgrade = nil
sequencer.fast_replaceable_group = nil
local sequencer_item = common.item("sequencer", "buildings", "h", 10, { place_result = P .. "sequencer" })
sequencer_item.icon = nil
sequencer_item.icons = sequencer.icons

data:extend({
  ant1, ant1_item, ant2, ant2_item, spinner, spinner_item, sequencer, sequencer_item,

  pack("dna-sample", "a"),
  pack("genome-sequence", "b"),
  common.item("silk", "materials", "g", 100),

  -- Science
  common.recipe("dna-sample", "crafting", 5, { { "carrot", 1 }, { "egg", 1 }, { "flax-fiber", 1 } }, { { "dna-sample", 1 } }),
  common.recipe("genome-sequence", "cozy-ant", 10, { { "dna-sample", 1 }, { "silk", 2 }, { "sugar", 1 } }, { { "genome-sequence", 1 } },
    { enabled = false }),
  common.recipe("silk", "cozy-spin", 6, { { "egg", 1 }, { "sugar", 1 } }, { { "silk", 3 } }, { enabled = false }),

  -- Buildings
  common.recipe("ant-workshop-1", "crafting", 5, { { "plank", 10 }, { "flax-fiber", 10 }, { "biocement", 5 }, { "sugar", 5 } },
    { { "ant-workshop-1", 1 } }, { enabled = false }),
  common.recipe("ant-workshop-2", "crafting", 5, { { "ant-workshop-1", 1 }, { "silk", 10 }, { "biocement", 10 } },
    { { "ant-workshop-2", 1 } }, { enabled = false }),
  common.recipe("spider-spinner", "crafting", 5, { { "plank", 10 }, { "biocement", 10 }, { "flax-fiber", 10 }, { "resin", 5 } },
    { { "spider-spinner", 1 } }, { enabled = false }),
  common.recipe("sequencer", "crafting", 10, { { "plank", 20 }, { "silk", 10 }, { "biocement", 10 }, { "resin", 10 } },
    { { "sequencer", 1 } }, { enabled = false }),
})

-- Technology tree ------------------------------------------------------------------------

local function tech(name, icon, unlocks, prereqs, count, packs, order)
  local effects = {}
  for _, r in ipairs(unlocks) do
    effects[#effects + 1] = { type = "unlock-recipe", recipe = (data.raw.recipe[r] and r) or (P .. r) }
  end
  local ingredients = {}
  for _, p in ipairs(packs) do ingredients[#ingredients + 1] = { P .. p, 1 } end
  local pre = {}
  for _, p in ipairs(prereqs) do pre[#pre + 1] = P .. p end
  return {
    type = "technology",
    name = P .. name,
    icon = icon,
    icon_size = 64,
    effects = effects,
    prerequisites = pre,
    unit = { count = count, ingredients = ingredients, time = 15 },
    order = "z-cozy-" .. order,
  }
end

local DNA = { "dna-sample" }
local DNA2 = { "dna-sample", "genome-sequence" }

data:extend({
  tech("root-logistics", "__base__/graphics/icons/splitter.png", { "underground-belt", "splitter" }, {}, 15, DNA, "a"),
  tech("ant-workshop-1", common.icon("ant"), { "ant-workshop-1" }, {}, 10, DNA, "b"),
  tech("spider-spinner", common.icon("spider"), { "spider-spinner", "silk" }, { "ant-workshop-1" }, 25, DNA, "c"),
  tech("mycelium-network", "__base__/graphics/icons/small-electric-pole.png",
    { "small-electric-pole", "solar-panel", "fermentation-chamber" }, { "ant-workshop-1" }, 20, DNA, "c-m"),
  tech("garden-tower", common.icon("tower-badge"), { "garden-tower", "agricultural-tower" }, { "mycelium-network" }, 30, DNA, "d"),
  tech("starch-tuber", "__base__/graphics/icons/accumulator.png", { "accumulator" }, { "mycelium-network" }, 30, DNA, "d-s"),
  tech("genome-sequencing", common.icon("genome-sequence"), { "genome-sequence", "sequencer" },
    { "spider-spinner", "mycelium-network" }, 40, DNA, "e"),
  tech("ant-workshop-2", common.icon("ant"), { "ant-workshop-2" }, { "genome-sequencing" }, 50, DNA2, "f"),
  tech("mycelium-network-2", "__base__/graphics/icons/medium-electric-pole.png", { "medium-electric-pole" },
    { "genome-sequencing" }, 40, DNA2, "f-m"),
})
