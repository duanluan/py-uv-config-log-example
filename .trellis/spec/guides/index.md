# Thinking Guides

> **Purpose**: Expand your thinking to catch things you might not have considered.

---

## Why Thinking Guides?

Use guides as checklists only. Put implementation contracts in `../backend/`.

---

## Available Guides

| Guide | Purpose | When to Use |
|-------|---------|-------------|
| [Code Reuse Thinking Guide](./code-reuse-thinking-guide.md) | Search for existing behavior before adding code | Changing constants, helpers, config |
| [Cross-Layer Thinking Guide](./cross-layer-thinking-guide.md) | Check runtime boundary contracts | Changing config, context, logging, resources |

---

## Quick Reference: Thinking Triggers

### When to Think About Cross-Layer Issues

- [ ] Config path or config key changes
- [ ] Context init, clear, or proxy changes
- [ ] Logger, archival, scheduler, or retention changes
- [ ] Packaged resource or wheel changes

### When to Think About Code Reuse

- [ ] Changing constants, config keys, filenames, or helper names
- [ ] Adding new helpers near existing runtime utilities
- [ ] Updating repeated tests or patterns

---

## Pre-Modification Rule (CRITICAL)

```bash
rg "value_or_name_you_are_changing"
```

---

## How to Use This Directory

1. Skim the matching guide.
2. Search before editing.
3. Update backend specs when runtime contracts change.

---

## Contributing

Keep guide additions as short triggers. Put detailed rules in backend specs.
