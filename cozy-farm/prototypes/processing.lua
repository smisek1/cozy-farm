-- Mill and kitchen: turn crops and animal products into food and farm science.
local common = require("prototypes.common")
local P = common.P

local function building(name, category, base, badge, tint, order)
  local e = table.deepcopy(data.raw["assembling-machine"][base])
  e.name = P .. name
  e.icon = nil
  e.icons = common.badged(data.raw["assembling-machine"][base].icon, badge, tint)
  e.minable = { mining_time = 0.3, result = P .. name }
  e.crafting_categories = { category }
  e.crafting_speed = 1
  e.energy_source = common.fed_energy()
  e.energy_usage = "50kW"
  e.next_upgrade = nil
  e.fast_replaceable_group = nil
  e.module_slots = 0
  e.allowed_effects = nil
  e.fluid_boxes = nil
  e.surface_conditions = nil
  common.tint_graphics(e.graphics_set, tint)
  local item = common.item(name, "buildings", order, 20, { place_result = P .. name })
  item.icon = nil
  item.icons = e.icons
  return e, item
end

local mill, mill_item = building("mill", "cozy-mill", "assembling-machine-1", "flour", { 0.95, 0.88, 0.7 }, "d")
local kitchen, kitchen_item = building("kitchen", "cozy-kitchen", "assembling-machine-1", "pumpkin-pie", { 1, 0.75, 0.55 }, "e")


data:extend({
  mill, mill_item, kitchen, kitchen_item,

  common.item("flour", "products", "e", 100),
  common.item("bread", "food", "a", 50, { type = "capsule", capsule_action = common.food_action(40) }),
  common.item("cheese", "food", "b", 50, { type = "capsule", capsule_action = common.food_action(40) }),
  common.item("vegetable-soup", "food", "c", 50, { type = "capsule", capsule_action = common.food_action(60) }),
  common.item("pumpkin-pie", "food", "d", 50, { type = "capsule", capsule_action = common.food_action(100) }),

  common.recipe("mill", "crafting", 3, { { "plank", 10 }, { "limestone", 10 }, { "flax-fiber", 5 } }, { { "mill", 1 } }),
  common.recipe("kitchen", "crafting", 3, { { "plank", 10 }, { "biocement", 10 }, { "resin", 5 } }, { { "kitchen", 1 } }),

  common.recipe("flour", "cozy-mill", 4, { { "wheat", 2 } }, { { "flour", 1 } }),
  common.recipe("bread", "cozy-kitchen", 8, { { "flour", 2 }, { "egg", 1 } }, { { "bread", 1 } }),
  common.recipe("cheese", "cozy-kitchen", 10, { { "milk", 3 } }, { { "cheese", 1 } }),
  common.recipe("vegetable-soup", "cozy-kitchen", 8, { { "carrot", 1 }, { "potato", 1 }, { "tomato", 1 } }, { { "vegetable-soup", 1 } }),
  common.recipe("pumpkin-pie", "cozy-kitchen", 12, { { "pumpkin", 1 }, { "flour", 1 }, { "egg", 1 }, { "milk", 1 } }, { { "pumpkin-pie", 1 } }),
})

