# Saddle Collaboration Modes

Saddle supports low-cognitive-load configuration for collaboration modes:

- File configuration: `.saddle/modes/*.yaml`
- CLI temporary override: `--mode` + `--set key=value`

Default execution pipeline (with no additional configuration):

`spec -> design -> develop`

## Quick Start

```bash
saddle run "Implement an order system with audit logging"

Using the built-in fast mode:

bash
saddle run "Implement an order system with audit logging" --mode fast
Temporary override (without modifying files):

bash
saddle run "Implement an order system with audit logging" \
  --mode default \
  --set design.deep_loop=true \
  --set develop.max_iters=20 \
  --set agent_selection.strategy=balanced
Top 5 Most Commonly Used Configuration Keys
pipeline.order: Stage order, default ['spec','design','develop']

design.deep_loop: Enable deep loop for design phase

design.max_iters: Maximum iterations for design deep loop

develop.deep_loop: Enable deep loop for develop phase

agent_selection.strategy: Agent selection strategy (minimal|balanced|custom)

Mode Templates
default.yaml: Zero-config default, suitable for general tasks

fast.yaml: Fast delivery, fewer iterations + compact prompt

deep.yaml: High-standard collaboration, deep loop enabled by default

Viewing and Diagnostics (saddle mode)
bash
# List available mode names under .saddle/modes/
saddle mode list

# Print merged full configuration (default cwd, default mode)
saddle mode show fast --project /path/to/repo

# Validate configuration; exits with code 1 on error
saddle mode validate default --set pipeline.order=[spec,design,develop]
List-type fields in --set must be written in bracket form, e.g., pipeline.order=[spec,develop].

Visual Configuration Panel (Saddle Studio)
saddle/studio provides a Stripe-style visual configuration panel featuring:

Welcome page (brand introduction, collaboration pipeline explanation)

Basic mode configuration (spec/design/develop, pipeline.order)

Advanced configuration (agent mental models, tool strategies, thresholds)

JSON/YAML live preview

Server-side validation and save (write back to .saddle/modes/*.yaml)

Launch
Development (Vite HMR, default port 4173):

bash
cd saddle/studio
npm install
npm run dev
Production (served by saddle serve after build, same port as API):

bash
cd saddle/studio
npm install
npm run build
cd ..
saddle serve
# Open http://127.0.0.1:1995/ (or your specified host/port)
Custom build output directory: saddle serve --studio-dir /path/to/dist or set the SADDLE_STUDIO_DIR environment variable.

text
