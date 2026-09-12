# Zathura keybindings

Everyday shortcuts for the managed Linux setup, checked against Zathura
2026.07.18. The [config](home/dot_config/zathura/zathurarc.tmpl) keeps native
bindings and adds three view shortcuts. Setup is in
[README](README.md#zathura).

Letters are case-sensitive: `j` scrolls, while `J` changes page. Type sequences
such as `18G` and `125=` directly in normal reading mode, without `:` or Enter.
Press Escape to cancel a prompt or leave the document index.

## Reading

| Keys | Action |
|---|---|
| `a` / `s` | Fit the whole page / fit page width |
| `P` | Align the current page in the view |
| `j` / `k` | Scroll down / up |
| `h` / `l` | Scroll left / right when zoomed in |
| `Page Down` or `J` | Next page |
| `Page Up` or `K` | Previous page |
| `Home` or `gg` | First page (start of the document) |
| `End` or `G` | Last page (end of the document) |
| `18G` | Go to physical PDF page 18 (with the default zero page offset) |
| `+` / `-` | Zoom in / out |
| `125=` / `=` | Set 125% zoom / reset zoom |

New documents start fitted to the whole page. For slides, press `a`, then `P`
to fit and align the current slide. For long pages, use `s` and scroll.
Previously opened documents restore their saved zoom, so press `a` once if an
old document still opens too large.

## Slide labels and PDF pages

In `[25 (35/71)]`, `25` is the slide/page label and `35` is the physical PDF
page. Several physical pages can share a label when a slide reveals content
in stages. `35G` goes directly to physical page 35; Page Up/Down move through
individual physical pages. Zathura displays embedded labels but has no native
shortcut to jump to a label or skip to the next distinct label. If the PDF
provides an index, use Tab to navigate its entries.

## Find and return

| Keys | Action |
|---|---|
| `/text` then Enter | Search the document |
| `n` / `N` | Next / previous search result |
| `Tab` | Open or close the document index |
| `f` | Follow a document link |
| `Ctrl-O` / `Ctrl-I` | Backward / forward through jump history |

After jumping through the index or following an internal link, `Ctrl-O`
returns to the previous reading position. Inside the index, use `j`/`k` to
choose an entry and Enter to open it.

## View controls

| Keys | Action |
|---|---|
| `Ctrl-R` or `F4` | Toggle recoloring |
| `d` or `F6` | Toggle one/two-page layout |
| `b` or `Ctrl-N` | Toggle the status bar |
| `r` | Rotate the page |
| `R` | Reload the document |
| `F5` / `F11` | Toggle presentation mode / fullscreen |
| `q` | Quit |

Recoloring starts off so diagrams and images keep their original colors.

References: [native Zathura shortcuts](https://pwmt.org/projects/zathura/documentation/)
and [default bindings for 2026.07.18](https://github.com/pwmt/zathura/blob/2026.07.18/zathura/config.c#L273-L290).
