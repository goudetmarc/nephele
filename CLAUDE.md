# Nephélé — project context

A form-matching application: finding figures in matter that carries none (clouds, rust, bark, paint), and reading non-figurative fields by what they *do* rather than by what they show. One HTML page per tool, zero build, zero dependencies, the Anthropic API called directly from the browser.

> Note: the app's interface and doctrine are written in **French** (see Working conventions). This `CLAUDE.md`, the `README.md` and `FONDEMENTS.md` are in English; the tool itself stays French. Code identifiers, doctrine constants (e.g. `AUDACE`, `TROUVER`), board names and move values (`CONFIRME`/`AFFINE`/`REMPLACE`) are literal app tokens — keep them as-is.

## The three files

| File | Role | Rule |
|---|---|---|
| `doctrine.js` | **Everything the model knows.** Base (SOCLE), finding moves, repertoire, sensible regime, affect derivation, the prompts of every pass, the bench lexicons. | This is THE working file. 95% of improvements happen here. |
| `index.html` | The plumbing: boards (canvas image processing), pipeline, second look, notebook, grammar, corpus. | Touch it only for mechanics, never for model behavior. |
| `banc.html` | The measuring instrument: 4 probes, degradation scale, paired test. | The arbiter of any doctrine change. |

A fourth surface, `dixit.html`, hosts the **projective regime** (the three gazes — see v6). Like the others, its doctrine lives in `doctrine.js` (`SOCLE_PROJECTIF`, `P_NAIF`, `P_CHERCHEUR`, `P_CONNAISSEUR`, `P_TISSAGE`, and the bridge `P_REGARD_NU`, `P_NAIF_SUBSTRAT`); the page itself is only plumbing and touches nothing in `index.html`. Still experimental.

## The doctrine ↔ code contract (do not break)

`index.html` normalizes everything it receives: keys recognized regardless of accents/case/synonyms, unknown fields ignored, missing ones defaulted, `72`/`"72%"`/`0.72` equivalent. Prompts can therefore be rewritten and fields renamed freely. Only three welds:

- `AUDACE` keeps its keys `1`–`5` with `.n`, `.d`, `.p`;
- a figure must carry something that looks like a name;
- the second look returns something that looks like a move (confirme/affine/remplace, synonyms accepted).

## Version history — the lessons paid for

- **v1**: a prompt machine. The model recited the corpus (“a dragon in the clouds”) instead of looking. **Lesson: the problem is upstream of the prompt — cut scene recognition by never showing the photo, only binarized boards.**
- **v2**: rigor imported from the sciences → total sterility. The “threshold artifact” attack invalidated 100% of figures by construction; the notebook learned to keep quiet. **Lesson: a pareidolia has no ground truth. The only valid question: “does it hold the contour?” (a criterion of sharing, not of truth). NEVER reject a figure on the grounds that it was produced by the processing.**
- **v3**: separating finding from sorting. Finding moves (drop down in scale first — measured bias: models give 87-90% whole responses on the Rorschach), quota + re-prompt, the adversary becomes a second look that never returns an empty slot. **Lesson: adding a finding move produces figures; adding a judgment criterion removes them.**
- **v4**: the sensible regime (10 dimensions: weight, forces, light, temperature, time, brushwork, eye path, tension, rhythm, economy) + color boards (warm/cool is the most revealing) + the abstraction bench. **Lesson: the empty words of art discourse (“vibrant”, “atmosphere”) are the dragons of the non-figurative — more dangerous because they pass for culture. If the model recognizes the artwork, it must keep quiet.**
- **v5**: the configuration → effect grammar. Affect is never an assertion, always the second half of an assertion whose first half is a configuration. The horoscope test: every relation must have an imaginable refutation. Admission = recurrence over 2 unrelated kinds of matter + human ratification. The state (candidate/admitted/suspended) is computed by the code, never declared by the model.
- **v5.1**: the corpus (phase 0). Each session records itself in IndexedDB in training format: board seen + doctrine actually injected + verdicts. SFT exports (clean boards only) and DPO exports (I-see-it / I-don't-see-it pairs on the same board).
- **v6** (in progress): the **projective regime** — the tool `dixit.html`. Everything inverts. The work is shown whole and in color, recognition is welcome, and the observer's projection is the *product*, not the contaminant. Three gazes (naïf, chercheur, connaisseur) run independently, then a weave that never flattens them; no judgment, no quota, no horoscope — projection is Barnum-like by nature, and here that is the phenomenon, not the failure. **The bridge**: a vision model's naïveté is faked over a recognition it has already made, so the blind regime — the only source of a pre-recognition percept — is put to work as a ground. An Otsu silhouette read as bare, unnamed forces (`P_REGARD_NU`) primes the naïve gaze (`P_NAIF_SUBSTRAT`); form becomes the soil of emotion (Arnheim, turned into a method). The two naïve readings, *à l'aveugle* and *à nu*, are shown side by side. **The opening**: a *personification of the gaze* — personas for the observer, beyond the observed. Reflection and research ongoing; see `FONDEMENTS.md` §10, and the working protocol with diagrams in `RECHERCHE.md`. **Lesson so far: the same discipline that keeps the observed honest — look before you name, derive don't assert, keep what can be refuted — is what keeps a persona from reciting the person it imitates.**

## The roadmap

- **Phase 1** (at 300 ratified readings): first SFT cycle — LoRA on an open 7B VLM (Qwen2.5-VL), TRL/HF recipe. Goal: the format, the anchoring reflex, the refusal of jargon.
- **Phase 2** (at 800 pairs): DPO cycle — learning Marc's preference.
- **Absolute rules**: NEVER train on unratified data (else an amplifier of defects, cf. the v2 notebook). The bench arbitrates each cycle on images never seen during training. Fine-tuning consolidates the grammar, it does not replace it (slow memory / fast memory).
- **Undervalued parallel track**: a CLIP/SigLIP fine-tuned silhouette → concept (ZS-SBIR field) as a non-verbal primer, uncontaminable by the corpus. The binarized boards are already near-sketches.

## Key references

Full citations, formulas and lineages in `FONDEMENTS.md`. The four (verified) empirical anchors:

- **FacesInThings** — Hamilton et al., *Seeing Faces in Things* (ECCV 2024, MIT, arXiv:2409.16143, `pip install facesinthings`): ~5,000 annotated images, the face test bench. The paper models a “pareidolic peak”; the evolutionary need to also detect *animal* faces explains part of the machine/human gap.
- **Bistable Images** — Panagopoulou, Melkin & Callison-Burch (CMCL @ ACL 2024, arXiv:2405.19423): over 29 images and 116 manipulations (brightness, tint, rotation), the variance is *minimal* — interpretive monomania is **robust** (it does not unlock from a mere pivot). Hence the necessity of the anti-monomania moves, not their validation.
- **Rorschach × AI** — *Human Shadows in Machine Minds* (JMIR Mental Health 2026, e88186): whole-response bias quantified — GPT-4o 86.7% and Grok 3 90% of “whole” (W) responses; Gemini detail-dominant (counter-example). Validates “drop down in scale” for W-dominant models.
- **Arnheim, *Art and Visual Perception*** (1954): the reference for the configuration → effect grammar.
- **GalleryGPT / PaintingForm** — Bin et al. (ACM MM 2024, doi:10.1145/3664647.3681656; arXiv:2408.00491): ~19k paintings + ~50k formal analyses — reference for the sensible regime.

## Working conventions

- Systematic testing in headless Playwright with a mocked Anthropic API (simulated SSE) before any delivery. Chromium is preinstalled: `executablePath:'/opt/pw-browsers/chromium'` in a cloud session.
- Tests include hostile cases: deformed JSON (dialects), poor boards (re-prompt), horoscope rules (removal).
- Never an empty page as a possible result. Doubt ranks, it does not silence.
- The interface and doctrine are in French, sober, without emphasis. (The docs — this file, `README.md`, `FONDEMENTS.md` — are in English.)
- Personal data (corpus, grammar, notebook, exports) is in `.gitignore` — never version it.
- Valid API models: `claude-opus-5`, `claude-sonnet-5`, `claude-haiku-4-5`. Recent models reject `temperature` (auto-handled in `ask()`).
