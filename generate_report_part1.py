"""Generate AttentionLens Report Part 1 as a Word document (~10 pages)."""
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import os

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

def add_numbered(text):
    p = doc.add_paragraph(style='List Number')
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.clear()
    run = p.add_run(text)
    set_font(run, size=11)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    return p

def add_page_break():
    doc.add_page_break()

def add_placeholder(label):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"\n{'─'*60}\n\n[ PLACEHOLDER: {label} ]\n\n{'─'*60}\n")
    set_font(run, size=10, italic=True, color=(120, 120, 120))
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(12)
    return p

# ============================================================
# TITLE PAGE
# ============================================================
for _ in range(4):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Explainable Artificial Intelligence (XAI)\nMini Project Report")
set_font(run, size=14, bold=True)
p.paragraph_format.space_after = Pt(30)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("AttentionLens: An Interactive Explainability and\nDebugging Framework for Vision Models")
set_font(run, size=16, bold=True)
p.paragraph_format.space_after = Pt(40)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Submitted by")
set_font(run, size=11)
p.paragraph_format.space_after = Pt(10)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Jaswanth Krishna Padarthi")
set_font(run, size=12, bold=True)
p.paragraph_format.space_after = Pt(6)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Registration No: [XXXXXXXXXX]")
set_font(run, size=11)
p.paragraph_format.space_after = Pt(30)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Under the Guidance of")
set_font(run, size=11)
p.paragraph_format.space_after = Pt(10)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("[Faculty Name]\n[Department]")
set_font(run, size=11, bold=True)
p.paragraph_format.space_after = Pt(40)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("School of Computer Science and Engineering\nVellore Institute of Technology (VIT)\nVellore, Tamil Nadu, India")
set_font(run, size=11)
p.paragraph_format.space_after = Pt(20)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("October 2026")
set_font(run, size=11, bold=True)

add_page_break()

# ============================================================
# ABSTRACT
# ============================================================
add_heading_styled("Abstract", level=1)

abstract_text = (
    "Deep learning models, particularly Convolutional Neural Networks (CNNs) and Vision "
    "Transformers (ViTs), have achieved remarkable performance in computer vision tasks "
    "ranging from image classification and object detection to semantic segmentation. "
    "However, their decision-making processes remain fundamentally opaque, operating as "
    "black boxes that process millions of parameters to produce predictions without "
    "providing any insight into the internal reasoning. This opacity raises critical "
    "concerns about trust, fairness, and reliability, particularly in high-stakes "
    "applications such as medical diagnosis, autonomous driving, and security systems "
    "where understanding why a model made a particular prediction is as important as the "
    "prediction itself. A model that classifies a skin lesion as malignant based on a "
    "ruler marking rather than the lesion characteristics may achieve high accuracy "
    "during testing but fail catastrophically in deployment when the ruler is absent."
)
add_body(abstract_text)

abstract_text2 = (
    "This project presents AttentionLens, an interactive explainability and debugging "
    "framework that makes attention mechanisms in vision models transparent and "
    "actionable. Unlike existing explainability tools that provide isolated heatmaps "
    "without quantitative rigor, AttentionLens introduces three key innovations. First, "
    "a unified dual-view abstraction that captures both native attention patterns and "
    "class-conditioned relevance evidence for both CNN and ViT architectures through a "
    "common schema, enabling fair apples-to-apples comparison across fundamentally "
    "different model types. Second, five quantitative attention quality metrics that "
    "transform qualitative heatmaps into measurable, comparable numbers. Third, an "
    "automated screening engine that converts per-image metrics into evidence-backed "
    "verdicts, detecting spurious correlations and diagnosing misclassifications with "
    "traceable proof."
)
add_body(abstract_text2)

abstract_text3 = (
    "The framework further integrates causal intervention capabilities, allowing users "
    "to mask image regions and observe how predictions change, thereby establishing "
    "cause-effect relationships between attention patterns and model behavior. "
    "Validation through planted-bias experiments on a Waterbirds-style synthetic "
    "dataset demonstrates that the screener correctly identifies background-driven "
    "classes with 100% precision, while ObjectNet natural-bias checks confirm that the "
    "framework detects real-world context reliance. A Gradio-based interactive interface "
    "provides researchers with an intuitive tool to explore layer-by-layer attention "
    "patterns and perform click-to-mask causal probing. With 21 unit and integration "
    "tests passing and support for both CPU and GPU execution, AttentionLens positions "
    "itself as a comprehensive, production-ready framework for vision model "
    "explainability, bridging the critical gap between attribution methods and "
    "actionable debugging insights."
)
add_body(abstract_text3)

# Keywords
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
run = p.add_run("Keywords: ")
set_font(run, size=10, bold=True)
run2 = p.add_run("Explainable AI (XAI), Vision Transformers, Attention Mechanisms, "
                 "Spurious Correlation Detection, Model Debugging, Grad-CAM, "
                 "Computer Vision, Deep Learning Interpretability")
set_font(run2, size=10, italic=True)
p.paragraph_format.space_before = Pt(12)

add_page_break()

# ============================================================
# 1. INTRODUCTION
# ============================================================
add_heading_styled("1. Introduction", level=1)

# 1.1 Background and Motivation
add_heading_styled("1.1 Background and Motivation", level=2)

add_body(
    "The field of artificial intelligence has witnessed an extraordinary transformation "
    "over the past decade, with deep learning emerging as the dominant paradigm for "
    "solving complex perceptual tasks. In computer vision specifically, the evolution "
    "from hand-crafted features to learned representations has led to performance that "
    "often surpasses human capability on benchmark tasks. The journey began with the "
    "seminal work of Krizhevsky et al. (2012) on AlexNet, which demonstrated that deep "
    "convolutional neural networks could achieve groundbreaking accuracy on the ImageNet "
    "Large Scale Visual Recognition Challenge. This was followed by a rapid succession "
    "of increasingly sophisticated architectures: VGGNet introduced deeper networks with "
    "smaller convolution filters, GoogLeNet pioneered the inception module for "
    "multi-scale feature extraction, and ResNet introduced skip connections that enabled "
    "training of networks with hundreds of layers by mitigating the vanishing gradient "
    "problem."
)

add_body(
    "While CNNs dominated the vision landscape for nearly a decade, the introduction of "
    "Vision Transformers (ViTs) by Dosovitskiy et al. (2020) marked a paradigm shift. "
    "By treating an image as a sequence of patches and applying the self-attention "
    "mechanism originally developed for natural language processing, ViTs demonstrated "
    "that transformer architectures could achieve state-of-the-art results on image "
    "classification when trained on sufficient data. The self-attention mechanism allows "
    "each patch to attend to all other patches, capturing long-range dependencies that "
    "are difficult for the local receptive fields of CNNs. Subsequent works such as "
    "DeiT (Training data-efficient image transformers, 2021), Swin Transformer (2021), "
    "and BEiT (2021) further refined the architecture, introducing training strategies "
    "and structural modifications that improved both efficiency and accuracy."
)

add_body(
    "Despite these remarkable achievements in predictive performance, a fundamental "
    "challenge persists: the opacity of the decision-making process. Deep learning "
    "models operate as black boxes, transforming input pixels through millions (or even "
    "billions) of parameters to produce output predictions, but providing no "
    "introspective access to the reasoning behind those predictions. This lack of "
    "transparency is not merely an academic concern; it has real-world consequences "
    "across numerous domains."
)

add_body(
    "In medical imaging, a deep learning model might achieve 95% accuracy in detecting "
    "pneumonia from chest X-rays, but if the model is actually detecting hospital "
    "specific markers or patient positioning rather than pathological features, it will "
    "fail when deployed at a different hospital. In autonomous driving, a self-driving "
    "car's perception system must be understood and trusted; a model that recognizes "
    "stop signs by detecting snow on the ground (a spurious correlation from training "
    "data collected in winter) will fail in summer conditions. In financial services, "
    "regulatory requirements under frameworks such as the EU AI Act and GDPR's right to "
    "explanation mandate that automated decisions affecting individuals must be "
    "explainable. A loan denial based on a black-box model without understandable "
    "reasoning is not legally defensible."
)

add_body(
    "These concerns have given rise to the field of Explainable Artificial Intelligence "
    "(XAI), which seeks to develop techniques and tools that make the behavior of "
    "machine learning models interpretable to humans. XAI methods can be broadly "
    "categorized into two approaches: inherently interpretable models (such as linear "
    "regression, decision trees, and attention-based architectures where the attention "
    "weights provide some visibility into information flow) and post-hoc explanation "
    "methods that analyze a trained model's behavior after the fact. The latter category "
    "includes gradient-based methods like Grad-CAM, Score-CAM, and Eigen-CAM that "
    "produce heatmaps highlighting regions important for a prediction; perturbation-"
    "based methods like LIME and SHAP that approximate model behavior locally using "
    "simpler interpretable models; and attention visualization techniques like attention "
    "rollout that trace how information flows through transformer layers."
)

add_body(
    "However, the current landscape of XAI tools for vision models, while rich in "
    "individual methods, lacks the unified, quantitative, and actionable characteristics "
    "needed for rigorous model debugging. Researchers and practitioners are often left "
    "with a collection of heatmaps that require subjective interpretation, with no "
    "systematic way to compare explanations across architectures, measure attention "
    "quality quantitatively, or automatically detect when a model is relying on spurious "
    "shortcuts rather than genuine features. This project addresses this critical gap "
    "through the development of AttentionLens, a comprehensive framework that unifies "
    "multiple explanation methods under a common schema, provides quantitative metrics "
    "for attention quality, automates the detection of spurious correlations, and enables "
    "causal debugging through intervention."
)

# 1.2 Problem Statement
add_heading_styled("1.2 Problem Statement", level=2)

add_body(
    "The central problem addressed by this project can be formally stated as follows: "
    "Given a trained vision model M (either a CNN or ViT) and an input image x, current "
    "XAI methods can produce visual explanations E(x) in the form of heatmaps or "
    "attribution maps. However, these explanations suffer from five fundamental "
    "limitations that prevent their effective use for model debugging and trust "
    "calibration."
)

add_heading_styled("Limitation 1: Architecture Fragmentation", level=3)
add_body(
    "Existing XAI tools are architecture-specific. Grad-CAM (Selvaraju et al., 2017) "
    "requires convolutional layers with spatial activation maps, making it inapplicable "
    "to pure transformer architectures. Attention rollout (Abnar and Zuidema, 2020) "
    "requires explicit attention matrices, making it inapplicable to CNNs. This "
    "fragmentation means that a researcher comparing a ResNet-50 with a ViT-B/16 must "
    "use entirely different toolchains, metrics, and visualization approaches for each "
    "model. Fair comparison becomes practically impossible because the explanations are "
    "incommensurable. No existing framework provides a unified schema that treats both "
    "architectures symmetrically, producing explanations in the same format that can be "
    "directly compared using identical metrics."
)

add_heading_styled("Limitation 2: Qualitative-Only Explanations", level=3)
add_body(
    "Heatmaps provide visual intuition but lack quantitative rigor. A Grad-CAM "
    "visualization might show bright red regions over both the object and the "
    "background, but without numerical metrics, a researcher cannot definitively state "
    "what fraction of the model's attention falls on the object versus the background. "
    "They cannot measure whether the model focuses on the bird's head (the "
    "discriminative part for species classification) or on the branch it is perched on. "
    "Without quantitative metrics computed against ground-truth annotations (bounding "
    "boxes, part keypoints), attention quality remains a matter of subjective visual "
    "inspection rather than rigorous measurement."
)

add_heading_styled("Limitation 3: No Automated Bias Detection", level=3)
add_body(
    "Current XAI tools show where a model looks but cannot automatically detect why it "
    "looks there or whether its reasoning is flawed. Spurious correlations, such as a "
    "model classifying waterbirds based on water background rather than bird "
    "morphology, require manual discovery through careful inspection of hundreds of "
    "heatmaps. At scale (thousands of images, dozens of classes), this manual process "
    "is impractical. No existing tool provides automated screening that aggregates "
    "per-image explanations into class-level statistics and produces evidence-backed "
    "verdicts about whether a model is relying on genuine features or spurious shortcuts."
)

add_heading_styled("Limitation 4: Absence of Causal Reasoning", level=3)
add_body(
    "Correlation-based explanations (heatmaps showing high activation in a region) do "
    "not establish causation. A Grad-CAM map might highlight both the object and a "
    "nearby text label, but without intervention, it is impossible to determine whether "
    "the model actually uses the text for its prediction or whether the text activation "
    "is merely a byproduct of correlated features. Causal reasoning requires "
    "intervention: masking the suspected region and observing whether the prediction "
    "changes. Existing tools rarely integrate such causal intervention into the "
    "explanation workflow, leaving researchers without a principled way to test "
    "hypotheses about model behavior."
)

add_heading_styled("Limitation 5: No Integrated Debugging Workflow", level=3)
add_body(
    "In practice, debugging a vision model requires combining multiple tools: an "
    "attribution method for heatmaps, a separate script for computing metrics, another "
    "tool for visualization, manual inspection for bias detection, and ad-hoc occlusion "
    "experiments for causal validation. This fragmented workflow is error-prone, "
    "difficult to reproduce, and does not scale to large datasets or production "
    "debugging scenarios. Researchers need an integrated framework that chains these "
    "steps together in a principled, reproducible pipeline."
)

add_body(
    "These five limitations collectively define the research problem: How can we design "
    "a unified, quantitative, and actionable framework for understanding and debugging "
    "vision models that overcomes architecture fragmentation, provides measurable "
    "attention quality metrics, automates bias detection, enables causal reasoning "
    "through intervention, and integrates all these capabilities into a coherent "
    "debugging workflow?"
)

# 1.3 Research Objectives
add_heading_styled("1.3 Research Objectives", level=2)

add_body(
    "To address the above problem, this project pursues six interconnected research "
    "objectives, each targeting one or more of the identified limitations. These "
    "objectives are designed to be individually verifiable through testing and "
    "experimentation, and collectively sufficient to demonstrate a comprehensive "
    "solution to the stated problem."
)

add_heading_styled("Objective 1: Unified Dual-View Abstraction", level=3)
add_body(
    "Design and implement a common schema (the LayerMap and ModelInspection data "
    "structures) that captures both native attention patterns and class-conditioned "
    "relevance evidence for both CNN and ViT architectures. The native view answers "
    "the question 'Where does the mechanism focus?' by capturing the model's own "
    "information flow (ViT attention rollout for transformers, mean-over-channel "
    "activation maps for CNNs). The class-conditioned view answers 'Where is the "
    "evidence for this specific prediction?' by capturing decision-relevant relevance "
    "(Grad-CAM for CNNs, gradient-weighted attention (AxG) for ViTs). Both views are "
    "produced as identically structured LayerMap objects, enabling downstream metrics, "
    "visualization, and screening to operate identically regardless of architecture. "
    "Success criterion: Both ResNet-50 and ViT-B/16 produce LayerMaps in the same "
    "schema for the same input image, with identical field structures."
)

add_heading_styled("Objective 2: Quantitative Attention Metrics", level=3)
add_body(
    "Implement five quantitative metrics that transform qualitative heatmaps into "
    "measurable, comparable numbers. Focus entropy measures whether attention is "
    "localized (low entropy, like ResNet) or distributed (high entropy, like ViT) using "
    "Shannon entropy of the normalized map. Object relevance share measures the "
    "fraction of total relevance falling inside the ground-truth object bounding box. "
    "Part alignment measures the fraction of relevance captured within a specified "
    "radius of ground-truth part keypoints (head, wing, bill for birds). Background "
    "sensitivity measures the relevance share outside the object bbox as a proxy for "
    "potential background reliance. Object sensitivity is the complement, measuring "
    "relevance share inside the object. Success criterion: Metrics produce "
    "numerically distinct, semantically meaningful values for known object-focused "
    "versus background-focused attention patterns, validated against CUB-200 ground "
    "truth annotations."
)

add_heading_styled("Objective 3: Automated Screening Engine", level=3)
add_body(
    "Build a verdict generation system that aggregates per-image metrics into "
    "class-level statistics and produces evidence-backed flags. The screener computes "
    "mean object relevance share and mean background relevance share for each class "
    "across all images of that class. When the mean background share exceeds the mean "
    "object share by a configurable threshold, the screener emits a class_bias flag "
    "with level 'flag' (warning), indicating suspected spurious correlation. Each flag "
    "includes links to the specific evidence images and maps that triggered it, "
    "enabling traceable investigation. The screener also produces failure diagnoses for "
    "misclassified images where background reliance is detected, and layer-role profiles "
    "that characterize what each layer attends to (edges, textures, parts). Success "
    "criterion: On a planted-bias dataset where class-background correlations are "
    "artificially introduced, the screener correctly identifies the correlated classes "
    "with no false positives on uncorrelated classes."
)

add_heading_styled("Objective 4: Causal Intervention Loop", level=3)
add_body(
    "Develop occlusion-based intervention tools that establish cause-effect "
    "relationships between attention patterns and model behavior. The intervention "
    "module masks specified regions of the input image using configurable strategies "
    "(zero-fill, noise injection, or box-average blur), re-runs the model, and measures "
    "the change in the target-class logit. A positive logit delta indicates that the "
    "masked region was relied upon by the model. Regular grid-based intervention "
    "divides the image into an NxN grid and occludes each cell, producing a spatial "
    "sensitivity map that can be compared with the Grad-CAM or attention rollout maps. "
    "Success criterion: Masking the head region of a bird image causes a significant "
    "drop in the correct-class logit, demonstrating causal dependence on that region."
)

add_heading_styled("Objective 5: Interactive Debugging Interface", level=3)
add_body(
    "Create a user-friendly Gradio web application that enables researchers to explore "
    "attention patterns layer-by-layer and perform click-to-mask causal probing without "
    "writing code. The interface provides a model selector (ResNet-50 or ViT-B/16), an "
    "image upload area, an 'Analyze' button that produces the full dual-view gallery "
    "of attention maps, and a 'Probe' section with coordinate sliders and mask size "
    "controls for causal intervention. The interface surfaces raw exceptions rather than "
    "silent failures, making debugging straightforward. Success criterion: An "
    "end-to-end interactive session (upload, analyze, probe) completes in under 30 "
    "seconds on CPU."
)

add_heading_styled("Objective 6: Validation Through Rigorous Experiments", level=3)
add_body(
    "Validate the entire framework through two complementary experiments. The "
    "planted-bias experiment (Waterbirds-style) creates a synthetic dataset where "
    "class-background correlations are artificially introduced, fine-tunes a classifier "
    "on this biased data, and verifies that the screener correctly identifies the "
    "planted shortcuts. The ObjectNet natural-bias check runs the framework on a "
    "standard ImageNet-pretrained model evaluated on objects in unusual contexts "
    "(objects on strange backgrounds, unusual rotations), verifying that the screener "
    "detects real-world context reliance. Together, these experiments prove that the "
    "framework catches both synthetic shortcuts (where we know the ground truth) and "
    "natural biases (where the ground truth is unknown but the effect is real). Success "
    "criterion: Both experiments produce evidence-backed verdicts that are verifiably "
    "correct."
)

# 1.4 Expected Contributions
add_heading_styled("1.4 Expected Contributions", level=2)

add_body(
    "This project makes the following contributions to the field of explainable "
    "artificial intelligence for computer vision. Each contribution addresses one or "
    "more of the limitations identified in the problem statement and is designed to "
    "advance the state of the art in vision model debugging and trust calibration."
)

add_body(
    "Contribution 1: A unified dual-view abstraction that treats CNN and ViT "
    "architectures symmetrically. Prior to this work, no framework provides a common "
    "schema for comparing attention patterns across fundamentally different mechanisms. "
    "The LayerMap data structure captures both the native information flow and the "
    "class-conditioned decision evidence in an architecture-agnostic format, enabling "
    "the first fair, apples-to-apples comparison of attention patterns between ResNet "
    "and ViT models. This contribution directly addresses Limitation 1 (architecture "
    "fragmentation)."
)

add_body(
    "Contribution 2: Five quantitative attention quality metrics computed against "
    "ground-truth annotations. While individual metrics such as pointing game and IoU-"
    "based saliency evaluation exist in isolation, no framework integrates a "
    "comprehensive suite of metrics that together characterize attention focus, "
    "localization, part sensitivity, and background reliance. These metrics, computed "
    "per image per layer per view, provide the quantitative foundation that transforms "
    "XAI from a qualitative art into a measurable science. This contribution addresses "
    "Limitation 2 (qualitative-only explanations)."
)

add_body(
    "Contribution 3: An automated screening engine that produces evidence-backed "
    "verdicts. This is the first tool in the XAI ecosystem that ships with automated "
    "bias detection. Every verdict includes traceable evidence links to the specific "
    "images and attention maps that triggered it, enabling researchers to investigate "
    "issues systematically rather than relying on manual inspection of hundreds of "
    "heatmaps. This contribution addresses Limitation 3 (no automated bias detection)."
)

add_body(
    "Contribution 4: An integrated causal debugging loop that combines attribution, "
    "intervention, and verdict generation in a single workflow. By enabling users to "
    "hypothesize (from heatmaps), intervene (by masking), and measure (logit change), "
    "the framework moves beyond post-hoc correlation to establish causal relationships "
    "between attention patterns and model predictions. This contribution addresses "
    "Limitation 4 (absence of causal reasoning) and Limitation 5 (no integrated "
    "debugging workflow)."
)

add_body(
    "Contribution 5: Comprehensive validation through both synthetic and natural bias "
    "experiments. The planted-bias experiment provides provably true positive detection "
    "(we know exactly what shortcut was planted), while the ObjectNet check demonstrates "
    "detection of real-world context reliance. Together, these experiments validate that "
    "the framework is both sensitive (catches biases) and specific (does not over-flag "
    "genuine object-focused attention)."
)

# 1.5 Scope and Positioning
add_heading_styled("1.5 Scope and Positioning", level=2)

add_body(
    "It is important to clearly delineate what AttentionLens is and is not. "
    "AttentionLens is a tool in the tradition of SHAP, Captum, and Lucid; it is not a "
    "new attribution algorithm. The XAI method space is saturated with gradient-based "
    "methods (Grad-CAM and its many variants, Integrated Gradients, Guided Backprop), "
    "perturbation-based methods (LIME, SHAP, RISE), and attention-based methods "
    "(attention rollout, attention×gradient). The contribution of AttentionLens lies "
    "not in inventing a new attribution method but in building a unified instrument "
    "over existing methods and adding the automated verdict layer that no other tool "
    "provides."
)

add_body(
    "AttentionLens is not a training framework; it does not propose new architectures "
    "or training objectives. It does use training in the planted-bias experiment "
    "(fine-tuning a classifier on biased data), but this is for validation purposes "
    "only, not as a contribution. AttentionLens is not an NLP or multimodal "
    "explainability tool; the current version (v1) targets vision models exclusively "
    "(CNNs and ViTs). AttentionLens is not a production-deployment tool; it is a "
    "research and debugging instrument designed for model developers who need to "
    "understand and trust their models before deployment."
)

add_body(
    "The positioning statement for AttentionLens captures its value proposition: "
    "'Grad-CAM shows you a heatmap. AttentionLens tells you the model cheated, and "
    "shows you the proof.' This distinguishes it from the long tail of attribution "
    "methods that provide visualizations without interpretation, and from the small "
    "number of tools that provide interpretation without automation."
)

# 1.6 Report Organization
add_heading_styled("1.6 Report Organization", level=2)

add_body(
    "The remainder of this report is organized as follows. Section 2 presents a "
    "comprehensive literature review of related work in explainable AI for computer "
    "vision, covering gradient-based attribution methods, perturbation-based methods, "
    "attention visualization techniques, spurious correlation detection, and existing "
    "XAI toolkits. A comparison table summarizes 50+ reviewed journal papers with their "
    "methods, findings, and limitations. Section 3 describes the datasets used for "
    "experimentation: CUB-200-2011 for fine-grained bird classification with ground-"
    "truth bounding boxes and part annotations, ObjectNet for natural-bias validation, "
    "and ImageNet subsets for pretrained model evaluation. The preprocessing pipeline "
    "is detailed with normalization parameters and augmentation strategies."
)

add_body(
    "Section 4 presents the proposed methodology, including the unified dual-view "
    "abstraction (LayerMap and ModelInspection schemas), the ResNet-50 extractor "
    "(Grad-CAM plus channel-weighted activation maps), the ViT-B/16 extractor (attention "
    "rollout plus gradient-weighted attention), the five attention quality metrics, the "
    "automated screening engine with verdict types and thresholds, the causal "
    "intervention loop with occlusion strategies, and the Gradio user interface design. "
    "Algorithm pseudocode is provided for the key components."
)

add_body(
    "Section 5 details the experimental setup, including hardware configuration, "
    "software stack, model configurations, and training hyperparameters. Results are "
    "presented for each milestone (M1 through M8), including dual-view visualization "
    "outputs, quantitative metrics on CUB-200, the planted-bias experiment results "
    "(with class-level statistics and verdict details), and the ObjectNet natural-bias "
    "check results. Confusion matrices, performance tables, and analysis graphs are "
    "included."
)

add_body(
    "Section 6 provides in-depth analysis of the XAI integration, demonstrating how "
    "AttentionLens explains model behavior through layer-by-layer attention analysis, "
    "spurious correlation detection, architecture comparison (ResNet vs. ViT), and "
    "failure diagnosis. This is the most important section of the report, as it "
    "demonstrates the framework's ability to transform raw attributions into actionable "
    "insights. Section 7 conducts an ablation study examining the impact of individual "
    "framework components. Section 8 concludes with a summary of contributions, "
    "limitations, and directions for future work."
)

add_page_break()

# ============================================================
# Save
# ============================================================
output_path = r"C:\Users\pbkar\Desktop\VIT\sem 7\Explainable AI\Project\AttentionLens\AttentionLens_Report_Part1.docx"
doc.save(output_path)
print(f"Part 1 saved to: {output_path}")
