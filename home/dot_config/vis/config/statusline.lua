local util = require('config.util')
local finish_yank = require('config.clipboard').finish_yank

local modes = {
  [vis.modes.NORMAL] = {'NORMAL', 'cyan'},
  [vis.modes.OPERATOR_PENDING] = {'PENDING', 'blue'},
  [vis.modes.INSERT] = {'INSERT', 'green'},
  [vis.modes.REPLACE] = {'REPLACE', 'magenta'},
  [vis.modes.VISUAL] = {'VISUAL', 'yellow'},
  [vis.modes.VISUAL_LINE] = {'VISUAL LINE', 'yellow'},
}
vis.events.subscribe(vis.events.WIN_STATUS, function(win)
  if win == vis.win then finish_yank() end
  local mode = modes[vis.mode]
  local keys = vis.input_queue
  local label = vis.mode == vis.modes.NORMAL and keys:sub(1, 1) == ' '
    and 'SPACE' .. keys:sub(2) .. ' …' or mode[1]
  local feedback = util.feedback
  local left = (win == vis.win and label .. ' | ' .. (feedback and feedback .. ' | ' or '') or '')
    .. (util.titles[win] or win.file.name or '[No Name]')
    .. (win.file.modified and ' [+]' or '') .. (vis.recording and ' @' or '')
  if win == vis.win then
    local foreground = vis.mode == vis.modes.OPERATOR_PENDING and 'white' or 'black'
    win:style_define(win.STYLE_STATUS_FOCUSED, 'fore:' .. foreground .. ',back:' .. mode[2] .. ',bold')
  end
  local selection = win.selection
  local right = keys ~= '' and keys or tostring(vis.count or '')
  if #win.selections > 1 then right = right .. ' ' .. selection.number .. '/' .. #win.selections end
  right = right .. ' ' .. (selection.line or 0) .. ':' .. (selection.col or 0)
  win:status(' ' .. left .. ' ', ' ' .. right .. ' ')
  return true
end, 1)
