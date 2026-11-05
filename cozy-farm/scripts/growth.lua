-- Planted sprouts grow into buildings. Progress is shown above the sprout.
-- A grown building placed by robots or blueprints is replaced by its sprout, so it has to grow too.
local GROWN = require("scripts.grown_list")
local P = "cozy-"

local growth = {}
local TARGET = {}   -- sprout entity name -> { target = building name, ticks = growth ticks }
local SPROUT = {}   -- grown building name -> sprout entity name
for short, seconds in pairs(GROWN) do
  TARGET[P .. short .. "-sprout"] = { target = P .. short, ticks = seconds * 60 }
  SPROUT[P .. short] = P .. short .. "-sprout"
end

growth.filters = {}
for name in pairs(TARGET) do growth.filters[#growth.filters + 1] = { filter = "name", name = name } end
for name in pairs(SPROUT) do growth.filters[#growth.filters + 1] = { filter = "name", name = name } end

-- True while grow() creates the grown building, so it is not turned back into a sprout.
local growing = false

function growth.init()
  storage.sprouts = storage.sprouts or {}
end

local function register(e, recipe)
  local t = TARGET[e.name]
  growth.init()
  local text = rendering.draw_text({
    text = "0%", surface = e.surface, target = { entity = e, offset = { 0, -0.5 } },
    color = { 0.75, 1, 0.6 }, scale = 1.5, alignment = "center", vertical_alignment = "middle",
  })
  storage.sprouts[e.unit_number] = {
    entity = e, target = t.target, start = game.tick, done = game.tick + t.ticks, text = text, recipe = recipe,
  }
end

--- A grown building appeared without growing (robots, blueprints, other mods): plant its sprout instead.
local function replant(e)
  local sprout_name = SPROUT[e.name]
  local surface, position, force, direction, quality = e.surface, e.position, e.force, e.direction, e.quality
  local recipe
  if e.type == "assembling-machine" then
    local r, q = e.get_recipe()
    if r then recipe = { name = r.name, quality = q and q.name } end
  end
  e.destroy()
  local sprout = surface.create_entity({
    name = sprout_name, position = position, force = force, direction = direction, quality = quality,
  })
  if sprout then register(sprout, recipe) end
end

function growth.on_built(event)
  local e = event.entity
  if not (e and e.valid) then return end
  if TARGET[e.name] then
    register(e)
  elseif SPROUT[e.name] and not growing then
    replant(e)
  end
end

local function grow(data)
  local e = data.entity
  local surface, position, force, direction, quality = e.surface, e.position, e.force, e.direction, e.quality
  e.destroy()
  growing = true
  local ok, built = pcall(surface.create_entity, {
    name = data.target, position = position, force = force, direction = direction, quality = quality,
    raise_built = true, create_build_effect_smoke = true,
  })
  growing = false
  if not ok then error(built) end
  if built and built.valid and data.recipe and built.type == "assembling-machine" then
    pcall(built.set_recipe, data.recipe.name, data.recipe.quality)
  end
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
