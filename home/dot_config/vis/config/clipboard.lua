local notify = require('config.util').notify
local M = {}

-- Keep native yanks; register 0 changes only when an unnamed yank completes.
local pending_yank
local function yank_text()
  local parts = vis.registers['0']
  for i, text in ipairs(parts) do parts[i] = text:gsub('%z$', '') end
  return table.concat(parts)
end
function M.finish_yank()
  if not pending_yank or vis.mode == vis.modes.OPERATOR_PENDING then return end
  local previous = pending_yank
  pending_yank = nil
  local text = yank_text()
  if text == '' then
    vis.registers['0'] = previous
    return
  end
  local clipboard = io.popen('vis-clipboard --copy --selection clipboard', 'w')
  if not clipboard then notify('Clipboard unavailable'); return end
  local written = clipboard:write(text)
  local ok = clipboard:close()
  notify(written and ok and 'Copied' or 'Clipboard copy failed')
end

for _, mode in ipairs({vis.modes.NORMAL, vis.modes.VISUAL, vis.modes.VISUAL_LINE}) do
  vis:map(mode, 'y', function()
    M.finish_yank()
    if vis.register == '"' then
      pending_yank = vis.registers['0']
      vis.registers['0'] = {}
    end
    vis:feedkeys('<vis-operator-yank>')
    M.finish_yank()
  end, 'Yank and copy to the system clipboard')
  for key, action in pairs({p = '<vis-put-after>', P = '<vis-put-before>'}) do
    vis:map(mode, key, function()
      M.finish_yank()
      if vis.register == '"' then
        local status, text = vis:pipe('vis-clipboard --paste --selection clipboard')
        if status ~= 0 then notify('Clipboard paste failed'); return end
        if not text or text == '' then notify('Clipboard is empty'); return end
        -- Preserve linewise and multiple-selection paste for our own yanks.
        vis.register = text == yank_text() and '0' or '+'
      end
      vis:feedkeys(action)
    end, 'Paste from the system clipboard')
  end
end

return M
