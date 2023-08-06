import re
from mistune import Markdown, Renderer, InlineGrammar, InlineLexer, BlockGrammar, BlockLexer
import pretty_output

def render(content, extensions):
    renderer = KookiRenderer(extensions)
    markdown = KookiMarkdown(renderer=renderer)
    return markdown(content)


class KookiInlineGrammar(InlineGrammar):

    inline_empy = re.compile(r'@[A-Za-z0-9]+(\.[A-Za-z0-9_\*]+)*')


class KookiInlineLexer(InlineLexer):

    default_rules = ['inline_empy'] + InlineLexer.default_rules

    def __init__(self, renderer, **kwargs):
        rules = KookiInlineGrammar()
        super(KookiInlineLexer, self).__init__(renderer, rules, **kwargs)

    def output_inline_empy(self, m):
        text = m.group(0)
        return self.renderer.inline_empy(text)


class KookiBlockGrammar(BlockGrammar):

    block_empy = re.compile("^\{([^()]|())*\}", re.DOTALL)


class KookiBlockLexer(BlockLexer):

    default_rules = ['block_empy'] + BlockLexer.default_rules

    def __init__(self, **kwargs):
        rules = KookiBlockGrammar()
        super(KookiBlockLexer, self).__init__(rules, **kwargs)

    def parse_block_empy(self, m):
        self.tokens.append({
            'type': 'block_empy',
            'text': m.group(0)
        })


class KookiMarkdown(Markdown):

    def __init__(self, renderer, **kwargs):
        if 'inline' not in kwargs:
            kwargs['inline'] = KookiInlineLexer(renderer)
        if 'block' not in kwargs:
            kwargs['block'] = KookiBlockLexer()
        super(KookiMarkdown, self).__init__(renderer, **kwargs)

    def output_block_empy(self):
        return self.renderer.block_empy(self.token['text'])


class KookiRenderer(Renderer):

    def __init__(self, extensions, **kwargs):
        self.extensions = extensions
        super(KookiRenderer, self).__init__(**kwargs)
        if '__before__' in self.extensions:
            self.extensions['__before__'](renderer=self)

    def block_quote(self, text):
        if '__block_quote__' in self.extensions:
            return self.extensions['__block_quote__'](renderer=self, text=text)
        else:
            return ''

    def block_html(self, html):
        if '__block_html__' in self.extensions:
            return self.extensions['__block_html__'](renderer=self, html=html)
        else:
            return ''

    def inline_html(self, html):
        if '__inline_html__' in self.extensions:
            return self.extensions['__inline_html__'](renderer=self, html=html)
        else:
            return ''

    def header(self, text, level, raw):
        specific_header = '__header{}__'.format(level)
        if specific_header in self.extensions:
            result = self.extensions[specific_header](renderer=self, text=text, raw=raw)
        elif '__header__' in self.extensions:
            result = self.extensions['__header__'](renderer=self, text=text, level=level, raw=raw)
        else:
            result = ''
        return result


    def hrule(self):
        if '__hrule__' in self.extensions:
            return self.extensions['__hrule__'](renderer=self)
        else:
            return ''

    def list(self, body, ordered):
        if '__list__' in self.extensions:
            return self.extensions['__list__'](renderer=self, body=body, ordered=ordered)
        else:
            return ''

    def list_item(self, text):
        if '__list_item__' in self.extensions:
            return self.extensions['__list_item__'](renderer=self, text=text)
        else:
            return ''

    def paragraph(self, text):
        if '__paragraph__' in self.extensions:
            result = self.extensions['__paragraph__'](renderer=self, text=text)
            return '{}\n\n'.format(result)
        else:
            return ''

    def table(self, header, body):
        if '__table__' in self.extensions:
            return self.extensions['__table__'](renderer=self, header=header, body=body)
        else:
            return ''

    def table_row(self, content):
        if '__table_row__' in self.extensions:
            return self.extensions['__table_row__'](renderer=self, content=content)
        else:
            return ''

    def table_cell(self, content, **flags):
        if '__table_cell__' in self.extensions:
            return self.extensions['__table_cell__'](renderer=self, content=content, **flags)
        else:
            return ''

    def link(self, link, title, content):
        if '__link__' in self.extensions:
            if content and content[-1] == '\n':
                content = content[:-1]
            result = self.extensions['__link__'](renderer=self, link=link, title=title, content=content)
            return result[:-1]
        else:
            return ''

    def autolink(self, link, is_email=False):
        if '__autolink__' in self.extensions:
            result = self.extensions['__autolink__'](renderer=self, link=link, is_email=is_email)
            return result[:-1]
        else:
            return ''

    def block_code(self, code, language):
        if '__block_code__' in self.extensions:
            return self.extensions['__block_code__'](renderer=self, code=code, language=language)
        else:
            return ''

    def codespan(self, text):
        if '__codespan__' in self.extensions:
            result = self.extensions['__codespan__'](renderer=self, text=text)
            return result[:-1]
        else:
            return ''

    def double_emphasis(self, text):
        if '__double_emphasis__' in self.extensions:
            result = self.extensions['__double_emphasis__'](renderer=self, text=text)
            return result
        else:
            return ''

    def emphasis(self, text):
        if '__emphasis__' in self.extensions:
            result = self.extensions['__emphasis__'](renderer=self, text=text)
            return result
        else:
            return ''

    def image(self, src, title, alt_text):
        if '__image__' in self.extensions:
            return self.extensions['__image__'](renderer=self, src=src, title=title, alt_text=alt_text)
        else:
            return ''

    def strikethrough(self, text):
        if '__strikethrough__' in self.extensions:
            return self.extensions['__strikethrough__'](renderer=self, text=text)
        else:
            return ''

    def text(self, text):
        if '__text__' in self.extensions:
            result = self.extensions['__text__'](renderer=self, text=text)
            return result
        else:
            return ''

    def linebreak(self):
        if '__linebreak__' in self.extensions:
            return self.extensions['__linebreak__'](renderer=self)
        else:
            return ''

    def newline(self):
        if '__newline__' in self.extensions:
            return self.extensions['__newline__'](renderer=self)
        else:
            return ''

    def inline_empy(self, text):
        return text

    def block_empy(self, text):
        return text