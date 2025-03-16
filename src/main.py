import os
import re
import shutil
import sys

from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextNode, TextType, BlockType

def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            html_node = LeafNode(None, text_node.text)
        case TextType.BOLD:
            html_node = LeafNode("b", text_node.text)
        case TextType.ITALIC:
            html_node = LeafNode("i", text_node.text)
        case TextType.CODE:
            html_node = LeafNode("code", text_node.text)
        case TextType.LINK:
            html_node = LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            html_node = LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
        case _:
            raise Exception("Unrecognized text type")
    return html_node

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
        else:
            dl_toggle = False
            prefix = ""
            text = ""
            postfix = node.text
            while (index := postfix.find(delimiter)) >= 0:
                #print(f"Delimiter Index: {index} Postfix Length: {len(postfix)}")
                if index >= (len(postfix) - 1):
                    raise Exception("Unmatched delimiter in text.")
                prefix += postfix[0: index]
                postfix = postfix[index + len(delimiter):]
                #print(f'Preceding/Remaining Text: "{prefix}" / "{postfix}"\n')
                if (delimiter == '*'):
                    if (postfix[0] == '*'):
                        #print("Found double asterisk")
                        dl_toggle = not dl_toggle
                        prefix += '**'
                        postfix = postfix[1:]
                        #if (dl_toggle):
                        #print("Skipping...\n")
                        continue
                    elif (postfix[0] == ' '):
                        #print("Found asterisked list item")
                        nl = postfix.find('\n') + 1
                        prefix += '*' + postfix[0: nl]
                        postfix = postfix[nl:]
                        continue
                #print(f"DELIMITER INDEX: {index} POSTFIX LENGTH: {len(postfix)}")
                #print(f"Delimiter = '{delimiter}', Postfix[0:3] = '{postfix[0:3]}'")
                if (delimiter == '`') and (postfix[0:3] == '``\n'):
                    #print("Found triple backquote & newline")
                    dl_toggle = not dl_toggle
                    prefix += '```\n'
                    postfix = postfix[3:]
                    if (dl_toggle):
                        #print("Skipping...\n")
                        continue
                if (index := postfix.find(delimiter)) != 0:
                    #print(f"DELIMITER INDEX: {index} POSTFIX LENGTH: {len(postfix)}")
                    #print(f"Delimiter = '{delimiter}', Postfix[0:3] = '{postfix[0:3]}'")
                    if index >= len(postfix):
                        raise Exception("Unmatched delimiter in text.")
                    text = postfix[0: index]
                    if (delimiter == '```\n'):
                        text = text[0:-2]
                    postfix = postfix[index + len(delimiter):]
                    #print(f'Prefix: "{prefix}" Fix: "{text}" Postfix: "{postfix}"')
                    if len(text) > 0:
                        if len(prefix) > 0:
                            new_nodes.append(TextNode(prefix, TextType.TEXT))
                            prefix = ""
                        new_nodes.append(TextNode(text, text_type))
                else:
                    raise Exception("Unmatched delimiter in text.")
                #print(new_nodes)
                #print('x' * 40)
            #print(f'PREFIX: "{prefix}" FIX: "{text}" POSTFIX: "{postfix}"')
            if len(text) == 0:
                new_nodes.append(TextNode(prefix + postfix, TextType.TEXT))
            if (len(text) > 0) and (len(postfix) > 0):
                new_nodes.append(TextNode(postfix, TextType.TEXT))
    return new_nodes

def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type == TextType.TEXT:
            new_nodes_text = re.split("(!\[.*?\]\(.*?\))", node.text)
            for text in new_nodes_text:
                if len(text) > 0:
                    match = re.match("!\[(.*?)\]\((.*?)\)", text)
                    if match == None:
                        new_nodes.append(TextNode(text, node.text_type))
                    else:
                        new_nodes.append(TextNode(match.group(1), TextType.IMAGE, match.group(2)))
        else:
            new_nodes.append(node)
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type == TextType.TEXT:
            new_nodes_text = re.split("((?<!!)\[.*?\]\(.*?\))", node.text)
            for text in new_nodes_text:
                if len(text) > 0:
                    match = re.match("\[(.*?)\]\((.*?)\)", text)
                    if match == None:
                        new_nodes.append(TextNode(text, node.text_type))
                    else:
                        new_nodes.append(TextNode(match.group(1), TextType.LINK, match.group(2)))
        else:
            new_nodes.append(node)
    return new_nodes

def extract_markdown_images(text):
    #"This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
    # [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")]
    matches = re.findall("!\[(.*?)\]", text), re.findall("\(http.*?\)", text)
    links = []
    for link in range(0, len(matches)):
        links.append((matches[0][link], matches[1][link].strip("()")))
    return links

def extract_markdown_links(text):
    #"This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
    # [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")]
    matches = re.findall("\[(.*?)\]", text), re.findall("\(http.*?\)", text)
    links = []
    for link in range(0, len(matches)):
        links.append((matches[0][link], matches[1][link].strip("()")))
    return links

def extract_title(markdown):
    match = re.search("^#{1}\s(.*)", markdown, re.MULTILINE)
    if match is None:
        raise Exception("No title found in markdown text")
    return match.group(1)

def print_nodes(nodes):
    for node in nodes:
        print(node)
    print()
    return

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_image(nodes)
    for delimiter in [('```', TextType.CODE), ('**', TextType.BOLD), ('*', TextType.ITALIC), ('_', TextType.ITALIC), ('`', TextType.CODE)]:
        for node in nodes:
            nodes = split_nodes_delimiter(nodes, delimiter[0], delimiter[1])
    return nodes

def markdown_to_blocks(markdown):
    blocks = []
    lines = markdown.split("\n")
    block = ""
    for i in range(len(lines)):
        if lines[i] != "":
            block += lines[i] + "\n"
            if (i == len(lines) - 1):
                blocks.append(block.strip())
        else:
            if len(block) > 0:
                blocks.append(block.strip())
            block = ""
    return blocks

def block_to_block_type(markdown):
    if re.match("^#{1,6}\s.*", markdown) != None:
        type = BlockType.HEADING
    elif re.match("^`{3}([\w]*)\n([\S\s]+?)\n`{3}", markdown, re.MULTILINE) != None:
        type = BlockType.CODE
    elif re.match("(\n|^)((>|> )*?) (.*?)(?=\n|$)", markdown, re.MULTILINE) != None:
        type = BlockType.QUOTE
    elif re.match("(?:(\*|-).*\s)+", markdown, re.MULTILINE) != None:
        type = BlockType.UNORDERED_LIST
    elif re.match("^(\s*)(\d+\.\s+)(.*)", markdown, re.MULTILINE) != None:
        type = BlockType.ORDERED_LIST
    else:
        type = BlockType.PARAGRAPH
    return type

def markdown_to_html_node(markdown):
    md_blocks = markdown_to_blocks(markdown)
    parent_nodes = []
    for md_block in md_blocks:
        block_type = block_to_block_type(md_block)
        #print(f"markdown_to_html_node: BLOCK_TYPE = '{block_type}'")
        #print(f"markdown_to_html_node: MD_BLOCK = '{md_block}'")
        match block_type:
            case BlockType.PARAGRAPH:
                leaf_nodes = []
                text_nodes = text_to_textnodes(md_block)
                for text_node in text_nodes:
                    text_node.text = text_node.text.replace('\n', ' ')
                    leaf_nodes.append(text_node_to_html_node(text_node))
                parent_nodes.append(ParentNode("p", leaf_nodes))

            case BlockType.HEADING:
                leaf_nodes = []
                text_nodes = text_to_textnodes(md_block)
                heading = text_nodes[0].text.count('#', 0, 6)
                text_nodes[0].text = text_nodes[0].text[heading + 1:]
                for text_node in text_nodes:
                    text_node.text = text_node.text.replace('\n', ' ')
                    leaf_nodes.append(text_node_to_html_node(text_node))
                parent_nodes.append(ParentNode(f"h{heading}", leaf_nodes))

            case BlockType.CODE:
                leaf_nodes = []
                text_nodes = text_to_textnodes(md_block)
                # Hack to get rid of unwanted newline character at start of text (from split_nodes_delimiter?)
                text_nodes[0].text = text_nodes[0].text.lstrip('\n')
                for text_node in text_nodes:
                    leaf_nodes.append(text_node_to_html_node(text_node))
                parent_nodes.append(ParentNode("pre", leaf_nodes))

            case BlockType.QUOTE:
                leaf_nodes = []
                text_nodes = text_to_textnodes(md_block)
                for text_node in text_nodes:
                    lines = text_node.text.split('\n')
                    for i in range(len(lines)):
                        lines[i] = lines[i].lstrip('> ')
                        lines[i] = lines[i].lstrip('>')
                    text_node.text = '\n'.join(lines)
                    leaf_nodes.append(text_node_to_html_node(text_node))
                parent_nodes.append(ParentNode("blockquote", leaf_nodes))

            case BlockType.UNORDERED_LIST:
                lines = list(filter(None, re.split("^(?:\*\s)|(?:-\s)", md_block, flags = re.MULTILINE)))
                #print(f"markdown_to_html_node: LINES = {lines}")
                list_nodes = []
                for i in range(len(lines)):
                    #print(f"markdown_to_html_node: LINES[{i}] = {lines[i]}")
                    leaf_nodes = []
                    text_nodes = text_to_textnodes(lines[i])
                    for text_node in text_nodes:
                        text_node.text = text_node.text.replace('\n', '')
                        leaf_nodes.append(text_node_to_html_node(text_node))
                        #print(f"markdown_to_html_node: LEAF_NODES = {leaf_nodes}")
                    list_nodes.append(ParentNode("li", leaf_nodes))
                    #print(f"markdown_to_html_node: LIST_NODE = {list_nodes}")
                parent_nodes.append(ParentNode("ul", list_nodes))
                #print(f"markdown_to_html_node: PARENT_NODES = {parent_nodes}")

            case BlockType.ORDERED_LIST:
                lines = list(filter(None, re.split("^\d*\.\s", md_block, flags = re.MULTILINE)))
                list_nodes = []
                for i in range(len(lines)):
                    leaf_nodes = []
                    text_nodes = text_to_textnodes(lines[i])
                    for text_node in text_nodes:
                        text_node.text = text_node.text.replace('\n', '')
                        leaf_nodes.append(text_node_to_html_node(text_node))
                    list_nodes.append(ParentNode("li", leaf_nodes))
                parent_nodes.append(ParentNode("ol", list_nodes))

    html_node = ParentNode("div", parent_nodes)
    return html_node

def listfiles(dir):
    if (os.path.isdir(dir)):
        for entry in os.listdir(dir):
            path = f"{dir}/{entry}"
            if (os.path.isdir(path)):
                listfiles(path)
            else:
                print(f"\t'{path}'")
    else:
        print(f"'{dir}' is not a directory")

def copyfiles(src, dst):
    if (os.path.isdir(src)):
        for entry in os.listdir(src):
            sp = f"{src}/{entry}"
            dp = f"{dst}/{entry}"
            if (os.path.isdir(sp)):
                os.mkdir(dp, mode=0o777)
                copyfiles(sp, dp)
            else:
                print(f"\tCopying '{sp}' to '{dp}'...")
                shutil.copy(sp, dp)
    else:
        print(f"'{src}' is not a directory")

def generate_page(from_path, base_path, template_path, dest_path):
    print(f"\tGenerating page from '{from_path}' to '{dest_path}' using '{template_path}'...")
    src = open(from_path)
    markdown = src.read()
    src.close()
    html_node = markdown_to_html_node(markdown)
    src = open(template_path)
    html_template = src.read()
    src.close()
    html_page = html_template.replace('{{ Title }}', extract_title(markdown))
    #print(html_node)
    #print(html_node.to_html())
    html_page = html_page.replace('{{ Content }}', html_node.to_html())
    if (base_path != '/'):
        html_page = html_page.replace('href="/', f'href="{base_path}')
        html_page = html_page.replace('src="/', f'src="{base_path}')
    dst = open(dest_path, mode = 'w')
    dst.write(html_page)
    dst.close()

def generate_pages_recursive(dir_path_content, base_path, template_path, dest_dir_path):
    if (os.path.isdir(dir_path_content)):
        if not (os.path.exists(dest_dir_path)):
            os.mkdir(dest_dir_path, mode=0o777)
        if (os.path.isdir(dest_dir_path)):
            print(f"Generating pages from '{dir_path_content}' to '{dest_dir_path}' using '{template_path}'...")
            for entry in os.listdir(dir_path_content):
                path = os.path.join(dir_path_content, entry)
                if (os.path.isdir(path)):
                    generate_pages_recursive(path, base_path, template_path, os.path.join(dest_dir_path, entry))
                else:
                    dot = entry.rfind('.')
                    if (0 < dot < (len(entry) - 1)):
                        name = entry[0:dot]
                        ext  = entry[dot + 1:]
                    else:
                        name = entry
                        ext  = ''
                    if (ext.lower() == 'md'):
                        generate_page(f"{os.path.join(dir_path_content, name)}.md", base_path, template_path, f"{os.path.join(dest_dir_path, name)}.html")
                    else:
                        print(f"\tIgnoring '{os.path.join(dest_dir_path, entry)}'...")
        else:
            print(f"'{dest_dir_path}' is not a directory")
    else:
        print(f"'{dir_path_content}' is not a directory")

def main():
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    else:
        basepath = '/'

    # text_node = TextNode("Hello World!", TextType.BOLD, "https://www.boot.dev")
    # print(text_node)

    #node1 = TextNode("This is a text node", TextType.TEXT)
    #node2 = TextNode("This is an italic text node", TextType.ITALIC)
    #nodel = TextNode("This is a link node", TextType.LINK, "http://microsoft.com")
    #nodei = TextNode("This is an image node", TextType.IMAGE, "http://microsoft.com")

    #print (text_node_to_html_node(node1))
    #print (text_node_to_html_node(node2))
    #print (text_node_to_html_node(nodel))
    #print (text_node_to_html_node(nodei))

    #node = ParentNode(
    #    "p",
    #    [
    #        LeafNode("b", "Bold text"),
    #        LeafNode(None, "Normal text"),
    #        LeafNode("i", "italic text"),
    #        LeafNode(None, "Normal text"),
    #    ],
    #)
    # print(node.to_html())

    #node2 = LeafNode("p", "This is a paragraph of text.")
    #node3 = LeafNode("p", "This is a paragraph of text.", {"style": "bold", "color": "red"})
    #node4 = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
    #nodet1 = ParentNode("p", [node2, node3], {"style": "parental", "color": "yellow"})
    #nodet2 = ParentNode("p", [node4])
    #node = ParentNode("p", [nodet1, nodet2], {"style": "parental", "color": "blue"})
    # print(node.to_html())

    # textnode1 = TextNode("This is text with a **bold** block contained.", TextType.TEXT)
    # textnode2 = TextNode("This is text with an *italic* block contained.", TextType.TEXT)
    # textnode3 = TextNode("This is text with an _italic_ block contained.", TextType.TEXT)
    # textnode4 = TextNode("This is text with a `code` block contained.", TextType.TEXT)
    # textnode5 = TextNode("```\nThis is text with a `code` block contained.\n```\n", TextType.TEXT)
    # textnode6 = TextNode("This is text with a **bold**, *italic* and `code` block contained.", TextType.TEXT)
    # textnode7 = TextNode("*This* is text with a **bold**, *italic* and `code` block *contained.*", TextType.TEXT)
    # textnode8 = TextNode("This* is text with a **bold**, _italic_ and `code` block *contained.*", TextType.TEXT)
    # textnode9 = TextNode("*This* is text with a **bold**, *italic* and `code` block *contained.", TextType.TEXT)

    # print('-' * 80)
    # print(f"TextNode: {textnode5.text}")
    # print('-' * 80)
    # print(split_nodes_delimiter([textnode5], "`", TextType.CODE))
    # print('-' * 80)
    # print(split_nodes_delimiter([textnode5], "```\n", TextType.CODE))
    # print('-' * 80)

    # for textnode in [textnode1, textnode2, textnode3, textnode4, textnode5, textnode6, textnode7, textnode8, textnode9]:
    #     print('-' * 80)
    #     print(f"TextNode: {textnode.text}")
    #     print()
    #     print(split_nodes_delimiter([textnode], "**", TextType.BOLD))
    #     print(split_nodes_delimiter([textnode], "*", TextType.ITALIC))
    #     print(split_nodes_delimiter([textnode], "_", TextType.ITALIC))
    #     print(split_nodes_delimiter([textnode], "`", TextType.CODE))
    #     print(split_nodes_delimiter([textnode], "```\n", TextType.CODE))
    #     print('-' * 80)
    #     print()

    #print(extract_markdown_images("This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"))
    # [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")]
    #node = TextNode(
    #    "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)",
    #    TextType.TEXT,
    #)
    #new_nodes = split_nodes_image([node])

    #print(extract_markdown_links("This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"))
    # [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")]
    #node = TextNode(
    #    "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
    #    TextType.TEXT,
    #)
    #new_nodes = split_nodes_link([node])

    #new_nodes = text_to_textnodes("This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)")

    #markdown = "# This is a heading\n\nThis is just some text\nWhich has no type\n\n> Comment\n> \n>more comm\n>ent\n\n```\nThis is a paragraph of text. It has some **bold** and *italic* words inside of it.\n```\n\n* This is the first list item in a list block\n* This is a list item\n* This is another list item\n\n2. This is the first list item in a list block\n3. This is a list item\n4. This is another list item\n"
    #markdown = "```Code\nblock\n```\n\nStandard\n"
    # markdown_blocks = markdown_to_blocks(markdown)
    # for block in markdown_blocks:
    #     print(block)
    #     type = block_to_block_type(block)
    #     print(type)
    #     print()

    #markdown = "# This is a heading\n\nThis is just some text\nWhich has no type\n\n> Comment\n> \n>more comm\n>ent\n\nThis is a paragraph of text. It has some **bold** and *italic* words inside of it.\n\n* This is the first list item in a list block\n* This is a list item\n* This is another list item\n\n2. This is the first list item in a list block\n3. This is a list item\n4. This is another list item\n"
    #markdown = "# This is a heading\n\nThis is just some text\nWhich has no type\n\nThis is some **bold text** and some *italic text* and some `code text` in a paragraph\n\n"
    #markdown = "```Code\nblock\n```\n\nStandard\n"
#     markdown = """
# This is **bolded** paragraph
# text in a p
# tag here

# This is another paragraph with _italic_ text and `code` here

# """
#     markdown = """
# ```
# This is text that _should_ remain
# the **same** even with inline stuff
# ```
# """

    #print(markdown)
    #html_node = markdown_to_html_node(markdown)
    #html = repr(html_node.to_html()).strip("',\"")
    #print(html)
    #return
    #cwd = os.getcwd()
    cwd = "./"
    src = cwd + "static"
    dst = cwd + "docs"
    if (os.path.exists(src)) and (os.path.isdir(src)):
        if (os.path.exists(dst)) and (os.path.isdir(dst)):
            print(f"Deleting existing directory '{dst}'...")
            shutil.rmtree(dst)
        if not(os.path.exists(dst)):
            print(f"Creating new directory '{dst}' from '{src}'")
            os.mkdir(dst, mode=0o777)
            if (os.path.exists(dst)) and (os.path.isdir(dst)):
                copyfiles(src, dst)
    generate_pages_recursive(cwd + 'content', basepath, cwd + 'template.html', dst)

if __name__ == "__main__":
    main()