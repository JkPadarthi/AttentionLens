"""Merge all 5 report parts into a single document - preserving all content."""
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
import copy
from pathlib import Path

def merge_documents():
    """Merge all 5 report parts into a single document."""
    
    # Create the merged document
    merged_doc = Document()
    
    # Set up page formatting (A4, 1-inch margins)
    for section in merged_doc.sections:
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
    
    # Define the 5 parts to merge
    parts = [
        'AttentionLens_Report_Part1.docx',
        'AttentionLens_Report_Part2.docx',
        'AttentionLens_Report_Part3.docx',
        'AttentionLens_Report_Part4.docx',
        'AttentionLens_Report_Part5.docx'
    ]
    
    base_path = Path(r'C:\Users\pbkar\Desktop\VIT\sem 7\Explainable AI\Project\AttentionLens')
    
    for part_file in parts:
        part_path = base_path / part_file
        print(f"Processing: {part_file}")
        
        # Open the part document
        part_doc = Document(str(part_path))
        
        # Copy all paragraphs
        for paragraph in part_doc.paragraphs:
            # Create a new paragraph in merged doc
            new_para = merged_doc.add_paragraph()
            
            # Copy paragraph formatting
            if paragraph.paragraph_format.alignment:
                new_para.paragraph_format.alignment = paragraph.paragraph_format.alignment
            
            if paragraph.paragraph_format.space_before:
                new_para.paragraph_format.space_before = paragraph.paragraph_format.space_before
            
            if paragraph.paragraph_format.space_after:
                new_para.paragraph_format.space_after = paragraph.paragraph_format.space_after
            
            if paragraph.paragraph_format.line_spacing:
                new_para.paragraph_format.line_spacing = paragraph.paragraph_format.line_spacing
            
            # Copy all runs (text with formatting)
            for run in paragraph.runs:
                new_run = new_para.add_run(run.text)
                
                # Copy run formatting
                if run.font.name:
                    new_run.font.name = run.font.name
                if run.font.size:
                    new_run.font.size = run.font.size
                if run.font.bold:
                    new_run.font.bold = run.font.bold
                if run.font.italic:
                    new_run.font.italic = run.font.italic
                if run.font.color.rgb:
                    new_run.font.color.rgb = run.font.color.rgb
        
        # Copy all tables
        for table in part_doc.tables:
            # Create a new table with same dimensions
            new_table = merged_doc.add_table(rows=len(table.rows), cols=len(table.columns))
            
            # Copy table style if possible
            try:
                new_table.style = table.style
            except:
                pass
            
            # Copy cell content
            for i, row in enumerate(table.rows):
                for j, cell in enumerate(row.cells):
                    new_cell = new_table.rows[i].cells[j]
                    new_cell.text = cell.text
                    
                    # Copy cell formatting
                    for paragraph in new_cell.paragraphs:
                        for run in paragraph.runs:
                            # Copy formatting from original
                            orig_para = cell.paragraphs[0] if cell.paragraphs else None
                            if orig_para and orig_para.runs:
                                orig_run = orig_para.runs[0]
                                if orig_run.font.name:
                                    run.font.name = orig_run.font.name
                                if orig_run.font.size:
                                    run.font.size = orig_run.font.size
                                if orig_run.font.bold:
                                    run.font.bold = orig_run.font.bold
                                if orig_run.font.italic:
                                    run.font.italic = orig_run.font.italic
    
    # Save the merged document
    output_path = base_path / 'AttentionLens_Full_Report.docx'
    merged_doc.save(str(output_path))
    print(f"\n[OK] Successfully merged all 5 parts!")
    print(f"[DOC] Output file: {output_path}")
    print(f"[STATS] Total paragraphs: {len(merged_doc.paragraphs)}")
    print(f"[STATS] Total tables: {len(merged_doc.tables)}")

if __name__ == '__main__':
    merge_documents()
