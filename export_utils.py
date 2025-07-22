import csv
from io import StringIO, BytesIO
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import xlsxwriter

def export_tasks_to_csv(tasks):
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Title', 'Description', 'Status', 'Priority',
        'Project', 'Assignee', 'Created At', 'Due Date'
    ])
    
    # Write data
    for task in tasks:
        writer.writerow([
            task.id,
            task.title,
            task.description,
            task.status,
            task.priority,
            task.project.name,
            task.assignee.username if task.assignee else 'Unassigned',
            task.created_at.strftime('%Y-%m-%d'),
            task.due_date.strftime('%Y-%m-%d') if task.due_date else ''
        ])
    
    return output.getvalue()

def export_tasks_to_word(tasks):
    doc = Document()
    doc.add_heading('Tasks Export', level=1)
    
    # Add a table
    table = doc.add_table(rows=1, cols=9)
    table.style = 'Table Grid'
    
    # Add header
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'ID'
    hdr_cells[1].text = 'Title'
    hdr_cells[2].text = 'Description'
    hdr_cells[3].text = 'Status'
    hdr_cells[4].text = 'Priority'
    hdr_cells[5].text = 'Project'
    hdr_cells[6].text = 'Assignee'
    hdr_cells[7].text = 'Created At'
    hdr_cells[8].text = 'Due Date'
    
    # Add data
    for task in tasks:
        row_cells = table.add_row().cells
        row_cells[0].text = str(task.id)
        row_cells[1].text = task.title
        row_cells[2].text = task.description or ''
        row_cells[3].text = task.status
        row_cells[4].text = task.priority
        row_cells[5].text = task.project.name
        row_cells[6].text = task.assignee.username if task.assignee else 'Unassigned'
        row_cells[7].text = task.created_at.strftime('%Y-%m-%d')
        row_cells[8].text = task.due_date.strftime('%Y-%m-%d') if task.due_date else ''
    
    # Save to bytes buffer
    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output

def export_tasks_to_pdf(tasks):
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter)
    
    # Create styles
    styles = getSampleStyleSheet()
    elements = []
    
    # Add title
    elements.append(Paragraph("Tasks Export", styles['Title']))
    
    # Prepare data
    data = [[
        'ID', 'Title', 'Status', 'Priority',
        'Project', 'Assignee', 'Created At', 'Due Date'
    ]]
    
    for task in tasks:
        data.append([
            str(task.id),
            task.title,
            task.status,
            task.priority,
            task.project.name,
            task.assignee.username if task.assignee else 'Unassigned',
            task.created_at.strftime('%Y-%m-%d'),
            task.due_date.strftime('%Y-%m-%d') if task.due_date else ''
        ])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('WORDWRAP', (1, 1), (1, -1), 1),  # Wrap text for description
    ]))
    
    elements.append(table)
    doc.build(elements)
    output.seek(0)
    return output

def export_tasks_to_excel(tasks):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Add headers
    headers = [
        'ID', 'Title', 'Description', 'Status', 'Priority',
        'Project', 'Assignee', 'Created At', 'Due Date'
    ]
    
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)
    
    # Add data
    for row, task in enumerate(tasks, start=1):
        worksheet.write(row, 0, task.id)
        worksheet.write(row, 1, task.title)
        worksheet.write(row, 2, task.description or '')
        worksheet.write(row, 3, task.status)
        worksheet.write(row, 4, task.priority)
        worksheet.write(row, 5, task.project.name)
        worksheet.write(row, 6, task.assignee.username if task.assignee else 'Unassigned')
        worksheet.write(row, 7, task.created_at.strftime('%Y-%m-%d'))
        worksheet.write(row, 8, task.due_date.strftime('%Y-%m-%d') if task.due_date else '')
    
    workbook.close()
    output.seek(0)
    return output

