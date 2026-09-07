-- Invoked only by tests/neovim.py with disposable HOME/XDG paths.
local function test()
  local case = vim.env.DOTFILES_NVIM_CASE
  local config = vim.fn.stdpath("config")
  local specs, options, notices
  notices = {}
  vim.notify = function(message, level)
    notices[#notices + 1] = { message = message, level = level }
  end

  if case == "config" then
    vim.fn.mkdir(vim.fn.stdpath("data") .. "/lazy/lazy.nvim", "p")
    local lock = vim.json.decode(table.concat(vim.fn.readfile(config .. "/lazy-lock.json"), "\n"))
    vim.fn.executable = function(name) return name == "git" and 1 or 0 end
    vim.system = function(args)
      assert(vim.deep_equal(args, { "git", "-C", vim.fn.stdpath("data") .. "/lazy/lazy.nvim", "rev-parse", "HEAD" }))
      return { wait = function() return { code = 0, stdout = lock["lazy.nvim"].commit .. "\n" } end }
    end
    package.preload.lazy = function()
      return { setup = function(s, o) specs, options = s, o end }
    end
  elseif case == "bootstrap_failure" or case == "checkout_failure" then
    local executable = vim.fn.executable
    vim.fn.executable = function(name) return name == "git" and 1 or executable(name) end
    vim.system = function(args)
      if case == "checkout_failure" and args[2] == "clone" then
        vim.fn.mkdir(args[#args], "p")
        return { wait = function() return { code = 0 } end }
      end
      return { wait = function() return { code = 1, stderr = "fixture download failure" } end }
    end
  elseif case == "integration" then
    vim.o.loadplugins = true
  end

  -- -u NONE omits the normal config runtime path; enable native module lookup.
  vim.opt.rtp:prepend(config)
  dofile(config .. "/init.lua")
  assert(vim.o.number and vim.o.ignorecase and vim.o.smartcase)
  assert(vim.o.splitright and vim.o.splitbelow and vim.o.confirm)
  assert(not vim.o.termguicolors and vim.g.colors_name == "vim")
  assert(vim.o.clipboard == "") -- Do not overwrite clipboard on ordinary deletes.
  assert(not vim.o.exrc) -- Do not implicitly execute project configs.
  assert(vim.fn.maparg("s", "n") == "")

  if case == "config" then
    assert(#specs == 5)
    assert(options.lockfile == config .. "/lazy-lock.json")
    assert(options.local_spec == false and options.rocks.enabled == false)
    assert(options.checker.enabled == false)
    local by_name = {}
    for _, spec in ipairs(specs) do by_name[spec[1]] = spec end
    local snacks = by_name["folke/snacks.nvim"]
    assert(#snacks.keys == 5)
    assert(vim.deep_equal(vim.tbl_keys(snacks.opts), { "explorer", "picker" })
      or vim.deep_equal(vim.tbl_keys(snacks.opts), { "picker", "explorer" }))
    local calls = {}
    _G.Snacks = { picker = {} }
    for _, name in ipairs({ "files", "grep", "buffers", "help" }) do
      Snacks.picker[name] = function() calls[#calls + 1] = name end
    end
    Snacks.explorer = function() calls[#calls + 1] = "explorer" end
    local keys = { "<leader><space>", "<leader>/", "<leader>,", "<leader>e", "<leader>sh" }
    for i, key in ipairs(snacks.keys) do
      assert(key[1] == keys[i] and key.desc)
      key[2]()
    end
    assert(vim.deep_equal(calls, { "files", "grep", "buffers", "explorer", "help" }))
    local escape = snacks.opts.picker.win.input.keys["<Esc>"]
    assert(escape[1] == "close" and vim.deep_equal(escape.mode, { "n", "i" }))
    package.preload.gitsigns = function()
      return {
        nav_hunk = function(direction) calls[#calls + 1] = direction end,
        preview_hunk_inline = function() calls[#calls + 1] = "preview" end,
      }
    end
    by_name["lewis6991/gitsigns.nvim"].opts.on_attach(vim.api.nvim_get_current_buf())
    for _, key in ipairs({ "]h", "[h", " ghp" }) do
      local map = vim.fn.maparg(key, "n", false, true)
      assert(map.buffer == 1 and map.desc)
      map.callback()
    end
    assert(calls[6] == "next" and calls[7] == "prev" and calls[8] == "preview")
    by_name["nvim-treesitter/nvim-treesitter"].config()
    vim.bo.filetype = "dotfiles_missing_parser"
    assert(not vim.treesitter.highlighter.active[vim.api.nvim_get_current_buf()])
    assert(#notices == 0, vim.inspect(notices))
  elseif case == "write_undo" then
    vim.cmd.edit(vim.fn.fnameescape(config .. "/sample.txt"))
    vim.api.nvim_buf_set_lines(0, 0, -1, false, { "before" })
    vim.cmd.write()
    vim.cmd("normal! A after")
    vim.cmd.write()
  elseif case == "read_undo" then
    vim.cmd.edit(vim.fn.fnameescape(config .. "/sample.txt"))
    assert(vim.api.nvim_get_current_line() == "before after")
    vim.cmd.undo()
    assert(vim.api.nvim_get_current_line() == "before")
  elseif case == "undo_failure" then
    assert(not vim.o.undofile)
    assert(notices[1].message:find("persistent undo disabled", 1, true))
  elseif case == "bootstrap_failure" or case == "checkout_failure" then
    assert(notices[1].message:find("fixture download failure", 1, true))
  elseif case == "invalid_lock" then
    assert(notices[1].message:find("invalid lazy-lock.json", 1, true))
  elseif case == "offline" then
    assert(notices[1].message:find("install Git", 1, true))
  elseif case == "existing_match" then
    assert(vim.g.fixture_manager_loaded == true)
    assert(#notices == 0, vim.inspect(notices))
  elseif case == "existing_mismatch" or case == "existing_no_git" then
    assert(not vim.g.fixture_manager_loaded, "Unverified existing manager was executed")
    assert(not package.loaded.lazy)
    assert(notices[1].message:find(case == "existing_no_git" and "install Git" or "cannot verify", 1, true))
  elseif case == "integration" then
    require("lazy").load({ plugins = { "which-key.nvim", "nvim-surround", "gitsigns.nvim" } })
    for name, plugin in pairs(require("lazy.core.config").plugins) do
      assert(plugin._.installed, name .. " was not installed")
      assert(plugin._.loaded, name .. " was not loaded")
    end
    assert(vim.fn.exists(":TSInstall") == 2)
    assert(vim.fn.maparg("  ", "n") ~= "")
    vim.api.nvim_buf_set_lines(0, 0, -1, false, { "hello" })
    vim.cmd('normal ysiw"')
    assert(vim.api.nvim_get_current_line() == '"hello"')
    vim.cmd([[normal cs"']])
    assert(vim.api.nvim_get_current_line() == "'hello'")
    vim.cmd("normal ds'")
    assert(vim.api.nvim_get_current_line() == "hello")
    vim.bo.filetype = "dotfiles_missing_parser"
    -- The supplied Neovim Lua parser tests the actual highlighting callback.
    if vim.treesitter.language.add("lua") then
      vim.bo.filetype = "lua"
      assert(vim.treesitter.highlighter.active[vim.api.nvim_get_current_buf()])
    end
    local picker = Snacks.picker.buffers()
    assert(picker and not picker.closed)
    assert(vim.wait(5000, function() return not picker:is_active() and #picker:items() > 0 end))
    picker:close()
    vim.cmd.cd(vim.fn.fnameescape(vim.env.DOTFILES_NVIM_PROJECT))
    vim.cmd("edit! sample.lua")
    local gs = require("gitsigns")
    assert(vim.wait(5000, function() return vim.b.gitsigns_head ~= nil end), "Gitsigns did not attach")
    vim.api.nvim_buf_set_lines(0, 0, -1, false, { "local message = 'after'" })
    vim.api.nvim_exec_autocmds("TextChanged", {})
    assert(vim.wait(5000, function() return #(gs.get_hunks() or {}) > 0 end), "No Git hunk")
    assert(vim.fn.maparg("]h", "n", false, true).buffer == 1)
    picker = Snacks.picker.files()
    -- Finder results arrive before the asynchronous matcher updates the list.
    assert(vim.wait(5000, function()
      return not picker:is_active() and #picker:items() >= 3
    end), "File search did not finish")
    local files = {}
    for _, item in ipairs(picker:items()) do files[item.file] = true end
    assert(files[".hidden.lua"] and files["sample.lua"] and not files["ignored.txt"], vim.inspect(files))
    picker:close()
    picker = Snacks.picker.grep({ search = "before" })
    assert(vim.wait(5000, function()
      return not picker:is_active() and #picker:items() > 0
    end), "Text search did not finish")
    picker:close()
    picker = Snacks.explorer()
    assert(picker and not picker.closed)
    assert(vim.wait(5000, function()
      return not picker:is_active() and #picker:items() > 0
    end), "Explorer did not finish opening")
    picker:close()
    vim.wait(100)
    for _, notice in ipairs(notices) do
      assert((notice.level or 0) < vim.log.levels.ERROR, notice.message)
    end
  end
  assert(vim.v.errmsg == "", vim.v.errmsg)
  print("NEOVIM TEST OK")
end

local ok, err = xpcall(test, debug.traceback)
if not ok then
  if package.loaded["lazy.core.config"] then
    local git = require("lazy.manage.git")
    for name, plugin in pairs(require("lazy.core.config").plugins) do
      io.stderr:write(name .. ": " .. vim.inspect(git.info(plugin.dir)) .. "\n")
    end
  end
  io.stderr:write(tostring(err) .. "\n")
  vim.cmd("cquit 1")
else
  vim.cmd("qa!")
end
