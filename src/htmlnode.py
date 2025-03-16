import functools

class HTMLNode():
    def __init__(self, tag = None, value = None, children = None, props = None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def __repr__(self):
        return f'HTMLNode("{self.tag}", "{self.value}", "{self.children}", "{self.props}")'

    def to_html(self):
        raise NotImplementedError("Not yet implemented")

    def props_to_html(self):
        if self.props == None:
            return ""
        return functools.reduce(lambda str, prop: str + ' ' + prop[0] + '="' + prop[1] + '"', self.props.items(), "")

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props = None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.value == None:
            raise ValueError("Leaf node must have a value")
        if self.tag == None:
            return self.value
        return f'<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>'

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props = None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        if self.tag == None:
            raise ValueError("Parent node must have a tag")
        if self.children == None:
            raise ValueError("Parent node must have at least one child node")
        html = f'<{self.tag}{self.props_to_html()}>'
        for node in self.children:
            html += node.to_html()
        html += f'</{self.tag}>'
        return html

