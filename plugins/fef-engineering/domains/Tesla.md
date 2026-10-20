# Tesla Domain Pack

## Focus Areas

- vehicle telemetry and data collection (TeslaMate, Fleet API, CAN)
- charging infrastructure and behavior
- FSD / Autopilot versioning and supervision requirements
- cabin and thermal systems
- software update cadence and regional differences
- operational dashboards and alerting
- EV maintenance and service constraints

## Rules

- Separate observed data (logs, telemetry, official release notes) from inference or user reports.
- Explicitly mark FSD/Autopilot capability, regulatory approval, and unsupervised operation claims as `[unverified]` unless backed by a primary source (Tesla, NHTSA, or equivalent regulator) with date and version.
- Distinguish hardware generation (HW3/HW4, Juniper, etc.) and software version when discussing behavior or features.
- Be careful with safety-critical recommendations (driving, charging, thermal). Prefer official service procedures.
- Note regional differences (Korea DCAS, China certification barriers, US unsupervised testing) when relevant.
- Prefer primary sources for current claims; mark secondary reports and rumors.

## Version-Sensitive Claims

Scope claims involving:

- FSD / Autopilot software version
- vehicle hardware revision
- charging curve or power limits
- cabin climate control behavior
- regional feature availability

State the vehicle model, hardware generation, and software version (or assumption) before recommending operational changes.
