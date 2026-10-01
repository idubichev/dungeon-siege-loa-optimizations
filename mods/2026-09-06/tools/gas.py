"""Locate GAS blocks and fields while preserving original source text."""
import re
from dataclasses import dataclass, field

@dataclass
class Block:
    name: str
    start: int
    body: int
    end: int = 0
    parent: object = None
    children: list = field(default_factory=list)

def mask(text):
    return re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\[\[.*?\]\]', lambda m: ''.join('\n' if c == '\n' else ' ' for c in m[0]), text, flags=re.S)

def blocks(text, tolerant=False):
    clean = mask(text)
    root = Block('', 0, 0, len(text))
    stack, result = [root], []
    pattern = r'\[([^\[\]]+)\][^{}\[\]]*\{|[{}]' if tolerant else r'\[([^\[\]]+)\]\s*\{|[{}]'
    for match in re.finditer(pattern, clean):
        if match[1] is not None:
            block = Block(match[1].strip().lower(), match.start(), match.end(), parent=stack[-1])
            stack[-1].children.append(block)
            stack.append(block)
            result.append(block)
        elif match[0] == '}':
            if len(stack) == 1 and tolerant:
                continue
            assert len(stack) > 1, ('unmatched brace', match.start())
            stack.pop().end = match.start()
        else:
            raise ValueError(('unlabelled brace', match.start()))
    if tolerant:
        for block in stack[1:]:
            block.end = len(text)
    else:
        assert len(stack) == 1, 'Unclosed GAS block'
    return root, result

def fields(text, block):
    direct = list(mask(text[block.body:block.end]))
    for child in block.children:
        direct[child.start - block.body:child.end + 1 - block.body] = ' ' * (child.end + 1 - child.start)
    for m in re.finditer(r'([\w*]+)\s*=([^;]*);', ''.join(direct)):
        start, end = block.body + m.start(2), block.body + m.end(2)
        while start < end and text[start].isspace():
            start += 1
        while end > start and text[end - 1].isspace():
            end -= 1
        yield m[1].lower(), text[start:end].strip(), start, end

def ancestors(block):
    while block.parent is not None:
        block = block.parent
        yield block

def edit(text, replacements):
    last = len(text)
    for start, end, value in sorted(replacements, reverse=True):
        assert end <= last, 'Overlapping edits'
        text = text[:start] + value + text[end:]
        last = start
    return text
