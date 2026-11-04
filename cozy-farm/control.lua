-- Cozy Farm: start kit for new games (seeds, soil and a few animals).

local START_KIT = {
  ["cozy-garden-soil"] = 50,
  ["cozy-carrot-seeds"] = 10,
  ["cozy-potato-seeds"] = 10,
  ["cozy-wheat-seeds"] = 10,
  ["cozy-tomato-seeds"] = 5,
  ["cozy-pumpkin-seeds"] = 5,
  ["cozy-chicken"] = 4,
  ["cozy-cow"] = 2,
  ["cozy-sheep"] = 2,
  ["cozy-flax-seeds"] = 10,
  ["cozy-hay"] = 20,
  ["cozy-plank"] = 20,
}

local function use_freeplay()
  if not (remote.interfaces["freeplay"] and remote.interfaces["freeplay"]["get_created_items"]) then return false end
  -- Replace the vanilla start (iron plates, burner drill, crashed ship) with the farm kit.
  local items = {}
  for name, count in pairs(START_KIT) do items[name] = count end
  remote.call("freeplay", "set_created_items", items)
  remote.call("freeplay", "set_respawn_items", {})
  pcall(remote.call, "freeplay", "set_disable_crashsite", true)
  pcall(remote.call, "freeplay", "set_skip_intro", true)
  return true
end

local function give(player)
  for name, count in pairs(START_KIT) do
    if player.can_insert({ name = name, count = count }) then
      player.insert({ name = name, count = count })
    end
  end
  player.print({ "cozy-farm.welcome" })
end

script.on_init(function()
  storage.freeplay = use_freeplay()
  storage.given = {}
  -- Mod added to an existing save: hand the kit to players that already exist.
  for _, player in pairs(game.players) do
    if player.character then
      give(player)
      storage.given[player.index] = true
    end
  end
end)

script.on_event(defines.events.on_player_created, function(event)
  local player = game.get_player(event.player_index)
  if not player then return end
  if storage.freeplay then
    player.print({ "cozy-farm.welcome" })
  elseif not storage.given[player.index] then
    give(player)
    storage.given[player.index] = true
  end
end)
