# Note Apps Comparison

A practical comparison of popular note-taking and knowledge management applications. This is not exhaustive — it focuses on what each app does well and where it falls short, based on real usage.

---

## Notion

**Best for**: Teams, project management, databases, all-in-one workspace.

### Good
- **Databases are powerful**: Relational databases with custom properties, views (table, board, calendar, gallery, timeline), filters, sorts, and rollups. Nothing else does this at the same level of polish.
- **Blocks are flexible**: Text, images, embeds, code, to-do lists, toggle lists, callouts, dividers, equations, mention any page or database inline. The block model makes pages composable.
- **Templates**: Massive template ecosystem. You can duplicate almost any setup from the community in seconds.
- **Collaboration**: Real-time multiplayer editing, comments, inline discussions, permission management. Works well for small to medium teams.
- **All-in-one**: Notes, project management, wikis, documentation, databases — in one tool. No context switching.
- **API access**: Public REST API with OAuth. This means it supports MCP servers, third-party tools, automation.
- **Publications**: Notion Sites lets you publish pages as websites.

### Bad
- **Offline support is poor**: The mobile app caches recently viewed pages, but you cannot work fully offline. This is the #1 complaint.
- **Search is mediocre**: Full-text search works but isn't fast. No regex, no advanced query syntax, no semantic search natively.
- **Export is limited**: Export to Markdown or PDF, but formatting is often lossy. No bulk export at scale.
- **Speed**: Can feel sluggish with large pages or databases with thousands of entries. The web app is heavier than local-first tools.
- **Vendor lock-in**: Your data lives on Notion's servers. There is no local file format. Migrating out is painful.
- **Not a PKM tool out of the box**: There is no native backlinking, graph view, or Zettelkasten workflow — these must be built manually.
- **Mobile app**: Functional but not great for quick capture. Search and navigation are slow.

---

## Obsidian

**Best for**: Personal knowledge management, power users, local-first workflows.

### Good
- **Local-first**: Everything is plain markdown files on your filesystem. No vendor lock-in — your notes are just text.
- **Graph view**: Interactive visualization of note connections. Useful for discovering relationships between ideas.
- **Backlinks natively**: Every note shows what links to it. Core to the Obsidian experience.
- **Plugin ecosystem**: Thousands of community plugins for everything from Kanban boards to Excalidraw drawings to spaced repetition.
- **Fast and lightweight**: Instant search, instant startup, works on large vaults (10,000+ files) without slowdown.
- **Offline-first**: Works fully offline. Sync is an optional paid add-on.
- **Customizable**: CSS snippets, themes, plugin API. You can make Obsidian look and behave exactly how you want.

### Bad
- **No built-in sync**: Sync across devices requires Obsidian Sync (paid) or a third-party solution (iCloud, Git, Syncthing) that comes with its own complexity.
- **No real-time collaboration**: Single-user first. You can collaborate via Git but there is no Google-Docs-style live editing.
- **No database model**: No spreadsheets, no views, no formulas. There are plugins (Dataview, DB Folder) that add queryable metadata, but it is not native or as polished as Notion's databases.
- **No mobile publishing**: Obsidian Publish exists (paid) but is separate from the app. The mobile app is good for editing but not for sharing.
- **Onboarding is steep**: The tool is simple to start but the ecosystem of plugins, workflows, and best practices takes time to learn.
- **Plugin quality varies**: Community plugins can break on updates, become unmaintained, or conflict with each other.
- **No native web clipper**: Third-party solutions exist but nothing built-in as polished as Notion's or Roam's.

---

## Roam Research

**Best for**: Daily journaling, bidirectional linking, outliner workflow.

### Good
- **Outliner-first**: Everything is a bullet that can be zoomed in/out, indented, reordered, and referenced. This is natural for thinking in hierarchies.
- **Daily notes are core**: Every day gets a page by default. This creates a journal that builds over time, and you organically link ideas across days.
- **Bidirectional links**: Every reference is tracked and shown inline. The linked references view is the best in class.
- **Block references**: You can reference any block from anywhere and see where it's used. This enables atomic note-taking at the block level.
- **Built for long-form thinking**: The UI is designed for slow, deliberate writing and connecting ideas over time.

### Bad
- **Cost**: $15/month individual, $25/month team. Expensive compared to Notion (free for personal) or Obsidian (free).
- **Vendor lock-in**: Proprietary format, no clean export. Your data is not portable.
- **Slow development**: Feature velocity is slow. Basic requests (tables, API, offline) took years or are still missing.
- **Notion-style databases**: No kanban, calendar, gallery views. It is a textual outliner, not a database tool.
- **No mobile app quality**: The mobile experience is poor compared to Notion or Obsidian.
- **Community decline**: Once the hot new thing, Roam has lost momentum to Obsidian and others as people migrated to open alternatives.

---

## Others

### Logseq
- Open-source, local-first outliner with a block-based model similar to Roam.
- **Good**: Free, local-first, great for journalling and task management, has a graph view, backlinks, block references.
- **Bad**: Markdown files but with a custom namespace convention; importing/exporting to standard markdown is messy. UI is less polished than Obsidian.

### Bear
- Beautiful, minimal markdown editor for macOS/iOS only.
- **Good**: Fast, beautiful typography, tags instead of folders, great writing experience.
- **Bad**: Apple-only, no databases, no collaboration, no web version.

### Apple Notes
- Built into every Apple device, free, syncs via iCloud.
- **Good**: Zero setup, quick capture, shared folders, scan documents, pencil support.
- **Bad**: No markdown, no backlinks, no API, no export, no graph view, limited organization.

### OneNote
- Free, feature-rich, part of Microsoft Office ecosystem.
- **Good**: Freeform canvas (click anywhere), excellent ink support, section/group hierarchy, tags, web clipper.
- **Bad**: Heavy, slow sync, no markdown, no backlinks, proprietary format, no API that matters.

### Joplin
- Open-source, local-first markdown editor with encryption and sync.
- **Good**: Free, open-source, E2E encryption, markdown, web clipper, works offline, syncs via Nextcloud/Dropbox/OneDrive.
- **Bad**: UI is functional but dated, no graph view, no real-time collaboration, plugin ecosystem is small.

---

## Quick Decision Guide

| You need... | Choose |
|-------------|--------|
| An all-in-one workspace for a small team | Notion |
| Offline-first personal knowledge base | Obsidian |
| Bi-directional linking and daily journaling | Obsidian or Roam (if you like outlines) |
| Databases with views and filters | Notion |
| Complete data ownership | Obsidian or Joplin |
| Something free that just works | Apple Notes (Apple) or OneNote (Windows) |
| Open-source, local-first, encrypted | Joplin |
| Beautiful writing experience | Bear (Mac only) or Obsidian with a nice theme |

## Bottom Line

There is no best app — only the best app for how you think and work. Notion is the most versatile single tool for most people (especially teams), but Obsidian wins for anyone who values local files, speed, and long-term data portability. Use the right tool for the job, and do not be afraid to use more than one.
