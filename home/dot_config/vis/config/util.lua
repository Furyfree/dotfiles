local M = {}

-- Display names for windows without a file path, such as directory listings.
M.titles = setmetatable({}, {__mode = 'k'})

-- Status feedback expires even when no further keys are pressed.
local feedback_timer, feedback_name
local feedback_serial = 0
function M.notify(text)
  if feedback_timer and io.type(feedback_timer) == 'file' then feedback_timer:close() end
  feedback_serial = feedback_serial + 1
  feedback_name = 'vis-status-feedback-' .. feedback_serial
  M.feedback = text
  feedback_timer = vis:communicate(feedback_name, 'exec sleep 2')
end
vis.events.subscribe(vis.events.PROCESS_RESPONSE, function(name, event)
  if not name:match('^vis%-status%-feedback%-') then return end
  if name == feedback_name and (event == 'EXIT' or event == 'SIGNAL') then
    M.feedback, feedback_timer, feedback_name = nil, nil, nil
    vis:redraw()
  end
  return true
end, 1)

function M.quote(text)
  return "'" .. text:gsub("'", "'\\''") .. "'"
end

-- Run an fzf picker from the working directory; nil when cancelled.
function M.pick(command)
  local status, choice, err = vis:pipe(command, true)
  if status == 0 and choice and choice ~= '' then
    return choice
  elseif status ~= 1 and status ~= 130 then
    vis:info(err and err ~= '' and err or 'Picker failed')
  end
end

-- Quote for Vis's command parser; :e keeps its unsaved-change check.
function M.open(path)
  return vis:command('e "' .. path:gsub('[\\"]', '\\%0') .. '"')
end

return M
