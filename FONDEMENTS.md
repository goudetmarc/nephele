# Foundations — science and art

> *“Look at walls covered with stains, or made of a mixture of stones, and you
> will be able to see in them the likeness of various landscapes, of battles, of
> figures in lively action, of expressions of faces, of costumes.”*
> — Leonardo da Vinci, *Trattato della pittura*, §60 (c. 1500)

This document lays out the intellectual scaffolding of Nephélé: what it borrows
from the psychology of perception, signal theory, formal aesthetics, decision
theory and machine learning — and how each borrowing translates into a precise
mechanism in the code. Nothing here is decorative: every reference answers to an
engineering or doctrinal decision.

The project has a single object: **matching forms** — finding figures in matter
that carries none (clouds, rust, bark, paint), and reading non-figurative fields
by what they *do* rather than by what they *show*. It is a problem of **directed
apophenia**: to provoke, then discipline, the perception of structure in chance.

---

## 1. The artistic lineage of finding forms

Seeing figures in formless matter is a technique of invention as old as it is
documented.

- **Leonardo da Vinci** (*Trattato della pittura*, c. 1500): the *macchia*, the
  stain on the wall as a trigger for invention. This is the historical matrix of
  Nephélé.
- **Alexander Cozens**, *A New Method of Assisting the Invention in Drawing
  Original Compositions of Landscape* (1785): *blot drawing* — starting from a
  random stain to compose a landscape. A method, not an accident.
- **Victor Hugo** (stains, folds, washes, ~1850–1870) and above all **Max Ernst**
  (*frottage* 1925, *decalcomania* 1936): graphic automatism generates the
  texture, the eye matches the figure to it. Surrealism theorizes **automatism**
  (Breton, *Manifesto* 1924) as a short-circuit of conscious control.
- **Hermann Rorschach**, *Psychodiagnostik* (1921): the symmetric inkblot as an
  instrument. Nephélé inherits the apparatus *and* its warning (§4).
- **Ludwig Wittgenstein** (*Philosophical Investigations*, II, xi, 1953) on
  *seeing-as* (**Jastrow**’s duck-rabbit, 1899): one and the same configuration
  supports two incompatible views, and “seeing” is already an interpretation.

> **In the code.** The photograph is **never** shown to the model, only
> binarized or recolored boards (`faireLesPlanches` in `index.html`). This is
> Leonardo’s wall, Cozens’ blot: cutting off scene recognition upstream to force
> matching rather than recitation.

---

## 2. Perception as inference: Gestalt, Helmholtz, Bayes

### 2.1 Gestalt theory

The psychology of form (**Wertheimer** 1923; **Koffka**, *Principles of Gestalt
Psychology*, 1935; **Köhler**) establishes that perception groups the field
according to laws — proximity, similarity, closure, good continuation, common
fate — under a governing principle, **Prägnanz** (the tendency toward the
simplest / most regular form).

**Hochberg & McAlister** (1953) give it a quantitative formulation — the
*minimum principle*: the “goodness” of a figure is inversely proportional to the
amount of information needed to specify it. A figure “holds” when it is the most
economical organization of the contour.

$$\text{goodness}(F) \;\propto\; \frac{1}{I(F)}, \qquad I(F) = \text{information to describe } F$$

> **In the code.** Nephélé’s criterion — *“does it hold the contour?”* — is a
> Prägnanz criterion: a figure is kept when you can say which part of the outline
> does what (closure, good continuation), i.e. when it economically organizes the
> contour. **Closure** is exactly what the second look tracks (`P_SECOND`: “do
> the designated parts do what is claimed?”).

### 2.2 Unconscious inference and the Bayesian brain

**Helmholtz** (1867): to perceive is to unconsciously infer the most probable
cause of the sensations. The modern reading — **Bayesian perception** and
**predictive coding** (**Friston**, *free-energy principle*, 2010) — writes
perception as a posterior inference:

$$P(H \mid D) \;=\; \frac{P(D \mid H)\,P(H)}{P(D)} \;\propto\; P(D \mid H)\,P(H)$$

**Pareidolia** is the case where a strong **prior** $P(H)$ (faces, animals,
bodies) dominates weak or ambiguous sensory evidence $P(D\mid H)$: the brain
“sees” the most expected hypothesis. Faces are the strongest prior — hence the
activation of the **fusiform face area** (FFA; **Kanwisher, McDermott & Chun**
1997) in front of mere blobs arranged in a triad (**Liu et al.** 2014,
*Seeing Jesus in toast*).

> **In the code.** The finding move *“Look for the head”* (`TROUVER`) exploits
> the most powerful prior; *“Follow an edge and let the word come, even an
> absurd one”* deliberately relaxes control to let the prior speak.

### 2.3 Information is in the contour: Attneave, Marr, Biederman

**Attneave** (*Some informational aspects of visual perception*, 1954) shows
that visual information concentrates at the **points of maximum curvature** of
the contour — his famous “cat”, reduced to segments joining the curvature
extrema, remains recognizable. **Marr** (*Vision*, 1982) formalizes the primal
sketch and its three levels (computational / algorithmic / implementational).
**Biederman** (*recognition-by-components*, 1987): objects are recognized as
assemblies of primitives (*geons*) defined by their contours.

> **In the code.** Two `TROUVER` moves follow directly:
> - *“Drop down in scale”* — a fragment of contour carries more exploitable
>   local information than a whole silhouette: most strong figures are promoted
>   fragments.
> - *“Look for the tip / the extremity”* — curvature extrema (in Attneave’s
>   sense) are the natural anchors of the figure.
>
> The bias measured on the Rorschach (≈87–90% of **whole responses** in GPT-4o
> and Grok 3, cf. §3) is precisely the failure to descend to the level where the
> information is.

---

## 3. Multistable perception and interpretive monomania

An ambiguous configuration (duck-rabbit, Necker cube, Rubin’s vase) admits
several mutually exclusive organizations; perception **flips** but holds only one
at a time — this is **perceptual rivalry**. The corollary, **interpretive
monomania**, is the central risk for a reader of forms: fixating on the first
reading and no longer seeing the others.

Project references (verified citations, §Bibliography):

- **Bistable Images** — Panagopoulou, Melkin & Callison-Burch (CMCL @ ACL 2024,
  arXiv:2405.19423). On 29 bistable images and 116 manipulations (brightness,
  tint, rotation), the models show a **pronounced preference for a single
  interpretation** and **minimal variance under manipulation** (with a few
  exceptions). In other words: interpretive monomania is *robust* — it does not
  unlock from a mere pivot, which makes the anti-monomania moves all the more
  necessary.
- **Rorschach × AI** — *Human Shadows in Machine Minds* (JMIR Mental Health 2026,
  e88186): quantifies the **whole-response bias**. GPT-4o and Grok 3 return
  **86.7% and 90% of “whole” (W) responses** respectively, where humans descend
  to detail; Gemini, detail-dominant (D), is the exception.
- **FacesInThings** — *Seeing Faces in Things*, Hamilton et al. (ECCV 2024, MIT,
  arXiv:2409.16143; ~5,000 annotated face-pareidolia images, MIT license). The
  paper models a **“pareidolic peak”** (an image complexity that is “just right”)
  and shows that the evolutionary need to also detect **animal** faces explains
  part of the machine/human gap.

> **In the code.** Three mechanisms:
> - `TROUVER` mandates *“Rotate”* (the ACL 2024 rotation) and *“Hold two figures
>   at once over the same zone, without choosing”* — explicit anti-monomania.
> - The **second look** does not demolish: it proposes the best competing reading
>   (CONFIRME / AFFINE / REMPLACE), institutionalizing bistability.
> - The six-figure quota and the automatic re-prompt (`P_AVEUGLE`) force going
>   past the first, whole response.

---

## 4. Epistemology: a pareidolia has no ground truth

This is the project’s most dearly paid lesson (the “v2” failure). The camel is
not in the cloud; it was never there and no verification will find it there.
Asking “does this figure really exist?” destroys the object under examination.

### 4.1 A criterion of sharing, not of truth — signal detection theory

**Signal detection theory** (**Green & Swets**, 1966) separates two orthogonal
quantities: **sensitivity** $d'$ (the ability to distinguish signal from noise)
and the **criterion** $\beta$ (the decision threshold, freely placed):

$$d' = z(\text{hit rate}) - z(\text{false-alarm rate})$$

In front of a pareidolia, **there is no signal in the ground-truth sense**: $d'$
is not definable. The criterion remains. Nephélé therefore explicitly replaces
the criterion of **truth** with a criterion of **sharing**: a successful figure
is not a true figure, it is a figure you can *make someone see*. It is an
inter-subjective criterion (ratification), not a test of existence.

### 4.2 Falsifiability and the Barnum effect: the horoscope test

For non-figurative fields, we still want to guard against empty discourse. Two
classic tools:

- **Popper** (*Logik der Forschung*, 1934): a statement has content only if it is
  **falsifiable** — if there exists a conceivable observation that would refute
  it.
- **Forer** (*The fallacy of personal validation*, 1949) — the **Barnum effect**:
  a statement vague enough to apply to everyone (a horoscope) is perceived as
  true precisely because it excludes nothing.

> **In the code — the horoscope test** (`AFFECT`, `P_GRAMMAIRE`). Before a
> *configuration → effect* relation enters the grammar, one question and one
> only: *“Can you imagine an image where this configuration is present and the
> effect absent?”* If not, the statement is a Barnum, non-falsifiable, rejected.
> “A rising diagonal interrupted by a horizontal produces a stop” passes; “red is
> passionate” fails. Each entry therefore carries the triple
> `configuration / effet / dementi_possible` — **all three or none**.

### 4.3 Two absolute prohibitions

Written throughout the doctrine: you **never** reject a figure (i) on the grounds
that it was produced by image processing, nor (ii) on the grounds that it “is not
really in the matter.” The first objection is a **universal solvent** (every
thresholding silhouette is produced by the threshold: the argument invalidates
100% of figures, hence says nothing); the second is the category error of §4.

---

## 5. The configuration → effect grammar: Arnheim, Kandinsky, Klee

A name found in a cloud is dead data (it holds only for that cloud). A
**relation** — *off-center dense mass + empty opposite quadrant → fall* — holds
for any image presenting that configuration. This is the difference between a
**catalog** (which lengthens) and a **grammar** (which tightens).

The tradition that writes this grammar:

- **Kandinsky**, *Concerning the Spiritual in Art* (1911), *Point and Line to
  Plane* (1926): an attempt at a lexicon of elementary plastic forces.
- **Paul Klee**, *Pedagogical Sketchbook* (1925, Bauhaus): the genesis of form
  through the movement of point and line.
- **Rudolf Arnheim**, *Art and Visual Perception* (1954) — the master reference:
  applied Gestalt, where each expressive quality is **derived** from a
  configuration and not asserted. Weight, direction, tension are perceptual
  facts, not metaphors.

Database for the sensible regime:

- **GalleryGPT / PaintingForm** (ACM MM 2024): ~19k paintings, ~50k formal
  analyses — a reference for non-catalog formal analysis.

> **In the code.** Affect is **never** an assertion; it is always the **second
> half** of an assertion whose first half is a configuration, with the mechanism
> in between (Arnheim). We learn the association toward the **effect on a
> viewer**, never toward the intent of the work (unreachable, and the catalog in
> disguise). The sensible regime measures **anchored observations**, not
> impressions; the “empty words” (*vibrant, atmosphere, poetic*) are the dragons
> of the non-figurative — more dangerous because they pass for culture.

---

## 6. Processing the boards: methods and formulas

The boards turn the image into fields that cut scene recognition while preserving
contour and relational information.

**Thresholding (binary boards) — Otsu (1979).** The threshold $t^\*$ maximizes
the between-class variance of the gray-level histogram:

$$t^\* = \arg\max_t \; \sigma_b^2(t), \qquad \sigma_b^2(t) = \omega_0(t)\,\omega_1(t)\,\big(\mu_0(t)-\mu_1(t)\big)^2$$

where $\omega_i$ are the masses of the two classes and $\mu_i$ their means.

**Edges — Canny (1986).** Contour extraction by gradient, non-maximum
suppression and hysteresis: the silhouette reduced to its lines of information
(Attneave, §2.3).

**Color families — k-means (Lloyd 1957/1982; MacQueen 1967).** Quantizing colors
into $k$ flats minimizing within-cluster inertia:

$$\min_{\{\mu_j\}} \; \sum_{i} \min_{j\in\{1..k\}} \lVert x_i - \mu_j \rVert^2$$

**Warm / cool — opponent-color theory (Hering; Hurvich & Jameson 1957).** The
projection onto the warm–cool axis (orange↔blue) isolates what temperature does
to space: warm advances, cool recedes — an operator of depth, not a mood. The
engraved grid turns green so as not to read as a warm zone.

> **In the code.** `planches` (recul, chaud/froid, valeur seule, la touche,
> chroma, familles) in `index.html`. The **warm/cool** board is the most
> revealing for painting: impressionism *is* a system of color relations.

---

## 7. The abstraction bench: measuring without judging

The bench (`banc.html`) measures what the model’s **discourse becomes** as the
image abstracts (step degradation, from sharp to ÷32). It summons no model to
evaluate: it **counts**, against editable lexicons. Four axes:

- **figuration** — density of concrete nouns (naming where there is nothing left);
- **jargon** — density of empty words (speaking without designating);
- **anchoring** — references to the grid and position terms, per sentence;
- **evasion** — density of *seems, could, it is difficult to*.

**Jargon as noise — Shannon (1948).** Discourse that adds no information about
the image is noise. Entropy

$$H(X) = -\sum_i p(x_i)\,\log_2 p(x_i)$$

gives the frame: the crossing of the bench’s curves is the model’s **abstraction
threshold** — the point where discourse stops designating and starts reciting.

**Paired test — a measure of recitation.** The same whole work, then an
unidentifiable fragment. If the recognized work triggers catalog terms (names of
painters, schools) and its own fragment does not, the discourse came from the
catalog, not the eye. It is a direct measure of contamination by memory.

**Textual similarity (test harness).** Two exact measures, without embeddings:

- **Cosine** bag-of-words between two readings:
  $$\cos(\theta) = \frac{\mathbf{a}\cdot\mathbf{b}}{\lVert\mathbf{a}\rVert\,\lVert\mathbf{b}\rVert} = \frac{\sum_i a_i b_i}{\sqrt{\sum_i a_i^2}\,\sqrt{\sum_i b_i^2}}$$
- **Levenshtein distance** (1966), minimal number of edits:
  $$d(i,j) = \min\begin{cases} d(i{-}1,j)+1 \\ d(i,j{-}1)+1 \\ d(i{-}1,j{-}1) + \mathbb{1}[a_i \neq b_j] \end{cases}$$

They bound the **drift** of the normalized output against deformed responses
(`tests/similarity.js`) and check the stability of the bench’s measures.

---

## 8. Learning: slow memory, fast memory

The learning architecture follows the theory of **complementary learning
systems** (**McClelland, McNaughton & O’Reilly**, 1995): a **slow memory** (the
cortex — here the model weights, consolidated by fine-tuning) and a **fast
memory** (the hippocampus — here the injected grammar, learned during a session).
Fine-tuning **consolidates** the grammar, it does not replace it.

### 8.1 Phase 0 — the corpus

Each session records itself in training format (board seen + injected doctrine +
verdicts). **Absolute rule: never train on unratified data** (else an amplifier
of defects). The bench arbitrates each cycle on images **never seen** during
training — hence the held-out split *by image* (`prepare_data.py`), leak-free.

### 8.2 Phase 1 — SFT (Supervised Fine-Tuning)

Supervised learning of the format and the anchoring reflex. Token-wise
cross-entropy minimization over the ratified target:

$$\mathcal{L}_{\text{SFT}} = -\sum_{t} \log \pi_\theta\big(y_t \mid y_{<t},\, x,\, \text{image}\big)$$

Backbone: the open VLM **Qwen2.5-VL-7B**, TRL/HF recipe.

### 8.3 Phase 2 — DPO (Direct Preference Optimization)

Preference learning starts from a classic model of pairwise choice, the
**Bradley–Terry** (1952) model:

$$P(y_w \succ y_l \mid x) = \frac{e^{\,r(x,y_w)}}{e^{\,r(x,y_w)} + e^{\,r(x,y_l)}} = \sigma\big(r(x,y_w) - r(x,y_l)\big)$$

**RLHF** (**Christiano et al.** 2017; **Ouyang et al.** 2022, InstructGPT) first
learned a reward $r$ then optimized by RL. **DPO** (**Rafailov et al.**, NeurIPS
2023) shows RL can be dropped: the optimal policy under a KL constraint expresses
the reward *implicitly*, and one directly optimizes

$$\mathcal{L}_{\text{DPO}} = -\,\mathbb{E}_{(x,\,y_w,\,y_l)}\Big[\log \sigma\Big(\beta \log \frac{\pi_\theta(y_w\mid x)}{\pi_{\text{ref}}(y_w\mid x)} - \beta \log \frac{\pi_\theta(y_l\mid x)}{\pi_{\text{ref}}(y_l\mid x)}\Big)\Big]$$

where $y_w$ (*chosen*) is the ratified reading, $y_l$ (*rejected*) the rejected
one, and $\beta$ tunes the deviation from the reference model. **Marc’s click *is*
the reward function.**

### 8.4 LoRA: low-rank adaptation

**Hu et al.** (*LoRA*, ICLR 2022): instead of updating $W_0$, one learns a
low-rank correction, cutting the trained parameters by orders of magnitude:

$$W = W_0 + \Delta W, \qquad \Delta W = \frac{\alpha}{r}\,B A, \quad B\in\mathbb{R}^{d\times r},\; A\in\mathbb{R}^{r\times k},\; r \ll \min(d,k)$$

Nephélé targets the attention modules with $r=16,\ \alpha=32$. **QLoRA**
(**Dettmers et al.**, 2023) adds 4-bit quantization — but we do **not** use it on
Apple Silicon (bitsandbytes is MPS-incompatible): with 64 GB of unified memory,
the 7B loads in native 16-bit.

### 8.5 Parallel track: silhouette → concept (ZS-SBIR)

A **non-verbal** primer, uncontaminable by the verbal corpus: a contrastive
encoder of the **CLIP** (**Radford et al.**, ICML 2021) / **SigLIP** (**Zhai et
al.**, ICCV 2023) family, fine-tuned for the *silhouette → concept* task (the
field of **zero-shot sketch-based image retrieval**). The binarized boards are
already near-sketches. The contrastive objective (InfoNCE) aligns image and
concept:

$$\mathcal{L}_{\text{NCE}} = -\log \frac{\exp(\langle f(x), g(c^{+})\rangle / \tau)}{\sum_{c}\exp(\langle f(x), g(c)\rangle / \tau)}$$

This path produces no text: it therefore cannot recite the catalog.

---

## 9. Synthesis: every decision, its reason

| Mechanism in the code | Foundation |
|---|---|
| Never show the photo, only boards | Leonardo, Cozens; cut scene recognition |
| *Drop down in scale*, *look for the tip* | Attneave 1954 (information at curvature extrema) |
| *Rotate*, *hold two figures* | Bistable Images ACL 2024; perceptual rivalry |
| *Look for the head* | FFA (Kanwisher 1997); Bayesian face prior |
| Second look (confirm/refine/replace) | Gestalt (closure); anti-monomania |
| “Does it hold the contour?” | Prägnanz / minimum principle (Hochberg 1953) |
| Criterion of sharing, not of truth | Signal detection (Green & Swets 1966) |
| The horoscope test | Popper 1934; Barnum-Forer effect 1949 |
| Configuration → effect grammar | Arnheim 1954; Kandinsky; Klee |
| Warm/cool as an operator of space | Opponent color (Hering; Hurvich & Jameson 1957) |
| Binary boards / families | Otsu 1979; Canny 1986; k-means |
| The bench counts jargon | Shannon 1948 (jargon = noise) |
| Cosine / Levenshtein similarity | Salton; Levenshtein 1966 |
| Injected grammar + fine-tuned weights | Complementary learning systems (McClelland 1995) |
| DPO on the verdicts | Bradley-Terry 1952; Rafailov 2023 |
| LoRA r=16 on attention | Hu et al. 2022 |
| Non-verbal primer | CLIP 2021; SigLIP 2023; ZS-SBIR |
| Projective regime, the three gazes (`dixit.html`) | Rorschach 1921; Iser 1974; Fish 1980 (reader-response) |
| Blind pass feeding the naïve gaze | Arnheim 1954 (affect derived from configuration), turned into a mechanism |
| World model as reading grid — strata, priors, surprise (see `RECHERCHE.md`) | Helmholtz; Friston 2010; Ha & Schmidhuber 2018; LeCun 2022 |

---

## 10. The projective turn: personas for the observer (research in progress)

Everything above concerns the *observed*: how to read matter or a field without reciting a corpus. The question it leaves untouched is the *observer*. A pareidolia, a reading, is never produced by a viewer in general; it is produced by *someone*, with a history, a culture, a mood. The move Nephélé is beginning to make is to take that seriously — to **personify the gaze**, give the reader explicit personas, and treat interpretation as a function of who looks as much as of what is looked at. This section records a direction, not a settled result.

### 10.1 A different question, and an inversion

The figurative and sensible regimes are anti-projective by construction (§4): they hide the photograph and forbid recognition precisely so that meaning does not come from the reader. The projective regime asks the opposite question — the one a Rorschach card or a Dixit image is *designed* for. Hermann Rorschach's inkblots (1921) are the canonical projective test: the stimulus is deliberately ambiguous so that what the subject brings is what shows. Literary theory made the same reversal — Wolfgang Iser's *implied reader* (1974), Stanley Fish's *interpretive communities* (1980): a text does not carry a meaning to be extracted; meaning is completed by the reader, and readers differently equipped complete it differently. The projective regime is an attempt to instrument that reversal — with the anchoring reflexes of the rest of the project carried over, so the projection does not dissolve into the empty words of §4.2.

### 10.2 The three gazes

Three postures face the same work: the naïve one (feels before it knows), the seeker (senses a hidden sense and digs), the connoisseur (recognizes, and reads for intention). They are run independently, so the naïve reading is not colored by the learned one; a fourth pass weaves them without choosing. The horoscope test (§4.2) does not apply here — projection is Barnum-like by nature, and that is now the phenomenon, not the failure. Symmetrically, what was an error mode elsewhere (a comment true without having looked) becomes, for the connoisseur, a named and bounded risk rather than a disqualification.

### 10.3 The fake naïveté, and the blind-pass bridge

A vision-language model cannot un-know. Asked to be naïve, it performs naïveté over a recognition it has already made; its "feeling" is the average of what is written about the work — affect as recitation, the dragon of §1 moved onto emotion. The one device that yields a percept from *before* recognition is the blind regime itself: boards with no scene, no color, no title. This is where the two halves of the project join. An Otsu silhouette (§6) is read as bare, anchored, unnamed forces (`P_REGARD_NU`); that substrate primes the naïve gaze (`P_NAIF_SUBSTRAT`), whose emotion then rises from the forces rather than the catalog. This is Arnheim's derivation (§5) used as a *mechanism*: a configuration is the antecedent of an affect, so a reading of pure configuration is the honest ground of a feeling. The interface shows both naïve readings — *à l'aveugle* and *à nu* — side by side, so the shift can be judged by feel, on the same work, by the human it is meant to move.

### 10.4 Open questions

Unfinished, and deliberately so. What remains:

- **The grammar as a vocabulary of emotion.** The sensible grammar (§5) already stores falsifiable form→effect relations, learned blind on unrelated matter and ratified by hand. The next step is to prime the naïve gaze with *it* — not the culture's associations, but relations earned under blinders. The naïve one would then feel in a language the project itself learned. (This is the "option 3" beyond the current blind-pass bridge.)
- **Which personas, and how many.** Three is a first cut. Culture, age, era, discipline, mood are all axes along which a gaze varies. The danger is caricature: a persona that recites a stereotype is the dragon again, one remove out.
- **Validation.** The bench (§7) measures the observed. Measuring a projection is another problem: the criterion is not accuracy but resonance and plurality — how many distinct, non-empty readings a work supports, and whether a human recognizes the feeling as their own. No metric here is settled.
- **The dividing line.** How far a persona may be pushed before it stops looking and starts reciting the person it imitates — the projective analogue of the empty-word failure — is not yet drawn.

The wager is that the observed and the observer are one subject seen from two sides, and that the discipline learned on the first — look before you name, derive rather than assert, keep only what could be refuted — is exactly what keeps the second honest.

The working plan that turns this direction into next steps — the two axes (education × disposition to the unknown), the friction obligation as an anti-monomania move for personas, the small-model architecture, and the day's experiments — is kept, with diagrams, in [`RECHERCHE.md`](RECHERCHE.md).

---

## Bibliography

**Perception, Gestalt, visual information**
- Wertheimer, M. (1923). *Untersuchungen zur Lehre von der Gestalt II.*
- Koffka, K. (1935). *Principles of Gestalt Psychology.*
- Hochberg, J. & McAlister, E. (1953). *A quantitative approach to figural goodness.* J. Exp. Psychol.
- von Helmholtz, H. (1867). *Handbuch der physiologischen Optik.*
- Attneave, F. (1954). *Some informational aspects of visual perception.* Psychol. Review.
- Marr, D. (1982). *Vision.*
- Biederman, I. (1987). *Recognition-by-components.* Psychol. Review.
- Friston, K. (2010). *The free-energy principle.* Nature Rev. Neuroscience.
- Kanwisher, McDermott & Chun (1997). *The fusiform face area.* J. Neuroscience.
- Liu, J. et al. (2014). *Seeing Jesus in toast* (face pareidolia). Cortex.
- Conrad, K. (1958). *Die beginnende Schizophrenie* (apophenia).

**Projection, reader-response, personas**
- Iser, W. (1974). *The Implied Reader.*
- Fish, S. (1980). *Is There a Text in This Class?* (interpretive communities).
- (Rorschach 1921 and the Barnum-Forer effect 1949, below, belong here too: the projective stimulus, and its epistemic hazard.)

**Multistability, pareidolia, Rorschach**
- Rorschach, H. (1921). *Psychodiagnostik.*
- Jastrow, J. (1899); Wittgenstein, L. (1953). *Philosophical Investigations* (seeing-as).
- Panagopoulou, A., Melkin, C. & Callison-Burch, C. (2024). *Evaluating Vision-Language Models on Bistable Images.* CMCL @ ACL 2024. arXiv:2405.19423 — https://aclanthology.org/2024.cmcl-1.2/
- *Human Shadows in Machine Minds: Quantitative Study Interpreting AI Responses to the Rorschach Test.* JMIR Mental Health, 2026;e88186 — https://mental.jmir.org/2026/1/e88186 (PMC13168847)
- Hamilton, M. et al. (2024). *Seeing Faces in Things: A Model and Dataset for Pareidolia.* ECCV 2024, MIT. arXiv:2409.16143 — https://arxiv.org/abs/2409.16143 · code: https://github.com/mhamilton723/FacesInThings
- *Diamonds in the Sky: Pareidolic Animals in Clouds.* arXiv:2606.01361 (directly on the project’s matter — animals in clouds).

**Decision, epistemology**
- Green, D. & Swets, J. (1966). *Signal Detection Theory and Psychophysics.*
- Popper, K. (1934). *Logik der Forschung.*
- Forer, B. (1949). *The fallacy of personal validation* (Barnum effect).

**Formal aesthetics**
- Leonardo da Vinci. *Trattato della pittura* (c. 1500).
- Cozens, A. (1785). *A New Method of Assisting the Invention…*
- Kandinsky, W. (1911) *Concerning the Spiritual in Art*; (1926) *Point and Line to Plane.*
- Klee, P. (1925). *Pedagogical Sketchbook.*
- Arnheim, R. (1954). *Art and Visual Perception.*
- Bin, Y. et al. (2024). *GalleryGPT: Analyzing Paintings with Large Multimodal Models* (PaintingForm dataset, ~19k paintings / ~50k analyses). ACM MM 2024. doi:10.1145/3664647.3681656; arXiv:2408.00491 — https://github.com/steven640pixel/GalleryGPT

**Image processing**
- Otsu, N. (1979). *A threshold selection method from gray-level histograms.* IEEE TSMC.
- Canny, J. (1986). *A computational approach to edge detection.* IEEE PAMI.
- Lloyd, S. (1982). *Least squares quantization in PCM*; MacQueen (1967).
- Hurvich, L. & Jameson, D. (1957). *An opponent-process theory of color vision.* Psychol. Review.
- Shannon, C. (1948). *A mathematical theory of communication.* Bell System Tech. J.
- Levenshtein, V. (1966). *Binary codes capable of correcting deletions, insertions, and reversals.*

**Machine learning**
- McClelland, McNaughton & O’Reilly (1995). *Complementary learning systems.* Psychol. Review.
- Bradley, R. & Terry, M. (1952). *Rank analysis of incomplete block designs.* Biometrika.
- Christiano, P. et al. (2017). *Deep RL from human preferences.* NeurIPS.
- Ouyang, L. et al. (2022). *Training language models to follow instructions* (InstructGPT).
- Rafailov, R. et al. (2023). *Direct Preference Optimization.* NeurIPS.
- Hu, E. et al. (2022). *LoRA: Low-Rank Adaptation of Large Language Models.* ICLR.
- Dettmers, T. et al. (2023). *QLoRA.* NeurIPS.
- Ha, D. & Schmidhuber, J. (2018). *World Models.* NeurIPS.
- Hafner, D. et al. (2020). *Dream to Control: Learning Behaviors by Latent Imagination* (Dreamer). ICLR.
- LeCun, Y. (2022). *A Path Towards Autonomous Machine Intelligence* (JEPA, position paper).
- Radford, A. et al. (2021). *Learning Transferable Visual Models (CLIP).* ICML.
- Zhai, X. et al. (2023). *Sigmoid Loss for Language-Image Pre-training (SigLIP).* ICCV.
- Qwen Team (2024–2025). *Qwen2.5-VL.*

---

*Dates and attributions point to the founding works; the four references marked
“project ref.” (FacesInThings, Bistable Images, Rorschach × AI,
GalleryGPT/PaintingForm) are the direct empirical anchors of Nephélé, detailed in
`CLAUDE.md`.*
