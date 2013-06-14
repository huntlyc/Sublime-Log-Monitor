import sublime, sublime_plugin, os.path, time
from threading import Timer

# Singleton to help store the last modified timestamp of the log file
# I need to hold this in memory, because otherwise it would get lost after
# the initial "LogMonitorViewCommand" is run and then GC'd.  Without this,
# the dialog box would always appear every time the watcher runs...
class LogHelper():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LogHelper, cls).__new__(
                                cls, *args, **kwargs)
            cls.last_modified = None
        return cls._instance


# This is a total hack... Could not figure out another way @TODO this
# Beacuse the edit object gets lost once the "LogMoitorViewCommand" run method
# is finished...
class ShowLogCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Load in prefs
        s = sublime.load_settings("LogMonitor.sublime-settings")
        log_file_uri = s.get("logmonitor_log_files")[0]
        file_watch_timeout = s.get("logmonitor_check_interval")

        lh = LogHelper() #Helper class stores last modified time between runs

        try:
            # If first run or file has been modified since last viewing...
            if(lh.last_modified is None or
               os.path.getmtime(log_file_uri) > lh.last_modified):
                lh.last_modified = os.path.getmtime(log_file_uri)

                #open the file and read the contents
                with open(log_file_uri, 'r') as lfile:
                    content = lfile.read().strip()
                lfile.close()

                #Create seperator to cover 'LOG: /name/of/log.log:'
                sep = (len(log_file_uri) + 6) * '=' # ========== seperator

                #Build up output
                text = 'LOG: {0}:\n{1}\n{2}'

                #Setup the output panel
                self.window = sublime.active_window()
                self.output_view = self.window.create_output_panel("LogMonitor")
                self.window.run_command("show_panel",
                                        {"panel": "output.LogMonitor"})

                #Write the text to the output panel
                self.output_view.set_read_only(False)
                self.output_view.insert(edit, 0, text.format(log_file_uri,
                                                             sep,
                                                             content))
                self.output_view.set_read_only(True)

                tstruct = time.gmtime(lh.last_modified)
                ttimes = "{0}/{1}/{2} {3}:{4}:{5}".format(str(tstruct.tm_year),
                                                          str(tstruct.tm_mon),
                                                          str(tstruct.tm_mday),
                                                          str(tstruct.tm_hour),
                                                          str(tstruct.tm_min),
                                                          str(tstruct.tm_sec))


                statMsg = "LogMonitor: {0} modified @ {1}"
                sublime.status_message(statMsg.format(log_file_uri, ttimes))
        except IOError: # Could not open log_file
            sublime.status_message('LogMonitor: Could not open log file, ' \
                                   'check your settings!')

# Command to show the log and kick off the watch timer
class LogMonitorViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Comes from a keyboard command, so clear last modified and show log...
        lh = LogHelper()
        lh.last_modified = None
        self.viewLog()

    def viewLog(self):
        # Load required settings
        s = sublime.load_settings("LogMonitor.sublime-settings")
        file_watch_timeout = s.get("logmonitor_check_interval")

        # Call the 'show_log' command to pop open the text area
        self.view.run_command('show_log')

        # Set a timer based on the user prefs to watch for file changes
        self.watcher = Timer(file_watch_timeout, self.viewLog)
        self.watcher.start()


# Command to clear the log file - for @DaganLev as he's the boss! :)
class LogMonitorDeleteCommand(sublime_plugin.WindowCommand):
    def run(self):

        try:
            s = sublime.load_settings("LogMonitor.sublime-settings")
            log_file_uri = s.get("logmonitor_log_files")[0]

            #Check file exists
            with open(log_file_uri): pass #will throw exception on no file

            # wipe the log file
            with open(log_file_uri, 'w') as log_file:
                log_file.truncate()
            log_file.close()

            statMsg = "LogMonitor: Cleared log file: {0}"
            sublime.status_message(statMsg.format(log_file_uri))
        except IOError: # Could not open log_file for writing
            sublime.status_message('LogMonitor: Could not clear log file, ' \
                                   'check your settings!')
