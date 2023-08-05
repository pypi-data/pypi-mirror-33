#!/usr/bin/env python
from format_keys import format_keys
from public import public


@public
class Badge:
    image = None
    link = ""
    title = ""
    markup = "md"
    branch = "master"
    visible = True

    def __init__(self, **kwargs):
        self.update(**kwargs)

    def update(self, *args, **kwargs):
        inputdict = dict(*args, **kwargs)
        for k, v in inputdict.items():
            setattr(self, k, v)

    def format(self, string):
        kwargs = dict()
        keys = format_keys(string)
        for key in keys:
            value = getattr(self, key, None)
            if value is None:
                value = ""
            kwargs[key] = value
        return string.format(**kwargs).replace(" ", "%20")

    def get_image(self):
        if not self.image:
            raise ValueError("image EMPTY")
        return self.format(self.image)

    def get_link(self):
        return self.format(self.link or "")

    def get_title(self):
        return self.title or ""

    def render_md(self):
        return "[![%s](%s)](%s)" % (self.get_title(), self.get_image(), self.get_link())

    def render_rst(self):
        target = self.get_link()
        if not self.link:
            target = "none"
        return """.. image: : %s
    : target: %s""" % (self.get_image(), target)

    @property
    def md(self):
        return self.render_md()

    @property
    def rst(self):
        return self.render_rst()


    def render(self, markup):
        if markup == "md":
            return self.render_md()
        if markup == "rst":
            return self.render_rst()
        raise ValueError("'%s' unknown markup" % markup)

    def __bool__(self):
        return getattr(self, "visible", True)

    def __nonzero__(self):
        return getattr(self, "visible", True)

    def __str__(self):
        if self:
            return self.render(self.markup)
        return ""

    def __repr__(self):
        return self.__str__()
