# Simulation patterns

How to choose and build the simulation for a Feynman Lab page.

## Contents
1. Choosing the simulation
2. Rules for every simulation
3. The FV helpers in the template
4. Patterns
   - A. Many particles or agents
   - B. Sliders driving a live graph
   - C. Motion and forces
   - D. Waves and light
   - E. Step-through process
   - F. Algorithm visualizer
   - G. Chance and statistics
   - H. Explorable diagram
   - I. Timeline scrubber
   - J. Cause-and-effect explorer
   - K. Scale explorer
5. Pointer input, SVG stages, and multiple simulations

---

## 1. Choosing the simulation

Ask: **what is the one thing the reader needs to see move to get it?** It is almost always the mechanism behind the hardest gap from Step 2. Build that, and only that. One simulation that nails the core mechanism beats three that decorate.

| The idea is about… | Pattern | Examples |
|---|---|---|
| Many small things whose crowd behaviour is the point | A. Particles / agents | gas pressure, diffusion, epidemics, natural selection, traffic jams, market crowds |
| How one quantity depends on others | B. Sliders → live graph | compound interest, supply and demand, Ohm’s law, lens focus, inflation eating savings |
| Things moving under forces | C. Motion | pendulum, orbits, projectiles, springs, tides, why satellites don’t fall |
| Oscillation, interference, colour | D. Waves and light | sound, why the sky is blue, rainbows, noise-cancelling, Wi-Fi |
| A fixed sequence of stages | E. Step-through | digestion, photosynthesis, how a bill becomes law, DNS lookup, how a vaccine trains immunity |
| A procedure that transforms data | F. Algorithm | sorting, search, pathfinding, hashing/blockchain, how a neural network learns, compression |
| Randomness and averages | G. Chance | Monty Hall, law of large numbers, polling margins, why casinos win, genetics crosses |
| A thing made of parts | H. Explorable diagram | the eye, a cell, a car engine, a computer, the heart |
| Change across years or ages | I. Timeline | an empire’s rise, evolution of life, history of the internet, a star’s life cycle |
| Choices with knock-on effects | J. Cause and effect | opportunity cost, why prices rise, climate feedbacks, a historical “what if” |
| Sizes or times beyond intuition | K. Scale | atoms to galaxies, deep time, how big a billion is |

Topics often combine two (a process with a chance element). Pick the one that fills the hardest gap; mention the other in Step 3 text.

## 2. Rules for every simulation

- **Correct before pretty.** The behaviour must be qualitatively right, and numbers shown must be real (or clearly labelled as illustrative). A wrong simulation teaches a wrong idea that’s hard to undo.
- **Start interesting.** On load it should already be doing the thing, not waiting at a blank state. If reduced motion is on, it starts paused, so draw a meaningful first frame.
- **Few controls, plain names.** 1–3 sliders named in everyday words (“How thick the air is”, not “optical depth τ”). Show units in the output. At the Deep level you may relabel with the technical term via `FV.onLevel`.
- **“Try this” experiments.** 2–3 concrete things to do, each with a prediction to test: “Before you drag it, guess: will the sunset get redder or bluer?”
- **Say what it simplifies.** Fill the “What this simulation simplifies” box honestly. That honesty is the Feynman spirit.
- **Theme-aware.** Read colours with `FV.color("--accent")` etc., never hard-code hex for ink or background; redraw on `FV.onTheme`. Physical colours (a red apple, a wavelength’s hue) can be literal.
- **Resize-proof.** Keep model coordinates in units (0–1, metres, years) and convert to pixels inside `draw()` using `view.w` / `view.h`.
- **Phone-friendly.** Thumb-sized hit areas (≥ 40px), no hover-only information, nothing wider than the stage. Test the stage at 390px wide.
- **Light on the CPU.** Under ~400 moving objects; avoid O(n²) loops over all pairs (use a grid or keep n small). The loop already pauses off-screen.
- **Vanilla first.** Canvas 2D or inline SVG is enough for nearly everything. Only reach for a library if it saves real complexity, loaded as a pinned UMD build from cdnjs or jsDelivr.
- **Accessibility.** Give the canvas a meaningful `aria-label`. Don’t put `aria-live` on numbers that change every frame; use the `.sim-narration` paragraph (aria-live) only for discrete step changes.

## 3. The FV helpers in the template

The template’s core script defines `window.FV`:

| Helper | What it does |
|---|---|
| `FV.setupCanvas(canvas, onResize)` | Returns `view = { ctx, w, h }` in CSS pixels, sharp on high-DPI screens. `onResize` runs on later size changes. |
| `FV.loop(watchEl, step, { button, autoplay })` | Calls `step(dt)` every frame (dt in seconds, capped at 0.05). Pauses off-screen and in background tabs; starts paused under reduced motion; wires a Play/Pause button. Returns `{ play, pause, toggle, running, stepOnce }`. |
| `FV.slider(id, format, onChange)` | Binds `<input id>` and `<output id="<id>-out">`. Calls `onChange` immediately and on input. Returns `{ value, set(v) }`. |
| `FV.color(name)` | Current value of a CSS colour token. |
| `FV.onTheme(fn)`, `FV.onLevel(fn)`, `FV.level()` | React to theme or level changes. |
| `FV.reduceMotion` | True if the reader prefers reduced motion. |

**Order matters** in the simulation script, because `FV.slider` calls `onChange` (which usually calls `draw`) immediately: declare colours → params → state → `view` → sliders → loop. The template skeleton is already in this order.

---

## 4. Patterns

Each skeleton replaces the `params / init / update / draw` parts of the template’s simulation script.

### A. Many particles or agents

Crowd behaviour emerging from simple rules. Show a live count or a small chart of the crowd statistic (pressure, infected, average trait) so the reader links the micro to the macro.

```js
const params = { count: 120, speed: 1 };
const init = () => ({
  t: 0,
  parts: Array.from({ length: params.count }, () => ({
    x: Math.random(), y: Math.random(),
    vx: (Math.random() - 0.5) * 0.4, vy: (Math.random() - 0.5) * 0.4, kind: 0
  })),
  history: []                       // e.g. a statistic sampled ~10×/s for a sparkline
});
function update(dt) {
  const s = dt * params.speed;
  for (const p of state.parts) {
    p.x += p.vx * s; p.y += p.vy * s;
    if (p.x < 0 || p.x > 1) { p.vx *= -1; p.x = Math.min(1, Math.max(0, p.x)); }
    if (p.y < 0 || p.y > 1) { p.vy *= -1; p.y = Math.min(1, Math.max(0, p.y)); }
  }
  state.t += dt;
}
function draw() {
  const { ctx, w, h } = view;
  ctx.clearRect(0, 0, w, h);
  const r = Math.max(2, Math.min(w, h) * 0.008);
  for (const p of state.parts) {
    ctx.fillStyle = p.kind ? C.red : C.accent;
    ctx.beginPath(); ctx.arc(p.x * w, p.y * h, r, 0, Math.PI * 2); ctx.fill();
  }
}
```
For neighbour interactions (infection, collisions), bucket particles into a grid of cells of the interaction radius and only compare within neighbouring cells. When a slider changes `count`, rebuild with `state = init()`.

### B. Sliders driving a live graph

The reader moves inputs and watches a curve respond. Always include a **comparison ghost** (simple vs compound interest, before vs after) so the difference is the thing they see. Show the key number at the end of the curve.

```js
const params = { rate: 0.08, years: 30, start: 1000 };
const series = () => {
  const comp = [], simp = [];
  for (let y = 0; y <= params.years; y++) {
    comp.push(params.start * Math.pow(1 + params.rate, y));
    simp.push(params.start * (1 + params.rate * y));
  }
  return { comp, simp };
};
function draw() {
  const { ctx, w, h } = view, pad = { l: 56, r: 16, t: 16, b: 36 };
  const { comp, simp } = series();
  const maxY = Math.max(...comp) * 1.05;
  const X = i => pad.l + (i / params.years) * (w - pad.l - pad.r);
  const Y = v => h - pad.b - (v / maxY) * (h - pad.t - pad.b);
  ctx.clearRect(0, 0, w, h);
  ctx.strokeStyle = C.rule; ctx.lineWidth = 1;          // axes
  ctx.beginPath(); ctx.moveTo(pad.l, pad.t); ctx.lineTo(pad.l, h - pad.b); ctx.lineTo(w - pad.r, h - pad.b); ctx.stroke();
  const line = (arr, col, dash) => {
    ctx.setLineDash(dash); ctx.strokeStyle = col; ctx.lineWidth = 2.5; ctx.beginPath();
    arr.forEach((v, i) => (i ? ctx.lineTo(X(i), Y(v)) : ctx.moveTo(X(i), Y(v)))); ctx.stroke(); ctx.setLineDash([]);
  };
  line(simp, C.soft, [6, 6]);
  line(comp, C.accent, []);
  ctx.fillStyle = C.ink; ctx.font = "600 13px system-ui"; ctx.textAlign = "left"; ctx.textBaseline = "alphabetic";
  // axis labels and end-of-curve values here
}
```
Usually no animation is needed: call `draw()` from each slider and skip `FV.loop` (delete the Play/Reset buttons too). If you animate (e.g. years ticking by), keep Play/Reset.

### C. Motion and forces

Use a fixed small timestep so the physics stays stable at any frame rate, and semi-implicit Euler (update velocity, then position).

```js
const params = { g: 9.81, length: 1.5 };
const init = () => ({ theta: 0.9, omega: 0, trail: [] });
let acc = 0; const H = 1 / 240;
function physicsStep(h) {
  const a = -(params.g / params.length) * Math.sin(state.theta);
  state.omega += a * h;
  state.theta += state.omega * h;
}
function update(dt) {
  acc += dt;
  while (acc >= H) { physicsStep(H); acc -= H; }
  // push a trail point every few frames; cap trail length (~120)
}
```
Draw force or velocity arrows when the forces are the lesson. Let the reader drag the object to set its start (see section 5). For orbits use real ratios but a scaled time (“1 second here = 10 days”) and say so in a readout.

### D. Waves and light

`y = A·sin(k·x − ω·t)`; superpose by summing. For colour by wavelength use:

```js
function wavelengthToRGB(nm) {              // approximate visible spectrum, 380–750 nm
  let r = 0, g = 0, b = 0;
  if (nm < 440) { r = (440 - nm) / 60; b = 1; }
  else if (nm < 490) { g = (nm - 440) / 50; b = 1; }
  else if (nm < 510) { g = 1; b = (510 - nm) / 20; }
  else if (nm < 580) { r = (nm - 510) / 70; g = 1; }
  else if (nm < 645) { r = 1; g = (645 - nm) / 65; }
  else { r = 1; }
  const f = nm < 420 ? 0.3 + 0.7 * (nm - 380) / 40 : nm > 700 ? 0.3 + 0.7 * (750 - nm) / 50 : 1;
  const c = v => Math.round(255 * Math.pow(Math.max(0, v) * f, 0.8));
  return `rgb(${c(r)}, ${c(g)}, ${c(b)})`;
}
```
For scattering (sky colour): fire “photons” of mixed wavelengths across the stage; each step a photon scatters with probability ∝ 1/λ⁴ × density × dt. Show what reaches an observer from overhead versus along a long low path (sunset) as two colour swatches.

### E. Step-through process

Use an inline SVG diagram instead of a canvas (replace the `<canvas>` with `<svg viewBox="0 0 800 500">`), give each part an `id`, and walk through steps. Add a `<p class="sim-narration" aria-live="polite"></p>` below the stage.

```js
const steps = [
  { title: "Food enters the mouth", parts: ["mouth"], text: { simple: "…", student: "…", deep: "…" } },
  // …
];
let i = 0, t = 0;
const narration = document.querySelector(".sim-narration");
function show() {
  document.querySelectorAll("#sim-svg .part").forEach(el => el.classList.toggle("on", steps[i].parts.includes(el.id)));
  const s = steps[i];
  narration.textContent = `${i + 1}/${steps.length}. ${s.title}: ${s.text[FV.level()] || s.text.simple}`;
}
function update(dt) { t += dt; if (t > 3.5) { t = 0; i = (i + 1) % steps.length; show(); } }
FV.onLevel(show);
```
Add Back / Next buttons (`.btn-quiet`) next to Play, and style `.part.on` with the accent colour in a `<style>` block. Moving tokens (a food particle, a data packet) along the active path make it feel alive.

### F. Algorithm visualizer

Write the algorithm as a generator that yields snapshots; the loop advances one snapshot every `1 / speed` seconds; a Step button calls it once.

```js
function* bubbleSort(a) {
  for (let end = a.length - 1; end > 0; end--)
    for (let j = 0; j < end; j++) {
      yield { a: [...a], look: [j, j + 1] };
      if (a[j] > a[j + 1]) { [a[j], a[j + 1]] = [a[j + 1], a[j]]; yield { a: [...a], swap: [j, j + 1] }; }
    }
  yield { a: [...a], done: true };
}
const init = () => { const it = bubbleSort(shuffled(24)); return { it, snap: it.next().value, acc: 0, comparisons: 0 }; };
function update(dt) {
  state.acc += dt * params.speed;
  while (state.acc >= 1 && !state.snap.done) { state.acc -= 1; state.snap = state.it.next().value; }
}
```
Count operations in a readout so the reader sees cost grow. For “how a neural network learns”: a tiny network (2 inputs → 6 hidden → 1 output) trained by gradient descent on 2D points, drawing the decision boundary on a coarse grid (about 50×30 cells) every few steps, with a loss sparkline and a learning-rate slider.

### G. Chance and statistics

Run trials in batches per frame and build a histogram; overlay the theoretical expectation as a dashed line so the reader watches randomness settle onto it. Offer “Run 1”, “Run 100” and “Run 10,000” buttons; show the running proportion. Use a seedable generator if you want Reset to replay the same luck:

```js
function mulberry32(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
```

### H. Explorable diagram

An inline SVG where each part is focusable and clickable; selecting one shows its name and job (level-aware) in a panel under the stage. Add a “What if it fails?” toggle that shows the consequence: that’s what turns a labelled picture into understanding.

```html
<g class="part" id="lens" tabindex="0" role="button" aria-label="Lens">…shapes…</g>
```
```js
document.querySelectorAll("#sim-svg .part").forEach(el => {
  const pick = () => select(el.id);
  el.addEventListener("click", pick);
  el.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); } });
});
```
No animation loop is needed unless parts move (a beating heart, a piston); delete Play/Reset if unused.

### I. Timeline scrubber

A range input over the years drives the picture (a map’s shading, a population bar, a tree of species), with the events list underneath highlighting the nearest event. Play advances the year. Use a log or piecewise scale when time spans are lopsided (deep time). Never fabricate dates: if unsure, search, or show a range.

### J. Cause-and-effect explorer

Levers (sliders and toggles) feed a small, transparent model; the outcome shows as bars or a short chain of arrows that light up (“more money printed → more spending → prices rise”). State the model’s rules plainly in “What this simulation simplifies”. For contested economic or political questions, present it as one simplified model, name its assumptions, and don’t declare which policy is right.

### K. Scale explorer

A log-scale slider (`value = 10 ** slider`) zooms through sizes or times; known objects fade in at their scale with labels (“a grain of sand, 0.5 mm”). Show the current scale as a ruler bar with a readable unit. Values must be real; give approximate figures with “about”.

---

## 5. Pointer input, SVG stages, and multiple simulations

**Dragging on a canvas** (setting a start position, drawing a barrier):

```js
canvas.style.touchAction = "none";          // only on canvases you drag, so the page still scrolls elsewhere
const toUnit = e => { const r = canvas.getBoundingClientRect(); return { x: (e.clientX - r.left) / r.width, y: (e.clientY - r.top) / r.height }; };
let dragging = false;
canvas.addEventListener("pointerdown", e => { dragging = true; canvas.setPointerCapture(e.pointerId); onDrag(toUnit(e)); });
canvas.addEventListener("pointermove", e => { if (dragging) onDrag(toUnit(e)); });
canvas.addEventListener("pointerup", () => { dragging = false; });
```
Tell the reader the canvas is draggable in the sim title or a “Try this” item.

**SVG stages:** replace the canvas with `<svg id="sim-svg" viewBox="…" role="img" aria-label="…">`, skip `FV.setupCanvas`, and update attributes in `draw()`. Use `style="fill: var(--accent)"` so colours follow the theme without redrawing.

**A second simulation** (only when a different gap genuinely needs one): duplicate the `<figure class="sim">` with new ids (`sim2-canvas`, `sim2-play`, …) and give it its own script block. Keep the page to two at most.
