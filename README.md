# WoWBlzCode

A dump of Blizzard's official World of Warcraft (WoW) user-interface (UI) code, kept as an API reference for addon development. It is a verbatim export from the game client, not original code. Blizzard Entertainment owns the content; this repository only mirrors it for reference.

Agent guidance is in [AGENT.md](AGENT.md) (and [CLAUDE.md](CLAUDE.md), which points to it).

## Current versions

| Flavour | Client product | Game version (build) | Folder | Last updated |
| --- | --- | --- | --- | --- |
| Retail | `wow` | 12.1.5.70575 | [`Retail/`](Retail/BlizzardInterfaceCode/Interface/AddOns) | 2026-10-28 |
| Forever | `wowf` | 1.60.1.70658 | [`Forever/`](Forever/BlizzardInterfaceCode/Interface/AddOns) | 2026-10-28 |

Versions are read from the `Version` column of the client's `.build.info` file. The exported code does not contain a build number.

## Update log

Newest first. Every refresh adds an entry here.

| Date | Flavour | Game version (build) | Notes |
| --- | --- | --- | --- |
| 2026-10-28 | Retail | 12.1.5.70575 | Initial export |
| 2026-10-28 | Forever | 1.60.1.70658 | Initial export |

## How the dump is produced

Run `ExportInterfaceFiles code` in the real in-game console at the login screen (client launched with `-console`). See [Viewing Blizzard's interface code](https://warcraft.wiki.gg/wiki/Viewing_Blizzard's_interface_code) on Warcraft Wiki. The output folder `BlizzardInterfaceCode` is copied into `Retail/` or `Forever/`.
