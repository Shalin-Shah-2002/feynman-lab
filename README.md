# Feynman Lab

A Claude skill that turns any topic into an interactive learning page built on the Feynman technique.

Ask Claude something like “help me understand compound interest” or “why is the sky blue?” and it builds one self-contained HTML page that:

- **Shows all four Feynman steps as a learning journal:** explain it simply, find the gaps, fill the gaps, explain it better.
- **Has a Simple / Student / Deep switch** so the same page works for a curious kid, a student or an adult who wants the precise version.
- **Puts the hardest idea into a live simulation** (sliders, particles, step-throughs, timelines) with “Try this” experiments and an honest note on what the model simplifies.
- **Ends with a quiz and a “now you teach it” box,** because you only really understand something once you can explain it yourself.

## Install

**Claude.ai:** zip this folder (named `feynman-lab`) and upload the zip in Claude’s settings, in the Skills section.

**Claude Code:** copy this folder to `~/.claude/skills/feynman-lab/`.

## Use

Just ask to learn something:

- “Explain how vaccines train the immune system.”
- “Teach me how a neural network learns, I’m a CS student.”
- “/feynman-lab the printing press”

## What’s inside

```
feynman-lab/
├── SKILL.md                          workflow Claude follows
├── assets/template.html              page skeleton: journal layout, themes, level switch, quiz, helpers
├── references/simulation-patterns.md how to pick and build the simulation (11 patterns with code)
└── scripts/check_page.py             catches placeholders, broken data and JS errors before publishing
```

## Credits

Built on the [Feynman technique](https://en.wikipedia.org/wiki/Learning_by_teaching#Feynman_technique). Pairs well with the text-only [`feynman`](https://github.com/neurofoo/agent-skills) skill by neurofoo.
