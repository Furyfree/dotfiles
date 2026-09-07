# Zed keybindings

The managed `keymap.json` contains only custom overrides. `base_keymap: VSCode`
in settings supplies the normal bindings underneath it. Keeping this file
small does not remove the inherited shortcuts.

The tables describe the managed setup, checked against Zed 1.18.1. Linux is
the current-machine comparison; macOS uses its own native bindings, not a blind
Ctrl-to-Cmd replacement. Windows uses the same custom terminal shortcut as Linux.

## Everyday workflow

These bindings assume normal editor focus, without Vim mode. Language-aware
actions need support from the file's language server.

| Action | Linux | macOS |
|---|---|---|
| Open a recent project | Ctrl+R | Cmd+Option+O |
| Find/open a file | Ctrl+P | Cmd+P |
| Command palette | Ctrl+Shift+P | Cmd+Shift+P |
| Search current file | Ctrl+F | Cmd+F |
| Search project | Ctrl+Shift+F | Cmd+Shift+F |
| Find symbols in current file | Ctrl+Shift+O | Cmd+Shift+O |
| Switch between open tabs | Ctrl+Tab | Ctrl+Tab |
| Go to definition | F12 | F12 |
| Rename symbol | F2 | F2 |
| Quick fixes/code actions | Ctrl+. | Cmd+. |
| Format document manually | Alt+Shift+F | Option+Shift+F |
| Save | Ctrl+S | Cmd+S |
| Toggle left sidebar | Ctrl+B | Cmd+B |
| Toggle bottom dock | Ctrl+J | Cmd+J |
| Focus agent panel | Ctrl+Alt+I | Ctrl+Cmd+I |
| Reopen closed tab | Ctrl+Shift+T | Cmd+Shift+T |
| Toggle terminal panel (custom) | Ctrl+Alt+Shift+J | Cmd+Option+Shift+J |

For example: open a project, use Ctrl+P to find a file, Ctrl+Shift+O to jump
to a function, and F12 to follow a definition. Edit, format, and save manually.
Use Ctrl+Tab to switch files and Ctrl+J to show or hide the bottom dock.

Ctrl+J is the simpler everyday choice when the terminal occupies the bottom
dock, but it toggles the last selected bottom panel, not specifically the
terminal. The custom four-key shortcut targets the terminal directly and
avoids backtick on a Danish keyboard. Native Ctrl+backtick remains available
on both Linux and macOS when the keyboard can send it.

Focus matters: Ctrl+R inside the terminal goes to the shell's history search,
not the recent-project picker. OS/compositor shortcuts can intercept keys;
the actual Danish layout and macOS input still need a manual check.

## Compared with the previous Linux overrides

"Previous" means the live keymap inspected when this Zed slice was created,
not a second keymap maintained by this repository.

| Action | Previous override | Managed setup |
|---|---|---|
| Toggle terminal specifically | Ctrl+Shift+T | Ctrl+Alt+Shift+J |
| Recent projects | Ctrl+Shift+O, requesting a new window | Ctrl+R, normal picker |
| Focus agent | Ctrl+Shift+A | Ctrl+Alt+I |
| Focus outline panel | Ctrl+Alt+B | Ctrl+Shift+B |
| Toggle right dock | Ctrl+Shift+B | Ctrl+Alt+B |

Removing those overrides restores Ctrl+Shift+T for reopening a closed tab,
Ctrl+Shift+O for the current-file symbol picker, and Ctrl+Shift+A for toggling
block comments in the editor. Other bindings continue to come from the base
keymap; there is no additional remapping hidden in this guide.

Keep native bindings unless a repeated workflow or keyboard-layout problem
justifies an override. See [README](README.md#zed) for inspecting the installed
keymaps and running validation.

Sources: [Zed keybinding inheritance and precedence](https://zed.dev/docs/key-bindings),
[Linux defaults](https://github.com/zed-industries/zed/blob/bebe92f469834a287f5a57ed78e8d51a918b8ada/assets/keymaps/default-linux.json),
[Linux/Windows VS Code overlay](https://github.com/zed-industries/zed/blob/bebe92f469834a287f5a57ed78e8d51a918b8ada/assets/keymaps/linux/vscode.json),
[macOS defaults](https://github.com/zed-industries/zed/blob/bebe92f469834a287f5a57ed78e8d51a918b8ada/assets/keymaps/default-macos.json),
and [macOS VS Code overlay](https://github.com/zed-industries/zed/blob/bebe92f469834a287f5a57ed78e8d51a918b8ada/assets/keymaps/macos/vscode.json).
