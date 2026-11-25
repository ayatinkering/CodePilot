# Factual starting point — 2026-11-25

CodePilot is newly in development. The initial repository contained only a README
(commit 449132d). Codex is implementing under Ayati's direction; Ayati selected
Gemini. No independently completed learner exercise is recorded.

Current scope: local Python 3.12 backend, partial snapshot/worker lifecycle, Tree-sitter structural extraction and a Gemini planning adapter. Provider: Gemini selected,
model/key/live calls not verified. Semantic model: not selected or downloaded.
No code-repair tasks attempted, no resolution rate, no product-generated PR.
No fine-tuning, reinforcement learning, GitHub App deployment, or hosted UI.

30-second current pitch: “I am building CodePilot, an inspectable AI-assisted
Python maintenance prototype. The current increments establish validated settings,
SQLite persistence, a local API, snapshots and structural extraction. The planned pipeline separates model proposals
from independent tests and human-approved PRs. I am using AI assistance and learning
the implementation; I do not yet claim the complete repair pipeline works.”

Known limitations and further milestones are in ../evidence/capabilities.md.
