#!/usr/bin/env python
# -*- coding: utf-8 -*-
from find import find
import click
import os
from public import public

# path/to/repo/.../<section_name>.md
# path/to/repo/.../<section_name2>.md


def _has_header(body):
    return body.lstrip()[0] == "#"


def clean(string):
    return string.lstrip().rstrip()

# default headers


HEADERS = dict(
    badges="",
    how="How it works"
)


@public
class Readme:
    ordering = ["badges", "description", "requirements", "install", "features", "usage", "config", "how", "examples", "todo"]
    disabled = []
    headers = None
    header_lvl = 3

    def __init__(self, path, **kwargs):
        self.load(path)
        self.update(**kwargs)
        self.headers = HEADERS

    def update(self, *args, **kwargs):
        inputdict = dict(*args, **kwargs)
        for k, v in inputdict.items():
            setattr(self, k, v)

    def header(self, section):
        header = self.headers.get(section, section.title())
        if not header:  # without header
            return ""
        if "#" in header:  # custom headering level
            return header
        return "%s %s" % ("#"*self.header_lvl,header)  # default headering level

    def render(self):
        sections = []
        for name in self.ordering:
            if name in self.disabled:
                continue
            section = str(getattr(self, name, ""))
            if not section:
                continue
            # todo: clean
            if section and not _has_header(section):  # without header
                header = self.header(name)
                section = "%s\n%s" % (header, str(section).lstrip())
            sections.append(str(section).lstrip().rstrip())
        return "\n\n".join(filter(None, sections))

    def save(self, path):
        output = self.render()
        if os.path.dirname(path) and not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        open(path, "w").write(output)

    def load_file(self, path):
        content = open(path).read()
        if content:
            name, ext = os.path.splitext(os.path.basename(path))
            setattr(self, name, content)

    def load(self, path="."):
        if not path:
            path = os.getcwd()
        self.files = list(find(path, followlinks=True))
        for f in self.files:
            name, ext = os.path.splitext(os.path.basename(f))
            if ext == ".md":
                self.load_file(f)


PROG_NAME = 'python -m %s' % os.path.basename(__file__).split(".")[0]


@click.command()
def cli():
    for path in ["setup.py", "setup.cfg"]:
        if not os.path.exists(path):
            raise OSError("%s NOT EXISTS" % path)
    print(Readme().render())


if __name__ == '__main__':
    cli(prog_name=PROG_NAME)
