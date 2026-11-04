-- Planted sprouts grow into buildings. Progress is shown above the sprout.
local GROWN = require("scripts.grown_list")
local P = "cozy-"

local growth = {}
local TARGET = {}   -- sprout entity name -> { target = building name, ticks = growth ticks }
for short, seconds in pairs(GROWN) do
  TARGET[P .. short .. "-sprout"] = { target = P .. short, ticks = seconds * 60 }
end

growth.filters = {}
for name in pairs(TARGET) do growth.filters[#growth.filters + 1] = { filter = "name", name = name } end

function growth.init()
  storage.sprouts = storage.sprouts or {}
end

function growth.on_built(event)
  local e = event.entity
  if not (e and e.valid) then return end
  local t = TARGET[e.name]
  if not t then return end
  growth.init()
  local text = rendering.draw_text({
    text = "0%", surface = e.surface, target = { entity = e, offset = { 0, -0.5 } },
    color = { 0.75, 1, 0.6 }, scale = 1.5, alignment = "center", vertical_alignment = "middle",
  })
  storage.sprouts[e.unit_number] = { entity = e, target = t.target, start = game.tick, done = game.tick + t.ticks, text = text }
end

local function grow(data)
  local e = data.entity
  local surface, position, force, direction, quality = e.surface, e.position, e.force, e.direction, e.quality
  e.destroy()
  surface.create_entity({
    name = data.target, position = position, force = force, direction = direction, quality = quality,
    raise_built = true, create_build_effect_smoke = true,
  })
end

function growth.tick()
  if not storage.sprouts then return end
  local now = game.tick
  for id, data in pairs(storage.sprouts) do
    if not data.entity.valid then
      if data.text and data.text.valid then data.text.destroy() end
      storage.sprouts[id] = nil
    elseif now >= data.done then
      if data.text and data.text.valid then data.text.destroy() end
      storage.sprouts[id] = nil
      grow(data)
    elseif data.text and data.text.valid then
      data.text.text = math.floor((now - data.start) * 100 / (data.done - data.start)) .. "%"
    end
  end
end

return growth
