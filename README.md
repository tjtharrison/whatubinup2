# What U bin up 2

A small desktop widget for logging time into configurable buckets.

The free version of the app provides access to:

* Configurable buckets (Create any number of buckets into which time can be logged)
* Configurable reminders/popups (Popup Hourly/minutely reminders to log your time!)
* Historic reports (View daily time logged into buckets)

Request a license and [contact me](https://readme.tjth.co) to arange upgrade to paid features.

## Paid features

* Cloud config storage

## Upcoming features

* Cloud report storage
* Integration with Cloud calendars (Gsuite, O365)
* Cleaner windows install (Pending MS approval)

# Installation

## MacOS

To use the package, install via pip..

```
pip3 install whatubinup2
```

Launch from the terminal as:

```
whatubinup2
```

On first launch, default settings will be applied (8 hour working days with 10 minute reminders). Config files and reports are stored in `~/whatubinup2/`

## Windows

### Python

_NOTE: Requires Python3 with pip - Download [here](https://www.python.org/downloads/windows/)_
_NOTE: During installation, ensure to tick the box to enable py shortcut commands from cmd_

```
py -m pip install whatubinup2
py c:\users\[Username]\appdata\local\programs\python\python310\lib\site-packages\whatubinup2 ## Based on a standard Python 3.10 installation
```

### Exe 

_Currently being raised as a virus by SafeScreen, support ticket logged with Microsoft_

Download zip from [here](static/wubu_win.zip), extract the archive and run the executable `__main__.exe`. (Aware )

# Local Development

To develop locally, install dependencies:

```
pip3 install -r requirements.txt
```

Launch the client:

```
python3 src/whatubinup2/__main__.py
```

## Github Pages

The github pages site is generated via a script in the pipeline by converting README.md into html and concatenating with template.html from the root directory. To work on this locally, build the docker container using docker-compose:

```
docker-compose up -d
```

The docs will then be available at `http://localhost:8080`

If you want to republish the README.md into the container, run the below script to reprocess the markdown (You will need to run `pip3 install -r requirements-html.txt` the first time):

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

