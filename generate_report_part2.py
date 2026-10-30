"""Generate AttentionLens Report Part 2: Literature Review (~10 pages)."""
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
from docx.enum.table import WD_TABLE_ALIGNMENT

doc = Document()

# ── Page Setup (A4, 1-inch margins) ──
for section in doc.sections:
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    # Page number at bottom center
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

# ── Style Helpers ──
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
    p.paragraph_format.first_line_indent = Inches(0.0)
    return p

def add_bullet(text):
    p = doc.add_paragraph(style='List Bullet')
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.clear()
    run = p.add_run(text)
    set_font(run, size=11)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    return p

def add_placeholder(label):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"\n{'─'*60}\n\n[ PLACEHOLDER: {label} ]\n\n{'─'*60}\n")
    set_font(run, size=10, italic=True, color=(120, 120, 120))
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(12)
    return p

def add_formula(formula_text, label):
    """Add a centered formula with equation number."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(formula_text)
    set_font(run, size=11, italic=True)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    
    # Add equation number on the right
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run2 = p2.add_run(f"({label})")
    set_font(run2, size=10)
    p2.paragraph_format.space_after = Pt(8)
    return p

def set_cell_shading(cell, color):
    """Set cell background color."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def add_page_break():
    doc.add_page_break()

# ============================================================
# 2. LITERATURE REVIEW
# ============================================================
add_heading_styled("2. Literature Review", level=1)

add_body(
    "This section presents a comprehensive review of existing work in explainable "
    "artificial intelligence (XAI) for computer vision, covering gradient-based "
    "attribution methods, perturbation-based approaches, attention visualization "
    "techniques for Vision Transformers, spurious correlation detection, and existing "
    "XAI toolkits. The review identifies the research gaps that motivate the development "
    "of AttentionLens."
)

# 2.1 Gradient-Based Attribution Methods
add_heading_styled("2.1 Gradient-Based Attribution Methods", level=2)

add_body(
    "Gradient-based attribution methods compute the importance of each input feature "
    "(pixel or region) by analyzing the gradient of the model's output with respect to "
    "the input. These methods leverage the fact that deep neural networks are "
    "differentiable, allowing backpropagation to trace which input regions most "
    "influence a given prediction."
)

add_heading_styled("2.1.1 Saliency Maps and Gradient × Input", level=3)
add_body(
    "The earliest gradient-based approach is the saliency map introduced by Simonyan "
    "et al. (2013), which computes the gradient of the target class score with respect "
    "to each input pixel. The saliency map S is defined as:"
)

add_formula("S_ij = ∂y/∂x_ij", "2.1")

add_body(
    "where y is the output score for the target class and x_ij is the pixel at position "
    "(i,j). While intuitive, raw saliency maps are often noisy and difficult to interpret. "
    "Gradient × Input (Kindermans et al., 2016) improves upon this by multiplying the "
    "gradient by the input itself, giving higher importance to pixels that are both "
    "non-zero and have high gradient magnitude."
)

add_heading_styled("2.1.2 Grad-CAM and Variants", level=3)
add_body(
    "Gradient-weighted Class Activation Mapping (Grad-CAM), introduced by Selvaraju "
    "et al. (2017), is one of the most widely used attribution methods for CNNs. "
    "Grad-CAM computes the importance of each channel in the final convolutional layer "
    "by globally averaging the gradients, then producing a coarse localization map "
    "highlighting important regions. The Grad-CAM importance weight α_k for channel k "
    "is computed as:"
)

add_formula("α_k = (1/Z) Σ_i Σ_j ∂y/∂A^k_ij", "2.2")

add_body(
    "where A^k_ij is the activation map at position (i,j) for channel k, y is the "
    "target class score, and Z is the number of pixels in the feature map. The final "
    "Grad-CAM heatmap is then:"
)

add_formula("α Grad-CAM = ReLU(Σ_k α_k A^k)", "2.3")

add_body(
    "The ReLU operation retains only features that have a positive influence on the "
    "class of interest, discarding negative contributions that may belong to other "
    "classes. Grad-CAM has inspired numerous variants: Guided Grad-CAM combines Grad-CAM "
    "with guided backpropagation for higher resolution; Grad-CAM++ improves localization "
    "by using weighted combinations of positive gradients; Score-CAM replaces gradients "
    "with score-based weights; Eigen-CAM uses principal component analysis on feature "
    "maps; and HiResCAM provides guaranteed faithful explanations by avoiding the "
    "averaging step that can cancel out important features."
)

add_body(
    "While Grad-CAM and its variants are effective for CNNs, they require convolutional "
    "layers with spatial structure and cannot be directly applied to Vision Transformers, "
    "which lack convolutional layers entirely. This architectural limitation motivates "
    "the need for architecture-agnostic explanation methods."
)

# 2.2 Perturbation-Based Methods
add_heading_styled("2.2 Perturbation-Based Methods", level=2)

add_body(
    "Perturbation-based methods estimate feature importance by observing how the model's "
    "output changes when input features are systematically perturbed (masked, occluded, "
    "or noised). These methods are model-agnostic and can be applied to any black-box "
    "model, but they are computationally expensive as they require multiple forward passes."
)

add_heading_styled("2.2.1 LIME (Local Interpretable Model-agnostic Explanations)", level=3)
add_body(
    "LIME, introduced by Ribeiro et al. (2016), explains individual predictions by "
    "learning a local interpretable model (typically linear) around the prediction. For "
    "image classification, LIME superpixels the image into segments, then generates "
    "perturbed samples by randomly turning segments on or off. It fits a weighted linear "
    "model to these perturbed samples, where the weights are based on proximity to the "
    "original image. The LIME explanation is defined as:"
)

add_formula("ξ(x) = argmin_g∈G L(f, g, π_x) + Ω(g)", "2.4")

add_body(
    "where f is the original complex model, g is the interpretable model from class G, "
    "π_x is a proximity measure around instance x, L is a loss function measuring how "
    "well g approximates f in the locality defined by π_x, and Ω is a complexity "
    "penalty. LIME provides locally faithful explanations but suffers from instability: "
    "different random seeds can produce substantially different explanations for the "
    "same input."
)

add_heading_styled("2.2.2 SHAP (SHapley Additive exPlanations)", level=3)
add_body(
    "SHAP, introduced by Lundberg and Lee (2017), is grounded in cooperative game "
    "theory. It assigns each feature an importance value (Shapley value) that "
    "represents its marginal contribution to the prediction across all possible "
    "coalitions of features. The Shapley value φ_i for feature i is computed as:"
)

add_formula("φ_i = Σ_{S⊆N\\{i}} |S|!(|N|-|S|-1)!/|N|! [f(S∪{i}) - f(S)]", "2.5")

add_body(
    "where N is the set of all features, S is a subset of features not including i, "
    "and f(S) is the model output for coalition S. SHAP provides theoretically "
    "guaranteed properties: local accuracy, missingness, and consistency. However, "
    "computing exact Shapley values is NP-hard, requiring approximations. For images, "
    "SHAP typically operates on superpixels rather than individual pixels, and Kernel "
    "SHAP uses a weighted linear regression to estimate Shapley values efficiently."
)

# 2.3 Attention Visualization for Vision Transformers
add_heading_styled("2.3 Attention Visualization for Vision Transformers", level=2)

add_body(
    "Vision Transformers (ViTs) process images as sequences of patches through self-"
    "attention layers. Each attention layer computes attention weights that determine "
    "how much each patch attends to every other patch. These attention weights provide "
    "a natural starting point for explainability, as they directly encode the "
    "information flow through the model."
)

add_heading_styled("2.3.1 Attention Rollout", level=3)
add_body(
    "Attention rollout, introduced by Abnar and Zuidema (2020), aggregates attention "
    "weights across all layers to produce a single attention map showing how information "
    "flows from input patches to the final classification token. The rollout is computed "
    "iteratively by multiplying attention matrices across layers. For a single layer with "
    "attention matrix A, the rollout R is updated as:"
)

add_formula("R^{(l)} = (αI + (1-α)A^{(l)}) · R^{(l-1)}", "2.6")

add_body(
    "where I is the identity matrix (representing residual connections), α is a "
    "hyperparameter controlling the balance between residual and attention flow "
    "(typically α=0.5), and R^{(0)} = I. The final rollout map shows the cumulative "
    "attention from the CLS token to all input patches."
)

add_body(
    "Attention rollout is class-agnostic: it shows where information flows, not which "
    "regions are important for a specific class prediction. To obtain class-conditioned "
    "explanations, researchers have proposed gradient-weighted attention rollout, where "
    "the rollout is weighted by the gradient of the target class score with respect to "
    "the attention weights."
)

add_heading_styled("2.3.2 Attention × Gradient (AxG)", level=3)
add_body(
    "Attention × Gradient (AxG) computes class-conditioned attention by multiplying "
    "the raw attention weights by their gradients with respect to the target class. "
    "For each attention head h and layer l, the AxG map is:"
)

add_formula("AxG^{(l,h)} = ReLU(A^{(l,h)} ⊙ ∂y/∂A^{(l,h)})", "2.7")

add_body(
    "where A^{(l,h)} is the attention matrix for head h at layer l, y is the target "
    "class score, and ⊙ denotes element-wise multiplication. The ReLU retains only "
    "attention patterns with positive gradients, indicating regions that increase the "
    "target class score. AxG is the Vision Transformer analogue of Grad-CAM: it provides "
    "per-layer, class-specific explanations that can be directly compared to CNN Grad-CAM "
    "maps."
)

add_body(
    "Recent work has explored more sophisticated ViT explanation methods: Attention "
    "Flow (Chefer et al., 2021) uses optimal transport to align attention with relevance; "
    "Transformer Interpretability Beyond Attention Visualization (Chefer et al., 2022) "
    "integrates attention with gradient information; and ATAT (Abnar and Zuidema, 2020) "
    "proposes full rollout with residual connections. However, these methods remain "
    "architecture-specific and cannot be directly compared to CNN attribution methods "
    "without a unified framework."
)

# 2.4 Spurious Correlation Detection
add_heading_styled("2.4 Spurious Correlation Detection", level=2)

add_body(
    "Spurious correlations occur when a model learns to associate a class with an "
    "irrelevant feature (such as background, watermark, or artifact) rather than the "
    "true discriminative features. These shortcuts lead to models that achieve high "
    "accuracy on training and test sets but fail catastrophically in deployment when "
    "the spurious feature is absent or changed."
)

add_heading_styled("2.4.1 Waterbirds Dataset and Background Bias", level=3)
add_body(
    "The Waterbirds dataset, introduced by Sagawa et al. (2020), is a benchmark for "
    "studying spurious correlations. It composes bird images from the CUB-200 dataset "
    "onto backgrounds that are correlated with species: water birds are placed on water "
    "backgrounds and land birds on land backgrounds with high probability (e.g., 95% "
    "correlation). A model trained on this biased dataset may learn to classify based "
    "on background rather than bird morphology, achieving high accuracy on the biased "
    "test set but failing on a balanced evaluation set where background and species are "
    "decorrelated."
)

add_body(
    "Detecting background bias requires methods that can separate object-focused "
    "attention from background-focused attention. Grad-CAM heatmaps can reveal whether "
    "a model focuses on the bird or the background, but without quantitative metrics, "
    "this detection requires manual inspection. Automated detection requires systematic "
    "measurement of attention distribution across object and background regions."
)

add_heading_styled("2.4.2 ObjectNet and Context Reliance", level=3)
add_body(
    "ObjectNet, introduced by Barbu et al. (2019), is a dataset designed to test "
    "object recognition under natural variation. It presents objects in unusual "
    "contexts: unusual viewpoints, unusual backgrounds, and unusual rotations. Standard "
    "ImageNet-trained models experience a dramatic accuracy drop on ObjectNet "
    "(from ~80% to ~20%), revealing their reliance on contextual cues rather than "
    "invariant object features."
)

add_body(
    "ObjectNet provides a natural-bias benchmark: if a model's attention is dominated "
    "by background when objects appear in unusual contexts, this indicates context "
    "reliance. Detecting this requires quantitative measurement of object versus "
    "background attention, combined with automated verdict generation to flag classes "
    "or images where context dominates."
)

# 2.5 Existing XAI Toolkits and Frameworks
add_heading_styled("2.5 Existing XAI Toolkits and Frameworks", level=2)

add_body(
    "Several open-source toolkits provide implementations of XAI methods for vision "
    "models. While these toolkits are valuable for researchers, they lack the unified "
    "abstraction, quantitative metrics, and automated screening capabilities that "
    "AttentionLens provides."
)

add_heading_styled("2.5.1 Captum", level=3)
add_body(
    "Captum (Kokhlikyan et al., 2020) is a comprehensive PyTorch-based library for "
    "model interpretability. It provides implementations of numerous attribution methods "
    "including Grad-CAM, Integrated Gradients, DeepLIFT, SHAP, and LIME. Captum is "
    "highly flexible and supports custom models, but it provides individual attribution "
    "methods without integration, metrics, or automated diagnosis. Users must manually "
    "combine methods, compute metrics, and interpret results."
)

add_heading_styled("2.5.2 SHAP Library", level=3)
add_body(
    "The SHAP library (Lundberg and Lee, 2017) provides efficient implementations of "
    "Shapley value estimation for various model types. For images, Kernel SHAP operates "
    "on superpixels and provides locally faithful explanations. However, SHAP is "
    "computationally expensive (requiring thousands of model evaluations per image) and "
    "provides only feature importance values, not spatial attention maps. It lacks "
    "architecture-specific optimizations for CNNs or ViTs."
)

add_heading_styled("2.5.3 torchcam and Lucid", level=3)
add_body(
    "torchcam (Godefroy, 2020) provides a collection of CAM (Class Activation Mapping) "
    "methods for PyTorch models, including Grad-CAM, Grad-CAM++, Score-CAM, and "
    "Eigen-CAM. It is lightweight and easy to use but focuses exclusively on CNN "
    "attribution methods. Lucid (Carter et al., 2019) is a TensorFlow-based framework "
    "for neural network interpretability, providing tools for feature visualization, "
    "neuron attribution, and model inspection. Lucid is powerful but TensorFlow-specific "
    "and lacks integration with modern transformer architectures."
)

add_heading_styled("2.5.4 What-If Tool and Facets", level=3)
add_body(
    "The What-If Tool (Wexler et al., 2020) is an interactive web interface for "
    "exploring ML models. It allows users to visualize predictions, examine feature "
    "importances, and perform counterfactual analysis. While the What-If Tool provides "
    "interactive exploration, it is designed for tabular data and lacks support for "
    "vision models. Facets (Wexler et al., 2019) is a suite of visualizations for "
    "understanding datasets, but it does not provide model explanation capabilities."
)

# 2.6 Comparative Analysis
add_heading_styled("2.6 Comparative Analysis of Existing Approaches", level=2)

add_body(
    "Table 2.1 provides a comprehensive comparison of existing XAI methods and toolkits "
    "across key dimensions relevant to vision model debugging. This comparison highlights "
    "the research gaps that motivate AttentionLens."
)

# Create comparison table
table = doc.add_table(rows=1, cols=6)
table.style = 'Light Grid Accent 1'
table.alignment = WD_TABLE_ALIGNMENT.CENTER

# Header row
hdr_cells = table.rows[0].cells
headers = ['Method/Tool', 'Architecture', 'Quantitative Metrics', 'Automated Screening', 'Causal Intervention', 'Unified Schema']
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

# Data rows
data = [
    ['Grad-CAM', 'CNN only', '✗', '✗', '✗', '✗'],
    ['Grad-CAM++', 'CNN only', '✗', '✗', '✗', '✗'],
    ['Attention Rollout', 'ViT only', '✗', '✗', '✗', '✗'],
    ['LIME', 'Both', '✗', '✗', '✓ (manual)', '✗'],
    ['SHAP', 'Both', '✓ (feature)', '✗', '✗', '✗'],
    ['Captum', 'Both', '✗', '✗', '✗', '✗'],
    ['torchcam', 'CNN only', '✗', '✗', '✗', '✗'],
    ['Lucid', 'CNN only', '✗', '✗', '✗', '✗'],
    ['What-If Tool', 'Tabular', '✓ (basic)', '✗', '✓', '✗'],
    ['AttentionLens', 'Both', '✓ (5 metrics)', '✓', '✓', '✓'],
]

for row_data in data:
    row_cells = table.add_row().cells
    for i, cell_text in enumerate(row_data):
        row_cells[i].text = cell_text
        for paragraph in row_cells[i].paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(9)

doc.add_paragraph()  # Spacing after table

# Table caption
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Table 2.1: Comparison of XAI Methods and Toolkits")
set_font(run, size=10, italic=True)
p.paragraph_format.space_after = Pt(12)

add_body(
    "Table 2.1 reveals several critical gaps in existing approaches. First, most "
    "attribution methods are architecture-specific: Grad-CAM works only for CNNs, while "
    "attention rollout applies only to ViTs. This fragmentation prevents fair comparison "
    "across architectures. Second, no existing toolkit provides quantitative metrics "
    "that characterize attention quality (focus, localization, part sensitivity, "
    "background reliance). Third, automated screening for spurious correlations is "
    "absent from all current tools. Fourth, causal intervention capabilities are either "
    "missing or require manual implementation. Finally, no framework provides a unified "
    "schema that treats CNNs and ViTs symmetrically."
)

# 2.7 Research Gap Identification
add_heading_styled("2.7 Research Gap Identification", level=2)

add_body(
    "The literature review reveals five critical research gaps that motivate the "
    "development of AttentionLens:"
)

add_body(
    "Gap 1: Architecture Fragmentation. Existing XAI methods are architecture-specific, "
    "preventing fair comparison between CNNs and ViTs. No unified schema treats both "
    "architectures symmetrically, producing explanations in the same format that can be "
    "directly compared using identical metrics."
)

add_body(
    "Gap 2: Lack of Quantitative Metrics. While attribution methods produce heatmaps, "
    "no framework provides a comprehensive suite of quantitative metrics that "
    "characterize attention quality against ground-truth annotations. Metrics such as "
    "focus entropy, object relevance share, part alignment, and background sensitivity "
    "are missing from existing toolkits."
)

add_body(
    "Gap 3: No Automated Bias Detection. Current tools require manual inspection of "
    "heatmaps to detect spurious correlations. At scale (thousands of images, dozens of "
    "classes), this is impractical. No existing framework provides automated screening "
    "that aggregates per-image metrics into class-level statistics and produces "
    "evidence-backed verdicts."
)

add_body(
    "Gap 4: Absence of Causal Integration. Attribution methods show correlation (where "
    "the model attends) but not causation (whether masking that region changes the "
    "prediction). No framework integrates causal intervention into the explanation "
    "workflow, leaving researchers without a principled way to test hypotheses about "
    "model behavior."
)

add_body(
    "Gap 5: Fragmented Debugging Workflow. In practice, debugging a vision model "
    "requires combining multiple tools: attribution for heatmaps, separate scripts for "
    "metrics, manual inspection for bias detection, and ad-hoc occlusion experiments. "
    "No integrated framework chains these steps together in a principled, reproducible "
    "pipeline."
)

add_body(
    "AttentionLens addresses all five gaps through its unified dual-view abstraction, "
    "quantitative metrics, automated screening engine, causal intervention loop, and "
    "integrated debugging interface. The following sections detail the methodology and "
    "experimental validation that demonstrate how AttentionLens fills these gaps."
)

# Placeholder for architecture diagram
add_placeholder("SYSTEM ARCHITECTURE DIAGRAM - AttentionLens Framework Overview showing Extractors, Metrics, Screening Engine, and UI components")

# Placeholder for project running screenshot
add_placeholder("PROJECT RUNNING SCREENSHOT - Gradio UI showing dual-view attention maps for a sample image")

add_page_break()

# ============================================================
# Save
# ============================================================
output_path = r"C:\Users\pbkar\Desktop\VIT\sem 7\Explainable AI\Project\AttentionLens\AttentionLens_Report_Part2.docx"
doc.save(output_path)
print(f"Part 2 saved to: {output_path}")
