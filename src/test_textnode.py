import unittest

from textnode import TextNode, TextType, BlockType
from main import split_nodes_delimiter, extract_markdown_images, extract_markdown_links, extract_title, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, block_to_block_type

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node1 = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node1, node2)

    def test_url(self):
        node1 = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is a text node", TextType.TEXT, "http://microsoft.com")
        self.assertNotEqual(node1, node2)

    def test_texttype(self):
        node1 = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node1, node2)

    def test_notext(self):
        node1 = TextNode(None, TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node1, node2)

    def test_emptytext(self):
        node1 = TextNode("", TextType.LINK)
        node2 = TextNode("This is a text node", TextType.LINK)
        self.assertNotEqual(node1, node2)

    def test_repr(self):
        node1 = TextNode(None, TextType.TEXT)
        node2 = TextNode("None", TextType.TEXT)
        str1 = str(node1)
        str2 = str(node2)
        self.assertEqual(str1, str2)

    def test_split_nodes_delimitersb1(self):
        textnode1 = TextNode("This is text with a **bold** block contained.", TextType.TEXT)
        list1 = [TextNode("This is text with a ", TextType.TEXT, None), TextNode("bold", TextType.BOLD, None), TextNode(" block contained.", TextType.TEXT, None)]
        self.assertEqual(split_nodes_delimiter([textnode1], "**", TextType.BOLD), list1)

    def test_split_nodes_delimitersb2(self):
        textnode2 = TextNode("This is text with an *italic* block contained.", TextType.TEXT)
        list2 = [TextNode("This is text with an *italic* block contained.", TextType.TEXT, None)]
        self.assertEqual(split_nodes_delimiter([textnode2], "**", TextType.BOLD), list2)

    def test_split_nodes_delimitersb3(self):
        textnode3 = TextNode("This is text with a `code` block contained.", TextType.TEXT)
        list3 = [TextNode("This is text with a `code` block contained.", TextType.TEXT, None)]
        self.assertEqual(split_nodes_delimiter([textnode3], "**", TextType.BOLD), list3)

    def test_split_nodes_delimitersb4(self):
        textnode4 = TextNode("This is text with a **bold**, *italic* and `code` block contained.", TextType.TEXT)
        list4 = [TextNode("This is text with a ", TextType.TEXT, None), TextNode("bold", TextType.BOLD, None), TextNode(", *italic* and `code` block contained.", TextType.TEXT, None)]
        self.assertEqual(split_nodes_delimiter([textnode4], "**", TextType.BOLD), list4)

    def test_split_nodes_delimitersb5(self):
        textnode5 = TextNode("*This* is text with a **bold**, *italic* and `code` block *contained.*", TextType.TEXT)
        list5 = [TextNode("*This* is text with a ", TextType.TEXT, None), TextNode("bold", TextType.BOLD, None), TextNode(", *italic* and `code` block *contained.*", TextType.TEXT, None)]
        self.assertEqual(split_nodes_delimiter([textnode5], "**", TextType.BOLD), list5)

    def test_split_nodes_delimitersb6(self):
        textnode6 = TextNode("This* is text with a **bold**, *italic* and `code` block *contained.*", TextType.TEXT)
        list6 = [TextNode("This* is text with a ", TextType.TEXT, None), TextNode("bold", TextType.BOLD, None), TextNode(", *italic* and `code` block *contained.*", TextType.TEXT, None)]
        self.assertEqual(split_nodes_delimiter([textnode6], "**", TextType.BOLD), list6)

    def test_split_nodes_delimitersb7(self):
        textnode7 = TextNode("*This* is text with a **bold**, *italic* and `code` block *contained.", TextType.TEXT)
        list7 = [TextNode("*This* is text with a ", TextType.TEXT, None), TextNode("bold", TextType.BOLD, None), TextNode(", *italic* and `code` block *contained.", TextType.TEXT, None)]
        self.assertEqual(split_nodes_delimiter([textnode7], "**", TextType.BOLD), list7)

    def test_split_nodes_delimitersi1(self):
        textnode1 = TextNode("This is text with a **bold** block contained.", TextType.TEXT)
        list1 = [TextNode("This is text with a **bold** block contained.", TextType.TEXT, None)]
        self.assertEqual(split_nodes_delimiter([textnode1], "*", TextType.ITALIC), list1)

    def test_split_nodes_delimitersi2(self):
        textnode2 = TextNode("This is text with an *italic* block contained.", TextType.TEXT)
        list2 = [TextNode("This is text with an ", TextType.TEXT, None), TextNode("italic", TextType.ITALIC, None), TextNode(" block contained.", TextType.TEXT, None)]
        self.assertEqual(split_nodes_delimiter([textnode2], "*", TextType.ITALIC), list2)

    def test_split_nodes_delimitersi3(self):
        textnode3 = TextNode("This is text with a `code` block contained.", TextType.TEXT)
        list3 = [TextNode("This is text with a `code` block contained.", TextType.TEXT, None)]
        self.assertEqual(split_nodes_delimiter([textnode3], "*", TextType.ITALIC), list3)

    def test_split_nodes_delimitersi4(self):
        textnode4 = TextNode("This is text with a **bold**, *italic* and `code` block contained.", TextType.TEXT)
        list4 = [TextNode("This is text with a **bold**, ", TextType.TEXT, None), TextNode("italic", TextType.ITALIC, None), TextNode(" and `code` block contained.", TextType.TEXT, None)]
        self.assertEqual(split_nodes_delimiter([textnode4], "*", TextType.ITALIC), list4)

    def test_split_nodes_delimitersi5(self):
        textnode5 = TextNode("*This* is text with a **bold**, *italic* and `code` block *contained.*", TextType.TEXT)
        list5 = [TextNode("This", TextType.ITALIC, None), TextNode(" is text with a **bold**, ", TextType.TEXT, None), TextNode("italic", TextType.ITALIC, None), TextNode(" and `code` block ", TextType.TEXT, None), TextNode("contained.", TextType.ITALIC, None)]
        self.assertEqual(split_nodes_delimiter([textnode5], "*", TextType.ITALIC), list5)

#    def test_split_nodes_delimitersi6(self):
#        textnode6 = TextNode("This* is text with a **bold**, *italic* and `code` block *contained.*", TextType.TEXT)
#        list6 = [TextNode("This* is text with a ", TextType.TEXT, None), TextNode("bold", TextType.BOLD, None), TextNode(", *italic* and `code` block *contained.*", TextType.TEXT, None)]
#        with self.assertRaises(Exception):
#            print(split_nodes_delimiter, [textnode6], "**", TextType.ITALIC)

        #with self.assertRaises(Exception) as context:
        #    split_nodes_delimiter([textnode6], "**", TextType.ITALIC)
        #self.assertTrue("Unmatched delimiter in text." in str(context.exception))

#    def test_split_nodes_delimitersi7(self):
#        textnode7 = TextNode("*This* is text with a **bold**, *italic* and `code` block *contained.", TextType.TEXT)
#        list7 = [TextNode("*This* is text with a ", TextType.TEXT, None), TextNode("bold", TextType.BOLD, None), TextNode(", *italic* and `code` block *contained.", TextType.TEXT, None)]
#        self.assertRaises(Exception, split_nodes_delimiter, [textnode7], "**", TextType.ITALIC)
        #with self.assertRaises(Exception) as context:
        #    split_nodes_delimiter([textnode7], "**", TextType.ITALIC)
        #self.assertTrue("Unmatched delimiter in text." in str(context.exception))

    def test_split_nodes_delimitersc1(self):
        textnode1 = TextNode("This is text with a **bold** block contained.", TextType.TEXT)
        list1 = [TextNode("This is text with a **bold** block contained.", TextType.TEXT, None)]
        self.assertEqual(split_nodes_delimiter([textnode1], "`", TextType.CODE), list1)

    def test_split_nodes_delimitersc2(self):
        textnode2 = TextNode("This is text with an *italic* block contained.", TextType.TEXT)
        list2 = [TextNode("This is text with an *italic* block contained.", TextType.TEXT, None)]
        self.assertEqual(split_nodes_delimiter([textnode2], "`", TextType.CODE), list2)

    def test_split_nodes_delimitersc3(self):
        textnode3 = TextNode("This is text with a `code` block contained.", TextType.TEXT)
        list3 = [TextNode("This is text with a ", TextType.TEXT, None), TextNode("code", TextType.CODE, None), TextNode(" block contained.", TextType.TEXT, None)]
        self.assertEqual(split_nodes_delimiter([textnode3], "`", TextType.CODE), list3)

    def test_split_nodes_delimitersc4(self):
        textnode4 = TextNode("This is text with a **bold**, *italic* and `code` block contained.", TextType.TEXT)
        list4 = [TextNode("This is text with a **bold**, *italic* and ", TextType.TEXT, None), TextNode("code", TextType.CODE, None), TextNode(" block contained.", TextType.TEXT, None)]
        self.assertEqual(split_nodes_delimiter([textnode4], "`", TextType.CODE), list4)

    def test_split_nodes_delimitersc5(self):
        textnode5 = TextNode("*This* is text with a **bold**, *italic* and `code` block *contained.*", TextType.TEXT)
        list5 = [TextNode("*This* is text with a **bold**, *italic* and ", TextType.TEXT, None), TextNode("code", TextType.CODE, None), TextNode(" block *contained.*", TextType.TEXT, None)]
        self.assertEqual(split_nodes_delimiter([textnode5], "`", TextType.CODE), list5)

    def test_split_nodes_delimitersc6(self):
        textnode6 = TextNode("This* is text with a **bold**, *italic* and `code` block *contained.*", TextType.TEXT)
        list6 = [TextNode("This* is text with a **bold**, *italic* and ", TextType.TEXT, None), TextNode("code", TextType.CODE, None), TextNode(" block *contained.*", TextType.TEXT, None)]
        self.assertEqual(split_nodes_delimiter([textnode6], "`", TextType.CODE), list6)

    #def test_split_nodes_delimitersc7(self):
    #    textnode7 = TextNode("*This* is text with a **bold**, *italic* and `code` block *contained.", TextType.TEXT)
    #    list7 = [TextNode("*This* is text with a **bold**, *italic* and ", TextType.TEXT, None), TextNode("code", TextType.CODE, None), TextNode(" block *contained.", TextType.TEXT, None)]
    #    self.assertEqual(split_nodes_delimiter([textnode7], "`", TextType.CODE), list7)

    def test_extract_images(self):
        self.assertEqual(extract_markdown_images("This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"), [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")])

    def test_extract_links(self):
        self.assertEqual(extract_markdown_links("This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"), [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")])

    def test_split_nodes_image(self):
        node = TextNode("This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)",TextType.TEXT,)
        self.assertEqual(split_nodes_image([node]), [TextNode("This is text with a ", "TextType.TEXT", "None"), TextNode("rick roll", "TextType.IMAGE", "https://i.imgur.com/aKaOqIh.gif"), TextNode(" and ", "TextType.TEXT", "None"), TextNode("obi wan", "TextType.IMAGE", "https://i.imgur.com/fJRm4Vk.jpeg")])

    def test_split_nodes_image(self):
        node = TextNode("*This* is text with a **bold**, *italic* and `code` block *contained.*", TextType.TEXT)
        self.assertEqual(split_nodes_image([node]), [TextNode("*This* is text with a **bold**, *italic* and `code` block *contained.*", TextType.TEXT)])

    def test_split_nodes_link(self):
        node = TextNode("This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)", TextType.TEXT,)
        self.assertEqual(split_nodes_link([node]), [TextNode("This is text with a link ", "TextType.TEXT", "None"), TextNode("to boot dev", "TextType.LINK", "https://www.boot.dev"), TextNode(" and ", "TextType.TEXT", "None"), TextNode("to youtube", "TextType.LINK", "https://www.youtube.com/@bootdotdev")])

    def test_split_nodes_link(self):
        node = TextNode("*This* is text with a **bold**, *italic* and `code` block *contained.*", TextType.TEXT)
        self.assertEqual(split_nodes_image([node]), [TextNode("*This* is text with a **bold**, *italic* and `code` block *contained.*", TextType.TEXT)])

    def test_text_to_textnodes(self):
        text = "This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        self.assertEqual(text_to_textnodes(text), [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev")
        ])

    def test_markdown_to_blocks(self):
        markdown = "# This is a heading\n\nThis is a paragraph of text. It has some **bold** and *italic* words inside of it.\n\n* This is the first list item in a list block\n* This is a list item\n* This is another list item\n"
        self.assertEqual(markdown_to_blocks(markdown), ['# This is a heading', 'This is a paragraph of text. It has some **bold** and *italic* words inside of it.', '* This is the first list item in a list block\n* This is a list item\n* This is another list item'])

    def test_markdown_to_blocks(self):
        markdown = ""
        self.assertEqual(markdown_to_blocks(markdown), [])

    def test_markdown_to_blocks(self):
        markdown = "\n\n\n# This\n\n"
        self.assertEqual(markdown_to_blocks(markdown), ['# This'])

    def test_block_to_block_type_code(self):
        markdown = "```Code\nblock\n```\n\n"
        self.assertEqual(block_to_block_type(markdown), BlockType.CODE)

    def test_block_to_block_type_h1(self):
        markdown = "# This is a heading\n"
        self.assertEqual(block_to_block_type(markdown), BlockType.HEADING)

    def test_block_to_block_type_h6(self):
        markdown = "###### This is a heading\n"
        self.assertEqual(block_to_block_type(markdown), BlockType.HEADING)

    def test_block_to_block_type_h7(self):
        markdown = "####### This is a heading\n"
        self.assertEqual(block_to_block_type(markdown), BlockType.PARAGRAPH)

    def test_block_to_block_type_q1(self):
        markdown = "> Comment\n> \n>more comm\n>ent\n\n```\n"
        self.assertEqual(block_to_block_type(markdown), BlockType.QUOTE)

    def test_block_to_block_type_ul1(self):
        markdown = "* This is the first list item in a list block\n* This is a list item\n* This is another list item\n"
        self.assertEqual(block_to_block_type(markdown), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_ul2(self):
        markdown = "- This is the first list item in a list block\n- This is a list item\n- This is another list item\n"
        self.assertEqual(block_to_block_type(markdown), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_ol1(self):
        markdown = "2. This is the first list item in a list block\n3. This is a list item\n4. This is another list item\n"
        self.assertEqual(block_to_block_type(markdown), BlockType.ORDERED_LIST)

    def test_block_to_block_type_ol2(self):
        markdown = "1. This is the first list item in a list block\n2. This is a list item\n3. This is another list item\n"
        self.assertEqual(block_to_block_type(markdown), BlockType.ORDERED_LIST)

    def test_extract_title(self):
        markdown = "# Title is title\n## 2t\n  <.># Not totel\n### 2nd Title\n"
        self.assertEqual(extract_title(markdown), "Title is title")
        markdown = "## Title is title\n## 2t\n  <.># Not totel\n# 2nd Title\n"
        self.assertEqual(extract_title(markdown), "2nd Title")

if __name__ == "__main__":
    unittest.main()