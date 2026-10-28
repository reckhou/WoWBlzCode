# AGENT.md

Guidance for AI coding agents (Claude Code and others) working in this repository. `CLAUDE.md` points here.

## Purpose

This repository is a **read-only reference dump** of Blizzard's official World of Warcraft (WoW) user-interface (UI) code, kept so addon authors and agents can look up the real API usage, frame templates, mixins and events. It contains no build system, tests, linter or application code of its own.

## Layout

```
Retail/BlizzardInterfaceCode/Interface/AddOns/   <- Retail client (product "wow", Mainline)
Forever/BlizzardInterfaceCode/Interface/AddOns/  <- "Forever" client (product "wowf")
README.md                                        <- update log + game versions
```

Both trees are raw output of the client's `ExportInterfaceFiles code` console command ([Warcraft Wiki: Viewing Blizzard's interface code](https://warcraft.wiki.gg/wiki/Viewing_Blizzard's_interface_code)). The folder name `BlizzardInterfaceCode` is that command's output name. Each tree holds one folder per Blizzard UI addon (`Blizzard_*`), roughly 340 to 350 per tree, with `.lua`, `.xml` and `.toc` files (the `.toc` is the addon's table-of-contents manifest that lists load order).

## Where to look

- **API signatures, events, enums:** `Blizzard_APIDocumentationGenerated/*Documentation.lua`. These are the machine-generated API definitions, one file per system (for example `ContainerDocumentation.lua`). Start here to confirm a function's arguments, returns or event payload.
- **Documentation engine:** `Blizzard_APIDocumentation/` (mixins that consume the generated tables).
- **Shared building blocks:** `Blizzard_SharedXML*`, `Blizzard_FrameXMLBase`, `Blizzard_FrameXMLUtil`; `Blizzard_SharedXML/UI.xsd` is the XML schema for UI XML files.
- **Feature UIs:** one addon per feature, such as `Blizzard_ActionBar`, `Blizzard_AchievementUI`, `Blizzard_EncounterJournal`.
- **Per-flavour code:** the `.toc` files load files conditionally using tags such as `[AllowLoadGameType mainline]` or `[AllowLoadGameType classic]`. Subfolders like `Mainline/`, `Cata/`, `Mists/`, `Camelot/` (present under, for example, `Blizzard_FrameXMLBase`) hold flavour-specific variants. `Retail` carries many flavour-suffixed `.toc` files (`_Mainline`, `_Classic`, `_Mists`, `_Vanilla`, `_TBC`, `_Wrath`); `Forever` has far fewer.
- **Project IDs:** `WOW_PROJECT_*` constants live in `Blizzard_FrameXMLBase/Constants.lua` and its flavour subfolders.

## Working rules

- **Do not edit files under `Retail/` or `Forever/`.** They are verbatim exports; any edit is lost on the next refresh and falsifies the reference. Put notes in `docs/` or this file instead.
- Searching is the main task. The trees are large (about 4,000 files each), so use `rg -n` scoped to one tree (`Retail` or `Forever`) and compare the two trees when asked about flavour differences.
- Keep `.gitattributes` (`* -text`) in place so line endings are stored exactly as exported and diffs between refreshes stay clean.

## Refreshing the dump

1. Install or update the client, then launch it with `-console` and, at the login screen, run `ExportInterfaceFiles code` in the real console (it does not work via `/console` or when in-world, per the wiki above).
2. Replace the matching tree (`Retail/BlizzardInterfaceCode` for product `wow`, `Forever/BlizzardInterfaceCode` for product `wowf`) with the new export.
3. Read the exact build from `<WoW install>/.build.info` (the `Version` column, rows for products `wow` and `wowf`). The code itself does not contain a build number.
4. Add a new entry at the top of the update log in `README.md` with the date, flavour and build number, and update the "Current versions" table there.
5. Commit and push. Commit messages should name the flavour and build, for example `Retail 12.1.5.70575 export`.

## README convention

`README.md` must always show the latest update and the game version for each flavour (Retail and Forever). Keep the "Current versions" table and the update log in step with every refresh.
