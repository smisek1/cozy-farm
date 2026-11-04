-- Shared helpers for Cozy Farm prototypes.
local common = {}

common.P = "cozy-"                       -- prototype name prefix
common.G = "__cozy-farm__/graphics/"

function common.icon(name) return common.G .. "icons/" .. name .. ".png" end

--- Icon layers: base icon (vanilla) with a small badge from our icons in the corner.
function common.badged(base_icon, badge, tint)
  return {
    { icon = base_icon, icon_size = 64, tint = tint },
    { icon = common.icon(badge), icon_size = 64, scale = 0.3, shift = { 8, 8 } },
  }
end

--- Recursively applies a tint to every sprite layer that is not a shadow.
function common.tint_graphics(t, tint, seen)
  seen = seen or {}
  if type(t) ~= "table" or seen[t] then return end
  seen[t] = true
  if t.filename or t.filenames or t.stripes then
    if not t.draw_as_shadow and not t.draw_as_light and not t.draw_as_glow then t.tint = tint end
  end
  for _, v in pairs(t) do common.tint_graphics(v, tint, seen) end
end

--- Healing capsule action (copied from the vanilla fish so sounds/cooldown match).
function common.food_action(heal)
  local action = table.deepcopy(data.raw.capsule["raw-fish"].capsule_action)
  local function walk(t)
    if type(t) ~= "table" then return end
    if t.type == "damage" and t.damage then t.damage.amount = -heal end
    for _, v in pairs(t) do walk(v) end
  end
  walk(action)
  return action
end

function common.item(name, subgroup, order, stack, extra)
  local proto = {
    type = "item",
    name = common.P .. name,
    icon = common.icon(name),
    icon_size = 64,
    subgroup = "cozy-farm-" .. subgroup,
    order = order,
    stack_size = stack or 50,
  }
  for k, v in pairs(extra or {}) do proto[k] = v end
  return proto
end

-- Ingredient names without the prefix that refer to vanilla items.
common.VANILLA = { ["wood"] = true, ["tree-seed"] = true, ["transport-belt"] = true, ["wooden-chest"] = true }

function common.ing(name, amount)
  local full = common.VANILLA[name] and name or (common.P .. name)
  return { type = "item", name = full, amount = amount }
end

function common.recipe(name, category, time, ingredients, results, extra)
  local ings, res = {}, {}
  for _, i in ipairs(ingredients) do ings[#ings + 1] = common.ing(i[1], i[2]) end
  for _, r in ipairs(results) do
    local x = common.ing(r[1], r[2])
    if r.probability then x.independent_probability = r.probability end
    res[#res + 1] = x
  end
  local proto = {
    type = "recipe",
    name = common.P .. name,
    categories = { category },
    energy_required = time,
    ingredients = ings,
    results = res,
    enabled = true,
    allow_productivity = false,
  }
  for k, v in pairs(extra or {}) do proto[k] = v end
  return proto
end

--- Energy source of a "living" building: it eats (fuel category cozy-food, food slot icon).
function common.fed_energy()
  return {
    type = "burner",
    fuel_categories = { "cozy-food" },
    effectivity = 1,
    fuel_inventory_size = 1,
    burner_usage = "food",
    emissions_per_minute = { pollution = -1 },
  }
end

--- Copy of a vanilla crafting machine turned into a living Cozy Farm building.
function common.machine(kind, base_name, name, opts)
  local base = data.raw[kind][base_name]
  local e = table.deepcopy(base)
  e.name = common.P .. name
  e.icon = nil
  e.icons = common.badged(base.icon, opts.badge, opts.tint)
  e.minable = { mining_time = 0.3, result = common.P .. name }
  if opts.categories then e.crafting_categories = opts.categories end
  if opts.speed then e.crafting_speed = opts.speed end
  e.energy_source = common.fed_energy()
  e.energy_usage = opts.usage or "75kW"
  e.next_upgrade = nil
  e.fast_replaceable_group = opts.replace_group
  e.module_slots = 0
  e.allowed_effects = nil
  e.effect_receiver = nil
  e.surface_conditions = nil
  e.heating_energy = nil
  if opts.tint then common.tint_graphics(e.graphics_set, opts.tint) end
  local item = common.item(name, opts.subgroup or "buildings", opts.order or "z", 20, { place_result = common.P .. name })
  item.icon = nil
  item.icons = e.icons
  return e, item
end

return common
