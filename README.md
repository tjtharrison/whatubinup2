# What U bin up 2

A small widget for tracking hours daily across a set of time bins.

# Usage

To use the widget, install via pip:

```
pip3 install whatubinup2
```

Launch the client!

```
whatubinup2
```

On first launch, default settings will be applied (8 hour working days with 10 minute reminders). Config files and reports are stored in `~/whatubinup2/`

# Local Development

To develop locally, install dependencies:

```
pip3 install -r requirements.txt
```

Launch the client:

```
python3 src/whatubinup2/__main__.py
```

# Build process

Build testing, code linting, package bump and publishing are completed via Github actions (`.github/workflows/`).

Build scripts require a commit message in the following format to generate a pull request

```
[PR|WIP]/$commit_message[[major]|[minor]|[patch]|[none]]
```

Example to create a PR for a minor change:

```
PR/some small fix [patch]
```

# Features coming soon
* Let me know!

# Stretch features
* Integration with gcal? (See you've been in a meeting)
