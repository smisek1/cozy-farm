local common = require("prototypes.common")

data:extend({
  {
    type = "item-group",
    name = "cozy-farm",
    order = "c-farm",
    icon = common.icon("pumpkin"),
    icon_size = 64,
  },
})

local subgroups = { "soil", "seeds", "crops", "animals", "products", "food", "buildings" }
for i, name in ipairs(subgroups) do
  data:extend({ { type = "item-subgroup", name = "cozy-farm-" .. name, group = "cozy-farm", order = string.char(96 + i) } })
end

for _, cat in ipairs({ "coop", "barn", "sheep-pen", "mill", "kitchen" }) do
  data:extend({ { type = "recipe-category", name = "cozy-" .. cat } })
end
