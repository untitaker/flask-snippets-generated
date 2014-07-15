import os
import io
import re
import html2rest

pjoin = os.path.join

snippets_base = './flask.pocoo.org/snippets/'
output_base = './output'

snippetlink_re = re.compile(r'(?<=/snippets/)[0-9\.]+')
title_re = re.compile(r'(?<=\<title\>)(.*)(?= \| Flask)')
categories = {}


def generate_rst(html, writer, category):
    tmpfile = io.BytesIO()
    parser = html2rest.Parser(tmpfile, 'utf-8', None, None)
    parser.feed(html.decode('utf-8'))
    parser.write()  # flush buffer
    writer.write(filter_rst(tmpfile.getvalue()).strip())

    parser.writer = writer

    # links got accidentally ripped out, write again
    # but remove useless ones
    useless_links = ('extensions', 'community', 'docs', 'overview',
                     'Armin Ronacher', 'search', 'snippets')
    for href, link in list(parser.hrefs.items()):
        if link in useless_links or category in href:
            del parser.hrefs[href]

    parser.end_body()


def urlify_title(x):
    x = x.lower()
    x = re.sub(r'[^a-z\s]', '', x)
    x = '-'.join(x.split())
    x = x.strip('-')
    return x


def filter_rst(text):
    # the first 10 lines are headers
    lines = text.splitlines()[10:]
    lines[1] = '=' * len(lines[1])
    del lines[3]

    delete_after = None
    for i, line in enumerate(lines):
        if 'can be used freely' in line:
            delete_after = i
            break

    del lines[delete_after:]
    return '\n'.join(lines)

#filter_rst = lambda x: x
for category in os.listdir(pjoin(snippets_base, 'category')):
    os.makedirs(pjoin(output_base, category))
    dirpath = pjoin(snippets_base, 'category', category)

    with open(pjoin(dirpath, 'index.html')) as f:
        for x in snippetlink_re.findall(f.read()):
            categories[x] = category

for snippet_id in os.listdir(snippets_base):
    dirpath = pjoin(snippets_base, snippet_id)
    if not os.path.isdir(dirpath) or not snippet_id[0].isdigit():
        continue

    with open(pjoin(dirpath, 'index.html')) as infile:
        instring = infile.read()
        title, = title_re.findall(instring)
        category = categories[snippet_id]
        with open(pjoin(output_base, category,
                        urlify_title(title) + '.rst'), 'wb+') as outfile:
            generate_rst(instring, outfile, category)
