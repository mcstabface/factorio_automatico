local function write_error(filename, message)
  helpers.write_file(filename, message, false, 0)
end

local function write_json(filename, payload)
  helpers.write_file(filename, helpers.table_to_json(payload), false, 0)
end

local function first_connected_player()
  local players = game.connected_players
  if #players == 0 then
    return nil
  end

  return players[1]
end

commands.add_command("chatgpt-get-position", "Write first connected player position to script-output/chatgpt/player_position.json", function(command)
  local player = first_connected_player()
  if player == nil then
    write_error("chatgpt/player_position_error.txt", "no-connected-players")
    return
  end

  local position = player.position
  write_json("chatgpt/player_position.json", {
    x = position.x,
    y = position.y
  })
end)

commands.add_command("chatgpt-move-step", "Take one bounded walking step toward target x,y and write result to script-output/chatgpt/move_to_result.json", function(command)
  local player = first_connected_player()
  if player == nil then
    write_error("chatgpt/move_to_error.txt", "no-connected-players")
    return
  end

  if command.parameter == nil or command.parameter == "" then
    write_error("chatgpt/move_to_error.txt", "missing-parameters")
    return
  end

  local x_str, y_str = string.match(command.parameter, "^%s*([%-%d%.]+)%s*,%s*([%-%d%.]+)%s*$")
  if x_str == nil or y_str == nil then
    write_error("chatgpt/move_to_error.txt", "invalid-parameters")
    return
  end

  local target_x = tonumber(x_str)
  local target_y = tonumber(y_str)
  if target_x == nil or target_y == nil then
    write_error("chatgpt/move_to_error.txt", "non-numeric-parameters")
    return
  end

  local target = { x = target_x, y = target_y }
  local position = player.position
  local dx = target.x - position.x
  local dy = target.y - position.y

  if math.abs(dx) < 0.2 and math.abs(dy) < 0.2 then
    write_json("chatgpt/move_to_result.json", {
      x = position.x,
      y = position.y
    })
    return
  end

  local direction = nil
  if dx > 0.2 and dy > 0.2 then
    direction = defines.direction.southeast
  elseif dx > 0.2 and dy < -0.2 then
    direction = defines.direction.northeast
  elseif dx < -0.2 and dy > 0.2 then
    direction = defines.direction.southwest
  elseif dx < -0.2 and dy < -0.2 then
    direction = defines.direction.northwest
  elseif dx > 0 then
    direction = defines.direction.east
  elseif dx < 0 then
    direction = defines.direction.west
  elseif dy > 0 then
    direction = defines.direction.south
  else
    direction = defines.direction.north
  end

  player.walking_state = {
    walking = true,
    direction = direction
  }

  write_json("chatgpt/move_to_started.json", {
    direction = helpers.direction_to_string(direction),
    x = position.x,
    y = position.y
  })
end)

commands.add_command("chatgpt-stop-walk", "Stop first connected player walking and write result to script-output/chatgpt/move_to_result.json", function(command)
  local player = first_connected_player()
  if player == nil then
    write_error("chatgpt/move_to_error.txt", "no-connected-players")
    return
  end

  player.walking_state = {
    walking = false,
    direction = player.walking_state.direction
  }

  local position = player.position
  write_json("chatgpt/move_to_result.json", {
    x = position.x,
    y = position.y
  })
end)