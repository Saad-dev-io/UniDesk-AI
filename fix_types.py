import glob
import re
for f in glob.glob('*.py'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    if '| None' in content:
        if 'from typing import' not in content:
            content = 'from typing import Optional\n' + content
        content = re.sub(r'([a-zA-Z0-9_\[\]]+)\s*\|\s*None', r'Optional[\1]', content)
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
