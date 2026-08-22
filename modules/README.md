# ESC-specific modules

`modules/` contains functionality that is genuinely specific to ESC Digital and is not ORP Core by default.

Each implemented module should document:

- purpose and owner;
- public/internal interfaces;
- data owned or consumed;
- dependencies and provider adapters;
- security/privacy classification;
- build/test procedure;
- operational/recovery requirements;
- criteria for possible promotion/generalization into ORP.

A module must not create a mandatory AI dependency for core editorial or customer-facing functionality unless explicitly approved. Provider-specific AI integration belongs behind an adapter/interface and canonical knowledge/data remains outside the AI provider.
