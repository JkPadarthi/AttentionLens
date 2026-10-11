// review1/generate_pipeline_deck.js
// AttentionLens — Whole Pipeline deck (M1 → M8, end-to-end)
// Style-matched to generate_deck.js so the two decks feel like siblings.

const pptxgen = require("pptxgenjs");
const path = require("path");

const out = path.join(__dirname, "AttentionLens-Pipeline.pptx");

// ── palette (same as Review 1 deck) ──────────────────────────────
const DARK = "14142B";     // midnight indigo
const INK = "2E2A72";      // indigo
const ACCENT = "00C9A7";   // lens teal
const CYAN = "7CE0E3";
const RED = "D9534F";
const GREEN = "006B59";
const LIGHT = "F7F7FC";    // light bg
const CARD = "FFFFFF";
const SOFT = "E6F7F4";     // teal wash
const SOFT2 = "E3E4F0";    // neutral border
const TEXT = "1F2340";
const MUTE = "5A5F7A";
const B9 = "B9BCE0";       // dark-bg muted

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE"; // 13.3 × 7.5
pptx.author = "Jaswanth Krishna Padarthi";
pptx.title = "AttentionLens — The Whole Pipeline";
pptx.subject = "Review 1 — M1 delivered, M2–M8 roadmap";

const FONT_H = "Cambria";
const FONT_B = "Calibri";

// ── helpers ──────────────────────────────────────────────────────
function title(pp, text, sub) {
  pp.addText(text, { x: 0.6, y: 0.35, w: 12.1, h: 0.85, fontFace: FONT_H, fontSize: 30, bold: true, color: TEXT, align: "left", margin: 0 });
  if (sub) pp.addText(sub, { x: 0.62, y: 1.18, w: 12.0, h: 0.45, fontFace: FONT_B, fontSize: 15, color: MUTE, margin: 0 });
}

function sectionChip(pp, n, label) {
  pp.addShape(pptx.ShapeType.ellipse, { x: 0.62, y: 0.45, w: 0.5, h: 0.5, fill: { color: ACCENT }, line: { type: "none" } });
  pp.addText(n, { x: 0.62, y: 0.45, w: 0.5, h: 0.5, fontFace: FONT_B, fontSize: 14, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
  pp.addText(label, { x: 1.2, y: 0.5, w: 8, h: 0.45, fontFace: FONT_B, fontSize: 12, bold: true, color: MUTE, margin: 0, valign: "middle" });
}

function arrow(pp, x, y, w, color = MUTE) {
  pp.addText("→", { x, y, w, h: 0.5, fontFace: FONT_B, fontSize: 18, bold: true, color, align: "center", valign: "middle", margin: 0 });
}

function pill(pp, x, y, w, h, text, fill, fg = "FFFFFF", fs = 11) {
  pp.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { type: "none" } });
  pp.addText(text, { x, y, w, h, fontFace: FONT_B, fontSize: fs, bold: true, color: fg, align: "center", valign: "middle", margin: 0 });
}

// ============================================================ SLIDE 1 — TITLE
{
  const s = pptx.addSlide();
  s.background = { color: DARK };
  s.addShape(pptx.ShapeType.rect, { x: 9.6, y: 0, w: 3.7, h: 7.5, fill: { color: "1B1B3A" }, line: { type: "none" } });
  s.addShape(pptx.ShapeType.ellipse, { x: 10.2, y: 2.3, w: 2.5, h: 2.5, fill: { color: INK }, line: { color: CYAN, width: 3 } });
  s.addShape(pptx.ShapeType.ellipse, { x: 11.15, y: 3.25, w: 0.6, h: 0.6, fill: { color: ACCENT }, line: { type: "none" } });
  s.addText("AttentionLens", { x: 0.9, y: 1.7, w: 8.4, h: 1.3, fontFace: FONT_H, fontSize: 54, bold: true, color: "FFFFFF", margin: 0 });
  s.addText("The Whole Pipeline — from image to verdict", { x: 0.92, y: 3.0, w: 8.2, h: 1.0, fontFace: FONT_B, fontSize: 19, color: CYAN, margin: 0 });
  s.addText("Project Review 1  ·  B.Tech CSE (AI & ML), VIT", { x: 0.92, y: 5.4, w: 8.2, h: 0.5, fontFace: FONT_B, fontSize: 15, color: B9, margin: 0 });
  s.addText("Jaswanth Krishna Padarthi", { x: 0.92, y: 5.9, w: 8.2, h: 0.5, fontFace: FONT_B, fontSize: 15, bold: true, color: "FFFFFF", margin: 0 });
  s.addText("M1 delivered · M2–M8 roadmapped · 15 slides", { x: 0.92, y: 6.5, w: 8.2, h: 0.5, fontFace: FONT_B, fontSize: 12, color: ACCENT, margin: 0 });
  s.addNotes("This deck is the whole-pipeline companion to the M1 gate deck. The M1 gate deck proves one milestone; this deck shows where every milestone fits, what each stage emits, and why the loop closes on a verdict rather than a heatmap.");
}

// ============================================================ SLIDE 2 — AGENDA
{
  const s = pptx.addSlide();
  s.background = { color: LIGHT };
  title(s, "Agenda", "From a raw image to a bias verdict — the road map");
  const items = [
    ["01", "Problem & Motivation",         "Why vision models need a debugger, not just explanations"],
    ["02", "Design — Dual-View Schema",     "One LayerMap contract, two views, CNN ⇄ ViT"],
    ["03", "The Pipeline — 6 Stages",       "Preprocess → Infer → Extract → Metrics → Intervene → Screen"],
    ["04", "Stage-by-Stage Detail",         "What each stage emits and what it costs"],
    ["05", "Milestones M1–M8",              "What's delivered, what's next, and why"],
    ["06", "Validation Experiments",        "Planted-bias (M7) + ObjectNet (M8) — both required"],
    ["07", "Novelty & Honest Limits",       "Tool-not-method · dual-view · auto-screening · known failures"],
    ["08", "Next Steps",                    "M2 ViT extractor — the next gate"],
  ];
  let ay = 1.7;
  items.forEach(([n, t, d]) => {
    s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: ay - 0.1, w: 11.9, h: 0.6, rectRadius: 0.1, fill: { color: CARD }, line: { color: SOFT2, width: 1 } });
    s.addText(n, { x: 0.95, y: ay - 0.05, w: 0.9, h: 0.5, fontFace: FONT_B, fontSize: 18, bold: true, color: ACCENT, margin: 0, valign: "middle" });
    s.addText(t, { x: 1.95, y: ay - 0.05, w: 4.1, h: 0.5, fontFace: FONT_B, fontSize: 15, bold: true, color: TEXT, margin: 0, valign: "middle" });
    s.addText(d, { x: 6.2, y: ay - 0.05, w: 6.2, h: 0.5, fontFace: FONT_B, fontSize: 12.5, color: MUTE, margin: 0, valign: "middle" });
    ay += 0.7;
  });
  s.addNotes("Eight sections. The spine of the talk is slide 5 — the 6-stage pipeline. Everything else expands one of those stages or frames why the stages exist.");
}

// ============================================================ SLIDE 3 — PROBLEM
{
  const s = pptx.addSlide();
  s.background = { color: LIGHT };
  title(s, "Problem & Motivation", "Explanations exist — but they don't talk to each other");
  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 1.8, w: 5.9, h: 2.7, rectRadius: 0.12, fill: { color: CARD }, line: { color: SOFT2, width: 1 } });
  s.addText("The field is fragmented", { x: 1.0, y: 2.0, w: 5.3, h: 0.5, fontFace: FONT_H, fontSize: 19, bold: true, color: INK, margin: 0 });
  s.addText([
    { text: "Attention maps (ViT) answer 'what does the model look at' — but they are class-agnostic.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Attribution maps (Grad-CAM) answer 'what drove this decision' — class-specific.",        options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "No shared schema: comparing two architectures or two views today means bespoke glue.", options: { bullet: true } },
  ], { x: 1.0, y: 2.6, w: 5.4, h: 1.8, fontFace: FONT_B, fontSize: 13.5, color: TEXT, margin: 0, lineSpacing: 14 });

  s.addShape(pptx.ShapeType.roundRect, { x: 6.8, y: 1.8, w: 5.9, h: 2.7, rectRadius: 0.12, fill: { color: CARD }, line: { color: SOFT2, width: 1 } });
  s.addText("Bias goes unnoticed", { x: 7.1, y: 2.0, w: 5.3, h: 0.5, fontFace: FONT_H, fontSize: 19, bold: true, color: INK, margin: 0 });
  s.addText([
    { text: "Spurious correlations (backgrounds, textures, artifacts) silently inflate accuracy.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Finding them today is manual, ad-hoc, and rarely automated end-to-end.",              options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Engineers need a verdict — not another heatmap to eyeball.",                            options: { bullet: true } },
  ], { x: 7.1, y: 2.6, w: 5.4, h: 1.8, fontFace: FONT_B, fontSize: 13.5, color: TEXT, margin: 0, lineSpacing: 14 });

  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 4.8, w: 12.0, h: 1.9, rectRadius: 0.12, fill: { color: SOFT }, line: { type: "none" } });
  s.addText("One framework, two jobs", { x: 1.0, y: 5.0, w: 4.0, h: 0.5, fontFace: FONT_H, fontSize: 18, bold: true, color: GREEN, margin: 0 });
  s.addText("① A unified CNN ⇄ ViT abstraction — every layer yields a standard LayerMap (native attention + class-conditioned relevance).   ② An automated bias-screening layer — attention-quality metrics and intervention experiments that produce a verdict, in the tradition of SHAP / Captum as a deployable tool.", { x: 1.0, y: 5.55, w: 11.4, h: 1.05, fontFace: FONT_B, fontSize: 14, color: "1F3D36", margin: 0 });

  s.addNotes("Two gaps: fragmentation (no shared schema between attention and attribution, CNN and ViT) and discovery (bias found manually). AttentionLens solves both with one abstraction plus automated screening verdicts — the novelty anchor is the combination, not a new XAI method.");
}

// ============================================================ SLIDE 4 — DUAL-VIEW SCHEMA
{
  const s = pptx.addSlide();
  s.background = { color: LIGHT };
  title(s, "Design — the Dual-View LayerMap", "Every layer, two views, one schema");
  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 1.85, w: 5.95, h: 2.7, rectRadius: 0.12, fill: { color: CARD }, line: { color: SOFT2, width: 1 } });
  s.addText("Native view — what the model attends to", { x: 1.0, y: 2.0, w: 5.3, h: 0.5, fontFace: FONT_H, fontSize: 17, bold: true, color: INK, margin: 0 });
  s.addText([
    { text: "Mechanism's own signal (CNN channel-mean, ViT attention rollout)", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Class-agnostic — broad by design, high entropy",                     options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Answers 'where does the mechanism focus?'",                          options: { bullet: true } },
  ], { x: 1.0, y: 2.6, w: 5.4, h: 1.9, fontFace: FONT_B, fontSize: 13.5, color: TEXT, margin: 0, lineSpacing: 14 });

  s.addShape(pptx.ShapeType.roundRect, { x: 6.8, y: 1.85, w: 5.95, h: 2.7, rectRadius: 0.12, fill: { color: CARD }, line: { color: SOFT2, width: 1 } });
  s.addText("Class-conditioned view — why the model decided", { x: 7.1, y: 2.0, w: 5.3, h: 0.5, fontFace: FONT_H, fontSize: 17, bold: true, color: INK, margin: 0 });
  s.addText([
    { text: "Decision evidence (Captum LayerGradCam; class-weighted rollout / LRP / token attr for ViT)", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Class-specific — sharp, ReLU'd, evidence for one class", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Screening verdicts always rest on this view (the comparable one)", options: { bullet: true } },
  ], { x: 7.1, y: 2.6, w: 5.4, h: 1.9, fontFace: FONT_B, fontSize: 13.5, color: TEXT, margin: 0, lineSpacing: 14 });

  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 4.8, w: 12.0, h: 1.9, rectRadius: 0.12, fill: { color: SOFT }, line: { type: "none" } });
  s.addText("Why two views?  Naive comparison is meaningless.", { x: 1.0, y: 4.95, w: 11.4, h: 0.5, fontFace: FONT_H, fontSize: 17, bold: true, color: GREEN, margin: 0 });
  s.addText("ViT attention and Grad-CAM are not the same kind of thing — the first is class-agnostic info flow, the second is class-specific decision evidence. Putting both behind one LayerMap dataclass makes CNN � ViT comparison honest by construction. Verified by tests/test_schema.py on Arjun.", { x: 1.0, y: 5.5, w: 11.4, h: 1.15, fontFace: FONT_B, fontSize: 14, color: "1F3D36", margin: 0 });

  s.addNotes("The core architectural decision: never conflate the two views. Native maps capture the mechanism; class-conditioned maps capture decision evidence. Both land in the same LayerMap dataclass so downstream metrics and screening treat them identically.");
}

// ============================================================ SLIDE 5 — THE PIPELINE (THE SPINE)
{
  const s = pptx.addSlide();
  s.background = { color: LIGHT };
  title(s, "The Pipeline — six stages, one loop", "Each stage emits; the loop closes on a verdict");
  // Stage chain
  const stages = [
    ["1", "Image",          "224×224 RGB",         CYAN,    "FFFFFF"],
    ["2", "Inference",      "ResNet-50 · ViT-B/16", ACCENT,  "FFFFFF"],
    ["3", "Dual-view",      "native + class-cond", RED,     "FFFFFF"],
    ["4", "Metrics",        "entropy · locality ·", INK,    "FFFFFF"],
    ["5", "Intervention",   "mask → re-run",       "5A5F7A", "FFFFFF"],
    ["6", "Verdict",        "screening report",    GREEN,   "FFFFFF"],
  ];
  let sx = 0.45, sw = 2.0, sgap = 0.12;
  stages.forEach(([n, t, d, c, fg], i) => {
    s.addShape(pptx.ShapeType.roundRect, { x: sx, y: 2.0, w: sw, h: 1.4, rectRadius: 0.1, fill: { color: c }, line: { type: "none" } });
    s.addText("STAGE " + n, { x: sx, y: 2.1, w: sw, h: 0.3, fontFace: FONT_B, fontSize: 10, bold: true, color: fg, align: "center", margin: 0 });
    s.addText(t, { x: sx, y: 2.4, w: sw, h: 0.5, fontFace: FONT_H, fontSize: 17, bold: true, color: fg, align: "center", margin: 0 });
    s.addText(d, { x: sx, y: 2.92, w: sw, h: 0.4, fontFace: FONT_B, fontSize: 10, color: fg, align: "center", margin: 0 });
    if (i < stages.length - 1) arrow(s, sx + sw + 0.005, 2.55, sgap + 0.04);
    sx += sw + sgap + 0.07;
  });

  // Loop-back arrow caption
  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 3.7, w: 12.0, h: 0.55, rectRadius: 0.08, fill: { color: "FFF6E6" }, line: { color: "E5C07B", width: 1 } });
  s.addText("Stage 5 (intervention) can re-enter Stage 3 with a masked image → evidence is causal, not correlative.", { x: 0.85, y: 3.78, w: 11.7, h: 0.4, fontFace: FONT_B, fontSize: 12.5, color: "6B4A12", margin: 0 });

  // Bottom — what each stage produces
  const emit = [
    ["Stage 1", "Tensor [1,3,224,224] fp32 (reversible to pixels)",      CARD, TEXT],
    ["Stage 2", "(label, class_idx) — class for conditioning",           CARD, TEXT],
    ["Stage 3", "LayerMap × (N layers × 2 views) — the unified contract", CARD, TEXT],
    ["Stage 4", "per-map metrics (object rel., entropy, part align., …)", CARD, TEXT],
    ["Stage 5", "InterventionResult (region, pred_before, pred_after)",   CARD, TEXT],
    ["Stage 6", "Verdict + evidence links + report",                       SOFT, GREEN],
  ];
  let ey = 4.45;
  emit.forEach(([k, v, fill, fc]) => {
    s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: ey, w: 12.0, h: 0.45, rectRadius: 0.06, fill: { color: fill }, line: { color: SOFT2, width: 1 } });
    s.addText(k, { x: 0.9, y: ey + 0.05, w: 1.4, h: 0.35, fontFace: FONT_B, fontSize: 11.5, bold: true, color: fc, margin: 0, valign: "middle" });
    s.addText(v, { x: 2.4, y: ey + 0.05, w: 10.2, h: 0.35, fontFace: FONT_B, fontSize: 12, color: TEXT, margin: 0, valign: "middle" });
    ey += 0.5;
  });
  s.addNotes("This is the spine of the whole project. Every milestone plugs into one of these six stages. Stages 1–3 are done in M1 (verified end-to-end on the Samoyed). Stages 4–6 are the forward path of the roadmap. The loop arrow is what turns heatmaps into verdicts.");
}

// ============================================================ SLIDE 6 — STAGE 1 PREPROCESSING
{
  const s = pptx.addSlide();
  s.background = { color: LIGHT };
  sectionChip(s, "01", "Preprocessing");
  s.addText("Stage 1 — Preprocessing", { x: 0.6, y: 1.0, w: 12.1, h: 0.7, fontFace: FONT_H, fontSize: 26, bold: true, color: TEXT, margin: 0 });
  s.addText("Resize → /255 → ImageNet normalize → tensor.  Reversible for overlay.", { x: 0.62, y: 1.65, w: 12.0, h: 0.4, fontFace: FONT_B, fontSize: 13, color: MUTE, margin: 0 });

  const pipe = ["load RGB", "resize 224×224", "÷255 → [0,1]", "−mean ÷std", "[1,3,224,224] fp32"];
  let px = 0.7;
  pipe.forEach((t, i) => {
    s.addShape(pptx.ShapeType.roundRect, { x: px, y: 2.3, w: 2.0, h: 0.8, rectRadius: 0.08, fill: { color: i === 4 ? INK : CARD }, line: { color: SOFT2, width: 1 } });
    s.addText(t, { x: px, y: 2.45, w: 2.0, h: 0.5, fontFace: FONT_B, fontSize: 11.5, bold: true, color: i === 4 ? "FFFFFF" : TEXT, align: "center", margin: 0 });
    if (i < 4) arrow(s, px + 2.0, 2.45, 0.32);
    px += 2.32;
  });

  // measured stats — raw
  s.addText("Raw pixel stats (0–1)", { x: 0.8, y: 3.4, w: 5.4, h: 0.45, fontFace: FONT_H, fontSize: 15, bold: true, color: INK, margin: 0 });
  const raw = [["R", "0.388 ± 0.320"], ["G", "0.431 ± 0.295"], ["B", "0.368 ± 0.337"]];
  raw.forEach(([c, v], i) => {
    s.addShape(pptx.ShapeType.roundRect, { x: 0.8 + i * 1.9, y: 3.85, w: 1.7, h: 0.8, rectRadius: 0.08, fill: { color: CARD }, line: { color: SOFT2, width: 1 } });
    s.addText(c, { x: 0.8 + i * 1.9, y: 3.9, w: 1.7, h: 0.3, fontFace: FONT_B, fontSize: 12, bold: true, color: MUTE, align: "center", margin: 0 });
    s.addText(v, { x: 0.8 + i * 1.9 + 0.05, y: 4.2, w: 1.6, h: 0.35, fontFace: FONT_B, fontSize: 9, bold: true, color: TEXT, align: "center", margin: 0 });
  });
  s.addText("Normalized tensor stats", { x: 5.0, y: 3.4, w: 5.6, h: 0.45, fontFace: FONT_H, fontSize: 15, bold: true, color: INK, margin: 0 });
  const norm = [["R", "-0.421 ± 1.398"], ["G", "-0.110 ± 1.316"], ["B", "-0.170 ± 1.498"]];
  norm.forEach(([c, v], i) => {
    s.addShape(pptx.ShapeType.roundRect, { x: 5.0 + i * 1.9, y: 3.85, w: 1.7, h: 0.8, rectRadius: 0.08, fill: { color: CARD }, line: { color: SOFT2, width: 1 } });
    s.addText(c, { x: 5.0 + i * 1.9, y: 3.9, w: 1.7, h: 0.3, fontFace: FONT_B, fontSize: 12, bold: true, color: MUTE, align: "center", margin: 0 });
    s.addText(v, { x: 5.0 + i * 1.9 + 0.05, y: 4.2, w: 1.6, h: 0.35, fontFace: FONT_B, fontSize: 9, bold: true, color: TEXT, align: "center", margin: 0 });
  });

  s.addShape(pptx.ShapeType.roundRect, { x: 0.8, y: 5.0, w: 11.6, h: 1.7, rectRadius: 0.12, fill: { color: SOFT }, line: { type: "none" } });
  s.addText([
    { text: "Design point: reversible — tensor_to_image() inverts every step exactly, so heatmaps overlay on real pixels.", options: { bullet: true, breakLine: true, paraSpaceAfter: 4 } },
    { text: "Stats above measured on Arjun — Python 3.12.10, torch 2.13.0+cpu.", options: { bullet: true, breakLine: true, paraSpaceAfter: 4 } },
    { text: "Tests: test_preprocess.py covers round-trip equivalence (hermetic — no downloads).", options: { bullet: true } },
  ], { x: 1.05, y: 5.15, w: 11.1, h: 1.45, fontFace: FONT_B, fontSize: 12.5, color: "1F3D36", margin: 0, lineSpacing: 14 });

  s.addNotes("Stage 1 is boring on purpose. It's a contract: any image, any size, into a normalized [1,3,224,224] float32 tensor on the device — and back. No information loss, no surprises downstream.");
}

// ============================================================ SLIDE 7 — STAGE 2 INFERENCE
{
  const s = pptx.addSlide();
  s.background = { color: LIGHT };
  sectionChip(s, "02", "Inference");
  s.addText("Stage 2 — Inference", { x: 0.6, y: 1.0, w: 12.1, h: 0.7, fontFace: FONT_H, fontSize: 26, bold: true, color: TEXT, margin: 0 });
  s.addText("One forward pass per model — yields the class that conditions every class-conditioned map.", { x: 0.62, y: 1.65, w: 12.0, h: 0.4, fontFace: FONT_B, fontSize: 13, color: MUTE, margin: 0 });

  const models = [
    { name: "ResNet-50", code: "resnet50(weights=IMAGENET1K_V2)", trained: "ImageNet-1K V2 (76% top-1)", purpose: "CNN baseline", status: "✅ M1 — wired", fill: INK },
    { name: "ViT-B/16", code: "timm.create_model('vit_base_patch16_224', pretrained=True)", trained: "ImageNet-1K", purpose: "Transformer comparison", status: "⏳ M2 — planned", fill: ACCENT },
  ];
  let my = 2.3;
  models.forEach((m) => {
    s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: my, w: 12.0, h: 1.55, rectRadius: 0.12, fill: { color: CARD }, line: { color: SOFT2, width: 1 } });
    s.addShape(pptx.ShapeType.rect, { x: 0.7, y: my, w: 0.15, h: 1.55, fill: { color: m.fill }, line: { type: "none" } });
    s.addText(m.name, { x: 1.0, y: my + 0.12, w: 3.0, h: 0.45, fontFace: FONT_H, fontSize: 20, bold: true, color: INK, margin: 0 });
    s.addText(m.status, { x: 1.0, y: my + 0.6, w: 3.0, h: 0.4, fontFace: FONT_B, fontSize: 12.5, bold: true, color: m.fill, margin: 0 });
    s.addText(m.code, { x: 4.2, y: my + 0.2, w: 8.7, h: 0.45, fontFace: "Consolas", fontSize: 10.5, color: TEXT, margin: 0, valign: "middle" });
    s.addText("Weights: " + m.trained, { x: 4.2, y: my + 0.75, w: 8.3, h: 0.35, fontFace: FONT_B, fontSize: 12, color: MUTE, margin: 0 });
    s.addText("Role: " + m.purpose, { x: 4.2, y: my + 1.1, w: 8.3, h: 0.35, fontFace: FONT_B, fontSize: 12, color: MUTE, margin: 0 });
    my += 1.7;
  });

  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 5.85, w: 12.0, h: 0.95, rectRadius: 0.12, fill: { color: SOFT }, line: { type: "none" } });
  s.addText("Output contract:  (label_str, class_idx)  →  becomes the conditioning target for every class-conditioned map downstream.  Labels come from weights.meta[\"categories\"] — a dict on torchvision 0.28 (gotcha: never getattr(meta, \"categories\")).", { x: 1.0, y: 6.0, w: 11.4, h: 0.7, fontFace: FONT_B, fontSize: 12.5, color: "1F3D36", margin: 0 });

  s.addNotes("Both models return the same shape contract: (label_str, class_idx). That label becomes the conditioning class for every Grad-CAM / class-weighted-rollout / token-attr call. One bug surfaced and fixed in M1: ImageNet weights.meta is a dict on this torchvision — use meta.get('categories'), not getattr.");
}

// ============================================================ SLIDE 8 — STAGE 3 DUAL-VIEW EXTRACTION
{
  const s = pptx.addSlide();
  s.background = { color: LIGHT };
  sectionChip(s, "03", "Dual-view extraction");
  s.addText("Stage 3 — Dual-view extraction", { x: 0.6, y: 1.0, w: 12.1, h: 0.7, fontFace: FONT_H, fontSize: 26, bold: true, color: TEXT, margin: 0 });
  s.addText("Four probe points × two views — every probe emits a native and a class-conditioned LayerMap.", { x: 0.62, y: 1.65, w: 12.0, h: 0.4, fontFace: FONT_B, fontSize: 13, color: MUTE, margin: 0 });

  // probe blocks
  const blocks = [
    ["layer1.2.conv3", "256 ch",  "edges / textures"],
    ["layer2.3.conv3", "512 ch",  "patterns / parts"],
    ["layer3.5.conv3", "1024 ch", "object parts"],
    ["layer4.2.conv3", "2048 ch", "object semantics"],
  ];
  let bx = 0.7;
  blocks.forEach(([l, c, d]) => {
    s.addShape(pptx.ShapeType.roundRect, { x: bx, y: 2.3, w: 2.9, h: 1.5, rectRadius: 0.1, fill: { color: CARD }, line: { color: SOFT2, width: 1 } });
    s.addText(l, { x: bx, y: 2.42, w: 2.9, h: 0.4, fontFace: "Consolas", fontSize: 12, bold: true, color: INK, align: "center", margin: 0 });
    s.addText(c, { x: bx, y: 2.82, w: 2.9, h: 0.35, fontFace: FONT_B, fontSize: 13, bold: true, color: ACCENT, align: "center", margin: 0 });
    s.addText(d, { x: bx, y: 3.17, w: 2.9, h: 0.5, fontFace: FONT_B, fontSize: 11, color: MUTE, align: "center", margin: 0 });
    bx += 3.05;
  });

  // two view cards
  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 4.05, w: 5.95, h: 2.2, rectRadius: 0.12, fill: { color: CARD }, line: { color: SOFT2, width: 1 } });
  s.addText("Native (mechanism)", { x: 1.0, y: 4.2, w: 5.3, h: 0.4, fontFace: FONT_H, fontSize: 16, bold: true, color: INK, margin: 0 });
  s.addText([
    { text: "Forward hook on the layer → activations[B,C,H,W]", options: { bullet: true, breakLine: true, paraSpaceAfter: 3 } },
    { text: "mean over channels → bilinear upsample → normalize [0,1]", options: { bullet: true, breakLine: true, paraSpaceAfter: 3 } },
    { text: "Cost: one forward pass total (hooks capture all layers)", options: { bullet: true, breakLine: true, paraSpaceAfter: 3 } },
    { text: "Class-agnostic — broad by nature", options: { bullet: true } },
  ], { x: 1.0, y: 4.65, w: 5.4, h: 1.5, fontFace: FONT_B, fontSize: 12, color: TEXT, margin: 0, lineSpacing: 14 });

  s.addShape(pptx.ShapeType.roundRect, { x: 6.8, y: 4.05, w: 5.95, h: 2.2, rectRadius: 0.12, fill: { color: CARD }, line: { color: SOFT2, width: 1 } });
  s.addText("Class-conditioned (evidence)", { x: 7.1, y: 4.2, w: 5.3, h: 0.4, fontFace: FONT_H, fontSize: 16, bold: true, color: INK, margin: 0 });
  s.addText([
    { text: "Captum LayerGradCam on the same conv, target = predicted class", options: { bullet: true, breakLine: true, paraSpaceAfter: 3 } },
    { text: "ReLU → bilinear upsample → normalize [0,1]", options: { bullet: true, breakLine: true, paraSpaceAfter: 3 } },
    { text: "Cost: one attribution per layer", options: { bullet: true, breakLine: true, paraSpaceAfter: 3 } },
    { text: "Honest failure: all-zero map ⇒ 'no positive evidence at this layer'", options: { bullet: true } },
  ], { x: 7.1, y: 4.65, w: 5.4, h: 1.5, fontFace: FONT_B, fontSize: 12, color: TEXT, margin: 0, lineSpacing: 14 });

  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 6.4, w: 12.0, h: 0.5, rectRadius: 0.08, fill: { color: SOFT }, line: { type: "none" } });
  s.addText("Emits:  8 LayerMaps per image (4 blocks × 2 views)  —  the contract every downstream stage reads.", { x: 0.9, y: 6.45, w: 11.6, h: 0.4, fontFace: FONT_B, fontSize: 12.5, bold: true, color: GREEN, margin: 0, valign: "middle" });

  s.addNotes("Four probe points chosen deliberately: the last conv of each bottleneck block, spanning 256→2048 channels and texture→semantics. Both views derive from the same probe points, so cross-view comparison is apples-to-apples. The layer-2 zero-map on the Samoyed is honest data — a degenerate explanation surfaced by the tool itself, which is exactly the failure mode an explainability debugger should expose.");
}

// ============================================================ SLIDE 9 — STAGE 4 METRICS
{
  const s = pptx.addSlide();
  s.background = { color: LIGHT };
  sectionChip(s, "04", "Metrics");
  s.addText("Stage 4 — Metrics", { x: 0.6, y: 1.0, w: 12.1, h: 0.7, fontFace: FONT_H, fontSize: 26, bold: true, color: TEXT, margin: 0 });
  s.addText("Numbers, not vibes — measured against CUB-200 bboxes + part keypoints.", { x: 0.62, y: 1.65, w: 12.0, h: 0.4, fontFace: FONT_B, fontSize: 13, color: MUTE, margin: 0 });

  const mets = [
    ["Object relevance share", "fraction of attention mass inside the object's bbox",        "Did the model look at the object or somewhere else?"],
    ["Part alignment",         "attention mass over annotated keypoints (beak, eye, wing)", "Did it find the right part of the object?"],
    ["Focus entropy",          "spread of the attention map",                                  "Broad background-y vs sharp object-y"],
    ["Background / object sensitivity", "prediction shift when the background is masked",    "How much does it lean on the background?"],
  ];
  let my = 2.3;
  mets.forEach(([n, f, q]) => {
    s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: my, w: 12.0, h: 0.95, rectRadius: 0.1, fill: { color: CARD }, line: { color: SOFT2, width: 1 } });
    s.addText(n, { x: 0.95, y: my + 0.1, w: 3.2, h: 0.4, fontFace: FONT_H, fontSize: 14, bold: true, color: INK, margin: 0 });
    s.addText(f, { x: 4.1, y: my + 0.12, w: 6.5, h: 0.75, fontFace: "Consolas", fontSize: 10, color: TEXT, margin: 0 });
    s.addText(q, { x: 10.65, y: my + 0.1, w: 2.0, h: 0.75, fontFace: FONT_B, fontSize: 10, italic: true, color: MUTE, margin: 0 });
    my += 1.05;
  });

  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 6.6, w: 12.0, h: 0.55, rectRadius: 0.08, fill: { color: SOFT }, line: { type: "none" } });
  s.addText("Why CUB-200?  Bounding boxes + part keypoints — metrics measurable against annotations, not eyeballs.  DECISIONS §4.", { x: 0.9, y: 6.65, w: 11.6, h: 0.4, fontFace: FONT_B, fontSize: 12.5, bold: true, color: GREEN, margin: 0, valign: "middle" });

  s.addNotes("Stage 4 is where 'looks like' becomes 'is'. Each metric has a measurement protocol: object bbox overlap, keypoint proximity, entropy of the map, and prediction delta under masking. Without ground truth, these would be vibes — that's why the dataset choice is locked in (DECISIONS §4).");
}

// ============================================================ SLIDE 10 — STAGE 5 INTERVENTION
{
  const s = pptx.addSlide();
  s.background = { color: LIGHT };
  sectionChip(s, "05", "Intervention");
  s.addText("Stage 5 — Intervention loop", { x: 0.6, y: 1.0, w: 12.1, h: 0.7, fontFace: FONT_H, fontSize: 26, bold: true, color: TEXT, margin: 0 });
  s.addText("Mask a region → re-run → pred_before ≠ pred_after is causal proof, not correlation.", { x: 0.62, y: 1.65, w: 12.0, h: 0.4, fontFace: FONT_B, fontSize: 13, color: MUTE, margin: 0 });

  // flow
  const steps = [
    ["User clicks region", "UI (Gradio)",       ACCENT],
    ["Mask (x,y,w,h)",    "InterventionResult", INK],
    ["Re-run forward",    "model(x_masked)",    RED],
    ["Compare preds",     "before vs after",    GREEN],
  ];
  let sx = 0.7;
  steps.forEach(([t, d, c], i) => {
    s.addShape(pptx.ShapeType.roundRect, { x: sx, y: 2.3, w: 2.85, h: 1.4, rectRadius: 0.1, fill: { color: c }, line: { type: "none" } });
    s.addText(t, { x: sx, y: 2.5, w: 2.85, h: 0.5, fontFace: FONT_B, fontSize: 14, bold: true, color: "FFFFFF", align: "center", margin: 0 });
    s.addText(d, { x: sx, y: 3.05, w: 2.85, h: 0.5, fontFace: FONT_B, fontSize: 11, color: "EFF0FF", align: "center", margin: 0 });
    if (i < steps.length - 1) arrow(s, sx + 2.85, 2.85, 0.35, MUTE);
    sx += 3.18;
  });

  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 3.95, w: 12.0, h: 2.15, rectRadius: 0.12, fill: { color: CARD }, line: { color: SOFT2, width: 1 } });
  s.addText("InterventionResult — the evidence packet", { x: 1.0, y: 4.05, w: 11.4, h: 0.4, fontFace: FONT_H, fontSize: 16, bold: true, color: INK, margin: 0 });
  s.addText([
    { text: "region          (x, y, w, h) in input coordinates",   options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "pred_before     e.g.  \"Samoyed\"",                     options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "pred_after      e.g.  \"white wolf\"",                  options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "logit_delta     e.g.  -4.21  (how much the prediction moved)", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "metadata        (mask type, baseline confidence, ...)",  options: { bullet: true } },
  ], { x: 1.0, y: 4.5, w: 11.4, h: 1.5, fontFace: "Consolas", fontSize: 10.5, color: TEXT, margin: 0, lineSpacing: 16 });

  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 6.1, w: 12.0, h: 0.7, rectRadius: 0.08, fill: { color: "FFF6E6" }, line: { color: "E5C07B", width: 1 } });
  s.addText("M4 gate:  masking the head must flip bird predictions on CUB-200.  If it doesn't, the explanation was wrong — and the tool tells you so.", { x: 0.9, y: 6.2, w: 11.6, h: 0.5, fontFace: FONT_B, fontSize: 12.5, color: "6B4A12", margin: 0, valign: "middle" });

  s.addNotes("Stage 5 closes the causal arrow. Heatmaps are correlative; interventions are causal. The M4 gate is the falsification test for the whole framework: if masking the bird's head does not flip the prediction, then no heatmap on earth was showing real evidence — and the tool reports that honestly.");
}

// ============================================================ SLIDE 11 — STAGE 6 SCREENING
{
  const s = pptx.addSlide();
  s.background = { color: LIGHT };
  sectionChip(s, "06", "Screening");
  s.addText("Stage 6 — Screening & verdict", { x: 0.6, y: 1.0, w: 12.1, h: 0.7, fontFace: FONT_H, fontSize: 26, bold: true, color: TEXT, margin: 0 });
  s.addText("Aggregate per-image metrics → class-level verdicts → evidence-backed report.", { x: 0.62, y: 1.65, w: 12.0, h: 0.4, fontFace: FONT_B, fontSize: 13, color: MUTE, margin: 0 });

  // pipeline
  const steps = [
    ["Batch inspections", "(model, image) × N", CARD, TEXT],
    ["Per-image metrics", "4 metrics × 8 maps", CARD, TEXT],
    ["Class-level aggregation", "group by class", CARD, TEXT],
    ["Verdicts + evidence links", "bias flag · role profile · failure dx", SOFT, GREEN],
  ];
  let sx = 0.7;
  steps.forEach(([t, d, fill, fc], i) => {
    s.addShape(pptx.ShapeType.roundRect, { x: sx, y: 2.3, w: 2.85, h: 1.5, rectRadius: 0.1, fill: { color: fill }, line: { color: SOFT2, width: 1 } });
    s.addText(t, { x: sx, y: 2.45, w: 2.85, h: 0.5, fontFace: FONT_H, fontSize: 14, bold: true, color: fc, align: "center", margin: 0 });
    s.addText(d, { x: sx, y: 2.95, w: 2.85, h: 0.4, fontFace: FONT_B, fontSize: 11, color: fc, align: "center", margin: 0 });
    if (i < steps.length - 1) arrow(s, sx + 2.85, 2.85, 0.35, MUTE);
    sx += 3.18;
  });

  // verdict types
  const verdicts = [
    ["Class bias flag",      "'wolf' classified on snow, not wolf",   RED],
    ["Layer-role profile",   "'layer 1 = edges, layer 4 = object'",  INK],
    ["Failure diagnosis",    "'misclassified because attention hit the bg'", ACCENT],
  ];
  let vy = 4.1;
  verdicts.forEach(([n, e, c]) => {
    s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: vy, w: 12.0, h: 0.65, rectRadius: 0.08, fill: { color: CARD }, line: { color: SOFT2, width: 1 } });
    s.addShape(pptx.ShapeType.rect, { x: 0.7, y: vy, w: 0.15, h: 0.65, fill: { color: c }, line: { type: "none" } });
    s.addText(n, { x: 1.0, y: vy + 0.1, w: 3.0, h: 0.45, fontFace: FONT_H, fontSize: 14, bold: true, color: c, margin: 0, valign: "middle" });
    s.addText(e, { x: 4.1, y: vy + 0.12, w: 8.5, h: 0.45, fontFace: FONT_B, fontSize: 12.5, color: TEXT, margin: 0, valign: "middle" });
    vy += 0.75;
  });

  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 6.45, w: 12.0, h: 0.55, rectRadius: 0.08, fill: { color: SOFT }, line: { type: "none" } });
  s.addText("Verdicts always rest on class-conditioned evidence — the comparable, trustworthy view (DECISIONS §2).", { x: 0.9, y: 6.5, w: 11.6, h: 0.4, fontFace: FONT_B, fontSize: 12.5, bold: true, color: GREEN, margin: 0, valign: "middle" });

  s.addNotes("Stage 6 is what turns the tool from 'visualizer' into 'debugger'. Verdicts are not free-form text — each is a typed object with a confidence and evidence links back to the LayerMaps that triggered it.");
}

// ============================================================ SLIDE 12 — MILESTONES M1–M8
{
  const s = pptx.addSlide();
  s.background = { color: LIGHT };
  title(s, "Milestones M1–M8", "Each milestone ends with a verification gate");
  const rows = [
    ["M1", "Schema + ResNet-50 dual-view",                       "✅ done",     INK,    "CUB image → 8 LayerMaps, sane maps"],
    ["M2", "ViT-B/16 dual-view (rollout + class-cond)",          "⏳ next",    ACCENT, "Same image → same schema, dual-view complete"],
    ["M3", "Metrics (object rel · part align · entropy · sens)", "⏳",        ACCENT, "Numbers sane on known cases"],
    ["M4", "Intervention loop (mask → re-run)",                 "⏳",        ACCENT, "Masking the head flips bird preds on CUB-200"],
    ["M5", "Gradio UI (per-layer grid + click-to-mask)",        "⏳",        ACCENT, "End-to-end interactive session"],
    ["M6", "Screening engine (aggregate → verdicts)",           "⏳",        ACCENT, "Flags fire on a known-biased model"],
    ["M7", "Planted-bias (Waterbirds-style) on CUB-200",        "⏳",        ACCENT, "Screener catches the exact planted shortcut"],
    ["M8", "ObjectNet natural-bias + wrap-up",                   "⏳",        ACCENT, "Screener flags context reliance"],
  ];
  // header
  s.addShape(pptx.ShapeType.rect, { x: 0.7, y: 1.85, w: 12.0, h: 0.5, fill: { color: DARK }, line: { type: "none" } });
  s.addText("Milestone", { x: 0.9, y: 1.9, w: 1.3, h: 0.4, fontFace: FONT_B, fontSize: 12, bold: true, color: "FFFFFF", margin: 0, valign: "middle" });
  s.addText("Scope",      { x: 2.3, y: 1.9, w: 4.6, h: 0.4, fontFace: FONT_B, fontSize: 12, bold: true, color: "FFFFFF", margin: 0, valign: "middle" });
  s.addText("Status",     { x: 7.0, y: 1.9, w: 1.4, h: 0.4, fontFace: FONT_B, fontSize: 12, bold: true, color: "FFFFFF", margin: 0, valign: "middle" });
  s.addText("Verification gate", { x: 8.5, y: 1.9, w: 4.2, h: 0.4, fontFace: FONT_B, fontSize: 12, bold: true, color: "FFFFFF", margin: 0, valign: "middle" });

  let ry = 2.4;
  rows.forEach(([m, t, st, c, v], i) => {
    const fill = i % 2 === 0 ? CARD : "F4F5FB";
    s.addShape(pptx.ShapeType.rect, { x: 0.7, y: ry, w: 12.0, h: 0.5, fill: { color: fill }, line: { color: SOFT2, width: 1 } });
    s.addShape(pptx.ShapeType.rect, { x: 0.7, y: ry, w: 0.15, h: 0.5, fill: { color: c }, line: { type: "none" } });
    s.addText(m, { x: 0.9, y: ry + 0.05, w: 1.3, h: 0.4, fontFace: FONT_B, fontSize: 13, bold: true, color: c, margin: 0, valign: "middle" });
    s.addText(t, { x: 2.3, y: ry + 0.07, w: 4.6, h: 0.4, fontFace: FONT_B, fontSize: 12, color: TEXT, margin: 0, valign: "middle" });
    s.addText(st, { x: 7.0, y: ry + 0.07, w: 1.4, h: 0.4, fontFace: FONT_B, fontSize: 12, bold: true, color: c, margin: 0, valign: "middle" });
    s.addText(v, { x: 8.5, y: ry + 0.07, w: 4.2, h: 0.4, fontFace: FONT_B, fontSize: 11.5, color: MUTE, margin: 0, valign: "middle" });
    ry += 0.55;
  });

  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 6.85, w: 12.0, h: 0.4, rectRadius: 0.06, fill: { color: SOFT }, line: { type: "none" } });
  s.addText("M1 fully verified end-to-end (Samoyed, 8 maps, correct prediction, commit 96c50b6).  M2 is the next gate.", { x: 0.9, y: 6.85, w: 11.6, h: 0.4, fontFace: FONT_B, fontSize: 11.5, bold: true, color: GREEN, margin: 0, valign: "middle" });

  s.addNotes("Each milestone ends with a verification step — nothing is done until it's proven. The M1 gate was a real image end-to-end. The M2 gate is 'same schema, dual-view complete for ViT-B/16'. The M7/M8 gates are the two validation experiments.");
}

// ============================================================ SLIDE 13 — VALIDATION EXPERIMENTS
{
  const s = pptx.addSlide();
  s.background = { color: LIGHT };
  title(s, "Validation — two killer experiments", "Proves the tool catches what we know + what's real");

  // M7 card
  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 1.85, w: 6.0, h: 4.6, rectRadius: 0.12, fill: { color: CARD }, line: { color: SOFT2, width: 1 } });
  s.addShape(pptx.ShapeType.rect, { x: 0.7, y: 1.85, w: 6.0, h: 0.55, fill: { color: INK }, line: { type: "none" } });
  s.addText("M7  ·  Planted-bias (Waterbirds-style)", { x: 0.9, y: 1.9, w: 5.6, h: 0.45, fontFace: FONT_B, fontSize: 14, bold: true, color: "FFFFFF", margin: 0, valign: "middle" });
  s.addText([
    { text: "Setup:  synthetic background/species correlation on CUB-200 → fine-tune ViT (+ResNet)", options: { bullet: true, breakLine: true, paraSpaceAfter: 8 } },
    { text: "What it tests:  does the screener catch a shortcut we deliberately planted?", options: { bullet: true, breakLine: true, paraSpaceAfter: 8 } },
    { text: "Pass criterion:  flag fires on the planted bias; bg/object sensitivity ≫ 1", options: { bullet: true, breakLine: true, paraSpaceAfter: 8 } },
    { text: "Why it matters:  proves the tool catches what we KNOW is there", options: { bullet: true } },
  ], { x: 0.95, y: 2.6, w: 5.5, h: 3.7, fontFace: FONT_B, fontSize: 12.5, color: TEXT, margin: 0, lineSpacing: 14 });

  // M8 card
  s.addShape(pptx.ShapeType.roundRect, { x: 6.9, y: 1.85, w: 6.0, h: 4.6, rectRadius: 0.12, fill: { color: CARD }, line: { color: SOFT2, width: 1 } });
  s.addShape(pptx.ShapeType.rect, { x: 6.9, y: 1.85, w: 6.0, h: 0.55, fill: { color: ACCENT }, line: { type: "none" } });
  s.addText("M8  ·  ObjectNet natural-bias", { x: 7.1, y: 1.9, w: 5.6, h: 0.45, fontFace: FONT_B, fontSize: 14, bold: true, color: "FFFFFF", margin: 0, valign: "middle" });
  s.addText([
    { text: "Setup:  standard pretrained ImageNet model on objects in bizarre contexts", options: { bullet: true, breakLine: true, paraSpaceAfter: 8 } },
    { text: "What it tests:  does the screener catch context reliance we did NOT plant?", options: { bullet: true, breakLine: true, paraSpaceAfter: 8 } },
    { text: "Pass criterion:  failure-diagnosis explains the misclassifications", options: { bullet: true, breakLine: true, paraSpaceAfter: 8 } },
    { text: "Why it matters:  proves the tool catches what's REAL", options: { bullet: true } },
  ], { x: 7.15, y: 2.6, w: 5.5, h: 3.7, fontFace: FONT_B, fontSize: 12.5, color: TEXT, margin: 0, lineSpacing: 14 });

  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 6.55, w: 12.0, h: 0.6, rectRadius: 0.1, fill: { color: SOFT }, line: { type: "none" } });
  s.addText("Both required.  A screening tool is only science if its verdicts are provably true positives — known bugs caught AND real bugs caught.", { x: 0.9, y: 6.6, w: 11.6, h: 0.5, fontFace: FONT_B, fontSize: 12.5, bold: true, color: GREEN, margin: 0, valign: "middle" });

  s.addNotes("These two experiments are the falsification tests. M7 is 'can we find what we put there' (sanity). M8 is 'can we find what's actually there' (the real test). Together they prove the tool is science, not just visualization.");
}

// ============================================================ SLIDE 14 — NOVELTY & HONEST LIMITS
{
  const s = pptx.addSlide();
  s.background = { color: LIGHT };
  title(s, "Novelty & honest limits", "Engineering novelty beats another Grad-CAM variant");

  // Novelty column
  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 1.85, w: 5.95, h: 4.6, rectRadius: 0.12, fill: { color: CARD }, line: { color: SOFT2, width: 1 } });
  s.addText("What is genuinely new", { x: 1.0, y: 2.0, w: 5.3, h: 0.5, fontFace: FONT_H, fontSize: 18, bold: true, color: INK, margin: 0 });
  s.addText([
    { text: "1. Unified dual-view abstraction — native + class-conditioned behind one schema, for both CNN and ViT. Apples-to-apples by construction.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "2. Automated screening verdicts — class-level bias flags, layer-role profiles, evidence-backed reports. No other tool ships this.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "3. Causal debugging loop — intervene → measure → verdict. Heatmaps are correlative; interventions are causal.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Combination (1+2) is the novelty anchor — neither alone is rare; together they are.", options: { bullet: true } },
  ], { x: 1.0, y: 2.6, w: 5.4, h: 3.7, fontFace: FONT_B, fontSize: 12.5, color: TEXT, margin: 0, lineSpacing: 14 });

  // Honest limits column
  s.addShape(pptx.ShapeType.roundRect, { x: 6.8, y: 1.85, w: 5.95, h: 4.6, rectRadius: 0.12, fill: { color: CARD }, line: { color: SOFT2, width: 1 } });
  s.addText("What's not new (and that's fine)", { x: 7.1, y: 2.0, w: 5.3, h: 0.5, fontFace: FONT_H, fontSize: 18, bold: true, color: INK, margin: 0 });
  s.addText([
    { text: "Tool, not method — we don't invent a new attribution algorithm. The XAI method space is saturated (Grad-CAM + 50 variants, attention rollout, LRP…).", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Engineering novelty (a genuinely useful tool) beats another Grad-CAM variant — this is how SHAP and Captum earned their place.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Honest failure: Grad-CAM can yield all-zero maps (observed at layer2.3 on the Samoyed). Reported, not faked — DECISIONS §9.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "GPU/scale runs are code-ready (device-agnostic) but not yet exercised at scale. M2+ moves to rented GPU / Jenga.", options: { bullet: true } },
  ], { x: 7.1, y: 2.6, w: 5.4, h: 3.7, fontFace: FONT_B, fontSize: 12.5, color: TEXT, margin: 0, lineSpacing: 14 });

  s.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 6.55, w: 12.0, h: 0.6, rectRadius: 0.1, fill: { color: "FFF6E6" }, line: { color: "E5C07B", width: 1 } });
  s.addText("Honest open items (logged, not hidden):  zero-map degeneracy guard · ViT class-conditioning method pick (M2) · GPU-scale validation.", { x: 0.9, y: 6.6, w: 11.6, h: 0.5, fontFace: FONT_B, fontSize: 12.5, color: "6B4A12", margin: 0, valign: "middle" });

  s.addNotes("Slide 14 is the credibility slide. A reviewer who hears only novelty will be skeptical; a reviewer who hears only limits will be unimpressed. Both, side by side, with the same weight, is the honest frame.");
}

// ============================================================ SLIDE 15 — THANK YOU
{
  const s = pptx.addSlide();
  s.background = { color: DARK };
  s.addShape(pptx.ShapeType.ellipse, { x: 10.6, y: 4.6, w: 2.2, h: 2.2, fill: { color: INK }, line: { color: CYAN, width: 3 } });
  s.addShape(pptx.ShapeType.ellipse, { x: 11.55, y: 5.4, w: 0.5, h: 0.5, fill: { color: ACCENT }, line: { type: "none" } });
  s.addText("Thank you", { x: 0.9, y: 2.4, w: 11.5, h: 1.0, fontFace: FONT_H, fontSize: 44, bold: true, color: "FFFFFF", margin: 0 });
  s.addText("Questions & discussion", { x: 0.92, y: 3.5, w: 11.5, h: 0.6, fontFace: FONT_B, fontSize: 20, color: CYAN, margin: 0 });
  s.addText("Next gate — M2: ViT extractor.  Same schema, dual-view, faithfulness check.", { x: 0.92, y: 4.3, w: 11.5, h: 0.5, fontFace: FONT_B, fontSize: 14, color: B9, margin: 0 });
  s.addText("AttentionLens — The Whole Pipeline  ·  Review 1  ·  Jaswanth Krishna Padarthi", { x: 0.92, y: 6.6, w: 11.5, h: 0.4, fontFace: FONT_B, fontSize: 13, color: B9, margin: 0 });

  s.addNotes("Thank you — happy to take questions on any of the six stages, the dual-view schema, or the validation experiments.");
}

// ── write
pptx.writeFile({ fileName: out })
   .then(f => console.log("WROTE", f))
   .catch(e => { console.error("FAILED", e); process.exit(1); });
