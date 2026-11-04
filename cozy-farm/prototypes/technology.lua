local common = require("prototypes.common")
local P = common.P

data:extend({
  {
    type = "technology",
    name = P .. "garden-tower",
    icon = "__space-age__/graphics/technology/agriculture.png",
    icon_size = 256,
    effects = {
      { type = "unlock-recipe", recipe = P .. "garden-tower" },
      { type = "unlock-recipe", recipe = "agricultural-tower" },
    },
    unit = {
      count = 30,
      ingredients = { { P .. "farm-pack", 1 } },
      time = 15,
    },
    order = "z-cozy-a",
  },
})
