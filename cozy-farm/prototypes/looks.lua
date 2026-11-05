-- Own graphics for the living buildings (drawn by tools/make_graphics.py), replacing the tinted vanilla machines.
-- Must load before prototypes/growth.lua so sprouts copy the new icons.
-- Animated things (belts, tendrils, bees, towers with cranes, poles, leaves, tubers) stay tinted vanilla.
local common = require("prototypes.common")
local P = common.P

local EMPTY = { filename = "__core__/graphics/empty.png", width = 1, height = 1 }

-- kind, entity name, sprite file, sprite width, height, building centre row
local S3 = { 224, 288, 176 }   -- 3x3 buildings
local LOOKS = {
  { "assembling-machine", P .. "digester", "digester", S3 },
  { "burner-generator", P .. "fermentation-chamber", "fermentation-chamber", S3 },
  { "assembling-machine", P .. "mushroom-farm", "mushroom-farm", S3 },
  { "assembling-machine", P .. "ant-workshop-1", "ant-workshop-1", S3 },
  { "assembling-machine", P .. "ant-workshop-2", "ant-workshop-2", S3 },
  { "assembling-machine", P .. "ant-workshop-3", "ant-workshop-3", S3 },
  { "assembling-machine", P .. "spider-spinner", "spider-spinner", S3 },
  { "assembling-machine", P .. "mill", "mill", S3 },
  { "assembling-machine", P .. "kitchen", "kitchen", S3 },
  { "assembling-machine", P .. "chicken-coop", "chicken-coop", S3 },
  { "assembling-machine", P .. "barn", "barn", S3 },
  { "assembling-machine", P .. "sheep-pen", "sheep-pen", S3 },
  { "lab", "lab", "genetic-lab", S3 },
  { "lab", P .. "sequencer", "sequencer", { 384, 448, 256 } },
  { "roboport", "roboport", "hive", { 288, 352, 208 } },
}

for _, l in ipairs(LOOKS) do
  local kind, name, file, size = l[1], l[2], l[3], l[4]
  local e = data.raw[kind][name]
  assert(e, "looks: entity not found: " .. name)
  common.own_look(e, data.raw.item[name], file)
  local sprite = common.own_sprite(file, size[1], size[2], size[3])
  if kind == "assembling-machine" then
    e.graphics_set = { animation = sprite }
    e.graphics_set_flipped = nil
  elseif kind == "burner-generator" then
    e.animation = sprite
    e.idle_animation = nil
  elseif kind == "lab" then
    e.on_animation = sprite
    e.off_animation = sprite
  elseif kind == "roboport" then
    e.base = sprite
    e.base_patch = EMPTY
    e.base_animation = EMPTY
    e.door_animation_up = EMPTY
    e.door_animation_down = EMPTY
  end
end
