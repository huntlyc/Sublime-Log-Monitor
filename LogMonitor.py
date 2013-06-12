import sublime, sublime_plugin

class LogmonitorHelloCommand(sublime_plugin.WimdowCommand):
    def run(self):
        sublime.status_message('Hello World!')
