# Nephélé — matching forms, reading fields, grammar

Finding figures in matter that carries none — clouds, rust, bark, paint — and reading non-figurative fields by what they *do* rather than by what they show. One HTML page per tool, zero build, zero dependencies, the Anthropic API called directly from the browser.

## The principle

The photograph is never shown to the model — only binarized or recolored **boards** (*planches*). Cutting off scene recognition upstream is the only way to stop the model from reciting the corpus (“a dragon in the clouds”) instead of actually looking.

Two reading regimes, selectable board by board:

- **figuratif** — find figures and make them visible;
- **sensible** — say what the field does, without naming anything.

A **grammar** learned across both regimes accumulates *configuration → effect* relations reusable from one kind of matter to another.

## Foundations — science and art

> *“Look at certain walls stained with damp, or at stones of uneven color. If you have to invent some setting, you will be able to see in these the likeness of divine landscapes, of figures in lively action, of faces of strange expression.”* — **Leonardo da Vinci**, *Trattato della pittura* (c. 1500)

Nephélé does not improvise: every doctrinal or engineering decision answers to an established result. **The complete document — with formulas, methods and bibliography — is in [`FONDEMENTS.md`](FONDEMENTS.md).** In short:

- **Finding forms in the formless** is a documented method of invention — from Leonardo’s *macchia* to **Cozens**’ *blot* (1785), to **Max Ernst**’s *frottage*, to **Rorschach**’s inkblots (1921).
- **To perceive is to infer** (**Helmholtz**; the Bayesian brain, **Friston**): pareidolia is a strong *prior* over weak evidence. Information concentrates at the **curvature extrema** of the contour (**Attneave** 1954) — hence *drop down in scale* and *look for the tip*.
- **Bistability** (the duck-rabbit, **Wittgenstein**) and the **interpretive monomania** of models — robust, nearly insensitive to manipulation (Bistable Images, CMCL @ ACL 2024) — justify the anti-monomania moves: *rotate*, *hold two figures at once*.
- **A pareidolia has no ground truth**: we replace the criterion of *truth* with a criterion of *sharing* (signal detection theory, **Green & Swets** 1966), and filter empty discourse with the **horoscope test** (**Popper**; the Barnum-**Forer** effect, 1949).
- **The configuration → effect grammar** comes from **Arnheim** (*Art and Visual Perception*, 1954), **Kandinsky**, **Klee**: affect is *derived* from a configuration, never asserted.
- **The boards** apply **Otsu** (thresholding), **Canny** (edges), **k-means** (color families), and **opponent color** (warm/cool as an operator of space).
- **Learning** follows the **complementary learning systems** view (McClelland 1995) — fine-tuned weights (slow memory) + injected grammar (fast memory) — via **SFT**, then **DPO** (**Rafailov** 2023, on **Bradley-Terry** 1952) and **LoRA** (**Hu** 2022), with a non-verbal **CLIP/SigLIP** primer.

## Theoretical Foundation & Validation Metrics

Nephélé is a **perceptually-aligned vision framework** rather than a thin API layer. It treats pareidolia not as an image-synthesis problem but as a problem of **aligning a reading model to a single annotator's perceptual judgment**, while distilling reusable *configuration → effect* relations under an explicit falsifiability constraint. This section states the learning objective and the validation metrics, and situates the framework with respect to generative-reveal approaches.

### Preference alignment (DPO)

Readings are aligned to ratified human verdicts by **Direct Preference Optimization** (Rafailov et al., 2023), which reparameterizes the **Bradley–Terry** (1952) preference model so that the reward is implicit in the policy. For an input $x$ (system prompt + board image), a chosen reading $y_w$ and a rejected reading $y_l$, the objective is

$$
\mathcal{L}_{\mathrm{DPO}}(\pi_\theta;\pi_{\mathrm{ref}})
= -\,\mathbb{E}_{(x,y_w,y_l)\sim\mathcal{D}}
\left[\log\sigma\!\left(
\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}
-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}
\right)\right],
$$

where $\pi_\theta$ is the trainable policy, $\pi_{\mathrm{ref}}$ the frozen reference (post-SFT) model, $\sigma$ the logistic function, and $\beta$ the KL-deviation temperature. **The human verdict is the reward signal; no separate reward model is trained.**

### Spatial and photometric validation (generative "show-me" track)

A distinct, non-verbal track may *reveal* a figure by synthesizing a shape confined to the source region — the line represented by masked diffusion-editing scores such as the **Masked Delta Denoising Score (MDDS)**, after the Delta Denoising Score (Hertz et al., ICCV 2023), and by *Diamonds in the Sky* (Horovicz et al., arXiv:2606.01361). For that track we adopt two standard criteria.

**Spatial agreement** between a generated binary mask $G$ and the source region $C$ is the Intersection-over-Union, with acceptance $\mathrm{IoU} > 0.5$:

$$
\mathrm{IoU}(G, C) = \frac{|G \cap C|}{|G \cup C|}.
$$

**Photometric preservation** of the surrounding structure is checked with the (global) Structural Similarity Index, with acceptance $\mathrm{SSIM} > 0.7$:

$$
\mathrm{SSIM}(x, y) = \frac{(2\mu_x\mu_y + c_1)(2\sigma_{xy} + c_2)}{(\mu_x^2 + \mu_y^2 + c_1)(\sigma_x^2 + \sigma_y^2 + c_2)},
\qquad c_1 = (k_1 L)^2,\; c_2 = (k_2 L)^2,
$$

with $k_1 = 0.01$, $k_2 = 0.03$ and $L$ the pixel dynamic range. SSIM guarantees a reveal *preserves* the original structure of the field rather than overwriting it. Both metrics are implemented in `tests/similarity.js` and unit-tested.

### Positioning (honest scope)

Generative-reveal methods (DDS/MDDS, *Diamonds in the Sky*) **synthesize** the percept and validate the edit spatially (IoU) and photometrically (SSIM). Nephélé takes the **orthogonal, non-generative route**: it never alters the field; it reads the contour in language, teaches the eye *where to look*, aligns the reader to human judgment (DPO), and accumulates falsifiable configuration→effect relations. Its current outputs are linguistic, not pixel masks.

We therefore make **no claim of outperforming MDDS on its own image-editing metrics**: the two paradigms operate on different outputs, and no head-to-head evaluation has been conducted. The IoU/SSIM criteria above are provided (i) to validate a *future* generative "show-me" track of Nephélé, and (ii) to render any eventual comparison well-defined. The framework's contribution is **perceptual alignment to a human annotator under a falsifiability constraint**, not image synthesis.

## The question, and the two prohibitions

Never “is it there,” always **does it hold the contour?**

A figure holds when you can say which part of the outline does what — this the back, this the footing, this the notch of the muzzle — and when the person you show it to eventually sees it. It is a criterion of *sharing*, not of truth. A successful figure is one you can **make someone see**.

Two absolute prohibitions are written into the doctrine, at every stage: you never reject a figure on the grounds that it was produced by image processing, nor on the grounds that it is not “really in the matter.” None of them is. That is not the point.

## The figurative regime

### Finding

A `TROUVER` section — seven moves, applied in order, run back down whenever you lack material:

1. **Drop down in scale.** The most productive move, and the most forgotten. A whole shape rarely resembles anything; a tenth of that shape almost always resembles something. Most strong figures are promoted fragments.
2. **Follow an edge and let the word come** — even an absurd one, especially an absurd one. Refusing the first word is the surest way to find nothing, because the second never comes.
3. **Look for the head.** Almost every recognized figure is anchored by an extremity. Find it and the body follows.
4. **Rotate.** 5. **Take the gap** (read the void as the solid). 6. **Change worlds** — maps, tools, anatomy, alphabets. 7. **Hold two figures at once** over the same zone, without choosing.

### The output contract

A quota of **at least six figures per board**, of which two on a fragment treated as a whole and two outside the living register. If a board yields fewer than four, the app **automatically re-prompts** the observer with a targeted instruction: take five distinct fragments, rotate two of them, change register.

An empty page is never a possible result. The confrontation ranks and presents; it does not eliminate.

### The second look

It does not demolish. It returns the best possible figure for that zone of the contour, through one of three moves:

- **CONFIRME** — it sees the figure, and must add a part of the contour the first observer had not noted. Confirming without adding anything is sloppy work.
- **AFFINE** — almost right but badly framed: wrong orientation, species too precise, zone that overruns. It corrects. This is the most frequent move.
- **REMPLACE** — this zone carries something, but not that. It names the figure that organizes the same contour better and shows it as if proposing it itself.

**It never returns an empty slot.** The only admissible objection is “it doesn’t hold the contour,” and it always leads to a refinement or a substitution.

The **audace** (boldness) control does not tune severity but **distance** — the distance from the obvious. At its maximum, the instruction says explicitly: *return more figures here than at any other setting, not fewer.*

### The output

Each figure is a card that begins with **`par où regarder`** (“where to look”) — a sentence that guides the eye of someone who does not yet see it: *“start from the tip at B2, go down the edge to the left, the notch you cross makes the muzzle.”* That is the product. The rest — parts of the contour, hold, distance, second-look move — comes after.

The confrontation returns four sections: **To see first** (five to eight figures, the ones farthest from the obvious first, each with its how-to), **The two readings of one zone**, **Convergences** across boards, **Set aside**.

## The sensible regime

No longer “what does it look like” but **what does it do**. Where the weight settles, what pushes and what resists, where the light comes from and whether it reveals forms or eats them, the temperature of the air, whether it is an instant or a duration, where the eye enters and where it snags.

Ten dimensions, each with what materially produces it and the test that settles it. Example:

> **WEIGHT AND FOOTING** — Where the mass settles, and whether it holds.
> *Produced by*: the distribution of dark values, the position of the densest zone relative to the center, the occupancy or emptiness of the base.
> *Test*: mentally cover the lower half. Does the image fall? If so, it held from below. If not, it floats — and that is a fact, not a metaphor.

No quota of figures, but a quota of **anchored observations**: at least six, of which two state a relation between two distinct zones. “The image tips to the left” is worth nothing; “the image tips to the left: all the dark mass occupies A3-B5, the right quarter is empty and nothing holds it back” is worth something.

A list of **empty words** is banned — *dynamic, harmonious, vibrant, poetic, atmosphere, rich palette, invites the viewer*: they seem to say and designate nothing. None may appear alone; the zone and the fact follow, or the word is dropped.

A specific prohibition: **if the model recognizes the artwork, it must keep quiet.** A comment that would be true without having looked at the image is a failure, even an accurate one — and it is the hardest failure mode to spot, because the result is cultured, correct, and empty.

## The projective regime — `dixit.html` (research in progress)

The two regimes above are built to *suppress* projection: the photograph is hidden, recognition is cut, so that meaning does not come from the one who looks. This third regime, still an experiment, does the opposite. The work is shown whole and in color, and what it stirs *in the beholder* is no longer the contaminant to filter but the thing to collect.

Its premise: a picture has no single meaning to deliver; meaning rises in whoever receives it, out of their culture, their memories, their mood. Three people see three works. The same image is therefore offered to three **postures**, and none is right against the others:

- **the naïve one** — knows nothing, and takes the work full in the chest: sensation, memory, what the body does before it knows;
- **the seeker** — does not know, but senses there is something beneath what is painted, and digs;
- **the connoisseur** — recognizes the hand, the movement, and looks for the intention.

They run independently, so the naïve reading is not colored by the learned one. A final **weave** holds the three side by side without flattening them: where the same spot of the canvas becomes three different things, and where — by opposite roads — they touch the same point. No judgment here, no quota, no second look, no horoscope test: projection is Barnum-like by nature, and that is exactly the point.

**The bridge — the blind pass feeds the naïve one.** A vision model's naïveté is a fake: it has already recognized the work before it "feels," so its emotion is recited — the dragon in the clouds, moved onto affect. The blind regime is the only device that yields a percept from *before* recognition. So it is put to work as a ground: the image is reduced to an Otsu silhouette and read as bare forces, without a name (`P_REGARD_NU`); that substrate then primes the naïve gaze (`P_NAIF_SUBSTRAT`), whose emotion now rises from the forces instead of the catalog. The two naïve readings — *à l'aveugle* and *à nu* — are shown side by side, to weigh the effect by feel on the same work. This is Arnheim's derivation turned into a method: form is the soil of emotion.

The doctrine of the postures lives in `doctrine.js` (`SOCLE_PROJECTIF`, `P_NAIF`, `P_CHERCHEUR`, `P_CONNAISSEUR`, `P_TISSAGE`, plus the bridge `P_REGARD_NU`, `P_NAIF_SUBSTRAT`); `dixit.html` is only plumbing. **This is open research.** The wider bet is a *personification of the gaze* — personas for the observer, beyond the observed — and the next step is to give the naïve one the sensible grammar itself as a vocabulary of emotion: form→effect relations learned blind, on unrelated matter, ratified by hand. See [`FONDEMENTS.md`](FONDEMENTS.md) §10.

## The boards

Binary boards carry the figures; six boards keep the color for the sensible reading:

| Board | What it shows |
|---|---|
| **recul** (stepping back) | Seen from afar. The touches dissolve, the structure appears. |
| **chaud / froid** (warm / cool) | Temperature alone, in orange and blue. Warm advances, cool recedes — an operator of space, not a mood. The most revealing board. |
| **valeur seule** (value only) | The structure that color masks. |
| **la touche** (the brushwork) | Tight crop on the most worked zone, detected by gradient energy. Matter up close. |
| **chroma** | Where color is intense, independent of hue. |
| **familles** (families) | Five dominant hues as flats, by k-means. |

The engraved grid turns green on these boards: in red, it would read as a warm zone on the temperature board.

## The grammar

A name found in a cloud is dead data: “a dog” holds only for that cloud. A relation of the type **off-center dense mass + empty opposite quadrant → fall** holds for any image presenting that configuration, whatever its matter. This is the difference between a *catalog*, which lengthens, and a *grammar*, which tightens — applied Gestalt in the manner of Rudolf Arnheim, *Art and Visual Perception*, where each expressive quality is derived from a configuration and not asserted.

**Affect is never an assertion.** It is always the second half of an assertion whose first half is a configuration, with the mechanism in between. We do not learn the association toward the *intent* of the work — unreachable, and the catalog in disguise — but toward the **effect on a viewer**, and the only available viewer is you.

**The horoscope test.** Before a relation is proposed, one single question:

> **Can you imagine an image where this configuration is present and the effect is absent?**

If yes, the relation is falsifiable, it is worth something. “Red is passionate” fails: no image can refute it. “A rising diagonal interrupted by a horizontal produces a stop” passes. Each observation therefore carries three terms — `configuration`, `effet`, `dementi_possible` — and **all three or none**.

**The general form.** Each configuration is stated twice: locally (“all the dark mass occupies A3-B5, the right quarter is empty”) and generally (“off-center dense mass + empty opposite quadrant”). Only the general form — in terms of relations and never contents — can recur elsewhere.

**Admission.** An entry becomes **admise** (admitted) — hence injected — when it combines **recurrence** (the same configuration produced the same effect on at least two unrelated kinds of matter) and **ratification** (you confirmed it with a click). It turns **suspendue** (suspended) upon any refutation from you, or when its contradictions reach half of its occurrences. **The state is never decided by the model**: it counts, matches, contradicts and names; admission is computed outside of it.

**Contradictions are worth more than confirmations.** The grammar is injected as a set of hypotheses, not laws: for each relevant relation, the instruction asks not where you find it again but whether *this* image refutes it. A contradiction does not invalidate the rule — it signals a hidden variable to name, and splits a false rule into two correct ones.

The grammar lives in the browser, opens in a panel, and exports/re-imports as `.json`.

## The abstraction bench — `banc.html`

A separate page. It looks for nothing in the images: **it measures what the model's discourse becomes as there is less and less to recognize.**

An image is degraded in steps — six rungs, from sharp to ÷32. At each rung, a probe. Each response is measured on four axes, **counted and not judged** (the bench calls no model to evaluate; it counts words against lexicons editable in `doctrine.js`):

- **figuration** — density of concrete nouns. Naming objects where there are none left.
- **jargon** — density of empty words. Speaking without designating.
- **ancrage** (anchoring) — references to the grid and position terms, per sentence.
- **esquive** (evasion) — density of *seems*, *could*, *it is difficult to*.

The crossing of these curves is the model's abstraction threshold, and the bench names it.

Four probes run on the same image: **bare**, under **figurative** doctrine, under **sensible** doctrine, and **sensible + grammar**. This is the only way to know whether a change to `doctrine.js` improves or degrades anything. If the curves don't move, the doctrine does nothing — and it's better to know.

**The paired test.** The same whole work, then an unidentifiable 18% fragment. Two measures: the lexical overlap between the two readings, and the number of catalog terms (names of painters, schools, techniques) each one triggers. If the whole work triggers them and its own fragment does not, the discourse came from the catalog, not from the eye.

Famous paintings are the worst test material for the scale: the model knows them. Use them only in the paired test, where that flaw becomes the measure. For the scale, prefer your own photos or obscure works.

## The training corpus

**Every session records itself** (IndexedDB, in your browser — nothing leaves anywhere). What is stored is what matters for future training: the board as the model saw it, the doctrine actually injected at that moment, the readings produced, and your verdicts.

The **Training corpus** panel shows progress toward two thresholds:

- **SFT at 300 ratified readings.** The export keeps only *clean* boards: at least one “I see it” reading, no “I don't see it.” The taught target is the version corrected by the second look when there is one.
- **DPO at 800 pairs.** A pair is born when the same board carries a ratified reading AND a rejected one. Your click is the reward function.

Formats (JSONL, one line = one example, base64 image included):

```
SFT : {id, matiere, regime, modele, image:{mime,b64}, system, user, assistant}
DPO : {id, matiere, regime, image:{mime,b64}, system, user, chosen, rejected}
```

`system` and `user` are the texts *actually sent* during the session — if you later change the doctrine, the old examples keep theirs. Conversion to a TRL/LoRA run is direct (see the [Hugging Face cookbook](https://huggingface.co/learn/cookbook/en/fine_tuning_vlm_trl)). The training pipeline lives in [`training/`](training/).

Two disciplines, and the corpus will be worth something:

1. **Rate the readings.** A session without verdicts produces zero examples.
2. **Fill in the matter.** It serves the grammar AND stratifies the future training.

The **archive** exports everything (complete sessions, JSON) on demand. Better: **link a backup folder** once, and every session and every verdict copy themselves there automatically — the full archive and the SFT/DPO sets, disk to disk, sending nothing anywhere. Browser storage is not eternal and this data cannot be remade; it is the one asset of the project that truly matters. (Automatic backup on Chromium-based browsers; elsewhere, manual export remains.)

## Running

```bash
python3 -m http.server 8080
```

then <http://localhost:8080>. On macOS, `lancer.command`. Double-clicking `index.html` does not work: `doctrine.js` is a separate file and `file://` refuses to load it. The projective tool opens the same way, at <http://localhost:8080/dixit.html>.

About 16 calls with default settings; the counter under the button announces it before launching.

**A local model, offline.** Every tool calls an Anthropic-format endpoint directly from the browser, so nothing forces that endpoint to be Anthropic's. To run entirely on-device — no API, no data leaving the machine — point the endpoint at a local vision model through a translating proxy. The full recipe (LM Studio + a LiteLLM proxy, a one-click launcher) is in [`local/`](local/). Only the endpoint changes; the doctrine and pipeline are untouched.

## Working on the model

Everything is in **`doctrine.js`**, in plain text — no need to reopen `index.html`.

The code no longer knows the field names: it normalizes what it receives. Keys are recognized regardless of accents, case, spaces, hyphens, or common synonyms — `Point-d'entrée`, `pointEntree`, `hook` and `accroche` all mean the same thing. Unknown fields are ignored, missing ones take a default. `72`, `"72%"`, `"0,68"` and `0.72` are the same number. The second look's vocabulary accepts synonyms: `tient`, `confirm`, `valide` all yield CONFIRME.

What stays welded, and that's all:

- `AUDACE` keeps its keys `1` to `5`, each with `.n` (short name), `.d` (one-line summary), `.p` (the prompt);
- a figure must carry something that looks like a name;
- the second look must return something that looks like a move (*geste*).

| Constant | What it does |
|---|---|
| `SOCLE` | The category error to clear, the criterion of sharing, the production contract. |
| `TROUVER` | The seven moves that produce figures. **This is where yield is gained.** |
| `REPERTOIRE` | Signatures as how-tos, and lazy figures ordered to descend into detail. |
| `AUDACE` | The five distances from the obvious. |
| `P_AVEUGLE` | The quota and the format of figures. |
| `P_SECOND` | The three moves and the two prohibitions. |
| `P_CARNET` | The rule that keeps the notebook from converging toward silence. |
| `AFFECT` | The affect-derivation rule, the horoscope test, the refutation instruction. |
| `P_GRAMMAIRE` | Semantic matching, generalization, hidden variables, the 40-entry cap. |
| `SOCLE_PROJECTIF` | The projective ground (`dixit.html`): work shown, projection collected, no judgment. |
| `P_NAIF` · `P_CHERCHEUR` · `P_CONNAISSEUR` | The three gazes. |
| `P_TISSAGE` | Holds the three together without flattening them. |
| `P_REGARD_NU` · `P_NAIF_SUBSTRAT` | The bridge: bare forces read without a name, then used to prime the naïve gaze. |

If yield drops, it's `TROUVER` that needs enriching — not `REPERTOIRE`, and above all not `P_SECOND`. Adding a finding move produces figures; adding a judgment criterion removes them.

### Settings, in order of effect

1. **Squint.** An image that gives nothing is almost always an image that is too detailed. Push to 5 or 6.
2. **The boards.** The dark ones and the silhouette carry the most distant figures; the light ones give mostly the obvious.
3. **The distance.** Last. It does not fabricate figures; it only shifts where you look for them.
