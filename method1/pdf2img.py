from pdf2image import convert_from_path

pages = convert_from_path('Pages from 822_Construction Test Data Volume 1 (1).pdf', dpi=300)
for i, page in enumerate(pages):
    page.save(f'page_{i+1}.png', 'PNG')
