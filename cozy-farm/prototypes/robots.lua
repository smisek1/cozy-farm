-- CRISPR-Cas9 (science pack 3) and biorobots: the hive (roboport), worker bees (logistic robots),
-- builder bumblebees (construction robots) and honeycombs (logistic chests).
local common = require("prototypes.common")
local P = common.P

local HONEY = { 1, 0.82, 0.4 }
local BEE = { 1, 0.9, 0.45 }

local function ing(list)
  local out = {}
  for _, i in ipairs(list) do out[#out + 1] = common.ing(i[1], i[2]) end
  return out
end

local function reskin(kind, name, tint, ingredients, count)
  local e = data.raw[kind][name]
  common.tint_graphics(e, tint)
  local icon_size = e.icon_size or 64
  e.icons = { { icon = e.icon, icon_size = icon_size, tint = tint } }
  local item = data.raw.item[name]
  if item then item.icons = e.icons end
  local r = data.raw.recipe[name]
  r.ingredients = ing(ingredients)
  r.results = { { type = "item", name = name, amount = count or 1 } }
  r.enabled = false
  COZY_KEEP_RECIPES[name] = true
end

reskin("roboport", "roboport", HONEY,
  { { "plank", 20 }, { "biocement", 20 }, { "chitin", 10 }, { "nerve-tissue", 10 }, { "resin", 10 } })
reskin("logistic-robot", "logistic-robot", BEE, { { "chitin", 2 }, { "nerve-tissue", 2 }, { "sugar", 1 } })
reskin("construction-robot", "construction-robot", BEE, { { "chitin", 2 }, { "nerve-tissue", 2 }, { "silk", 1 } })
local COMB = { { "wooden-chest", 1 }, { "resin", 2 }, { "nerve-tissue", 1 } }
for _, chest in ipairs({ "passive-provider-chest", "active-provider-chest", "storage-chest", "requester-chest", "buffer-chest" }) do
  reskin("logistic-container", chest, nil, COMB)
end

-- Science pack 3
local crispr = common.item("crispr-kit", "science", "c", 200)
crispr.type = "tool"
crispr.durability = 1
table.insert(data.raw.lab[P .. "sequencer"].inputs, P .. "crispr-kit")

local function tech(name, icon, unlocks, prereqs, count, packs, order)
  local effects, pre, ings = {}, {}, {}
  for _, r in ipairs(unlocks) do
    effects[#effects + 1] = { type = "unlock-recipe", recipe = data.raw.recipe[r] and r or (P .. r) }
  end
  for _, p in ipairs(prereqs) do pre[#pre + 1] = P .. p end
  for _, p in ipairs(packs) do ings[#ings + 1] = { P .. p, 1 } end
  return {
    type = "technology", name = P .. name, icon = icon, icon_size = 64,
    effects = effects, prerequisites = pre, order = "z-cozy-" .. order,
    unit = { count = count, ingredients = ings, time = 30 },
  }
end
local DNA2 = { "dna-sample", "genome-sequence" }
local DNA3 = { "dna-sample", "genome-sequence", "crispr-kit" }

data:extend({
  crispr,
  common.item("bacteria-culture", "materials", "k", 100),
  common.recipe("bacteria-culture", "cozy-digest", 10, { { "sugar", 1 }, { "mycelium", 1 } }, { { "bacteria-culture", 2 } },
    { enabled = false }),
  common.recipe("crispr-kit", "cozy-ant", 15, { { "genome-sequence", 1 }, { "bacteria-culture", 2 }, { "nerve-tissue", 1 } },
    { { "crispr-kit", 1 } }, { enabled = false }),

  tech("crispr", common.icon("crispr-kit"), { "bacteria-culture", "crispr-kit" }, { "mushroom-farm" }, 50, DNA2, "j"),
  tech("bee-hive", common.icon("bee"),
    { "roboport", "logistic-robot", "construction-robot", "passive-provider-chest", "storage-chest" },
    { "crispr", "chitin" }, 75, DNA3, "k"),
  tech("honeycomb-logistics", "__base__/graphics/icons/requester-chest.png",
    { "requester-chest", "active-provider-chest", "buffer-chest" }, { "bee-hive" }, 100, DNA3, "l"),
})
