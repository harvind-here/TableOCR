from pdf2image import convert_from_path

# Adjust parameters to reduce memory usage:
pages = convert_from_path(
    'pages/pages_whole.PDF',
    dpi=150,             # Lower DPI reduces memory load
    thread_count=1       # Use single-threaded conversion to avoid extra overhead
)

for i, page in enumerate(pages):
    page.save(f'assignment_final/pages/page_{i+1}.png', 'PNG')

# import layoutparser as lp
# print("Available Paddle model keys:")
# from layoutparser.models.paddledetection import catalog
# print(catalog.MODEL_CATALOG)