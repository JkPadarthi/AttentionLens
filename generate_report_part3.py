"""Generate AttentionLens Report Part 3: Dataset Description and Preprocessing (~12 pages)."""
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
# 3. DATASET DESCRIPTION AND PREPROCESSING
# ============================================================
add_heading_styled("3. Dataset Description and Preprocessing", level=1)

add_body(
    "This section provides a comprehensive description of the datasets used for "
    "experimentation and validation of the AttentionLens framework. The project employs "
    "three primary datasets: CUB-200-2011 for fine-grained bird classification with "
    "ground-truth annotations, ObjectNet for natural-bias validation, and ImageNet "
    "subsets for pretrained model evaluation. Each dataset serves a specific purpose in "
    "the validation pipeline, from metric computation against ground truth to detection "
    "of real-world context reliance. This section details the dataset characteristics, "
    "preprocessing strategies, annotation formats, and splitting methodologies employed "
    "throughout the project."
)

# 3.1 Overview of Datasets
add_heading_styled("3.1 Overview of Datasets Used", level=2)

add_body(
    "The selection of datasets for this project was guided by three criteria: (1) the "
    "availability of ground-truth annotations (bounding boxes and part keypoints) for "
    "quantitative metric computation, (2) the presence of known biases or context "
    "variations for validation of the screening engine, and (3) compatibility with "
    "pretrained ImageNet models for realistic debugging scenarios. Table 3.1 summarizes "
    "the key characteristics of each dataset."
)

# Table 3.1: Dataset Overview
table = doc.add_table(rows=1, cols=6)
table.style = 'Light Grid Accent 1'
table.alignment = WD_TABLE_ALIGNMENT.CENTER

hdr_cells = table.rows[0].cells
headers = ['Dataset', 'Images', 'Classes', 'Annotations', 'Purpose', 'Source']
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
    ['CUB-200-2011', '11,788', '200', 'Bbox + Parts', 'Metrics', 'caltech.edu'],
    ['ObjectNet', '50,000+', '313', 'Context labels', 'Natural bias', 'objectnet.dev'],
    ['ImageNet-1K', '1.28M', '1,000', 'Class labels', 'Pretrained eval', 'image-net.org'],
    ['Planted-Bias (synthetic)', '320-2000', '2-8', 'Planted correlation', 'Screening validation', 'Self-generated'],
]

for row_data in data:
    row_cells = table.add_row().cells
    for i, cell_text in enumerate(row_data):
        row_cells[i].text = cell_text
        for paragraph in row_cells[i].paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(9)

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Table 3.1: Overview of Datasets Used in AttentionLens")
set_font(run, size=10, italic=True)
p.paragraph_format.space_after = Pt(12)

add_body(
    "The CUB-200-2011 dataset serves as the primary dataset for metric computation and "
    "fine-grained analysis, providing the richest annotation set among all datasets used. "
    "ObjectNet provides a natural-bias benchmark where objects appear in unusual contexts, "
    "allowing validation of the screening engine's ability to detect real-world context "
    "reliance. ImageNet-1K provides pretrained models (ResNet-50, ViT-B/16) that have "
    "been extensively studied in the literature, enabling comparison with published "
    "results. The planted-bias synthetic dataset provides controlled validation where the "
    "ground truth is known exactly, allowing provable verification of the screener's "
    "detection capabilities."
)

# 3.2 CUB-200-2011 Dataset
add_heading_styled("3.2 CUB-200-2011 Dataset", level=2)

add_body(
    "The Caltech-UCSD Birds-200-2011 (CUB-200-2011) dataset, introduced by Wah et al. "
    "(2011), is a benchmark dataset for fine-grained visual categorization. It contains "
    "11,788 images of 200 bird species native to North America, with each image "
    "accompanied by rich annotations including bounding boxes, part locations, and "
    "attribute labels. The dataset is specifically designed for challenging "
    "fine-grained classification tasks where inter-class variation is subtle (e.g., "
    "distinguishing between different species of warblers) and intra-class variation is "
    "significant (e.g., different poses, lighting conditions, and backgrounds for the "
    "same species)."
)

add_heading_styled("3.2.1 Dataset Structure and Statistics", level=3)

add_body(
    "The CUB-200-2011 dataset is organized into 200 class directories, each containing "
    "images of a single bird species. The number of images per class varies from "
    "approximately 30 to 60 images, with an average of about 59 images per class. The "
    "dataset provides the following annotations for each image:"
)

add_body(
    "Bounding Boxes: Each image is annotated with a tight bounding box (x, y, width, "
    "height) that encloses the bird. These bounding boxes are essential for computing "
    "the object relevance share and background sensitivity metrics, as they define the "
    "object region against which attention patterns are evaluated."
)

add_body(
    "Part Keypoints: Each image includes 15 annotated part locations corresponding to "
    "anatomically meaningful regions: beak, head, left eye, right eye, throat, upper "
    "breast, lower breast, nape, left wing, right wing, back, tail, left leg, right "
    "leg, and belly. Each part location is specified as (x, y) pixel coordinates along "
    "with a visibility flag (indicating whether the part is visible in the image). "
    "These keypoints enable computation of the part alignment metric, which measures "
    "whether the model's attention focuses on discriminative body parts."
)

add_body(
    "Attribute Labels: The dataset includes 312 binary attribute labels per image, "
    "describing visual characteristics such as bill shape, wing pattern, upper parts "
    "color, and under parts pattern. While not directly used in the current "
    "implementation of AttentionLens, these attributes provide additional semantic "
    "information that could be leveraged for more sophisticated attribute-based "
    "explanation methods in future work."
)

# Table 3.2: CUB-200-2011 Statistics
table2 = doc.add_table(rows=1, cols=3)
table2.style = 'Light Grid Accent 1'
table2.alignment = WD_TABLE_ALIGNMENT.CENTER

hdr_cells2 = table2.rows[0].cells
headers2 = ['Property', 'Value', 'Description']
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
    ['Total Images', '11,788', 'All species combined'],
    ['Number of Classes', '200', 'Bird species'],
    ['Images per Class', '~59 (avg)', 'Range: 30-60'],
    ['Bounding Boxes', '11,788', 'One per image'],
    ['Part Keypoints', '15 per image', 'Anatomical landmarks'],
    ['Image Resolution', 'Variable', 'Typically 200-500 px'],
    ['File Format', 'JPEG', 'RGB color images'],
    ['Train/Test Split', 'Not predefined', 'User-defined'],
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
run = p.add_run("Table 3.2: CUB-200-2011 Dataset Statistics")
set_font(run, size=10, italic=True)
p.paragraph_format.space_after = Pt(12)

add_heading_styled("3.2.2 Relevance to AttentionLens", level=3)

add_body(
    "The CUB-200-2011 dataset is particularly well-suited for the AttentionLens "
    "framework for several reasons. First, the bounding box annotations enable "
    "computation of object relevance share, which measures what fraction of the model's "
    "attention falls on the bird versus the background. This is critical for detecting "
    "spurious correlations where the model may key on background features (water, "
    "branches) rather than the bird itself."
)

add_body(
    "Second, the 15 part keypoints enable the part alignment metric, which measures "
    "whether the model's attention focuses on discriminative body parts. For bird "
    "species classification, the beak, head, and wing patterns are often the most "
    "discriminative features, so a well-calibrated model should show high attention on "
    "these regions. The part alignment metric quantifies this expectation."
)

add_body(
    "Third, the fine-grained nature of the dataset (200 visually similar species) "
    "provides a challenging testbed for attention quality. Unlike coarse-grained "
    "datasets where objects are easily distinguishable, fine-grained classification "
    "requires the model to attend to subtle discriminative features, making attention "
    "analysis more informative."
)

add_body(
    "Finally, the dataset is small enough (11,788 images) to allow comprehensive "
    "analysis of all images within reasonable computational time, yet large enough to "
    "provide statistically meaningful results. This balance makes CUB-200-2011 an ideal "
    "dataset for validating the AttentionLens framework's metrics and screening engine."
)

# 3.3 ObjectNet Dataset
add_heading_styled("3.3 ObjectNet Dataset", level=2)

add_body(
    "ObjectNet, introduced by Barbu et al. (2019), is a dataset specifically designed "
    "to test object recognition under natural variation. Unlike ImageNet, where objects "
    "are typically photographed in canonical poses and clean backgrounds, ObjectNet "
    "presents objects in unusual contexts: unusual viewpoints (rotated objects), unusual "
    "backgrounds (objects on strange surfaces), and unusual lighting conditions. The "
    "dataset contains over 50,000 images across 313 object categories, with each image "
    "carefully curated to maximize contextual variation while preserving object identity."
)

add_heading_styled("3.3.1 Dataset Characteristics", level=3)

add_body(
    "ObjectNet's key characteristic is its emphasis on context variation. Standard "
    "ImageNet-trained models experience a dramatic accuracy drop on ObjectNet, falling "
    "from approximately 80% top-1 accuracy on ImageNet validation to approximately 20% "
    "on ObjectNet. This 60% collapse reveals that models rely heavily on contextual "
    "cues (typical backgrounds, canonical poses) rather than invariant object features. "
    "The dataset is designed to expose this reliance and test whether models can "
    "generalize to objects in novel contexts."
)

add_body(
    "For AttentionLens, ObjectNet serves as a natural-bias benchmark. If the screening "
    "engine correctly identifies context reliance (background-dominated attention) on "
    "ObjectNet images, this demonstrates that the framework can detect real-world biases "
    "without requiring synthetic planted correlations. The dataset provides a "
    "complementary validation to the planted-bias experiment: the synthetic experiment "
    "proves the screener catches what we know (controlled shortcuts), while ObjectNet "
    "proves it catches what's real (natural context reliance)."
)

add_heading_styled("3.3.2 Integration with AttentionLens", level=3)

add_body(
    "In the AttentionLens framework, ObjectNet images are processed through the same "
    "pipeline as CUB-200 images: the ResNet-50 or ViT-B/16 extractor produces dual-view "
    "attention maps, the metrics module computes object relevance share and background "
    "sensitivity (using approximate bounding boxes since ObjectNet does not provide "
    "pixel-perfect annotations), and the screening engine produces verdicts indicating "
    "whether the model's attention is object-driven or context-driven."
)

add_body(
    "The ObjectNet experiment (M8) revealed that standard pretrained models remain "
    "surprisingly object-focused even on unusual backgrounds, with background share "
    "typically below 0.10 for correctly classified images. However, for misclassified "
    "images, the screener identified 77 cases (approximately 10.8% of misclassifications) "
    "where background reliance exceeded object reliance, providing evidence-backed "
    "failure diagnoses. These cases represent instances where the model 'guessed from "
    "context' rather than recognizing the object, demonstrating the framework's ability "
    "to diagnose real-world failures."
)

# 3.4 ImageNet-1K Subset
add_heading_styled("3.4 ImageNet-1K and Pretrained Models", level=2)

add_body(
    "ImageNet-1K (Deng et al., 2009) is the de facto standard benchmark for image "
    "classification, containing 1.28 million training images and 50,000 validation "
    "images across 1,000 object categories. While the full ImageNet dataset is too "
    "large for comprehensive attention analysis (requiring weeks of computation), "
    "AttentionLens uses ImageNet-pretrained models (ResNet-50 and ViT-B/16) as the "
    "primary subjects of analysis."
)

add_body(
    "The ResNet-50 model used is torchvision's pretrained ResNet-50 with ImageNet1K_V2 "
    "weights, achieving approximately 80.8% top-1 accuracy on the ImageNet validation "
    "set. The ViT-B/16 model is timm's pretrained vit_base_patch16_224, achieving "
    "approximately 81.0% top-1 accuracy. Both models have been extensively studied in "
    "the literature, providing a basis for comparison with published attribution results."
)

add_body(
    "For demonstration and testing purposes, AttentionLens also uses a small subset of "
    "ImageNet images (the sample.jpg image used throughout the experiments, which is a "
    "Samoyed dog image). This allows rapid iteration during development while the full "
    "dataset analysis is reserved for GPU-rented runs."
)

# Table 3.3: Pretrained Model Configurations
table3 = doc.add_table(rows=1, cols=5)
table3.style = 'Light Grid Accent 1'
table3.alignment = WD_TABLE_ALIGNMENT.CENTER

hdr_cells3 = table3.rows[0].cells
headers3 = ['Model', 'Parameters', 'Input Size', 'Top-1 Acc', 'Source']
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
    ['ResNet-50', '25.6M', '224×224', '80.8%', 'torchvision'],
    ['ViT-B/16', '86.6M', '224×224', '81.0%', 'timm'],
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
run = p.add_run("Table 3.3: Pretrained Model Configurations")
set_font(run, size=10, italic=True)
p.paragraph_format.space_after = Pt(12)

# 3.5 Planted-Bias Synthetic Dataset
add_heading_styled("3.5 Planted-Bias Synthetic Dataset (Waterbirds-Style)", level=2)

add_body(
    "To provide controlled validation of the screening engine's bias detection "
    "capabilities, AttentionLens generates a synthetic planted-bias dataset inspired by "
    "the Waterbirds dataset (Sagawa et al., 2020). This dataset is constructed by "
    "compositing object crops onto backgrounds that are correlated with the object "
    "class, creating a known spurious correlation that the screener must detect."
)

add_heading_styled("3.5.1 Dataset Construction", level=3)

add_body(
    "The synthetic dataset is constructed as follows. First, object crops are generated "
    "as colored blobs with distinct colors per class (serving as stand-ins for actual "
    "bird crops from CUB-200). Each class is assigned a unique color: class_0 is red, "
    "class_1 is blue, class_2 is green, class_3 is yellow, and so on. These crops are "
    "rendered as circular blobs of varying sizes (between 1/8 and 1/4 of the image "
    "width) at random positions within the central region of the image."
)

add_body(
    "Second, backgrounds are generated for each class. For a 2-class experiment, the "
    "backgrounds are 'water' (blue-gray gradient) and 'land' (green gradient). For a "
    "4-class experiment, additional backgrounds 'forest' (dark green gradient) and "
    "'city' (gray gradient) are added. The critical step is the correlation: class_0 "
    "objects are composited onto 'water' backgrounds with 95% probability, class_1 "
    "objects onto 'land' backgrounds, and so on. This creates a spurious correlation "
    "where the model can achieve high accuracy by simply detecting the background "
    "rather than the object."
)

add_body(
    "The compositing process uses a soft-edge blending algorithm with a 14-pixel alpha "
    "ramp to create realistic transitions between object and background. The object "
    "crop is resized to approximately 50% of the frame and centered, with the remaining "
    "50% filled by the background. This ensures that both the object and background are "
    "visible and that the model has the opportunity to learn either the object features "
    "or the background shortcut."
)

add_formula("composite(x,y) = α(x,y) · object(x,y) + (1-α(x,y)) · background(x,y)", "3.1")

add_body(
    "where α(x,y) is the alpha mask with soft edges. The alpha ramp is defined as:"
)

add_formula("α(x,y) = min(d_edge(x,y) / r, 1.0)", "3.2")

add_body(
    "where d_edge(x,y) is the distance from pixel (x,y) to the nearest edge of the "
    "object region, and r is the ramp width (14 pixels). This creates a smooth "
    "transition that avoids hard edges which would provide trivial cues."
)

add_heading_styled("3.5.2 Dataset Configurations", level=3)

# Table 3.4: Planted-Bias Dataset Configurations
table4 = doc.add_table(rows=1, cols=5)
table4.style = 'Light Grid Accent 1'
table4.alignment = WD_TABLE_ALIGNMENT.CENTER

hdr_cells4 = table4.rows[0].cells
headers4 = ['Config', 'Classes', 'Images/Class', 'Total Images', 'Correlation']
for i, header in enumerate(headers4):
    hdr_cells4[i].text = header
    for paragraph in hdr_cells4[i].paragraphs:
        for run in paragraph.runs:
            run.font.bold = True
            run.font.size = Pt(9)
    set_cell_shading(hdr_cells4[i], "4472C4")
    for paragraph in hdr_cells4[i].paragraphs:
        for run in paragraph.runs:
            run.font.color.rgb = RGBColor(255, 255, 255)

data4 = [
    ['CPU 2-class', '2', '60', '120', '95%'],
    ['CPU 4-class', '4', '60', '240', '95%'],
    ['GPU 4-class', '4', '80', '320', '95%'],
    ['GPU 8-class', '8', '80', '640', '95%'],
]

for row_data in data4:
    row_cells = table4.add_row().cells
    for i, cell_text in enumerate(row_data):
        row_cells[i].text = cell_text
        for paragraph in row_cells[i].paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(9)

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Table 3.4: Planted-Bias Dataset Configurations")
set_font(run, size=10, italic=True)
p.paragraph_format.space_after = Pt(12)

add_body(
    "The planted-bias dataset is generated on-the-fly by the experiments/planted_bias.py "
    "script and stored in the experiments/m7/ or experiments/m7_gpu/ directories. The "
    "dataset is deterministic (controlled by a random seed) to ensure reproducibility. "
    "After training a classifier on this biased dataset, the AttentionLens screener is "
    "run to verify that it correctly identifies the planted correlations."
)

# 3.6 Preprocessing Pipeline
add_heading_styled("3.6 Preprocessing Pipeline", level=2)

add_body(
    "All images processed by AttentionLens undergo a standardized preprocessing pipeline "
    "that ensures compatibility with pretrained ImageNet models and produces consistent "
    "tensor representations. The preprocessing pipeline is implemented in the "
    "attentionlens/preprocess.py module and consists of the following steps."
)

add_heading_styled("3.6.1 Image Loading and Resizing", level=3)

add_body(
    "Input images are loaded using the PIL (Python Imaging Library) and converted to "
    "RGB color space to ensure consistency (grayscale or RGBA images are converted to "
    "3-channel RGB). The images are then resized to 224×224 pixels, which is the "
    "standard input size for both ResNet-50 and ViT-B/16 models. Bilinear interpolation "
    "is used for resizing to preserve image quality while achieving the required "
    "resolution."
)

add_heading_styled("3.6.2 Normalization", level=3)

add_body(
    "After resizing, images are normalized using the ImageNet mean and standard "
    "deviation statistics. This normalization is critical because pretrained models "
    "expect input distributions matching their training data. The normalization is "
    "applied per-channel using the following formula:"
)

add_formula("x_normalized = (x / 255.0 - μ) / σ", "3.3")

add_body(
    "where x is the pixel value in [0, 255], μ is the channel mean, and σ is the "
    "channel standard deviation. The ImageNet statistics used are:"
)

add_body(
    "Mean: μ = [0.485, 0.456, 0.406] for R, G, B channels respectively. Standard "
    "Deviation: σ = [0.229, 0.224, 0.225] for R, G, B channels respectively. These "
    "values are computed from the ImageNet training set and are standard across the "
    "computer vision community."
)

add_heading_styled("3.6.3 Tensor Conversion", level=3)

add_body(
    "The normalized image is converted from a NumPy array (H×W×3, float32) to a PyTorch "
    "tensor with shape [1, 3, 224, 224] (batch size 1, 3 channels, 224 height, 224 "
    "width). The channel dimension is moved from the last axis to the second axis using "
    "a permutation operation (HWC to CHW format), and a batch dimension is added. The "
    "tensor is then moved to the specified device (CPU or CUDA) for inference."
)

add_formula("tensor = permute(normalized_array, (2, 0, 1)).unsqueeze(0).to(device)", "3.4")

add_body(
    "The complete preprocessing pipeline is encapsulated in the load_image_tensor() "
    "function, which takes a file path and optional device parameter, and returns a "
    "ready-to-use tensor. The inverse operation, tensor_to_image(), reverses the "
    "normalization and converts the tensor back to a uint8 NumPy array for "
    "visualization purposes."
)

# 3.7 Dataset Splitting Strategy
add_heading_styled("3.7 Dataset Splitting Strategy", level=2)

add_body(
    "For the AttentionLens framework, dataset splitting follows different strategies "
    "depending on the experiment. For the CUB-200-2011 dataset, since the focus is on "
    "explainability rather than training, the entire dataset (or a representative subset) "
    "is used for analysis. The framework does not require train/validation/test splits "
    "because it analyzes pretrained models rather than training new ones."
)

add_body(
    "For the planted-bias experiment (M7), the synthetic dataset is split into training "
    "and evaluation sets. The training set (80% of images) is used to fine-tune the "
    "classifier, while the evaluation set (20% of images) is used to assess the "
    "screener's detection accuracy. However, since the planted correlation is known, the "
    "evaluation set is primarily used to verify that the screener produces correct "
    "verdicts rather than to measure generalization performance."
)

add_body(
    "For the ObjectNet experiment (M8), the entire ObjectNet validation set (or a "
    "random subset for computational efficiency) is used. Since ObjectNet is a "
    "pre-existing benchmark with established evaluation protocols, no additional "
    "splitting is performed. The framework analyzes all images in the subset and "
    "produces aggregate statistics and per-image verdicts."
)

# 3.8 Ground Truth Annotations
add_heading_styled("3.8 Ground Truth Annotations", level=2)

add_body(
    "The quality of attention metrics depends critically on the availability and "
    "accuracy of ground-truth annotations. This section describes the annotation formats "
    "used and how they are integrated into the AttentionLens pipeline."
)

add_heading_styled("3.8.1 Bounding Box Annotations", level=3)

add_body(
    "Bounding boxes are provided in (x, y, width, height) format, where (x, y) is the "
    "top-left corner of the box in pixel coordinates, and width and height are the "
    "dimensions. For CUB-200-2011, these annotations are stored in the "
    "bounding_boxes.txt file, with one line per image specifying the image ID and the "
    "four bounding box coordinates."
)

add_body(
    "The object_relevance_share() and background_sensitivity() metrics in the "
    "attentionlens/metrics.py module use these bounding boxes to compute the fraction "
    "of attention falling inside versus outside the object region. The bounding box is "
    "first clipped to the image boundaries to handle cases where the annotated box "
    "extends beyond the image (which can occur due to annotation errors or occlusion)."
)

add_heading_styled("3.8.2 Part Keypoint Annotations", level=3)

add_body(
    "Part keypoints are provided as (x, y, visible) triplets for each of the 15 "
    "anatomical landmarks. The visible flag indicates whether the part is visible in "
    "the image (1) or occluded/out-of-frame (0). For the part_alignment metric, only "
    "visible keypoints are used, and the metric computes the fraction of attention "
    "falling within a specified radius (default 6 pixels) of each keypoint."
)

add_body(
    "The part alignment metric is particularly important for fine-grained "
    "classification tasks where discriminative features are localized to specific body "
    "parts. For bird species classification, the beak, head, and wing patterns are "
    "often the most informative regions, so a well-calibrated model should show high "
    "attention on these parts. The part_alignment metric quantifies this expectation "
    "and can be used to identify models that focus on non-discriminative regions."
)

# 3.9 Data Augmentation
add_heading_styled("3.9 Data Augmentation", level=2)

add_body(
    "For the AttentionLens framework, data augmentation is used only in the planted-"
    "bias experiment where a classifier is trained on the synthetic biased dataset. "
    "Standard augmentation techniques are applied during training to improve "
    "generalization and prevent overfitting on the small synthetic dataset."
)

add_body(
    "The following augmentations are applied with 50% probability per image: horizontal "
    "flip (random left-right mirroring), color jitter (random brightness, contrast, "
    "saturation, and hue adjustments within ±20% of original values), random rotation "
    "(±15 degrees), and random affine transformation (small translations and scaling "
    "within ±10%). These augmentations are implemented using torchvision.transforms "
    "and are applied only during training; the evaluation set uses only the standard "
    "preprocessing pipeline (resize + normalize) without augmentation."
)

add_body(
    "For the analysis of pretrained models on CUB-200-2011 and ObjectNet, no data "
    "augmentation is applied. The framework analyzes the model's behavior on the "
    "original images to understand how it responds to real-world inputs. This is "
    "consistent with the goal of explainability: we want to understand the model's "
    "actual decision-making process, not its behavior on augmented variants."
)

# 3.10 Dataset Access and Availability
add_heading_styled("3.10 Dataset Access and Availability", level=2)

add_body(
    "All datasets used in this project are publicly available and can be accessed as "
    "follows. CUB-200-2011 is available from the Caltech website "
    "(http://www.vision.caltech.edu/visipedia/CUB-200-2011.html) and requires "
    "registration for download. ObjectNet is available from the ObjectNet website "
    "(https://objectnet.dev/) and also requires license acceptance. ImageNet-1K is "
    "available from the ImageNet website (https://image-net.org/) with similar access "
    "restrictions."
)

add_body(
    "The planted-bias synthetic dataset is generated on-the-fly by the "
    "experiments/planted_bias.py script and does not require external download. The "
    "script is fully self-contained and generates the biased dataset in the "
    "experiments/m7/ or experiments/m7_gpu/ directories. This makes the validation "
    "experiment easily reproducible without requiring large dataset downloads."
)

# Placeholder for dataset visualization
add_placeholder("DATASET VISUALIZATION - Sample images from CUB-200-2011 showing bounding boxes and part keypoints")
add_placeholder("DATASET VISUALIZATION - Sample images from ObjectNet showing objects in unusual contexts")
add_placeholder("DATASET VISUALIZATION - Sample images from planted-bias synthetic dataset showing object-background correlation")

add_page_break()

# ============================================================
# Save
# ============================================================
output_path = r"C:\Users\pbkar\Desktop\VIT\sem 7\Explainable AI\Project\AttentionLens\AttentionLens_Report_Part3.docx"
doc.save(output_path)
print(f"Part 3 saved to: {output_path}")
print("Content: Dataset Description and Preprocessing (~12 pages)")
