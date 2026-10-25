---
name: feynman-lab
description: Turn any topic into an interactive visual learning page built on the Feynman technique. Produces one self-contained HTML page, published as an artifact, that shows all four Feynman steps as a learning journal (explain it simply, find the gaps, fill them, explain it better), with a live simulation of the core mechanism, a Simple/Student/Deep level switch, glossary pop-ups, a quiz and an explain-it-back box. Use this whenever someone wants to understand or learn a concept, even if they don't ask for visuals or a page — "explain X", "help me understand X", "teach me X", "how does X work", "why does X happen", "I don't get X", "ELI5 X", "make a visual explainer / interactive lesson / study page on X", or /feynman together with visuals. Works for any subject (physics, biology, chemistry, maths, money, economics, history, computing). Skip only for one-line factual lookups (a date, a quick definition) or when the user asks for a plain text answer.
---

# Feynman Lab

Build one self-contained HTML page that teaches a topic the way Richard Feynman learned: explain it simply, notice where the explanation goes fuzzy, fill those gaps, then explain it again, better. The page shows all four steps as a learning journal, lets the reader switch between three levels of depth, and turns the hardest idea into a live simulation they can play with.

Why this shape: a reader learns more from watching an explanation get *repaired* than from a polished answer alone, and they really understand a mechanism once they’ve seen it move and poked at it themselves. Aim for the moment where the reader thinks “oh, *that’s* why”.

## Files in this skill

- `assets/template.html` is the page skeleton: journal layout, light and dark themes, the level switch, glossary pop-ups, quiz, explain-it-back box, and small simulation helpers (`window.FV`). Always start from it; don’t rewrite these parts.
- `references/simulation-patterns.md` explains how to choose and build the simulation, with code skeletons for eleven kinds of ideas. Read it before writing the simulation.
- `scripts/check_page.py` catches leftover placeholders, broken JSON, missing glossary entries, blocked external files and JavaScript syntax errors. Run it before delivering.

## Workflow

### 1. Pin down the topic

Turn the request into one concrete question the page answers: “Why is the sky blue?” works better than “Light scattering”. That question becomes the page title.

- **Huge topics** (quantum physics, the economy, World War II): pick the single core idea a newcomer most needs, build the page on that, and in your reply say which slice you chose and suggest 2–3 follow-up pages.
- **Ambiguous terms:** go with the most common meaning and mention the other in your reply.
- **Don’t stop to ask** unless the topic truly can’t be guessed; a good page plus “want a page on X next?” is more useful than a question.
- **Level hints:** if the user signals their level (“for my 10-year-old”, “I’m a med student”), set `data-default-level` to match. Otherwise default to `simple`.
- **Language:** write the page in the language of the user’s message and set `<html lang>`. For scripts Atkinson Hyperlegible doesn’t cover (Gujarati, Devanagari, Bengali, Tamil, Arabic, Chinese, Japanese, Korean and so on), add the matching Noto Sans family to the Google Fonts link and put it first in `--font-body`.

### 2. Get the facts right

Stable knowledge (physics, chemistry, maths, core biology, well-established history) can come from what you know. Search the web first when the topic involves numbers that change (rates, prices, populations, records), recent events or technology, or anything you’re unsure about. The Deep level must be accurate enough that an expert would nod along: simplify, never falsify. Where something is genuinely unknown or debated, say so on the page. That’s an honest gap, which is exactly what the Feynman method values.

### 3. Draft the Feynman content before any HTML

Write the content first (in your head or a scratch file), because the page structure depends on what the gaps turn out to be.

1. **Step 1, explain it simply,** at all three levels, plus one everyday analogy you’ll draw as an SVG.
2. **Step 2, find the gaps.** 3–5 gaps. A gap is a sentence from the Simple explanation that sounds fine but skips the *why* or *how*: the question a curious reader would ask next. Quote the actual sentence, then write the honest question underneath (“But why does blue bounce around more than red?”). Avoid fake-humble filler; every gap must be one Step 3 really answers. Also list 4–8 jargon words used anywhere on the page, each rated honestly: did Step 1 explain it simply? Yes, Partly or No.
3. **Step 3, fill the gaps.** For each: the question, the answer (with level variants only where they really differ), and “Now I can say it as:” in one plain sentence. The hardest gap, usually the one about the core mechanism, gets the simulation.
4. **Step 4, explain it better,** at all three levels. It must actually use what Step 3 filled in; if it reads like Step 1 reworded, the gaps weren’t real. Add an improved analogy that says where the first analogy broke down, and 3–5 key takeaways.
5. **The 30-second version** at all three levels, for the top of the page.
6. **Test yourself.** 4–6 quiz questions that test understanding rather than recall; prediction questions work best (“If Earth had no atmosphere, the daytime sky would look…”). Make the wrong options the real misconceptions, and give each question a short “why”. Most questions use level `all`; one or two can be level-specific. Then write 3–5 key points that a good explain-it-back answer must cover.

### 4. Pick the simulation

Read `references/simulation-patterns.md`. Ask: what is the one thing the reader needs to see *move* to get it? Build that. Nearly every topic has something to simulate or explore. When there’s no physical mechanism (a historical turning point, a poem’s structure, an ethical dilemma), use the closest interactive pattern (timeline scrubber, cause-and-effect explorer, explorable diagram) rather than forcing physics onto it.

### 5. Build the page

1. Copy `assets/template.html` to `/mnt/user-data/outputs/<topic-slug>.html`.
2. Replace every `{{PLACEHOLDER}}` and fill every `FILL` comment, then delete the `FILL` comments. Repeat the gap, jargon-row, fill and key-point blocks as needed.
3. Fill all three level variants wherever the template has them. Use `class="lvl" data-level="student deep"` when two levels share text.
4. Wrap jargon in the text (first use in each section) as `<button type="button" class="term" data-term="key" aria-controls="term-pop" aria-expanded="false">word</button>`, and give each key a glossary entry (a string, or `{simple, student, deep}`).
5. Write the simulation in the second script block, following the pattern you chose. Delete controls you don’t use (for example Play and Reset for a static graph).
6. You may retune `--accent` (light and dark values) to suit the subject, keeping at least 4.5:1 contrast against `--paper-raised`. Leave the rest of the journal frame alone: a consistent look across pages helps readers build a habit.

Writing conventions:
- Use typographic apostrophes and quotes (’ “ ”) in visible text, and straight quotes in code and JSON.
- Use sentence case for headings.
- Write every level in plain words, with no unexplained term at the Simple level.
- Aim for these lengths per explanation: Simple 100–180 words (short sentences, everyday words), Student 150–250 (proper terms, each defined), Deep 250–400 (precise terms, numbers or equations where they genuinely help, and the limits of the model).

Constraints of a published page (the template already follows them):
- Everything goes in one file, with inline CSS and JS.
- External scripts may come only from cdnjs.cloudflare.com or cdn.jsdelivr.net/npm, pinned to an exact version at least two weeks old.
- No remote images and no network requests. Draw pictures as inline SVG or embed them as data URIs.
- Use localStorage only through try/catch, as the template does.
- The file must stay under 16 MB.

### 6. Check it

Run `python3 scripts/check_page.py <page.html>` and fix every error. Then reread the page against this list:

- Could a bright 12-year-old follow the Simple level with no help?
- Is every gap a real question, quoting a real sentence from Step 1?
- Does Step 4 visibly use what Step 3 found?
- Does the simulation show the mechanism, start out doing something interesting, label its units, and offer 2–3 “Try this” experiments with predictions?
- Is everything at the Deep level correct?
- On a phone, does nothing scroll sideways and are the controls easy to tap?

If a headless browser is available (Playwright), screenshot the page at 390px and 1280px wide in both light and dark mode, check the console for errors, and look at the screenshots before delivering.

### 7. Deliver

Publish with the Artifact tool (`action: "publish"`, `file_path` set to the page, `title` set to the question, and a single fitting emoji as `favicon`). If the Artifact tool isn’t available, call `present_files` on the HTML file instead.

Then reply in chat in 2–4 sentences:
- which slice of the topic the page covers, if you narrowed it,
- what the simulation lets them try,
- 2–3 follow-up topics they could ask for next.

Don’t repeat the page’s content in chat.

For changes, update the same artifact rather than making a new one. Use `action: "edit"` with the artifact’s url for small fixes, or republish the file with `url` for big rewrites, and keep the same favicon.
