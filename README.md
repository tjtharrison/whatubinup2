# What U bin up 2

A small desktop app widget for tracking hours across a set of time bins.

## Installation

To use the package, install via pip..

```
pip3 install whatubinup2
```

## Launching

Launch from the terminal as:

```
whatubinup2
```

On first launch, default settings will be applied (8 hour working days with 10 minute reminders). Config files and reports are stored in `~/whatubinup2/`

## Local Development

To develop locally, install dependencies:

```
pip3 install -r requirements.txt
```

Launch the client:

```
python3 src/whatubinup2/__main__.py
```

## Github Pages

The github pages site is generated via a script in the pipeline by converting README.md into html and concatenating with template.html from the roor directory. To work on this locally, build the docker container using docker-compose:

```
docker-compose up -d
```

If you want to republish the README.md into the container, run the below script to reprocess the markdown:

```
python3 scripts/convert_markdown.py 
```

## Build process

Build testing, code linting, package bump and publishing are completed via Github actions.

Build scripts require a commit message in the following format to generate a pull request

```
[PR|WIP]/$commit_message[[major]|[minor]|[patch]|[none]]
```

Example to create a PR for a patch change:

```
PR/some small fix [patch]
```

## Paid features

* Cloud config storage

## Stretch features
* Integration with gcal? (See you've been in a meeting)
