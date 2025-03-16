import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextNode, TextType, BlockType
from main import text_node_to_html_node, markdown_to_html_node

class TestHTMLNode(unittest.TestCase):
    def test_props_p(self):
        node1 = HTMLNode("p", "This is an HTML node", None, {"style": "bold", "color": "red"})
        str1 = node1.props_to_html()
        str2 = ' style="bold" color="red"'
        self.assertEqual(str1, str2)

    def test_props_a(self):
        node1 = HTMLNode("a", "This is an HTML node", None, {"href": "https://www.microsoft.com", "target": "_blank"})
        str1 = node1.props_to_html()
        str2 = ' href="https://www.microsoft.com" target="_blank"'
        self.assertEqual(str1, str2)

    def test_repr(self):
        node1 = HTMLNode("p", "This is an HTML node")
        node2 = HTMLNode("p", "This is an HTML node", None, None)
        str1 = str(node1)
        str2 = str(node2)
        self.assertEqual(str1, str2)

    def test_leaf_p_noprops(self):
        node1 = LeafNode("p", "This is a paragraph of text.")
        str1 = node1.props_to_html()
        str2 = ''
        self.assertEqual(str1, str2)

    def test_leaf_p_props(self):
        node1 = LeafNode("p", "This is a paragraph of text.", {"style": "bold", "color": "red"})
        str1 = node1.props_to_html()
        str2 = ' style="bold" color="red"'
        self.assertEqual(str1, str2)

    def test_leaf_p_html_noprops(self):
        node1 = LeafNode("p", "This is a paragraph of text.")
        str1 = node1.to_html()
        str2 = '<p>This is a paragraph of text.</p>'
        self.assertEqual(str1, str2)

    def test_leaf_p_html(self):
        node1 = LeafNode("p", "This is a paragraph of text.", {"style": "bold", "color": "red"})
        str1 = node1.to_html()
        str2 = '<p style="bold" color="red">This is a paragraph of text.</p>'
        self.assertEqual(str1, str2)

    def test_leaf_a_html(self):
        node1 = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        str1 = node1.to_html()
        str2 = '<a href="https://www.google.com">Click me!</a>'
        self.assertEqual(str1, str2)

    def parent_childless_html(self):
        node = ParentNode("p", None, None)
        str1 = node.to_html()
        str2 = 'Parent node must have at least one child node'
        self.assertEqual(str1, str2)
        
    def parent_children_html(self):
        node2 = LeafNode("p", "This is a paragraph of text.")
        node3 = LeafNode("p", "This is a paragraph of text.", {"style": "bold", "color": "red"})
        node = ParentNode("p", [node2, node3], {"style": "parental", "color": "blue"})
        str1 = node.to_html()
        str2 = '<p style="parental" color="blue"><p>This is a paragraph of text."</p><p style="bold" color="red">This is a paragraph of text.</p></p>'
        self.assertEqual(str1, str2)

    def parent_tree_html(self):
        node2 = LeafNode("p", "This is a paragraph of text.")
        node3 = LeafNode("p", "This is a paragraph of text.", {"style": "bold", "color": "red"})
        node4 = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        nodet1 = ParentNode("p", [node2, node3], {"style": "parental", "color": "yellow"})
        nodet2 = ParentNode("p", [node4])
        node = ParentNode("p", [nodet1, nodet2], {"style": "parental", "color": "blue"})
        str1 = node.to_html()
        str2 = '<p style="parental" color="blue"><p style="parental" color="yellow"><p>This is a paragraph of text."</p><p style="bold" color="red">This is a paragraph of text.</p></p><p><a href="https://www.google.com">Click me!</a></p></p>'
        self.assertEqual(str1, str2)

    def test_text_to_html_normal(self):
        node1 = TextNode("This is a text node", TextType.TEXT)
        str1 = str(text_node_to_html_node(node1))
        str2 = 'HTMLNode("None", "This is a text node", "None", "None")'
        self.assertEqual(str1, str2)

    def test_text_to_html_italic(self):
        node1 = TextNode("This is an italic text node", TextType.ITALIC)
        str1 = str(text_node_to_html_node(node1))
        str2 = 'HTMLNode("i", "This is an italic text node", "None", "None")'
        self.assertEqual(str1, str2)

    def test_text_to_html_link(self):
        node1 = TextNode("This is a link node", TextType.LINK, "http://microsoft.com")
        str1 = str(text_node_to_html_node(node1))
        str2 = 'HTMLNode("a", "This is a link node", "None", "{\'href\': \'http://microsoft.com\'}")'
        self.assertEqual(str1, str2)

    def test_text_to_html_image(self):
        node1 = TextNode("This is an image node", TextType.IMAGE, "http://microsoft.com")
        str1 = str(text_node_to_html_node(node1))
        str2 = 'HTMLNode("img", "", "None", "{\'src\': \'http://microsoft.com\', \'alt\': \'This is an image node\'}")'
        self.assertEqual(str1, str2)

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>\nThis is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

if __name__ == "__main__":
    unittest.main()