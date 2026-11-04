-- Animals live inside their buildings: the building is crafted from wood + animals and then
-- turns feed (hay) into products. Everything goes through normal inserters / belts.
local common = require("prototypes.common")
local P = common.P

local function building(name, category, badge, tint, order)
  local e = table.deepcopy(data.raw["assembling-machine"]["assembling-machine-1"])
  e.name = P .. name
  e.icon = nil
  e.icons = common.badged("__base__/graphics/icons/assembling-machine-1.png", badge, tint)
  e.minable = { mining_time = 0.3, result = P .. name }
  e.crafting_categories = { category }
  e.crafting_speed = 1
  e.energy_source = { type = "void" }
  e.energy_usage = "1kW"
  e.next_upgrade = nil
  e.fast_replaceable_group = nil
  e.module_slots = 0
  e.allowed_effects = nil
  e.surface_conditions = nil
  common.tint_graphics(e.graphics_set, tint)
  local item = common.item(name, "buildings", order, 20, { place_result = P .. name })
  item.icon = nil
  item.icons = e.icons
  return e, item
end

local wood = { 0.85, 0.62, 0.4 }
local barn_red = { 0.9, 0.45, 0.38 }
local meadow = { 0.75, 0.9, 0.6 }

local coop, coop_item = building("chicken-coop", "cozy-coop", "chicken", wood, "a")
local barn, barn_item = building("barn", "cozy-barn", "cow", barn_red, "b")
local pen, pen_item = building("sheep-pen", "cozy-sheep-pen", "sheep", meadow, "c")

data:extend({
  coop, coop_item, barn, barn_item, pen, pen_item,

  common.item("chicken", "animals", "a", 10),
  common.item("cow", "animals", "b", 5),
  common.item("sheep", "animals", "c", 5),
  common.item("hay", "products", "a", 100, { fuel_categories = { "cozy-food" }, fuel_value = "1MJ" }),
  common.item("egg", "products", "b", 50, { type = "capsule", capsule_action = common.food_action(8) }),
  common.item("milk", "products", "c", 50, { type = "capsule", capsule_action = common.food_action(8) }),
  common.item("wool", "products", "d", 100),

  -- Buildings
  common.recipe("chicken-coop", "crafting", 3, { { "plank", 10 }, { "limestone", 5 }, { "chicken", 2 } }, { { "chicken-coop", 1 } }),
  common.recipe("barn", "crafting", 5, { { "plank", 20 }, { "limestone", 10 }, { "cow", 1 } }, { { "barn", 1 } }),
  common.recipe("sheep-pen", "crafting", 4, { { "plank", 15 }, { "limestone", 5 }, { "sheep", 1 } }, { { "sheep-pen", 1 } }),

  -- Feed
  common.recipe("hay", "crafting", 1, { { "wheat", 1 } }, { { "hay", 2 } }, { subgroup = "cozy-farm-products", order = "a" }),

  -- Products
  common.recipe("eggs", "cozy-coop", 20, { { "hay", 1 } }, { { "egg", 2 } }, { main_product = P .. "egg" }),
  common.recipe("milk", "cozy-barn", 30, { { "hay", 2 } }, { { "milk", 1 } }),
  common.recipe("wool", "cozy-sheep-pen", 40, { { "hay", 2 } }, { { "wool", 2 } }),

  -- Breeding
  common.recipe("hatch-chicken", "cozy-coop", 60, { { "egg", 2 }, { "hay", 2 } }, { { "chicken", 1 } },
    { subgroup = "cozy-farm-animals", order = "a-b" }),
  common.recipe("breed-cow", "cozy-barn", 120, { { "cow", 1 }, { "hay", 10 } }, { { "cow", 2 } },
    { subgroup = "cozy-farm-animals", order = "b-b" }),
  common.recipe("breed-sheep", "cozy-sheep-pen", 90, { { "sheep", 1 }, { "hay", 8 } }, { { "sheep", 2 } },
    { subgroup = "cozy-farm-animals", order = "c-b" }),
})
