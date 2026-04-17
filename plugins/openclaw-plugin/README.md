# Saddle OpenClaw Plugin

Context-engine plugin for OpenClaw that provides:

- automatic memory recall before reply (`assemble`)
- automatic memory save after each turn (`afterTurn`)

## Local Install

```bash
cd saddle/plugins/openclaw-plugin
node bin/install.js
openclaw gateway restart
```

Default backend: `http://127.0.0.1:1995`.
