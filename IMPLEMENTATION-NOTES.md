# AMS 4.0 implementation notes

This candidate preserves AMS root authority and adaptive routing while adding modular quality controls.

Key changes:

- one unnumbered master configuration contract; retired `schema_version` is ignored;
- explicit lazy route for every optional capability;
- direct named governance-capability invocation when full governance is off;
- default-on convergence with independent correction/redesign limits;
- pre-trigger campaign finalization, bounded state discovery, owner lease, generation fencing, and immutable history records;
- shared package/runtime lock observed by convergence writers and installers;
- root fallback only after convergence releases a failed/blocked campaign and still subject to independent validation;
- one canonical work-order/result envelope with special-case addenda only;
- app-task and local observation as compatibility-gated companions;
- Sol Ultra as a reduced standalone special directive without standard convergence control;
- repository verification outside the install manifest; no AMS runtime testing subsystem.

Selective exact prompt-edge repetition remains intentionally excluded.
