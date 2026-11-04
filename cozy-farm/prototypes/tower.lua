-- Garden tower: a smaller agricultural tower that plants/harvests crops on a 1x1 grid.
local common = require("prototypes.common")
local P = common.P

local seeds = {}
for _, c in ipairs({ "carrot", "potato", "wheat", "tomato", "pumpkin", "flax" }) do seeds[#seeds + 1] = P .. c .. "-seeds" end

local tower = table.deepcopy(data.raw["agricultural-tower"]["agricultural-tower"])
tower.name = P .. "garden-tower"
tower.icon = nil
tower.icons = common.badged("__space-age__/graphics/icons/agricultural-tower.png", "tower-badge", { 0.8, 1, 0.75 })
tower.minable = { mining_time = 0.3, result = P .. "garden-tower" }
tower.growth_grid_tile_size = 1
tower.growth_area_radius = 0.4
tower.random_growth_offset = 0
tower.radius = 4
tower.accepted_seeds = seeds
tower.fast_replaceable_group = nil
tower.next_upgrade = nil
tower.energy_usage = "20kJ"
tower.crane_energy_usage = "50kW"
tower.energy_source = common.fed_energy()

local item = common.item("garden-tower", "buildings", "f", 20, { place_result = P .. "garden-tower" })
item.icon = nil
item.icons = tower.icons

local recipe = common.recipe("garden-tower", "crafting", 5,
  { { "plank", 20 }, { "flax-fiber", 10 }, { "resin", 10 }, { "biocement", 5 } },
  { { "garden-tower", 1 } }, { enabled = false })

data:extend({ tower, item, recipe })
