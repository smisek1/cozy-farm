-- Garden soil: a placeable tile. Crops can only be planted on it.
local common = require("prototypes.common")

-- Own collision layer marks soil tiles; plants require it via tile_buildability_rules.
data:extend({ { type = "collision-layer", name = "cozy_garden_soil", order = "z-cozy" } })

local tile = table.deepcopy(data.raw.tile["dirt-4"])
tile.name = "cozy-garden-soil"
tile.autoplace = nil
tile.order = "z[cozy-farm]-a[garden-soil]"
tile.subgroup = nil
tile.minable = { mining_time = 0.2, result = "cozy-garden-soil" }
tile.mined_sound = table.deepcopy(data.raw.tile["landfill"].mined_sound)
tile.build_sound = table.deepcopy(data.raw.tile["landfill"].build_sound)
tile.tint = { 0.62, 0.48, 0.36 }
tile.map_color = { 92, 60, 32 }
tile.layer = 23
tile.can_be_part_of_blueprint = true
tile.is_foundation = false
tile.collision_mask = table.deepcopy(tile.collision_mask)
tile.collision_mask.layers.cozy_garden_soil = true

data:extend({
  tile,
  common.item("garden-soil", "soil", "a", 100, {
    place_as_tile = {
      result = "cozy-garden-soil",
      condition_size = 1,
      condition = { layers = { water_tile = true } },
    },
  }),
  common.recipe("garden-soil", "crafting", 1, { { "plank", 1 }, { "limestone", 2 } }, { { "garden-soil", 10 } }),
})
