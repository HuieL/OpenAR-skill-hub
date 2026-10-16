---
name: craft-suite
description: Use OpenRA Craft Suite to edit project assets with its installed components, request a supported agent proposal, and return editable source with previews to the same project.
---

# Craft Suite

Use the project's existing Craft Suite entry. Choose the component for the
asset and keep the current project, original, editable source and preview
revisions together. Component selection is a preference; it does not install
an engine or authorize execution. Read [roundtrip.md](references/roundtrip.md)
when preparing an edit, recovering an interrupted save, or reading a returned
source.

Inspect the installed component's actual version, supported operation and
current availability before offering an edit. Use its existing controls and
admitted actions. The session's live extension-action listing is authoritative
for agent invocation; a static schema or this skill is not an action grant.
Craft Suite1.3 editing actions currently use the human channel. Its request
controls create genuine model Tasks through the host; this does not make the
same actions directly callable by an agent. If the required control is human
only, explain the concrete next UI action and continue other authorized work.
Never change actor, lifecycle, approval records or request channel to bypass
a refusal.

Keep the editable source as the input for further edits and questions. A PNG,
PDF, video or audio preview can remain at an earlier revision after a
source-only return. Identify it as such. Request a fresh read of the current
source through the supported reader and check the returned ContextRef and
revision before reporting what the agent observed.

Report the resulting original/source/preview identities and the operation
actually observed. Distinguish saved bytes, successful native reopening,
browser rendering and native human editing. Engine launch, exit0 or an older
preview alone does not establish that an edited result returned to the
project. Linux execution does not establish Mac native behavior.
