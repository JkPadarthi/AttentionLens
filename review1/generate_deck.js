// review1/generate_deck.js — AttentionLens Review 1 deck
const pptxgen = require("pptxgenjs");
const path = require("path");

const p = path.join(__dirname, "..", "experiments", "eda");
const out = path.join(__dirname, "..", "experiments", "out");

const DARK = "14142B";     // midnight indigo
const INK = "2E2A72";      // indigo
const ACCENT = "00C9A7";   // lens teal
const CYAN = "7CE0E3";
const LIGHT = "F7F7FC";    // light bg
const CARD = "FFFFFF";
const TEXT = "1F2340";
const MUTE = "5A5F7A";

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
pptx.author = "Jaswanth Krishna Padarthi";
pptx.title = "AttentionLens — Review 1";

const FONT_H = "Cambria";
const FONT_B = "Calibri";

function title(pp, text, sub) {
  pp.addText(text, { x: 0.6, y: 0.35, w: 12.1, h: 0.9, fontFace: FONT_H, fontSize: 30, bold: true, color: TEXT, align: "left", margin: 0 });
  if (sub) pp.addText(sub, { x: 0.62, y: 1.15, w: 12.0, h: 0.5, fontFace: FONT_B, fontSize: 15, color: MUTE, margin: 0 });
}

function chip(pp, x, y, text, color) {
  pp.addShape(pptx.ShapeType.ellipse, { x, y, w: 0.42, h: 0.42, fill: { color }, line: { color: color } });
  pp.addText(text, { x: x + 0.55, y: y - 0.06, w: 10, h: 0.5, fontFace: FONT_B, fontSize: 14, bold: true, color: color, margin: 0, valign: "middle" });
}

// ================================================================ SLIDE 1: TITLE
const s1 = pptx.addSlide();
s1.background = { color: DARK };
s1.addShape(pptx.ShapeType.rect, { x: 9.6, y: 0, w: 3.7, h: 7.5, fill: { color: "1B1B3A" }, line: { type: "none" } });
s1.addShape(pptx.ShapeType.ellipse, { x: 10.2, y: 2.3, w: 2.5, h: 2.5, fill: { color: INK }, line: { color: CYAN, width: 3 } });
s1.addShape(pptx.ShapeType.ellipse, { x: 11.15, y: 3.25, w: 0.6, h: 0.6, fill: { color: ACCENT }, line: { type: "none" } });
s1.addText("AttentionLens", { x: 0.9, y: 2.0, w: 8.4, h: 1.3, fontFace: FONT_H, fontSize: 54, bold: true, color: "FFFFFF", margin: 0 });
s1.addText("Interactive Explainability & Automated Bias-Screening for Vision Models", { x: 0.92, y: 3.3, w: 8.2, h: 1.0, fontFace: FONT_B, fontSize: 19, color: CYAN, margin: 0 });
s1.addText("Project Review 1  ·  B.Tech CSE (AI & ML), VIT", { x: 0.92, y: 5.6, w: 8.2, h: 0.5, fontFace: FONT_B, fontSize: 15, color: "B9BCE0", margin: 0 });
s1.addText("Jaswanth Krishna Padarthi", { x: 0.92, y: 6.1, w: 8.2, h: 0.5, fontFace: FONT_B, fontSize: 15, bold: true, color: "FFFFFF", margin: 0 });
s1.addNotes("Welcome. AttentionLens is an interactive debugging and explainability framework for vision models — with an automated bias-screening layer. Today I will present M1: the unified schema and the ResNet-50 dual-view extractor, with real extraction results.");

// ================================================================ SLIDE 2: AGENDA
const s2 = pptx.addSlide();
s2.background = { color: LIGHT };
title(s2, "Agenda");
const agenda = [
  ["01", "Problem & Motivation", "Why vision models need a debugger, not just explanations"],
  ["02", "Design & Architecture", "Unified dual-view LayerMap schema (CNN ⇄ ViT)"],
  ["03", "Dataset", "ImageNet demo sample — provenance & representation"],
  ["04", "Preprocessing Results", "Resize → normalize → tensor, with measured stats"],
  ["05", "Feature Engineering", "Native activations + Grad-CAM, per-block, normalized"],
  ["06", "EDA Visualizations", "Montage, distributions, concentration, correlations"],
  ["07", "Demo — M1 Gate", "Live ResNet-50 run on a real image (Samoyed)"],
  ["08", "Results & Next Steps", "Findings, honest failures, M2 ViT roadmap"],
];
let ay = 1.75;
agenda.forEach(([n, t, d]) => {
  s2.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: ay - 0.12, w: 11.9, h: 0.62, rectRadius: 0.1, fill: { color: "FFFFFF" }, line: { color: "E3E4F0", width: 1 } });
  s2.addText(n, { x: 0.95, y: ay - 0.05, w: 0.9, h: 0.5, fontFace: FONT_B, fontSize: 18, bold: true, color: ACCENT, margin: 0, valign: "middle" });
  s2.addText(t, { x: 1.95, y: ay - 0.05, w: 4.1, h: 0.5, fontFace: FONT_B, fontSize: 15, bold: true, color: TEXT, margin: 0, valign: "middle" });
  s2.addText(d, { x: 6.2, y: ay - 0.05, w: 6.2, h: 0.5, fontFace: FONT_B, fontSize: 12.5, color: MUTE, margin: 0, valign: "middle" });
  ay += 0.72;
});
s2.addNotes("Eight sections — problem, design, dataset, preprocessing, features, EDA, demo, and next steps.");

// ================================================================ SLIDE 3: PROBLEM
const s3 = pptx.addSlide();
s3.background = { color: LIGHT };
title(s3, "Problem & Motivation", "Explanations exist — but they don't talk to each other");
s3.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 1.8, w: 5.9, h: 2.6, rectRadius: 0.12, fill: { color: CARD }, line: { color: "E3E4F0", width: 1 } });
s3.addText("The field is fragmented", { x: 1.0, y: 2.0, w: 5.3, h: 0.5, fontFace: FONT_H, fontSize: 19, bold: true, color: INK, margin: 0 });
s3.addText([
  { text: "Attention maps (ViT) answer 'what does the model look at' — but they are class-agnostic.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
  { text: "Attribution maps (Grad-CAM) answer 'what drove this decision' — class-specific.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
  { text: "No shared schema: comparing two architectures or two views today means writing bespoke glue.", options: { bullet: true } },
], { x: 1.0, y: 2.6, w: 5.4, h: 1.7, fontFace: FONT_B, fontSize: 13.5, color: TEXT, margin: 0, lineSpacing: 14 });
s3.addShape(pptx.ShapeType.roundRect, { x: 6.8, y: 1.8, w: 5.9, h: 2.6, rectRadius: 0.12, fill: { color: CARD }, line: { color: "E3E4F0", width: 1 } });
s3.addText("Bias goes unnoticed", { x: 7.1, y: 2.0, w: 5.3, h: 0.5, fontFace: FONT_H, fontSize: 19, bold: true, color: INK, margin: 0 });
s3.addText([
  { text: "Spurious correlations (backgrounds, textures, artifacts) silently inflate accuracy.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
  { text: "Finding them today is manual, ad-hoc, and rarely automated end-to-end.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
  { text: "Engineers need a verdict — not another heatmap to eyeball.", options: { bullet: true } },
], { x: 7.1, y: 2.6, w: 5.4, h: 1.7, fontFace: FONT_B, fontSize: 13.5, color: TEXT, margin: 0, lineSpacing: 14 });
s3.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 4.7, w: 12.0, h: 2.1, rectRadius: 0.12, fill: { color: "E6F7F4" }, line: { type: "none" } });
s3.addText("One framework, two jobs", { x: 1.0, y: 4.9, w: 3.6, h: 0.5, fontFace: FONT_H, fontSize: 18, bold: true, color: "006B59", margin: 0 });
s3.addText("① A unified CNN ⇄ ViT abstraction — every layer yields a standard LayerMap (native attention + class-conditioned relevance).  ② An automated bias-screening layer — attention-quality metrics and intervention experiments that produce a verdict, in the tradition of SHAP / Captum as a deployable tool.", { x: 1.0, y: 5.45, w: 11.4, h: 1.2, fontFace: FONT_B, fontSize: 14.5, color: "1F3D36", margin: 0 });
s3.addNotes("Two gaps: fragmentation (no shared schema between attention and attribution, CNN and ViT) and discovery (bias found manually). AttentionLens solves both with one abstraction plus automated screening verdicts — the novelty anchor is the combination, not a new XAI method.");

// ================================================================ SLIDE 4: ARCHITECTURE
const s4 = pptx.addSlide();
s4.background = { color: LIGHT };
title(s4, "Design — the Dual-View LayerMap", "Every layer, two views, one schema");
// flow
const steps = [
  ["Image", "224×224 RGB", ACCENT],
  ["Model", "ResNet-50", INK],
  ["LayerMap", "native + class-cond", "D9534F"],
  ["Metrics", "entropy · locality", "2E2A72"],
  ["Verdict", "screening report", "006B59"],
];
let sx = 0.7;
steps.forEach(([t, d, c]) => {
  s4.addShape(pptx.ShapeType.roundRect, { x: sx, y: 2.0, w: 2.15, h: 1.15, rectRadius: 0.1, fill: { color: c }, line: { type: "none" } });
  s4.addText(t, { x: sx, y: 2.15, w: 2.15, h: 0.5, fontFace: FONT_B, fontSize: 15, bold: true, color: "FFFFFF", align: "center", margin: 0 });
  s4.addText(d, { x: sx, y: 2.62, w: 2.15, h: 0.4, fontFace: FONT_B, fontSize: 10.5, color: "EFF0FF", align: "center", margin: 0 });
  if (sx < 9.8) s4.addText("→", { x: sx + 2.18, y: 2.3, w: 0.5, h: 0.5, fontFace: FONT_B, fontSize: 20, bold: true, color: MUTE, align: "center", margin: 0 });
  sx += 2.68;
});
s4.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 3.6, w: 5.95, h: 2.7, rectRadius: 0.12, fill: { color: CARD }, line: { color: "E3E4F0", width: 1 } });
s4.addText("Native view — what the model attends to (mechanism)", { x: 1.0, y: 3.78, w: 5.4, h: 0.5, fontFace: FONT_H, fontSize: 16, bold: true, color: INK, margin: 0 });
s4.addText([
  { text: "Mean over channels of each block's last conv activation", options: { bullet: true, breakLine: true, paraSpaceAfter: 5 } },
  { text: "Upsampled to input resolution (bilinear)", options: { bullet: true, breakLine: true, paraSpaceAfter: 5 } },
  { text: "Normalized to [0, 1]", options: { bullet: true, breakLine: true, paraSpaceAfter: 5 } },
  { text: "Class-agnostic: shows where the model looks", options: { bullet: true } },
], { x: 1.0, y: 4.35, w: 5.45, h: 1.8, fontFace: FONT_B, fontSize: 13.5, color: TEXT, margin: 0, lineSpacing: 14 });
s4.addShape(pptx.ShapeType.roundRect, { x: 6.8, y: 3.6, w: 5.95, h: 2.7, rectRadius: 0.12, fill: { color: CARD }, line: { color: "E3E4F0", width: 1 } });
s4.addText("Class-conditioned view — why the model decided", { x: 7.1, y: 3.78, w: 5.4, h: 0.5, fontFace: FONT_H, fontSize: 16, bold: true, color: INK, margin: 0 });
s4.addText([
  { text: "Grad-CAM on the same conv, for the predicted class", options: { bullet: true, breakLine: true, paraSpaceAfter: 5 } },
  { text: "ReLU → upsample → normalize to [0, 1]", options: { bullet: true, breakLine: true, paraSpaceAfter: 5 } },
  { text: "Evidence for this specific decision", options: { bullet: true, breakLine: true, paraSpaceAfter: 5 } },
  { text: "Same LayerMap contract — comparable by construction", options: { bullet: true } },
], { x: 7.1, y: 4.35, w: 5.45, h: 1.8, fontFace: FONT_B, fontSize: 13.5, color: TEXT, margin: 0, lineSpacing: 14 });
s4.addNotes("The core architectural decision: we never conflate the two views. Native maps capture the mechanism; class-conditioned maps capture decision evidence. Both land in the same LayerMap dataclass so downstream metrics and screening treat them identically.");

// ================================================================ SLIDE 5: DATASET
const s5 = pptx.addSlide();
s5.background = { color: LIGHT };
title(s5, "Dataset", "ImageNet provenance, real pipeline ingestion");
s5.addImage({ path: path.join(__dirname, "..", "experiments", "sample.jpg"), x: 0.7, y: 1.95, w: 4.4, h: 3.3, sizing: { type: "cover", w: 4.4, h: 3.3 } });
s5.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 5.25, w: 4.4, h: 0.6, rectRadius: 0.08, fill: { color: INK }, line: { type: "none" } });
s5.addText("sample.jpg — Samoyed (ImageNet)", { x: 0.7, y: 5.4, w: 4.4, h: 0.4, fontFace: FONT_B, fontSize: 12.5, bold: true, color: "FFFFFF", align: "center", margin: 0 });
const dset = [
  ["Source", "ImageNet (demo sample)"],
  ["True label", "Samoyed"],
  ["Original size", "1546 × 1213 px"],
  ["Pipeline input", "224 × 224 RGB"],
  ["Extraction", "8 LayerMaps (4 blocks × 2 views)"],
  ["Heavy runs", "CPU on Arjun (M1); GPU/Jenga planned (M2+)"],
];
let dy = 2.0;
dset.forEach(([k, v]) => {
  s5.addText(k, { x: 5.5, y: dy, w: 2.6, h: 0.45, fontFace: FONT_B, fontSize: 13.5, bold: true, color: MUTE, margin: 0 });
  s5.addText(v, { x: 8.2, y: dy, w: 4.4, h: 0.45, fontFace: FONT_B, fontSize: 13.5, color: TEXT, margin: 0 });
  dy += 0.5;
});
s5.addShape(pptx.ShapeType.roundRect, { x: 5.5, y: 5.25, w: 7.1, h: 1.1, rectRadius: 0.1, fill: { color: "E6F7F4" }, line: { type: "none" } });
s5.addText("Review-1 scope: a single curated sample exercises the full pipeline end-to-end. Screening-scale corpora (planted-bias CUB, ObjectNet) are scheduled in the validation milestone.", { x: 5.8, y: 5.42, w: 6.6, h: 0.85, fontFace: FONT_B, fontSize: 12.5, color: "1F3D36", margin: 0 });
s5.addNotes("For review 1 the dataset section shows a real ImageNet sample flowing through the real pipeline — honest scope. The bias-screening datasets come in the validation milestone: a synthetic planted-bias set (proves the screener catches what we know) plus ObjectNet (proves it catches real-world distribution shift).");
// note: image file lives at experiments/sample.jpg

// ================================================================ SLIDE 6: PREPROCESSING
const s6 = pptx.addSlide();
s6.background = { color: LIGHT };
title(s6, "Preprocessing Results", "Resize → /255 → ImageNet normalize → tensor (measured on Arjun)");
const pipe = ["load RGB", "resize 224×224", "÷255 → [0,1]", "−mean ÷std", "[1,3,224,224] fp32"];
let px = 0.7;
pipe.forEach((t, i) => {
  s6.addShape(pptx.ShapeType.roundRect, { x: px, y: 1.75, w: 2.0, h: 0.8, rectRadius: 0.08, fill: { color: i === 4 ? INK : "FFFFFF" }, line: { color: "D6D8EA", width: 1 } });
  s6.addText(t, { x: px, y: 1.9, w: 2.0, h: 0.5, fontFace: FONT_B, fontSize: 11.5, bold: true, color: i === 4 ? "FFFFFF" : TEXT, align: "center", margin: 0 });
  if (i < 4) s6.addText("→", { x: px + 2.0, y: 1.9, w: 0.32, h: 0.5, fontFace: FONT_B, fontSize: 16, bold: true, color: MUTE, align: "center", margin: 0 });
  px += 2.32;
});
s6.addText("Raw pixel stats (0–1, before normalize)", { x: 0.8, y: 2.95, w: 5.4, h: 0.45, fontFace: FONT_H, fontSize: 16, bold: true, color: INK, margin: 0 });
const rawRows = [
  ["R", "0.388 ± 0.320"],
  ["G", "0.431 ± 0.295"],
  ["B", "0.368 ± 0.337"],
];
rawRows.forEach(([c, v], i) => {
  s6.addShape(pptx.ShapeType.roundRect, { x: 0.8 + i * 1.9, y: 3.45, w: 1.7, h: 0.85, rectRadius: 0.08, fill: { color: CARD }, line: { color: "E3E4F0", width: 1 } });
  s6.addText(c, { x: 0.8 + i * 1.9, y: 3.5, w: 1.7, h: 0.3, fontFace: FONT_B, fontSize: 12, bold: true, color: MUTE, align: "center", margin: 0 });
  s6.addText(v, { x: 0.8 + i * 1.9, y: 3.82, w: 1.7, h: 0.35, fontFace: FONT_B, fontSize: 13, bold: true, color: TEXT, align: "center", margin: 0 });
});
s6.addText("Normalized tensor stats (after −mean ÷std)", { x: 5.0, y: 2.95, w: 5.6, h: 0.45, fontFace: FONT_H, fontSize: 16, bold: true, color: INK, margin: 0 });
const normRows = [
  ["R", "−0.421 ± 1.398"],
  ["G", "−0.110 ± 1.316"],
  ["B", "−0.170 ± 1.498"],
];
normRows.forEach(([c, v], i) => {
  s6.addShape(pptx.ShapeType.roundRect, { x: 5.0 + i * 1.9, y: 3.45, w: 1.7, h: 0.85, rectRadius: 0.08, fill: { color: CARD }, line: { color: "E3E4F0", width: 1 } });
  s6.addText(c, { x: 5.0 + i * 1.9, y: 3.5, w: 1.7, h: 0.3, fontFace: FONT_B, fontSize: 12, bold: true, color: MUTE, align: "center", margin: 0 });
  s6.addText(v, { x: 5.0 + i * 1.9, y: 3.82, w: 1.7, h: 0.35, fontFace: FONT_B, fontSize: 13, bold: true, color: TEXT, align: "center", margin: 0 });
});
s6.addShape(pptx.ShapeType.roundRect, { x: 0.8, y: 4.7, w: 11.6, h: 1.7, rectRadius: 0.12, fill: { color: "E6F7F4" }, line: { type: "none" } });
s6.addText([
  { text: "Design point: preprocessing is a lossless, reversible step — tensor_to_image() inverts it exactly for visualization overlay.", options: { bullet: true, breakLine: true, paraSpaceAfter: 4 } },
  { text: "Facts: input [1,3,224,224], dtype float32, on-device; stats above measured on Arjun, python 3.12, torch 2.13 CPU.", options: { bullet: true, breakLine: true, paraSpaceAfter: 4 } },
  { text: "Tests: test_preprocess.py covers round-trip equivalence (hermetic — no downloads).", options: { bullet: true } },
], { x: 1.05, y: 4.85, w: 11.1, h: 1.45, fontFace: FONT_B, fontSize: 13, color: "1F3D36", margin: 0, lineSpacing: 14 });
s6.addNotes("Real measured numbers: the raw image averages R .388 G .431 B .368; after ImageNet normalization the tensor channels are −.421 / −.110 / −.170 with stds 1.40 / 1.32 / 1.50. The round-trip denormalizer guarantees overlays align with the original pixels.");

// ================================================================ SLIDE 7: FEATURE ENGINEERING I — SCHEMA
const s7 = pptx.addSlide();
s7.background = { color: LIGHT };
title(s7, "Feature Engineering I — the LayerMap contract", "One dataclass rules all extractors, metrics, screening, UI");
const fields = [
  ["layer_name", "str", "\"layer4.2.conv3\" / \"block11\" / \"attn_head_3\""],
  ["arch", "str", "\"cnn\" | \"vit\""],
  ["view", "str", "\"native\" | \"class_conditioned\""],
  ["model_class", "str", "class used for conditioning (argmax for native)"],
  ["map", "np.ndarray", "H×W float32, normalized [0,1], input resolution"],
  ["head_or_channel", "int | None", "per-head / per-channel breakdown (future)"],
  ["metadata", "dict", "method, reduction, entropy, locality — extensible"],
];
let fy = 1.85;
s7.addText("Field", { x: 0.9, y: 1.8, w: 2.4, h: 0.4, fontFace: FONT_B, fontSize: 13, bold: true, color: MUTE, margin: 0 });
s7.addText("Type", { x: 3.4, y: 1.8, w: 1.8, h: 0.4, fontFace: FONT_B, fontSize: 13, bold: true, color: MUTE, margin: 0 });
s7.addText("Meaning", { x: 5.3, y: 1.8, w: 6.0, h: 0.4, fontFace: FONT_B, fontSize: 13, bold: true, color: MUTE, margin: 0 });
fields.forEach(([f, t, d]) => {
  s7.addText(f, { x: 0.9, y: fy, w: 2.4, h: 0.5, fontFace: "Consolas", fontSize: 12.5, bold: true, color: INK, margin: 0 });
  s7.addText(t, { x: 3.4, y: fy, w: 1.8, h: 0.5, fontFace: FONT_B, fontSize: 12.5, color: "C0392B", margin: 0 });
  s7.addText(d, { x: 5.3, y: fy, w: 6.0, h: 0.5, fontFace: FONT_B, fontSize: 12.5, color: TEXT, margin: 0 });
  fy += 0.52;
});
s7.addShape(pptx.ShapeType.roundRect, { x: 0.9, y: 5.8, w: 11.5, h: 0.9, rectRadius: 0.1, fill: { color: "E6F7F4" }, line: { type: "none" } });
s7.addText("ModelInspection bundles one (model, image) pair: model_id, image_id, true/pred label, LayerMaps, intervention_results. Verified by test_schema.py (7 tests green on Arjun).", { x: 1.15, y: 5.95, w: 11.0, h: 0.65, fontFace: FONT_B, fontSize: 13, color: "1F3D36", margin: 0 });
s7.addNotes("The schema is the contract. Any extractor — CNN or ViT — emits LayerMaps; every downstream consumer (metrics, screening, UI) reads the same shape. M1 ships with ModelInspection as the container.");

// ================================================================ SLIDE 8: FEATURE ENGINEERING II — EXTRACTION
const s8 = pptx.addSlide();
s8.background = { color: LIGHT };
title(s8, "Feature Engineering II — extraction methods", "Probing the last conv of each ResNet bottleneck block");
s8.addText("RESNET_BLOCK_LAYERS", { x: 0.9, y: 1.8, w: 5.8, h: 0.4, fontFace: "Consolas", fontSize: 13, bold: true, color: INK, margin: 0 });
s8.addText("\"layer1.2.conv3\" · \"layer2.3.conv3\" · \"layer3.5.conv3\" · \"layer4.2.conv3\"", { x: 0.9, y: 2.25, w: 9.0, h: 0.4, fontFace: "Consolas", fontSize: 12.5, color: TEXT, margin: 0 });
const blocks = [
  ["layer1.2.conv3", "256 ch", "early texture/edges"],
  ["layer2.3.conv3", "512 ch", "patterns/parts"],
  ["layer3.5.conv3", "1024 ch", "object parts"],
  ["layer4.2.conv3", "2048 ch", "object-level semantics"],
];
let bx = 0.7;
blocks.forEach(([l, c, d]) => {
  s8.addShape(pptx.ShapeType.roundRect, { x: bx, y: 3.0, w: 2.9, h: 1.5, rectRadius: 0.1, fill: { color: CARD }, line: { color: "E3E4F0", width: 1 } });
  s8.addText(l, { x: bx, y: 3.12, w: 2.9, h: 0.4, fontFace: "Consolas", fontSize: 12, bold: true, color: INK, align: "center", margin: 0 });
  s8.addText(c, { x: bx, y: 3.5, w: 2.9, h: 0.35, fontFace: FONT_B, fontSize: 13, bold: true, color: ACCENT, align: "center", margin: 0 });
  s8.addText(d, { x: bx, y: 3.85, w: 2.9, h: 0.5, fontFace: FONT_B, fontSize: 11, color: MUTE, align: "center", margin: 0 });
  bx += 3.05;
});
s8.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 4.85, w: 5.95, h: 1.6, rectRadius: 0.12, fill: { color: CARD }, line: { color: "E3E4F0", width: 1 } });
s8.addText("Native (mechanism)", { x: 1.0, y: 5.0, w: 5.3, h: 0.4, fontFace: FONT_H, fontSize: 15, bold: true, color: INK, margin: 0 });
s8.addText("Forward hook → activations[B,C,H,W] → mean(dim=1) → bilinear upsample → min-max normalize. Cost: one forward pass.", { x: 1.0, y: 5.42, w: 5.4, h: 0.95, fontFace: FONT_B, fontSize: 12, color: TEXT, margin: 0 });
s8.addShape(pptx.ShapeType.roundRect, { x: 6.8, y: 4.85, w: 5.95, h: 1.6, rectRadius: 0.12, fill: { color: CARD }, line: { color: "E3E4F0", width: 1 } });
s8.addText("Class-conditioned (evidence)", { x: 7.1, y: 5.0, w: 5.3, h: 0.4, fontFace: FONT_H, fontSize: 15, bold: true, color: INK, margin: 0 });
s8.addText("Captum LayerGradCam on the same conv, target = predicted class → ReLU → upsample → normalize. Cost: one attribution per layer.", { x: 7.1, y: 5.42, w: 5.4, h: 0.95, fontFace: FONT_B, fontSize: 12, color: TEXT, margin: 0 });
s8.addNotes("Four probe points chosen deliberately: the last conv of each bottleneck block, spanning 256→2048 channels and texture→semantics. Both views derive from identical probe points, so cross-view comparison is apples-to-apples.");

// ================================================================ SLIDE 9: EDA — MONTAGE
const s9 = pptx.addSlide();
s9.background = { color: LIGHT };
title(s9, "EDA — dual-view montage (live output)", "ResNet-50 on sample.jpg — predicted: Samoyed ✓");
s9.addImage({ path: path.join(p, "eda_montage.png"), x: 0.55, y: 1.7, w: 12.25, h: 5.4, sizing: { type: "contain", w: 12.25, h: 5.4 } });
s9.addNotes("Top row: Grad-CAM (class-conditioned, evidence). Bottom row: native mean-channel activation (mechanism). Left to right: layer1→4. Note how Grad-CAM concentrates and moves to the dog; native maps stay diffuse until deep layers. This is real extraction data — no cherry-picking.");
// montage generated by eda_review1.py from the live pipeline

// ================================================================ SLIDE 10: EDA — DISTRIBUTIONS & CONCENTRATION
const s10 = pptx.addSlide();
s10.background = { color: LIGHT };
title(s10, "EDA — value distributions & spatial concentration", "Why the two views can't be swapped");
s10.addImage({ path: path.join(p, "eda_histograms.png"), x: 0.55, y: 1.75, w: 12.2, h: 2.55, sizing: { type: "contain", w: 12.2, h: 2.55 } });
s10.addImage({ path: path.join(p, "eda_concentration.png"), x: 0.55, y: 4.35, w: 12.2, h: 2.55, sizing: { type: "contain", w: 12.2, h: 2.55 } });
s10.addNotes("Native maps are near-uniform (high entropy — a little everywhere); Grad-CAM maps are sharply peaked (low entropy — evidence is localized). The concentration curves make the contrast visible: Grad-CAM reaches ~100% cumulative energy in a small pixel fraction at early layers; native maps spread energy far more evenly.");
// both figures generated live on Arjun

// ================================================================ SLIDE 11: EDA — CORRELATION + FINDING
const s11 = pptx.addSlide();
s11.background = { color: LIGHT };
title(s11, "EDA — cross-view correlation (the key finding)", "Mechanism and evidence diverge early, converge deep");
s11.addImage({ path: path.join(p, "eda_correlations.png"), x: 0.55, y: 1.85, w: 11.0, h: 2.55, sizing: { type: "contain", w: 11.0, h: 2.55 } });
const cards = [
  ["Layer 1 · r = 0.00", "Native and Grad-CAM are decorrelated — the model looks broadly, but class evidence is tiny and sharp."],
  ["Layer 2 · undefined", "Grad-CAM collapsed to an all-zero map for this image (ReLU'd gradients vanished) — a real, surfaced failure."],
  ["Layer 3 · r = 0.41", "Mechanism starts aligning with evidence as receptive fields widen."],
  ["Layer 4 · r = 0.48", "Deep features: where the model looks is where the decision lives."],
];
let cx = 0.7, cy = 4.55;
cards.forEach(([t, d]) => {
  s11.addShape(pptx.ShapeType.roundRect, { x: cx, y: cy, w: 2.9, h: 1.65, rectRadius: 0.1, fill: { color: CARD }, line: { color: "E3E4F0", width: 1 } });
  s11.addText(t, { x: cx, y: cy + 0.1, w: 2.9, h: 0.45, fontFace: FONT_B, fontSize: 12.5, bold: true, color: INK, align: "center", margin: 0 });
  s11.addText(d, { x: cx + 0.12, y: cy + 0.55, w: 2.66, h: 1.0, fontFace: FONT_B, fontSize: 10.2, color: TEXT, align: "center", margin: 0 });
  cx += 3.05;
});
s11.addNotes("Pearson r between native and Grad-CAM per block: 0.00, undefined, 0.41, 0.48. The layer-2 zero-map is honest data — a degenerate explanation surfaced by the tool itself, which is exactly the failure mode an explainability debugger should expose. This motivates the intervention experiments in the roadmap.");
// r values from live run: layer1 0.0, layer2 NaN (zero map), layer3 0.407, layer4 0.48

// ================================================================ SLIDE 12: DEMO
const s12 = pptx.addSlide();
s12.background = { color: DARK };
s12.addText("Demo — M1 gate on Arjun", { x: 0.7, y: 0.5, w: 11.9, h: 0.7, fontFace: FONT_H, fontSize: 30, bold: true, color: "FFFFFF", margin: 0 });
const demoImgs = [
  ["layer1.2.conv3_class_conditioned.png", "B1 · Grad-CAM"],
  ["layer1.2.conv3_native.png", "B1 · native"],
  ["layer2.3.conv3_class_conditioned.png", "B2 · Grad-CAM"],
  ["layer2.3.conv3_native.png", "B2 · native"],
  ["layer3.5.conv3_class_conditioned.png", "B3 · Grad-CAM"],
  ["layer3.5.conv3_native.png", "B3 · native"],
  ["layer4.2.conv3_class_conditioned.png", "B4 · Grad-CAM"],
  ["layer4.2.conv3_native.png", "B4 · native"],
];
let Dx = 0.55, Dy = 1.5;
demoImgs.forEach(([f, cap], i) => {
  s12.addImage({ path: path.join(out, f), x: Dx, y: Dy, w: 2.95, h: 2.6, sizing: { type: "contain", w: 2.95, h: 2.6 } });
  s12.addText(cap, { x: Dx, y: Dy + 2.55, w: 2.95, h: 0.35, fontFace: FONT_B, fontSize: 10.5, bold: true, color: "B9BCE0", align: "center", margin: 0 });
  Dx += 3.05;
  if ((i + 1) % 4 === 0) { Dx = 0.55; Dy += 3.05; }
});
s12.addText("One forward pass + 4 Grad-CAM attributions · predicted Samoyed (correct) · CPU, torch 2.13 · commit 96c50b6", { x: 0.7, y: 6.9, w: 11.9, h: 0.4, fontFace: FONT_B, fontSize: 12, color: ACCENT, align: "center", margin: 0 });
s12.addNotes("Live demo artifacts: all eight maps are real output files from experiments/out/. Prediction Samoyed matches the true label. The pipeline is committed (first commit, M1 complete) and the working tree is clean.");

// ================================================================ SLIDE 13: RESULTS & NEXT
const s13 = pptx.addSlide();
s13.background = { color: LIGHT };
title(s13, "Results & Next Steps", "M1 delivered; M2 opens the ViT frontier");
s13.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 1.85, w: 5.9, h: 3.3, rectRadius: 0.12, fill: { color: CARD }, line: { color: "E3E4F0", width: 1 } });
s13.addText("Delivered (M1)", { x: 1.0, y: 2.0, w: 5.3, h: 0.45, fontFace: FONT_H, fontSize: 17, bold: true, color: INK, margin: 0 });
s13.addText([
  { text: "Unified LayerMap / ModelInspection schema — tested (7 green)", options: { bullet: true, breakLine: true, paraSpaceAfter: 5 } },
  { text: "ResNet-50 dual-view extractor — native + Grad-CAM, 4 blocks", options: { bullet: true, breakLine: true, paraSpaceAfter: 5 } },
  { text: "Preprocessing with exact round-trip visualization", options: { bullet: true, breakLine: true, paraSpaceAfter: 5 } },
  { text: "End-to-end demo: Samoyed, 8 maps, correct prediction", options: { bullet: true, breakLine: true, paraSpaceAfter: 5 } },
  { text: "Hermetic test suite — runs without downloads", options: { bullet: true } },
], { x: 1.0, y: 2.55, w: 5.45, h: 2.5, fontFace: FONT_B, fontSize: 13, color: TEXT, margin: 0, lineSpacing: 14 });
s13.addShape(pptx.ShapeType.roundRect, { x: 6.8, y: 1.85, w: 5.9, h: 3.3, rectRadius: 0.12, fill: { color: CARD }, line: { color: "E3E4F0", width: 1 } });
s13.addText("Roadmap", { x: 7.1, y: 2.0, w: 5.3, h: 0.45, fontFace: FONT_H, fontSize: 17, bold: true, color: INK, margin: 0 });
s13.addText([
  { text: "M2: ViT extractor — attention maps through the same LayerMap", options: { bullet: true, breakLine: true, paraSpaceAfter: 5 } },
  { text: "M3: attention-quality metrics (entropy, locality, faithfulness)", options: { bullet: true, breakLine: true, paraSpaceAfter: 5 } },
  { text: "M4: screening pipeline + planted-bias & ObjectNet validation", options: { bullet: true, breakLine: true, paraSpaceAfter: 5 } },
  { text: "M5: interactive UI (Gradio) + intervention experiments", options: { bullet: true } },
], { x: 7.1, y: 2.55, w: 5.45, h: 2.5, fontFace: FONT_B, fontSize: 13, color: TEXT, margin: 0, lineSpacing: 14 });
s13.addShape(pptx.ShapeType.roundRect, { x: 0.7, y: 5.4, w: 12.0, h: 1.15, rectRadius: 0.12, fill: { color: INK }, line: { type: "none" } });
s13.addText("Honest open items: zero-map degeneracy at layer 2 needs a stability guard; GPU/device portability is code-ready, not yet exercised at scale.", { x: 1.0, y: 5.6, w: 11.4, h: 0.8, fontFace: FONT_B, fontSize: 13.5, color: "EFF0FF", margin: 0 });
s13.addNotes("M1 is committed and clean. Next: the ViT extractor (M2) so CNN and ViT become comparable under one schema, then metrics, screening with validation, and an interactive UI. The layer-2 zero-map observation is logged as an open item — a guard for degenerate explanations is planned.");

// ================================================================ SLIDE 14: END
const s14 = pptx.addSlide();
s14.background = { color: DARK };
s14.addShape(pptx.ShapeType.ellipse, { x: 10.6, y: 4.6, w: 2.2, h: 2.2, fill: { color: INK }, line: { color: CYAN, width: 3 } });
s14.addShape(pptx.ShapeType.ellipse, { x: 11.55, y: 5.4, w: 0.5, h: 0.5, fill: { color: ACCENT }, line: { type: "none" } });
s14.addText("Thank you", { x: 0.9, y: 2.6, w: 11.5, h: 1.0, fontFace: FONT_H, fontSize: 44, bold: true, color: "FFFFFF", margin: 0 });
s14.addText("Questions & discussion", { x: 0.92, y: 3.7, w: 11.5, h: 0.6, fontFace: FONT_B, fontSize: 20, color: CYAN, margin: 0 });
s14.addText("AttentionLens · Review 1 · Jaswanth Krishna Padarthi", { x: 0.92, y: 6.6, w: 11.5, h: 0.4, fontFace: FONT_B, fontSize: 13, color: "B9BCE0", margin: 0 });
s14.addNotes("Thank you — happy to take questions.");

pptx.writeFile({ fileName: path.join(__dirname, "AttentionLens-Review1.pptx") }).then(f => console.log("WROTE", f));