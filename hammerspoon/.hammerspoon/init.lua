local menu = hs.menubar.new()

function updateMenu()
  local uuid = hs.screen.mainScreen():getUUID()
  local all = hs.spaces.allSpaces()[uuid]
  local current = hs.spaces.focusedSpace()

  local display = {}

  for i, sid in ipairs(all) do
    if sid == current then
      table.insert(display, "[" .. i .. "]")
    else
      table.insert(display, tostring(i))
    end
  end

  menu:setTitle(table.concat(display, "  "))
end

hs.spaces.watcher.new(updateMenu):start()
updateMenu()
