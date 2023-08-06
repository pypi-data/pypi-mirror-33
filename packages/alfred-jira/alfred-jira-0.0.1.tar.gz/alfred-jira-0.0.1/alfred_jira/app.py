#!/usr/bin/env python
import os
from chuda import App, autorun
from chuda.utils import Null
from passepartout import Workflow
from .core.jira import Jira
from .commands.search import SearchCommand
from .commands.close import CloseCommand
from .commands.url import UrlCommand


@autorun()
class AlfredJiraApp(App):
    app_name = "alfred-jira"
    workflow = Workflow()

    config_path = [x.replace("~", os.getenv("HOME")) for x in [
        "~/.alfredjirarc",
        "~/.alfredjirarc.yml",
        "~/.alfredjirarc.yaml"
    ]]
    config_parser = "yaml"

    @property
    def jira(self):
        if self.config != {}:
            return Jira(self.config)

        return Null()

    subcommands = [
        SearchCommand, CloseCommand, UrlCommand
    ]
