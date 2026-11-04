-- Fungi and insects: mushroom farm (mycelium), nerve tissue (instead of circuits),
-- chitin (instead of steel) and the ant workshop III built from them.
local common = require("prototypes.common")
local P = common.P

data:extend({ { type = "recipe-category", name = "cozy-mushroom" } })

local farm, farm_item = common.machine("assembling-machine", "assembling-machine-3", "mushroom-farm",
  { badge = "mushroom", tint = { 0.85, 0.75, 0.95 }, categories = { "cozy-mushroom" }, speed = 1, usage = "75kW", order = "g-d" })
local ant3, ant3_item = common.machine("assembling-machine", "assembling-machine-3", "ant-workshop-3",
  { badge = "ant", tint = { 0.85, 0.5, 0.3 }, categories = { "crafting", "cozy-ant" }, speed = 1.25, usage = "250kW", order = "g-b2" })
ant3.energy_source = { type = "electric", usage_priority = "secondary-input" }

local function tech(name, icon, unlocks, prereqs, count, order)
  local effects, pre = {}, {}
  for _, r in ipairs(unlocks) do effects[#effects + 1] = { type = "unlock-recipe", recipe = P .. r } end
  for _, p in ipairs(prereqs) do pre[#pre + 1] = P .. p end
  return {
    type = "technology", name = P .. name, icon = icon, icon_size = 64,
    effects = effects, prerequisites = pre, order = "z-cozy-" .. order,
    unit = { count = count, ingredients = { { P .. "dna-sample", 1 }, { P .. "genome-sequence", 1 } }, time = 20 },
  }
end

data:extend({
  farm, farm_item, ant3, ant3_item,
  common.item("mycelium", "materials", "h", 100),
  common.item("nerve-tissue", "materials", "i", 100),
  common.item("chitin", "materials", "j", 100),

  common.recipe("mycelium", "cozy-mushroom", 20, { { "wood", 2 }, { "hay", 1 } }, { { "mycelium", 3 } }, { enabled = false }),
  common.recipe("nerve-tissue", "cozy-ant", 8, { { "mycelium", 2 }, { "silk", 1 } }, { { "nerve-tissue", 1 } }, { enabled = false }),
  common.recipe("chitin", "cozy-ant", 10, { { "sugar", 2 }, { "hay", 1 } }, { { "chitin", 1 } }, { enabled = false }),
  common.recipe("mushroom-farm", "crafting", 5, { { "plank", 10 }, { "biocement", 10 }, { "resin", 5 } },
    { { "mushroom-farm", 1 } }, { enabled = false }),
  common.recipe("ant-workshop-3", "crafting", 5, { { "ant-workshop-2", 1 }, { "chitin", 10 }, { "nerve-tissue", 10 }, { "silk", 5 } },
    { { "ant-workshop-3", 1 } }, { enabled = false }),

  tech("mushroom-farm", common.icon("mushroom"), { "mushroom-farm", "mycelium", "nerve-tissue" }, { "genome-sequencing" }, 40, "g"),
  tech("chitin", common.icon("chitin"), { "chitin" }, { "ant-workshop-2" }, 40, "h"),
  tech("ant-workshop-3", common.icon("ant"), { "ant-workshop-3" }, { "mushroom-farm", "chitin" }, 75, "i"),
})
