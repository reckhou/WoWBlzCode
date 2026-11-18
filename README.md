# WoWBlzCode

A dump of Blizzard's official World of Warcraft (WoW) user-interface (UI) code, kept as an API reference for addon development. It is a verbatim export from the game client, not original code. Blizzard Entertainment owns the content; this repository only mirrors it for reference.

Agent guidance is in [AGENT.md](AGENT.md) (and [CLAUDE.md](CLAUDE.md), which points to it).

## Current versions

| Flavour | Client product | Game version (build) | Folder | Last updated |
| --- | --- | --- | --- | --- |
| Forever | `wowf` | 1.60.1.70959 | [`Forever/`](Forever/BlizzardInterfaceCode/Interface/AddOns) | 2026-11-18 |

Versions are read from the `Version` column of the client's `.build.info` file. The exported code does not contain a build number.

## Agent lookup instructions (for addon development)

Intended use: add this repository as a Git submodule of an addon project, then have the agent look things up here rather than rely on memory. In the paths below, `<repo>` is the submodule path. The dump covers the Forever flavour only.

**Never read a whole index file** (`functions.txt` is about 860 KB). Search it with `rg -n` and read only the matching lines.

1. **Check an API or event first, in the compact index** (`<repo>/index/Forever/`). Each file holds one record per line, taken from Blizzard's own generated API documentation:

   | File | Record format | Example search |
   | --- | --- | --- |
   | `functions.txt` | `Namespace.Name(args) -> returns [flags] -- doc @System` | `rg -n "GetBagName" <repo>/index/Forever/functions.txt` |
   | `events.txt` | `EVENT_NAME(payload) [flags] @System` | `rg -n "^BAG_UPDATE" <repo>/index/Forever/events.txt` |
   | `enums.txt` | `EnumName = Member:value, ... @System` | `rg -n "^BagIndex =" <repo>/index/Forever/enums.txt` |
   | `structures.txt` | `StructName { field: Type, ... } @System`, or `callback Name(args)` | `rg -n "^ContainerItemInfo" <repo>/index/Forever/structures.txt` |
   | `constants.txt` | `Group.NAME: Type = value @System` | `rg -n "MAX_" <repo>/index/Forever/constants.txt` |

   Notation: `name?: Type` is nilable (may be nil); `= x` is the default value; `Type<Inner>` is a table of `Inner`; `Type(Mixin)` names the mixin the value uses; `[flags]` lists restriction markers such as `SecretArguments=...` or `IsProtectedFunction`; `@System` means the record comes from `<repo>/Forever/BlizzardInterfaceCode/Interface/AddOns/Blizzard_APIDocumentationGenerated/<System>Documentation.lua`. If a name is not in the index, it is not in that flavour's documented API, so say so rather than guessing.

2. **Find the full definition or documentation text** by opening the `@System` source file named on the index line.
3. **See how Blizzard really uses it**: search the feature addons for call sites, mixins, frame templates and XML, for example `rg -n "C_Container.GetBagName" <repo>/Forever/BlizzardInterfaceCode/Interface/AddOns --glob "*.lua"`.
4. **Do not edit** anything under `Forever/` or `index/`. The index is generated; rebuild it with `python -I tools/build_index.py` (needs Python 3 only) after each refresh.

## Update log

Newest first. Every refresh adds an entry here.

| Date | Flavour | Game version (build) | Notes |
| --- | --- | --- | --- |
| 2026-11-18 | Forever | 1.60.1.70959 | Re-export of Forever tree from the client `.build.info` (`wowf` 1.60.1.70959); compact index rebuilt (`index/`). |
| 2026-11-14 | Forever | 1.60.1.70938 | Re-export of Forever tree; compact index rebuilt (`index/`). |
| 2026-10-28 | Forever | 1.60.1.70658 | Added compact API index (`index/`) and builder script (`tools/build_index.py`); game data unchanged |
| 2026-10-28 | Forever | 1.60.1.70658 | Initial export |

## How the dump is produced

Run `ExportInterfaceFiles code` in the real in-game console at the login screen (client launched with `-console`). See [Viewing Blizzard's interface code](https://warcraft.wiki.gg/wiki/Viewing_Blizzard's_interface_code) on Warcraft Wiki. The output folder `BlizzardInterfaceCode` is copied into `Forever/`.
