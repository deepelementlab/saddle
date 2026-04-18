---
description: Validate the default Saddle mode via CLI
---

From the **project root** (where `.saddle/modes` lives), run:

```bash
python -m saddle mode validate default
```

If the user uses another mode name, replace `default` accordingly.

If `python -m saddle` is not found, ask them to install Saddle (`pip install -e /path/to/saddle`) and use the same interpreter as `saddle serve`.

Report exit code: 0 means the mode YAML is valid.
