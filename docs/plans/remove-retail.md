# Plan: Remove Retail and keep Forever only

Status: done. Approved. Retail kept in git history (question 1: keep). Retail rows removed from the README update log (question 2: remove).

Abbreviations:
- UI: user interface (the game's Lua and XML addon code).
- API index: the compact list of functions, events, enums, structures and constants in `index/`.
- wow / wowf: the client product codes for Retail and Forever.

## Scope

The repo currently holds two trees: Retail (4,022 tracked files under `Retail/`) and Forever (under `Forever/`). The goal is to keep only Forever.

## Steps

1. Delete the Retail UI tree: `git rm -r Retail/` (4,022 files).
2. Delete the Retail API index: `git rm -r index/Retail/` (5 files).
3. Edit `tools/build_index.py`: change `FLAVOURS = ["Retail", "Forever"]` to `FLAVOURS = ["Forever"]`. Rebuild the index with `python -I tools/build_index.py`. It must report 0 failures.
4. Edit `AGENT.md`: remove the Retail lines (layout, refresh step 2, the commit example, the README convention). Change the "Do not edit" and "compare trees" rules so they name Forever only.
5. Edit `README.md`: remove the Retail row from "Current versions", change the lookup paths from `index/Retail` and `Retail/` to Forever, and decide on the old Retail update log rows (see question 2).
6. Commit with a message such as `Remove Retail tree and index; Forever only`, then push. Do not bump a version or tag, per the release rule.

## Not changing

- Forever's own code that mentions Retail stays. These lines are part of the Forever export, so editing them would falsify the reference:
  - `Forever/.../Blizzard_APIDocumentationGenerated/ClientSettingsDocumentation.lua` (flags such as `ClientSettingsConfigRetail`).
  - `Forever/.../Blizzard_GlueXMLBase/Mainline/Localization.lua` (the text "full retail account").
  - `index/Forever/enums.txt` (the same ClientSettings flags).

## Reversibility

Removing files in a commit is reversible: `git revert` or `git checkout <commit> -- Retail/` brings them back. The Retail code stays in the history of earlier commits such as `21ec933`.

## Open questions

1. Keep Retail in git history (recommended; the commit only stops tracking it), or rewrite history to purge it? A rewrite changes every commit hash and needs a force push, which breaks existing clones.
2. In the README update log, keep the old Retail rows as history (recommended), or remove them?
