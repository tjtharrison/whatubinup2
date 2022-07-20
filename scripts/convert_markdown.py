""" Script to generate HTML files from Markdown for publication """
import glob

import markdown

TEMPLATE_FILE = "template.html"

# Build out html files
for file_name in glob.iglob("README.md", recursive=True):

    print("Converting " + file_name + " to HTML")

    DESTINATION_FILE = "docs/index.html"

    # Load Markdown content
    with open(file_name, "r", encoding="UTF-8") as f:
        text = f.read()
        html = markdown.markdown(
            text,
            extensions=[
                "attr_list",
                "md_in_html",
                "markdown.extensions.tables",
                "pymdownx.superfences",
            ],
        )
        ## Formatting fixes
        fix_list = [
            ("./docs/", ""),
            ("<code>", "<pre>"),
            ("</code>", "</pre>"),
            ('<pre class="highlight">', "<p>"),
            ("</pre></pre>", "</pre></p>"),
        ]
        for fix_item in fix_list:
            html = html.replace(fix_item[0], fix_item[1])

    # Load header content
    with open(TEMPLATE_FILE, "r", encoding="UTF-8") as t:
        completed_template = t.read().replace("{{ BODY }}", html)

    # Build file
    with open(DESTINATION_FILE, "w", encoding="UTF-8") as a:
        a.write(completed_template)
    print(DESTINATION_FILE + " written!")
