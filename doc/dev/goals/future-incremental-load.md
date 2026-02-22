# Future Goal: Incremental Load

## Problem

`flextag.load(dir=[...])` re-parses every `.ft` file in every directory on every call. For a project with 7 directories and 123 sections across ~30 files, this means a single settings change (one file modified) triggers a full re-parse of all files — including pipelines, schemas, workspaces, and plugin definitions that didn't change.

In the Techie Trading frontend, this showed up as a performance bottleneck: changing a color setting triggered a full reload, which cascaded into plugin cache invalidation, WebSocket broadcasts, and redundant API calls. The downstream cascade was fixed at the application level (batch writes, skipping full reload for settings, selective bundle clearing), but the core issue remains — `flextag.load()` is all-or-nothing.

As the number of plugins, pipelines, and data files grows, the cost of a full reload increases linearly.

## Current Behavior

- `flextag.load(dir=[...])` scans all directories, reads all `.ft` files, parses all sections, returns a new `FlexView`
- No way to say "reload only this file" or "reload only files that changed"
- Sections already track `source_path`, so the information about where each section came from exists
- The consuming application (Techie Trading) works around this by tracking file mtimes externally and avoiding `load()` when possible

## Possible Approaches

### A. File-level incremental reload

Track file checksums or mtimes internally. On reload, only re-parse files that actually changed. Merge updated sections into the existing view, replacing sections from changed files while keeping sections from unchanged files intact.

Considerations:
- Sections from deleted files need to be removed
- New files need to be detected and added
- `source_path` already provides the grouping key
- Validation (schemas) may need to re-run if schema files themselves changed

### B. Selective directory reload

Allow `flextag.load()` to accept a subset of directories to reload while preserving the rest. Something like `view.reload_dirs(["plugins/user/"])` that only re-scans the specified directories.

Simpler than file-level, covers the common case: settings and user plugins change frequently, builtin plugins and schemas rarely change.

### C. Section-level patching

Expose an API to update individual sections in-place without touching the file system. Useful for settings where the application already knows the new value and just needs the view to reflect it.

Something like `view.patch_section(source_path="plugins/user/settings.ft", tag="#settings category=#colors #user", content={...})`.

Most surgical, but also the most complex API surface.

## Notes

- The React-based parser rewrite (if it happens) may make this less urgent — a faster parser reduces the cost of full reloads
- A config flag to toggle between full and incremental reload could help catch correctness issues during development
- The file watcher in the consuming app already tracks mtimes, so approach A would partly duplicate that logic — worth considering whether the watcher should live in FlexTag itself
