import sublime, sublime_plugin, os.path, time
from threading import Timer

class LogHelper():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LogHelper, cls).__new__(
                                cls, *args, **kwargs)

            s = sublime.load_settings("LogMonitor.sublime-settings")
            cls.log_file = s.get("logmonitor_log_files")[0]
            cls.file_watch_timeout = s.get("logmonitor_check_interval")

            cls.last_modified = os.path.getmtime(cls.log_file)
        return cls._instance

class LogMonitorViewCommand(sublime_plugin.WindowCommand):
    def run(self):
        lh = LogHelper()
        self.viewLog()
        self.watcher = Timer(lh.file_watch_timeout, self.checkForLogChanges)
        self.watcher.start()

    def viewLog(self):
        lh = LogHelper()
        input = open(lh.log_file,'r')
        content = input.read()
        input.close()

        if(len(content) > 0):
            print("\n\nLOG ALERT:\n-----------------")
            print(content)
            self.window.run_command("show_panel", {"panel": "console"})

    def checkForLogChanges(self):
        lh = LogHelper()
        fo = open(lh.log_file,'r')
        if(os.path.getmtime(lh.log_file) > lh.last_modified):
            lh.last_modified = os.path.getmtime(lh.log_file)
            self.viewLog()

        self.watcher = Timer(lh.file_watch_timeout, self.checkForLogChanges)
        self.watcher.start()


class LogMonitorDeleteCommand(sublime_plugin.WindowCommand):
    def run(self):
        lh = LogHelper()
        input = open(lh.log_file,'w')
        input.truncate()
        input.close()
        self.window.run_command("show_panel", {"panel": "console"})
        print("LOG CLEARED")