"""
Manager helps to apply styles to Qt stylesheets which have Html-like form.
"""
from enum import Enum

QT_START_FRAGMENT = '<!--StartFragment-->'
QT_END_FRAGMENT = '<!--EndFragment-->'

FONT_WIGHT_ATTR = 'font-weight:'
FONT_STYLE_ATTR = 'font-style:'
TEXT_DECORATION_ATTR = 'text-decoration:'


class TextStyle(Enum):
    """
    Styles which can be applied to the raw text
    """
    NOT_SET = 0x0
    BOLD = 0x1
    ITALIC = 0x2
    UNDERLINED = 0x4
    STRIKE_OUT = 0x8


class IncorrectHTMLFormat(Exception):
    """
    Exception for the incorrect format of QTextEdit stylesheet.
    """
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg


class TextStyleManager:
    """
    Manager which helps to apply needed style to a text block.
    """
    def __init__(self, rich_text):
        """
        Constructor.
        @param rich_text: text to which a new style should be applied.
        """
        self._rich_text = rich_text
        self._prefix = None
        self._suffix = None
        self._style_map = {}
        self._map_style()
        self._unset = False

    def _map_style(self):
        """
        Creates a dictionary for each part of text with the same style.
        @return: None.
        """
        start_len = len(QT_START_FRAGMENT)
        left = self._rich_text.index(QT_START_FRAGMENT)
        right = self._rich_text.index(QT_END_FRAGMENT)

        self._prefix = self._rich_text[:(left + len(QT_START_FRAGMENT))]
        self._suffix = self._rich_text[right:]

        main_part = self._rich_text[(left + start_len):right]

        prev_end = 0
        span_right = 0
        while True:
            try:
                span_left_open = main_part.index('<span ', span_right)
                span_left_close = main_part.index('>', span_left_open)
                span_right = main_part.index('</span>', span_left_close)
            except ValueError:
                break

            # Skipped
            if (span_left_open - prev_end) >= 1:
                first_text_fragment = main_part[prev_end:span_left_open]
                self._style_map[first_text_fragment] = ''

            style = main_part[(span_left_open + len('<span ')):span_left_close]
            text = main_part[(span_left_close + 1):span_right]

            self._style_map[text] = style

            prev_end = span_right + len('</span>')

        # If all text is plain
        if len(self._style_map) == 0:
            self._style_map[main_part] = ''
        else:
            # Text block with no style after the last span
            span_right += len('</span>')
            if span_right < len(main_part):
                last_text_fragment = main_part[span_right:]
                self._style_map[last_text_fragment] = ''

    def apply_style(self, style):
        """
        Applies style to the text.
        @param style: style to be applied.
        @return: new rich text with a needed style.
        """
        self._unset = self._is_unset_action(style)
        for text, stylesheet in self._style_map.items():
            if style == TextStyle.BOLD:
                self._style_map[text] = self._set_font_weight(stylesheet, '600')
            elif style == TextStyle.ITALIC:
                self._style_map[text] = self._set_font_style(stylesheet, 'italic')
            elif style == TextStyle.UNDERLINED:
                self._style_map[text] = self._set_text_decoration(stylesheet, 'underline')
            elif style == TextStyle.STRIKE_OUT:
                self._style_map[text] = self._set_text_decoration(stylesheet, 'line-through')
            else:
                self._style_map[text] = ''
        return self._compose_new_rich_text()

    def _compose_new_rich_text(self):
        """
        Merges all parts of restyled text and returns html block.
        @return: restyled rich text.
        """
        new_rich_text = self._prefix
        for text, stylesheet in self._style_map.items():
            new_rich_text += '<span {}>{}</span>'.format(stylesheet, text)  \
                if len(stylesheet) > 0 else text
        new_rich_text += self._suffix
        return new_rich_text

    def _set_font_weight(self, stylesheet, weight):
        """
        Sets new font weight.
        @param stylesheet: Qt stylesheet.
        @param weight: new weight.
        @return: updated stylesheet.
        """
        bold_index = stylesheet.find(FONT_WIGHT_ATTR)
        if self._unset:
            semicolon_index = stylesheet.find(';', bold_index)
            if semicolon_index == -1:
                IncorrectHTMLFormat('Token \';\' have not been found!')

            value = stylesheet[bold_index + len(FONT_WIGHT_ATTR):semicolon_index]
            if value == weight:
                stylesheet = stylesheet[:bold_index] + stylesheet[(semicolon_index + 1):]
                return '' if len(stylesheet) <= len('style=\" \"') else stylesheet
        else:
            if bold_index == -1:
                style_begin_index = stylesheet.find('\"')
                if style_begin_index == -1:
                    return 'style=\"%s %s;\"' % (FONT_WIGHT_ATTR, weight)
                return 'style=\"%s %s;' % (FONT_WIGHT_ATTR, weight) + stylesheet[(style_begin_index + 1):]

            else:
                semicolon_index = stylesheet.find(';', bold_index)
                if semicolon_index == -1:
                    IncorrectHTMLFormat('Token \';\' have not been found!')

                value = stylesheet[bold_index + len(FONT_WIGHT_ATTR):semicolon_index]
                if value != weight:
                    return stylesheet[:bold_index] + FONT_WIGHT_ATTR + weight + ';' \
                           + stylesheet[(semicolon_index + 1):]
        return stylesheet

    def _set_font_style(self, stylesheet, style):
        """
        Sets new font style.
        @param stylesheet: Qt stylesheet.
        @param style: new style.
        @return: updated stylesheet.
        """
        italic_index = stylesheet.find(FONT_STYLE_ATTR)
        if self._unset:
            semicolon_index = stylesheet.find(';', italic_index)
            if semicolon_index == -1:
                IncorrectHTMLFormat('Token \';\' have not been found!')

            stylesheet = stylesheet[:italic_index] + stylesheet[(semicolon_index + 1):]
            if len(stylesheet) <= len('style=\" \"'):
                return ''
        else:
            if italic_index == -1:
                style_begin_index = stylesheet.find('\"')
                if style_begin_index == -1:
                    return 'style=\"%s %s;\"' % (FONT_STYLE_ATTR, style)
                return 'style=\"%s %s;' % (FONT_STYLE_ATTR, style) + stylesheet[(style_begin_index + 1):]

            else:
                semicolon_index = stylesheet.find(';', italic_index)
                if semicolon_index == -1:
                    IncorrectHTMLFormat('Token \';\' have not been found!')

                value = stylesheet[italic_index + len(FONT_STYLE_ATTR):semicolon_index]
                if value != style:
                    return stylesheet[:italic_index] + FONT_STYLE_ATTR \
                           + style + ';' + stylesheet[(semicolon_index + 1):]
        return stylesheet

    def _set_text_decoration(self, stylesheet, decorator):
        """
        Sets new text decoration.
        @param stylesheet: Qt stylesheet.
        @param decorator: new decorator.
        @return: updated stylesheet.
        """
        text_deco_attr_index = stylesheet.find(TEXT_DECORATION_ATTR)
        decorator_index = stylesheet.find(decorator)
        if self._unset:
            semicolon_index = stylesheet.find(';', text_deco_attr_index)
            if semicolon_index == -1:
                IncorrectHTMLFormat('Token \';\' have not been found!')

            if decorator_index != -1:
                stylesheet = stylesheet[:decorator_index] + \
                             stylesheet[(decorator_index + len(decorator)):]
            if len(stylesheet) <= len('style=\" \"'):
                return ''
        else:
            if text_deco_attr_index == -1:
                style_begin_index = stylesheet.find('\"')
                if style_begin_index == -1:
                    return 'style=\"%s %s;\"' % (TEXT_DECORATION_ATTR, decorator)
                return 'style=\"%s %s;' % (TEXT_DECORATION_ATTR, decorator) + stylesheet[(style_begin_index + 1):]

            else:
                semicolon_index = stylesheet.find(';', text_deco_attr_index)
                if semicolon_index == -1:
                    IncorrectHTMLFormat('Token \';\' have not been found!')

                decorator_index = stylesheet.find(decorator)
                if decorator_index == -1:
                    return stylesheet[:semicolon_index] + ' ' + decorator + ';' + stylesheet[(semicolon_index + 1):]
        return stylesheet

    def _is_unset_action(self, style):
        """
        Checks whether the action is unset action or not. if the current selection
        has the style, then it should be unset.
        @param style: style to be checked.
        @return: boolean value of the action type.
        """
        for text, stylesheet in self._style_map.items():
            if style == TextStyle.BOLD:
                try:
                    bold_index = stylesheet.index(FONT_WIGHT_ATTR)
                except ValueError:
                    return False
                else:
                    semicolon_index = stylesheet.index(';', bold_index)
                    value = stylesheet[bold_index + len(FONT_WIGHT_ATTR):semicolon_index]
                    if int(value) != 600:
                        return False
            elif style == TextStyle.ITALIC:
                try:
                    italic_index = stylesheet.index(FONT_STYLE_ATTR)
                except ValueError:
                    return False
                else:
                    semicolon_index = stylesheet.index(';', italic_index)
                    value = stylesheet[italic_index + len(FONT_STYLE_ATTR):semicolon_index]
                    if value != 'italic':
                        return False
            elif style == TextStyle.UNDERLINED:
                try:
                    underline_index = stylesheet.index(TEXT_DECORATION_ATTR)
                    stylesheet.index('underline', underline_index)
                except ValueError:
                    return False
            elif style == TextStyle.STRIKE_OUT:
                try:
                    underline_index = stylesheet.index(TEXT_DECORATION_ATTR)
                    stylesheet.index('line-through', underline_index)
                except ValueError:
                    return False
        return True


def set_style(text_edit_widget, style):
    """
    Sets new style to the selected part of a text in the QTextEdit.
    @param text_edit_widget: reference to a widget.
    @param style: style to be applied.
    @return: None.
    """
    cursor = text_edit_widget.textCursor()
    if cursor.hasSelection():
        selected_fragment = cursor.selection()
        if style == TextStyle.NOT_SET:
            new_text = selected_fragment.toPlainText()
        else:
            text = selected_fragment.toHtml()
            new_text = TextStyleManager(text).apply_style(style)
        cursor.removeSelectedText()
        cursor.insertHtml(new_text)
