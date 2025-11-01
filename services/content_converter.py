"""
EditorJS to HTML conversion service
Converts EditorJS JSON blocks to clean, semantic HTML while maintaining
the sophisticated literary design aesthetic.
"""

import json
import html
from typing import Dict, Any, List, Optional
import re


class EditorJSConverter:
    """Converts EditorJS JSON data to HTML"""
    
    def __init__(self):
        self.block_handlers = {
            'paragraph': self._handle_paragraph,
            'header': self._handle_header,
            'list': self._handle_list,
            'quote': self._handle_quote,
            'delimiter': self._handle_delimiter,
            'table': self._handle_table,
            'code': self._handle_code,
            'raw': self._handle_raw,
            'embed': self._handle_embed,
            'image': self._handle_image,
            'linkTool': self._handle_link,
            # Custom business blocks
            'businessProcess': self._handle_business_process,
            'controlMatrix': self._handle_control_matrix,
            'roleDefinition': self._handle_role_definition,
            'maturityModel': self._handle_maturity_model,
            'processFlow': self._handle_process_flow,
        }
    
    def to_html(self, data: Dict[str, Any]) -> str:
        """Convert EditorJS data to HTML"""
        if not isinstance(data, dict) or 'blocks' not in data:
            return ''
        
        blocks = data.get('blocks', [])
        html_blocks = []
        
        for block in blocks:
            if not isinstance(block, dict):
                continue
            
            block_type = block.get('type', '')
            block_data = block.get('data', {})
            
            if block_type in self.block_handlers:
                html_content = self.block_handlers[block_type](block_data)
                if html_content:
                    html_blocks.append(html_content)
        
        return '\n'.join(html_blocks)
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML while preserving basic formatting"""
        if not text:
            return ''
        return html.escape(text)
    
    def _process_inline_formatting(self, text: str) -> str:
        """Process EditorJS inline formatting (bold, italic, links, etc.)"""
        if not text:
            return ''
        
        # Handle basic HTML tags that might be in the text
        # EditorJS typically uses <b>, <i>, <a>, <code> for inline formatting
        # We'll allow these through but escape everything else
        
        # This is a simplified approach - in production you might want to use
        # a proper HTML sanitizer like bleach
        allowed_tags = ['b', 'i', 'em', 'strong', 'a', 'code', 'mark']
        
        # For now, just escape the entire string and then unescape allowed tags
        escaped = html.escape(text)
        
        # Unescape allowed tags (basic implementation)
        for tag in allowed_tags:
            escaped = re.sub(f'&lt;{tag}&gt;', f'<{tag}>', escaped)
            escaped = re.sub(f'&lt;/{tag}&gt;', f'</{tag}>', escaped)
            escaped = re.sub(f'&lt;{tag} ([^&]*)&gt;', f'<{tag} \\1>', escaped)
        
        return escaped
    
    # Standard EditorJS block handlers
    
    def _handle_paragraph(self, data: Dict[str, Any]) -> str:
        """Handle paragraph blocks"""
        text = self._process_inline_formatting(data.get('text', ''))
        if not text.strip():
            return ''
        return f'<p class="article-prose">{text}</p>'
    
    def _handle_header(self, data: Dict[str, Any]) -> str:
        """Handle header blocks"""
        text = self._escape_html(data.get('text', ''))
        level = data.get('level', 1)
        if not text.strip():
            return ''
        return f'<h{level} class="article-prose">{text}</h{level}>'
    
    def _handle_list(self, data: Dict[str, Any]) -> str:
        """Handle list blocks"""
        items = data.get('items', [])
        list_type = data.get('style', 'unordered')
        if not items:
            return ''
        tag = 'ol' if list_type == 'ordered' else 'ul'
        html_items = []
        for item in items:
            item_text = self._process_inline_formatting(item)
            if item_text.strip():
                html_items.append(f'<li>{item_text}</li>')
        if not html_items:
            return ''
        return f'<{tag} class="article-prose">{"".join(html_items)}</{tag}>'
    
    def _handle_quote(self, data: Dict[str, Any]) -> str:
        """Handle quote blocks"""
        text = self._process_inline_formatting(data.get('text', ''))
        caption = self._escape_html(data.get('caption', ''))
        if not text.strip():
            return ''
        quote_html = f'<blockquote class="article-prose">{text}'
        if caption:
            quote_html += f'<cite>{caption}</cite>'
        quote_html += '</blockquote>'
        return quote_html
    
    def _handle_delimiter(self, data: Dict[str, Any]) -> str:
        """Handle delimiter blocks"""
        return '<hr>'
    
    def _handle_table(self, data: Dict[str, Any]) -> str:
        """Handle table blocks"""
        content = data.get('content', [])
        with_headings = data.get('withHeadings', False)
        if not content or not content[0]:
            return ''
        html_rows = []
        for i, row in enumerate(content):
            if not row:
                continue
            is_header = with_headings and i == 0
            cell_tag = 'th' if is_header else 'td'
            cells = []
            for cell in row:
                cell_content = self._process_inline_formatting(cell)
                cells.append(f'<{cell_tag}>{cell_content}</{cell_tag}>')
            html_rows.append(f'<tr>{"".join(cells)}</tr>')
        if not html_rows:
            return ''
        table_body = "".join(html_rows)
        if with_headings and html_rows:
            # Move first row to thead
            header_row = html_rows[0]
            body_rows = html_rows[1:] if len(html_rows) > 1 else []
            return f'<table class="article-prose"><thead>{header_row}</thead><tbody>{"".join(body_rows)}</tbody></table>'
        else:
            return f'<table class="article-prose"><tbody>{table_body}</tbody></table>'
    
    def _handle_code(self, data: Dict[str, Any]) -> str:
        """Handle code blocks"""
        code = self._escape_html(data.get('code', ''))
        
        if not code.strip():
            return ''
        
        return f'<pre><code>{code}</code></pre>'
    
    def _handle_raw(self, data: Dict[str, Any]) -> str:
        """Handle raw HTML blocks (use with caution)"""
        html_content = data.get('html', '')
        # In production, you should sanitize this HTML
        return html_content
    
    def _handle_embed(self, data: Dict[str, Any]) -> str:
        """Handle embed blocks (videos, etc.)"""
        embed_url = data.get('embed', '')
        caption = self._escape_html(data.get('caption', ''))
        
        if not embed_url:
            return ''
        
        html = f'<div class="embed-container my-8 text-center">'
        html += f'<iframe src="{embed_url}" class="w-full h-96 border rounded"></iframe>'
        if caption:
            html += f'<p class="text-sm text-gray-500 mt-2">{caption}</p>'
        html += '</div>'
        
        return html
    
    def _handle_image(self, data: Dict[str, Any]) -> str:
        """Handle image blocks"""
        url = data.get('file', {}).get('url', '')
        caption = self._escape_html(data.get('caption', ''))
        with_border = data.get('withBorder', False)
        with_background = data.get('withBackground', False)
        stretched = data.get('stretched', False)
        
        if not url:
            return ''
        
        img_classes = "max-w-full h-auto"
        if with_border:
            img_classes += " border border-gray-200"
        if with_background:
            img_classes += " bg-gray-50 p-4"
        if stretched:
            img_classes += " w-full"
        
        html = f'<figure class="my-8 text-center">'
        html += f'<img src="{url}" alt="{caption}" class="{img_classes}">'
        if caption:
            html += f'<figcaption class="text-sm text-gray-500 mt-2 italic">{caption}</figcaption>'
        html += '</figure>'
        
        return html
    
    def _handle_link(self, data: Dict[str, Any]) -> str:
        """Handle link tool blocks"""
        link = data.get('link', '')
        title = self._escape_html(data.get('meta', {}).get('title', ''))
        description = self._escape_html(data.get('meta', {}).get('description', ''))
        image = data.get('meta', {}).get('image', {}).get('url', '')
        
        if not link:
            return ''
        
        html = f'<div class="link-preview border border-gray-200 rounded-lg p-6 my-8 hover:bg-gray-50 transition-colors">'
        html += f'<a href="{link}" class="block text-decoration-none" target="_blank" rel="noopener noreferrer">'
        
        if image:
            html += f'<img src="{image}" alt="{title}" class="w-full h-32 object-cover rounded mb-4">'
        
        if title:
            html += f'<h4 class="text-lg font-medium text-gray-900 mb-2">{title}</h4>'
        
        if description:
            html += f'<p class="text-gray-600 text-sm">{description}</p>'
        
        html += f'<p class="text-blue-600 text-sm mt-2">{link}</p>'
        html += '</a></div>'
        
        return html
    
    # Custom business block handlers
    
    def _handle_business_process(self, data: Dict[str, Any]) -> str:
        """Handle custom business process blocks"""
        name = self._escape_html(data.get('name', ''))
        description = self._escape_html(data.get('description', ''))
        steps = data.get('steps', [])
        owner = self._escape_html(data.get('owner', ''))
        
        if not name:
            return ''
        
        html = f'<div class="business-process border-l-4 border-blue-500 bg-blue-50 p-6 my-8 rounded-r-lg">'
        html += f'<h4 class="text-xl font-semibold text-blue-900 mb-3">📋 {name}</h4>'
        
        if description:
            html += f'<p class="text-blue-800 mb-4">{description}</p>'
        
        if owner:
            html += f'<p class="text-sm text-blue-700 mb-4"><strong>Process Owner:</strong> {owner}</p>'
        
        if steps:
            html += '<ol class="space-y-3 list-decimal pl-6">'
            for step in steps:
                step_text = self._escape_html(step.get('description', ''))
                if step_text:
                    html += f'<li class="text-blue-800">{step_text}</li>'
            html += '</ol>'
        
        html += '</div>'
        return html
    
    def _handle_control_matrix(self, data: Dict[str, Any]) -> str:
        """Handle custom control matrix blocks"""
        controls = data.get('controls', [])
        
        if not controls:
            return ''
        
        html = '<div class="control-matrix my-8">'
        html += '<h4 class="text-xl font-semibold text-red-900 mb-4">🛡️ Control Matrix</h4>'
        html += '<div class="overflow-x-auto">'
        html += '<table class="min-w-full bg-white border border-red-200 rounded-lg">'
        html += '<thead class="bg-red-50">'
        html += '<tr><th class="px-4 py-3 text-left font-medium text-red-900">Control ID</th>'
        html += '<th class="px-4 py-3 text-left font-medium text-red-900">Description</th>'
        html += '<th class="px-4 py-3 text-left font-medium text-red-900">Type</th>'
        html += '<th class="px-4 py-3 text-left font-medium text-red-900">Risk Level</th></tr>'
        html += '</thead><tbody>'
        
        for control in controls:
            control_id = self._escape_html(control.get('id', ''))
            desc = self._escape_html(control.get('description', ''))
            control_type = self._escape_html(control.get('type', ''))
            risk = self._escape_html(control.get('risk', ''))
            
            html += f'<tr class="border-b border-red-100">'
            html += f'<td class="px-4 py-3 text-red-800">{control_id}</td>'
            html += f'<td class="px-4 py-3 text-red-700">{desc}</td>'
            html += f'<td class="px-4 py-3 text-red-700">{control_type}</td>'
            html += f'<td class="px-4 py-3 text-red-700">{risk}</td>'
            html += '</tr>'
        
        html += '</tbody></table></div></div>'
        return html
    
    def _handle_role_definition(self, data: Dict[str, Any]) -> str:
        """Handle custom role definition blocks"""
        title = self._escape_html(data.get('title', ''))
        department = self._escape_html(data.get('department', ''))
        responsibilities = data.get('responsibilities', [])
        skills = data.get('skills', [])
        
        if not title:
            return ''
        
        html = f'<div class="role-definition border-l-4 border-green-500 bg-green-50 p-6 my-8 rounded-r-lg">'
        html += f'<h4 class="text-xl font-semibold text-green-900 mb-3">👤 {title}</h4>'
        
        if department:
            html += f'<p class="text-sm text-green-700 mb-4"><strong>Department:</strong> {department}</p>'
        
        if responsibilities:
            html += '<div class="mb-4">'
            html += '<h5 class="font-medium text-green-800 mb-2">Key Responsibilities:</h5>'
            html += '<ul class="space-y-1 list-disc pl-6">'
            for resp in responsibilities:
                resp_text = self._escape_html(resp)
                html += f'<li class="text-green-800">{resp_text}</li>'
            html += '</ul></div>'
        
        if skills:
            html += '<div>'
            html += '<h5 class="font-medium text-green-800 mb-2">Required Skills:</h5>'
            html += '<div class="flex flex-wrap gap-2">'
            for skill in skills:
                skill_text = self._escape_html(skill)
                html += f'<span class="bg-green-200 text-green-800 px-2 py-1 rounded text-sm">{skill_text}</span>'
            html += '</div></div>'
        
        html += '</div>'
        return html
    
    def _handle_maturity_model(self, data: Dict[str, Any]) -> str:
        """Handle custom maturity model blocks"""
        domain = self._escape_html(data.get('domain', ''))
        levels = data.get('levels', [])
        
        if not domain:
            return ''
        
        html = f'<div class="maturity-model border-l-4 border-purple-500 bg-purple-50 p-6 my-8 rounded-r-lg">'
        html += f'<h4 class="text-xl font-semibold text-purple-900 mb-4">📊 Maturity Model: {domain}</h4>'
        
        if levels:
            html += '<div class="space-y-3">'
            for i, level in enumerate(levels, 1):
                level_name = self._escape_html(level.get('name', f'Level {i}'))
                description = self._escape_html(level.get('description', ''))
                
                html += f'<div class="bg-white border border-purple-200 rounded p-4">'
                html += f'<h6 class="font-medium text-purple-900 mb-2">Level {i}: {level_name}</h6>'
                if description:
                    html += f'<p class="text-purple-800 text-sm">{description}</p>'
                html += '</div>'
            html += '</div>'
        
        html += '</div>'
        return html
    
    def _handle_process_flow(self, data: Dict[str, Any]) -> str:
        """Handle custom process flow blocks"""
        steps = data.get('steps', [])
        title = self._escape_html(data.get('title', 'Process Flow'))
        
        if not steps:
            return ''
        
        html = f'<div class="process-flow my-8">'
        html += f'<h4 class="text-xl font-semibold text-indigo-900 mb-4">🔄 {title}</h4>'
        html += '<div class="flex flex-col space-y-4">'
        
        for i, step in enumerate(steps):
            step_text = self._escape_html(step.get('text', ''))
            is_last = i == len(steps) - 1
            
            html += '<div class="flex items-center">'
            html += f'<div class="flex-shrink-0 w-8 h-8 bg-indigo-500 text-white rounded-full flex items-center justify-center text-sm font-medium">{i+1}</div>'
            html += f'<div class="ml-4 flex-grow">'
            html += f'<p class="text-indigo-800">{step_text}</p>'
            html += '</div></div>'
            
            if not is_last:
                html += '<div class="ml-4 w-px h-4 bg-indigo-300"></div>'
        
        html += '</div></div>'
        return html


class HTMLToEditorJS:
    """Converts HTML back to EditorJS JSON format (for editing existing content)"""
    
    def __init__(self):
        # This would be implemented for converting existing HTML content
        # to EditorJS format, which is more complex and would require HTML parsing
        pass
    
    def from_html(self, html: str) -> Dict[str, Any]:
        """Convert HTML to EditorJS format"""
        # This is a placeholder - implementing this would require
        # HTML parsing and conversion back to EditorJS blocks
        return {
            'blocks': [
                {
                    'type': 'paragraph',
                    'data': {'text': 'HTML to EditorJS conversion not implemented yet'}
                }
            ],
            'version': '2.28.2'
        }