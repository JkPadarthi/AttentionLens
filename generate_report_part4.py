"""Generate AttentionLens Report Part 4: Proposed Methodology (~12 pages)."""
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
from docx.enum.table import WD_TABLE_ALIGNMENT

doc = Document()

# ── Page Setup ──
for section in doc.sections:
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    footer = section.footer
    footer.is_linked_to_previous = False
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = fp.add_run()
    fldChar1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
    run._r.append(fldChar1)
    run2 = fp.add_run()
    instrText = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>')
    run2._r.append(instrText)
    run3 = fp.add_run()
    fldChar2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
    run3._r.append(fldChar2)

# ── Helpers ──
def set_font(run, name="Times New Roman", size=11, bold=False, italic=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)

def add_heading_styled(text, level=1):
    p = doc.add_paragraph()
    if level == 1:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        set_font(run, size=16, bold=True)
        p.paragraph_format.space_before = Pt(24)
        p.paragraph_format.space_after = Pt(16)
    elif level == 2:
        run = p.add_run(text)
        set_font(run, size=12, bold=True)
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(10)
    elif level == 3:
        run = p.add_run(text)
        set_font(run, size=11, bold=True)
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(8)
    return p

def add_body(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    set_font(run, size=11)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.15
    return p

def add_formula(formula_text, label):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(formula_text)
    set_font(run, size=11, italic=True)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run2 = p2.add_run(f"({label})")
    set_font(run2, size=10)
    p2.paragraph_format.space_after = Pt(8)
    return p

def set_cell_shading(cell, color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def add_placeholder(label):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"\n{'─'*60}\n\n[ PLACEHOLDER: {label} ]\n\n{'─'*60}\n")
    set_font(run, size=10, italic=True, color=(120, 120, 120))
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(12)
    return p

def add_page_break():
    doc.add_page_break()

# ============================================================
# 4. PROPOSED METHODOLOGY
# ============================================================
add_heading_styled("4. Proposed Methodology", level=1)

add_body(
    "This section presents the complete methodology underlying the AttentionLens framework, "
    "including system architecture, unified dual-view abstraction, attention extractors for "
    "both CNN and ViT models, quantitative attention metrics, the automated screening engine, "
    "the causal intervention loop, and the interactive user interface. The methodology is "
    "designed to address the five limitations identified in the problem statement and achieve "
    "the six research objectives outlined in Section 1."
)

# Placeholder for architecture diagram
add_placeholder("SYSTEM ARCHITECTURE DIAGRAM - Complete AttentionLens Framework showing all components and data flow")

# 4.1 System Architecture
add_heading_styled("4.1 System Architecture", level=2)

add_body(
    "The AttentionLens framework follows a modular architecture consisting of five primary "
    "components: (1) the Preprocessing Module, which handles image loading and normalization; "
    "(2) the Attention Extractors, which produce dual-view attention maps for CNN and ViT models; "
    "(3) the Metrics Module, which computes quantitative attention quality measures; (4) the "
    "Screening Engine, which aggregates metrics and generates evidence-backed verdicts; and "
    "(5) the Interactive Interface, which provides a Gradio-based web UI for exploration and "
    "debugging."
)

add_body(
    "The architecture is designed around a unified data schema (LayerMap) that treats CNN and "
    "ViT attention patterns symmetrically, enabling downstream components to operate identically "
    "regardless of the underlying model architecture. This unified abstraction is the key "
    "innovation that enables fair cross-architecture comparison and metric computation."
)

add_body(
    "The system follows a pipeline architecture where input images flow through preprocessing, "
    "then through the appropriate extractor (ResNet or ViT), producing LayerMap objects that are "
    "consumed by the metrics module. The computed metrics are then aggregated by the screening "
    "engine, which produces verdicts and evidence reports. The interactive interface provides "
    "real-time access to all components, enabling researchers to explore attention patterns and "
    "perform causal interventions."
)

# 4.2 Unified Dual-View Abstraction
add_heading_styled("4.2 Unified Dual-View Abstraction", level=2)

add_body(
    "The core innovation of AttentionLens is the unified dual-view abstraction, which captures "
    "both native attention patterns and class-conditioned relevance evidence in a common schema. "
    "This abstraction addresses Limitation 1 (architecture fragmentation) by providing a single "
    "data structure that works identically for CNNs and ViTs."
)

add_heading_styled("4.2.1 LayerMap Schema", level=3)

add_body(
    "The LayerMap data structure is the fundamental unit of attention representation in "
    "AttentionLens. Each LayerMap object represents one attention map for one layer, one view "
    "(native or class-conditioned), and one model class. The schema is defined as follows:"
)

add_body(
    "class LayerMap: layer_name (string identifier for the layer, e.g., 'layer4' for ResNet or "
    "'block11' for ViT), arch (architecture type: 'cnn' or 'vit'), view (view type: 'native' or "
    "'class_conditioned'), model_class (the predicted or target class), map (H×W numpy array "
    "normalized to [0,1] at input resolution), head_or_channel (optional per-head or per-channel "
    "breakdown identifier), and metadata (dictionary containing computed metrics such as entropy, "
    "locality, and part-overlap)."
)

add_body(
    "The map field is the most important: it contains the actual attention heatmap as a 2D numpy "
    "array at input resolution (224×224 pixels), normalized to the range [0,1] where 0 represents "
    "no attention and 1 represents maximum attention. This normalization ensures that maps from "
    "different layers and architectures are directly comparable."
)

add_body(
    "The view field distinguishes between two types of attention maps. The native view captures "
    "the mechanism's own information flow: for ViTs, this is the attention rollout showing how "
    "information propagates from the CLS token to all patches; for CNNs, this is the mean-over-"
    "channel activation map showing what the layer amplifies. The class-conditioned view captures "
    "decision-relevant evidence: for CNNs, this is the Grad-CAM map weighted by the gradient of "
    "the target class; for ViTs, this is the gradient-weighted attention (AxG) showing which "
    "attention patterns contribute to the target class prediction."
)

# Table 4.1: LayerMap Fields
table1 = doc.add_table(rows=1, cols=4)
table1.style = 'Light Grid Accent 1'
table1.alignment = WD_TABLE_ALIGNMENT.CENTER

hdr_cells = table1.rows[0].cells
headers = ['Field', 'Type', 'Description', 'Example']
for i, header in enumerate(headers):
    hdr_cells[i].text = header
    for paragraph in hdr_cells[i].paragraphs:
        for run in paragraph.runs:
            run.font.bold = True
            run.font.size = Pt(9)
    set_cell_shading(hdr_cells[i], "4472C4")
    for paragraph in hdr_cells[i].paragraphs:
        for run in paragraph.runs:
            run.font.color.rgb = RGBColor(255, 255, 255)

data = [
    ['layer_name', 'str', 'Layer identifier', 'layer4 / block11'],
    ['arch', 'str', 'Architecture type', 'cnn / vit'],
    ['view', 'str', 'View type', 'native / class_conditioned'],
    ['model_class', 'str', 'Target class', 'Samoyed / class_258'],
    ['map', 'ndarray', 'H×W attention map [0,1]', '224×224 float32'],
    ['head_or_channel', 'int', 'Per-head/channel ID', '3 (attention head 3)'],
    ['metadata', 'dict', 'Computed metrics', '{entropy: 2.1, obj_share: 0.72}'],
]

for row_data in data:
    row_cells = table1.add_row().cells
    for i, cell_text in enumerate(row_data):
        row_cells[i].text = cell_text
        for paragraph in row_cells[i].paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(9)

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Table 4.1: LayerMap Schema Fields")
set_font(run, size=10, italic=True)
p.paragraph_format.space_after = Pt(12)

add_heading_styled("4.2.2 ModelInspection Schema", level=3)

add_body(
    "The ModelInspection data structure aggregates all LayerMap objects produced for a single "
    "(model, image) pair. It contains the model identifier, image identifier, true label (if "
    "known), predicted label, a list of LayerMap objects (one per layer per view), and a list "
    "of InterventionResult objects from causal probing. This structure provides a complete "
    "record of the model's attention patterns and intervention results for a given input."
)

add_body(
    "The ModelInspection object is the primary output of the extractors and the primary input "
    "to the metrics module. It enables batch processing of multiple images and aggregation of "
    "results across the dataset for screening and analysis."
)

# 4.3 Attention Extractors
add_heading_styled("4.3 Attention Extractors", level=2)

add_body(
    "AttentionLens provides two extractors: the ResNetExtractor for CNN-based models and the "
    "VitExtractor for Vision Transformer models. Both extractors implement the same interface "
    "and produce LayerMap objects in the unified schema, enabling fair comparison across "
    "architectures."
)

add_heading_styled("4.3.1 ResNet Extractor (CNN)", level=3)

add_body(
    "The ResNetExtractor produces dual-view attention maps for ResNet-50 and similar CNN "
    "architectures. For the native view, it computes mean-over-channel activation maps at each "
    "of the four residual blocks (layer1, layer2, layer3, layer4). For the class-conditioned "
    "view, it computes Grad-CAM maps at the final convolutional layer of each block (layer1.2.conv3, "
    "layer2.3.conv3, layer3.5.conv3, layer4.2.conv3)."
)

add_body(
    "The native activation maps are computed by registering forward hooks on each target layer, "
    "capturing the activation tensors during the forward pass, and then computing the mean across "
    "the channel dimension. The resulting H×W map is upsampled to input resolution (224×224) using "
    "bilinear interpolation and normalized to [0,1]."
)

add_formula("native_map = mean(activations, dim=channel)", "4.1")

add_body(
    "The Grad-CAM maps are computed using Captum's LayerGradCam implementation. For each target "
    "layer, the gradient of the target class logit with respect to the layer activations is "
    "computed, then globally averaged across spatial dimensions to produce channel importance "
    "weights. These weights are multiplied by the activations and summed across channels, followed "
    "by ReLU to retain only positive contributions. The resulting map is upsampled and normalized."
)

add_formula("α_k = (1/Z) Σ_i Σ_j ∂y/∂A^k_ij", "4.2")
add_formula("GradCAM = ReLU(Σ_k α_k · A^k)", "4.3")

add_body(
    "where α_k is the importance weight for channel k, y is the target class logit, A^k is the "
    "activation map for channel k, and Z is the number of spatial locations. The ResNetExtractor "
    "produces 8 LayerMap objects per image (4 native + 4 class-conditioned), providing a layer-"
    "by-layer view of attention patterns from early (layer1) to late (layer4) layers."
)

add_heading_styled("4.3.2 ViT Extractor (Transformer)", level=3)

add_body(
    "The VitExtractor produces dual-view attention maps for Vision Transformer models such as "
    "ViT-B/16. For the native view, it computes attention rollout maps showing how information "
    "flows from the CLS token to all input patches. For the class-conditioned view, it computes "
    "gradient-weighted attention (AxG) maps showing which attention patterns contribute to the "
    "target class prediction."
)

add_body(
    "Attention rollout is computed by iteratively multiplying attention matrices across all 12 "
    "transformer blocks. At each block, the attention matrix A (of shape [B, H, N, N] where B is "
    "batch size, H is number of heads, and N is number of tokens) is averaged across heads to "
    "produce a [B, N, N] matrix. A residual connection (identity matrix) is added with weight α "
    "(typically 0.5) to prevent attention collapse, then the matrix is row-normalized and "
    "multiplied with the accumulated rollout from previous blocks."
)

add_formula("R^(l) = (αI + (1-α)A^(l)) · R^(l-1)", "4.4")

add_body(
    "where R^(l) is the rollout matrix at block l, I is the identity matrix, A^(l) is the "
    "attention matrix at block l (averaged across heads), and α is the residual weight. The "
    "final rollout map is extracted from the CLS token row (row 0) and reshaped to the spatial "
    "grid (14×14 for ViT-B/16 with 224×224 input and 16×16 patch size), then upsampled to "
    "224×224."
)

add_body(
    "The gradient-weighted attention (AxG) maps are computed by taking the gradient of the target "
    "class logit with respect to each block's attention matrix, multiplying element-wise with the "
    "raw attention, applying ReLU, and extracting the CLS token row. This produces one class-"
    "conditioned map per block, showing which attention patterns at that layer contribute to the "
    "target class."
)

add_formula("AxG^(l) = ReLU(A^(l) ⊙ ∂y/∂A^(l))", "4.5")

add_body(
    "where A^(l) is the attention matrix at block l, y is the target class logit, and ⊙ denotes "
    "element-wise multiplication. The VitExtractor produces 25 LayerMap objects per image (12 "
    "native partial rollouts + 1 full rollout + 12 class-conditioned AxG maps), providing a "
    "detailed layer-by-layer view of attention flow and class-specific evidence."
)

# Table 4.2: Extractor Comparison
table2 = doc.add_table(rows=1, cols=5)
table2.style = 'Light Grid Accent 1'
table2.alignment = WD_TABLE_ALIGNMENT.CENTER

hdr_cells2 = table2.rows[0].cells
headers2 = ['Extractor', 'Model', 'Native Maps', 'Class-Cond Maps', 'Total Maps']
for i, header in enumerate(headers2):
    hdr_cells2[i].text = header
    for paragraph in hdr_cells2[i].paragraphs:
        for run in paragraph.runs:
            run.font.bold = True
            run.font.size = Pt(9)
    set_cell_shading(hdr_cells2[i], "4472C4")
    for paragraph in hdr_cells2[i].paragraphs:
        for run in paragraph.runs:
            run.font.color.rgb = RGBColor(255, 255, 255)

data2 = [
    ['ResNetExtractor', 'ResNet-50', '4 (layer1-4)', '4 (Grad-CAM)', '8'],
    ['VitExtractor', 'ViT-B/16', '13 (rollouts)', '12 (AxG)', '25'],
]

for row_data in data2:
    row_cells = table2.add_row().cells
    for i, cell_text in enumerate(row_data):
        row_cells[i].text = cell_text
        for paragraph in row_cells[i].paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(9)

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Table 4.2: Extractor Comparison")
set_font(run, size=10, italic=True)
p.paragraph_format.space_after = Pt(12)

# 4.4 Attention Quality Metrics
add_heading_styled("4.4 Attention Quality Metrics", level=2)

add_body(
    "The Metrics Module computes five quantitative measures of attention quality for each "
    "LayerMap, using ground-truth annotations (bounding boxes and part keypoints) from the "
    "CUB-200-2011 dataset. These metrics transform qualitative heatmaps into measurable, "
    "comparable numbers, addressing Limitation 2 (qualitative-only explanations)."
)

add_heading_styled("4.4.1 Focus Entropy", level=3)

add_body(
    "Focus entropy measures whether attention is localized (concentrated on a small region) or "
    "distributed (spread across the image). It is computed as the Shannon entropy of the "
    "normalized attention map, treated as a probability distribution."
)

add_formula("H = -Σ p_i · log2(p_i)", "4.6")

add_body(
    "where p_i is the normalized attention value at pixel i (p_i = map_i / Σ map_j). Low entropy "
    "(close to 0) indicates highly localized attention (all mass concentrated on one pixel), while "
    "high entropy (close to log2(N) where N is the number of pixels) indicates uniformly distributed "
    "attention. For a 224×224 image, the maximum entropy is log2(50176) ≈ 15.6 bits."
)

add_body(
    "Focus entropy is particularly useful for comparing CNN and ViT attention patterns. CNN "
    "Grad-CAM maps tend to have low entropy (localized on the object), while ViT attention rollout "
    "maps tend to have high entropy (distributed across many patches). This metric quantifies the "
    "intuitive observation that ViTs have more distributed attention than CNNs."
)

add_heading_styled("4.4.2 Object Relevance Share", level=3)

add_body(
    "Object relevance share measures the fraction of total attention falling inside the ground-"
    "truth object bounding box. It is computed as the sum of attention values inside the bbox "
    "divided by the total sum of attention values."
)

add_formula("obj_share = Σ_{i∈bbox} map_i / Σ_{all i} map_i", "4.7")

add_body(
    "where map_i is the attention value at pixel i, and the numerator sums only over pixels "
    "inside the bounding box. This metric ranges from 0 to 1, where 1 indicates all attention "
    "is focused on the object and 0 indicates no attention on the object (all attention on "
    "background)."
)

add_body(
    "Object relevance share is the primary metric for detecting spurious correlations. If a model "
    "is classifying based on background rather than the object, the obj_share will be low (close "
    "to 0). The screening engine uses this metric to flag classes where the mean obj_share is "
    "below a threshold, indicating suspected background reliance."
)

add_heading_styled("4.4.3 Background Sensitivity", level=3)

add_body(
    "Background sensitivity is the complement of object relevance share, measuring the fraction "
    "of attention falling outside the object bounding box."
)

add_formula("bg_sensitivity = 1 - obj_share", "4.8")

add_body(
    "This metric provides a direct measure of potential background reliance. High background "
    "sensitivity (close to 1) indicates that most attention is focused on the background, which "
    "is a red flag for spurious correlations."
)

add_heading_styled("4.4.4 Part Alignment", level=3)

add_body(
    "Part alignment measures the fraction of attention falling within a specified radius of "
    "ground-truth part keypoints (e.g., beak, head, wing for birds). It is computed by creating "
    "a binary mask of pixels within the radius of any keypoint, then summing attention values "
    "inside the mask."
)

add_formula("part_align = Σ_{i∈mask} map_i / Σ_{all i} map_i", "4.9")

add_body(
    "where the mask includes all pixels within radius r (default 6 pixels) of any visible part "
    "keypoint. This metric measures whether the model focuses on discriminative body parts. For "
    "bird classification, high part alignment indicates the model is attending to anatomically "
    "meaningful regions (beak, head, wings) rather than non-discriminative regions (background, "
    "body)."
)

add_heading_styled("4.4.5 Object Sensitivity", level=3)

add_body(
    "Object sensitivity is an alias for object relevance share, emphasizing the causal "
    "interpretation: if we were to mask the object region, how much would the prediction change? "
    "High object sensitivity indicates the model relies heavily on the object for its prediction."
)

# Table 4.3: Metrics Summary
table3 = doc.add_table(rows=1, cols=4)
table3.style = 'Light Grid Accent 1'
table3.alignment = WD_TABLE_ALIGNMENT.CENTER

hdr_cells3 = table3.rows[0].cells
headers3 = ['Metric', 'Range', 'High Value Means', 'Low Value Means']
for i, header in enumerate(headers3):
    hdr_cells3[i].text = header
    for paragraph in hdr_cells3[i].paragraphs:
        for run in paragraph.runs:
            run.font.bold = True
            run.font.size = Pt(9)
    set_cell_shading(hdr_cells3[i], "4472C4")
    for paragraph in hdr_cells3[i].paragraphs:
        for run in paragraph.runs:
            run.font.color.rgb = RGBColor(255, 255, 255)

data3 = [
    ['Focus Entropy', '0 - 15.6', 'Distributed attention', 'Localized attention'],
    ['Object Relevance', '0 - 1', 'Object-focused', 'Background-focused'],
    ['Background Sensitivity', '0 - 1', 'Background-focused', 'Object-focused'],
    ['Part Alignment', '0 - 1', 'Parts-focused', 'Non-parts-focused'],
    ['Object Sensitivity', '0 - 1', 'Object-reliant', 'Object-independent'],
]

for row_data in data3:
    row_cells = table3.add_row().cells
    for i, cell_text in enumerate(row_data):
        row_cells[i].text = cell_text
        for paragraph in row_cells[i].paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(9)

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Table 4.3: Attention Quality Metrics Summary")
set_font(run, size=10, italic=True)
p.paragraph_format.space_after = Pt(12)

# 4.5 Screening Engine
add_heading_styled("4.5 Automated Screening Engine", level=2)

add_body(
    "The Screening Engine aggregates per-image metrics into class-level statistics and produces "
    "evidence-backed verdicts, addressing Limitation 3 (no automated bias detection). It "
    "transforms individual LayerMap metrics into actionable insights about model behavior."
)

add_heading_styled("4.5.1 Verdict Types", level=3)

add_body(
    "The screening engine produces three types of verdicts: (1) class_bias flags indicating "
    "suspected spurious correlations for specific classes, (2) layer_role profiles characterizing "
    "what each layer attends to (edges, textures, parts), and (3) failure_diagnosis reports "
    "explaining why specific images were misclassified."
)

add_body(
    "Class bias flags are produced when the mean background sensitivity for a class exceeds the "
    "mean object relevance share by a configurable threshold (default 0.05). The flag includes "
    "the class name, the mean object and background shares, the number of images analyzed, and "
    "links to the top 3 evidence images (the images with the highest background sensitivity for "
    "that class)."
)

add_formula("flag if: mean(bg_sensitivity) > mean(obj_share) + threshold", "4.10")

add_body(
    "Layer role profiles are produced by analyzing the focus entropy and part alignment metrics "
    "across all images for each layer. Layers with low entropy are characterized as 'localized' "
    "(focusing on specific regions), while layers with high entropy are characterized as "
    "'distributed' (attending broadly). Layers with high part alignment are characterized as "
    "'part-focused' (attending to discriminative body parts)."
)

add_body(
    "Failure diagnosis reports are produced for misclassified images where the background "
    "sensitivity exceeds the object relevance share. The report includes the image ID, the true "
    "and predicted labels, the object and background shares, and the attention maps showing where "
    "the model focused. This enables researchers to quickly identify cases where the model "
    "'guessed from context' rather than recognizing the object."
)

add_heading_styled("4.5.2 Screening Algorithm", level=3)

# Algorithm pseudocode as a table
algo_table = doc.add_table(rows=1, cols=1)
algo_table.style = 'Light Grid Accent 1'
algo_table.alignment = WD_TABLE_ALIGNMENT.CENTER

cell = algo_table.rows[0].cells[0]
cell.text = (
    "Algorithm 1: Automated Screening Engine\n"
    "────────────────────────────────────────\n"
    "Input: List of LayerMap objects with computed metrics\n"
    "Output: ScreeningReport with verdicts and class statistics\n\n"
    "1. For each image in dataset:\n"
    "2.   Extract class-conditioned LayerMap for predicted class\n"
    "3.   Compute obj_share and bg_sensitivity using bbox\n"
    "4.   Store ImageEntry(image_id, class_name, correct, obj_share, bg_sensitivity)\n"
    "5. End For\n\n"
    "6. Group ImageEntries by class_name\n"
    "7. For each class:\n"
    "8.   Compute mean_obj_share = mean(obj_share for all images in class)\n"
    "9.   Compute mean_bg_share = mean(bg_sensitivity for all images in class)\n"
    "10.  If mean_bg_share > mean_obj_share + threshold:\n"
    "11.    Emit class_bias verdict with level='flag'\n"
    "12.  Else:\n"
    "13.    Emit class_bias verdict with level='info'\n"
    "14. End For\n\n"
    "15. For each misclassified image:\n"
    "16.   If bg_sensitivity > obj_share:\n"
    "17.     Emit failure_diagnosis verdict\n"
    "18. End For\n\n"
    "19. Return ScreeningReport(verdicts, class_stats)"
)
for paragraph in cell.paragraphs:
    for run in paragraph.runs:
        set_font(run, size=9, name='Consolas')

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Algorithm 1: Automated Screening Engine")
set_font(run, size=10, italic=True)
p.paragraph_format.space_after = Pt(12)

# 4.6 Causal Intervention Loop
add_heading_styled("4.6 Causal Intervention Loop", level=2)

add_body(
    "The Intervention Module enables causal debugging by masking regions of the input image and "
    "measuring how the prediction changes, addressing Limitation 4 (absence of causal reasoning). "
    "This moves beyond correlation (heatmaps showing where the model attends) to causation "
    "(testing whether masking that region actually changes the prediction)."
)

add_heading_styled("4.6.1 Occlusion Strategies", level=3)

add_body(
    "The intervention module supports three occlusion strategies for masking regions: (1) zero "
    "fill, which sets the masked region to 0 (the ImageNet mean after normalization, representing "
    "'no information'); (2) noise injection, which fills the region with Gaussian noise (mean 0, "
    "std 0.5), representing 'random information'; and (3) box-average blur, which replaces the "
    "region with its mean pixel value, representing 'coarse information without detail'."
)

add_body(
    "The zero-fill strategy is the default and most interpretable: it removes all information "
    "from the masked region, allowing us to test whether the model relies on that region for its "
    "prediction. If masking a region causes the target-class logit to drop significantly, this "
    "provides causal evidence that the model uses that region."
)

add_heading_styled("4.6.2 Intervention Procedure", level=3)

add_body(
    "The intervention procedure takes as input the model, the original image tensor, a list of "
    "regions to mask (specified as (x, y, width, height) tuples), the target class, and the "
    "occlusion strategy. For each region, it creates a masked copy of the input tensor, runs the "
    "model on the masked input, and computes the logit delta (change in target-class logit)."
)

add_formula("logit_delta = logit_before - logit_after", "4.11")

add_body(
    "A positive logit_delta indicates that masking the region caused the target-class logit to "
    "drop, providing evidence that the model relied on that region. A negative logit_delta "
    "indicates that masking the region caused the logit to increase, suggesting the region was "
    "'hurting' the prediction (perhaps containing confusing or contradictory information)."
)

add_body(
    "The intervention module also supports regular grid-based intervention, which divides the "
    "image into an N×N grid (default 4×4) and occludes each cell independently. This produces "
    "a spatial sensitivity map showing which regions of the image are most important for the "
    "prediction. The sensitivity map can be visualized as a heatmap and compared with the Grad-CAM "
    "or attention rollout maps to validate whether the attribution methods correctly identify "
    "important regions."
)

# 4.7 Interactive Interface
add_heading_styled("4.7 Interactive Interface (Gradio UI)", level=2)

add_body(
    "The Interactive Interface provides a Gradio-based web application that enables researchers "
    "to explore attention patterns and perform causal interventions without writing code, "
    "addressing Limitation 5 (no integrated debugging workflow). The interface is implemented in "
    "the attentionlens/ui/app.py module and provides a user-friendly way to interact with all "
    "framework components."
)

add_heading_styled("4.7.1 Interface Components", level=3)

add_body(
    "The interface consists of four main components: (1) an image upload area supporting file "
    "upload and clipboard paste, (2) a model selector allowing users to choose between ResNet-50 "
    "and ViT-B/16, (3) an 'Analyze' button that runs the full dual-view extraction and displays "
    "the gallery of attention maps, and (4) a 'Probe' section with coordinate sliders and mask "
    "size controls for causal intervention."
)

add_body(
    "When the user clicks 'Analyze', the interface runs the appropriate extractor (ResNet or ViT) "
    "on the uploaded image, produces all LayerMap objects, and displays them in a gallery with "
    "captions showing the layer name and view type. Each map is overlayed on the original image "
    "using a jet colormap with 65% transparency, allowing users to see both the attention pattern "
    "and the underlying image content."
)

add_body(
    "The 'Probe' section allows users to specify a region to mask by adjusting the center "
    "coordinates (X, Y) and mask size (width/height) using sliders. When the user clicks 'Run "
    "Probe', the interface runs the intervention module with the specified region and displays "
    "the results: the masked region coordinates, the prediction before and after masking, and the "
    "logit delta. This enables interactive hypothesis testing: users can hypothesize that a "
    "certain region is important, mask it, and immediately see whether the prediction changes."
)

add_heading_styled("4.7.2 Error Handling", level=3)

add_body(
    "The interface implements robust error handling to surface raw exceptions rather than silent "
    "failures. If an error occurs during analysis or probing, the interface displays the full "
    "exception message and traceback (limited to 3 frames) in the UI, enabling users to diagnose "
    "issues without checking server logs. This is particularly important for debugging "
    "architecture-specific issues (e.g., timm ViT compatibility, Captum version mismatches)."
)

# Placeholder for UI screenshot
add_placeholder("GRADIO UI SCREENSHOT - AttentionLens Interactive Interface showing dual-view attention maps and causal probe controls")

add_page_break()

# ============================================================
# Save
# ============================================================
output_path = r"C:\Users\pbkar\Desktop\VIT\sem 7\Explainable AI\Project\AttentionLens\AttentionLens_Report_Part4.docx"
doc.save(output_path)
print(f"Part 4 saved to: {output_path}")
print("Content: Proposed Methodology (~12 pages)")
