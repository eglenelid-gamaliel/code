# window.py
#
# Copyright 2022 Eglenelid Gamaliel Gutierrez Hernandez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pathlib import Path
import time

from gi.repository import Adw, Gio, GLib, Gtk

from .widgets import Codeview, FileRow, FolderRow


@Gtk.Template(resource_path="/dev/eglenelidgamaliel/code/window.ui")
class CodeWindow(Adw.ApplicationWindow):
    __gtype_name__ = "CodeWindow"

    # Get the tabview widget
    tab_view = Gtk.Template.Child()
    flap = Gtk.Template.Child()
    file_explorer_list = Gtk.Template.Child()
    window_title = Gtk.Template.Child()
    open_folder_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create the 'toggle_sidebar' action referenced in window.ui
        toggle_sidebar_action = Gio.SimpleAction(name="toggle_sidebar")
        toggle_sidebar_action.connect("activate", self.on_toggle_sidebar)
        self.add_action(toggle_sidebar_action)

        # Create the 'new_file' action referenced in window.ui
        new_file_action = Gio.SimpleAction(name="new_file")
        new_file_action.connect("activate", self.on_new_file)
        self.add_action(new_file_action)

        # Create the 'open_file' action referenced in window.ui
        open_file_action = Gio.SimpleAction(name="open_file")
        open_file_action.connect("activate", self.open_file_dialog)
        self.add_action(open_file_action)

        # Create the 'open_folder' action referenced in window.ui
        open_folder_action = Gio.SimpleAction(name="open_folder")
        open_folder_action.connect("activate", self.open_folder_dialog)
        self.add_action(open_folder_action)

        # Create the 'save' action referenced in window.ui
        save_action = Gio.SimpleAction(name="save")
        save_action.connect("activate", self.save)
        self.add_action(save_action)

        # Create the 'save_as' action referenced in window.ui
        save_as_action = Gio.SimpleAction(name="save_as")
        save_as_action.connect("activate", self.save_as_file_dialog)
        self.add_action(save_as_action)

        # Create the GSettings instance for the app schema id
        self.settings = Gio.Settings(schema_id="dev.eglenelidgamaliel.code")

        # Remember the window size
        self.settings.bind("window-width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-maximized", self, "maximized", Gio.SettingsBindFlags.DEFAULT)

    def on_toggle_sidebar(self, action, _):
        self.flap.set_reveal_flap(not self.flap.get_reveal_flap())

    # Save (or overwrite) the file
    def save(self, action, _):
        # Check if there is a file associated with the current code view
        code_view = self.tab_view.get_selected_page().get_child().get_child()
        if code_view.file:
            self.save_file(code_view.file)
        else:
            self.save_as_file_dialog()

    # Save the file as
    def save_as_file_dialog(self, action=None, _=None):
        self._native = Gtk.FileChooserNative(
            title="Save File As",
            transient_for=self,
            action=Gtk.FileChooserAction.SAVE,
            accept_label="_Save",
            cancel_label="_Cancel",
        )
        self._native.connect("response", self.on_save_response)
        self._native.show()

    # Called when the file chooser dialog is closed
    def on_save_response(self, native, response):
        if response == Gtk.ResponseType.ACCEPT:
            self.save_file(native.get_file())
        self._native = None

    # Function called when the file contents are saved
    def save_file(self, file):
        # Retrieve the current editor widget
        buffer = self.tab_view.get_selected_page().get_child().get_child().get_buffer()

        # Retrieve the iterator at the start of the buffer
        start = buffer.get_start_iter()
        # Retrieve the iterator at the end of the buffer
        end = buffer.get_end_iter()
        # Retrieve all the visible text between the two bounds
        text = buffer.get_text(start, end, False)

        # If there is nothing to save, return early
        if not text:
            return

        bytes = GLib.Bytes.new(text.encode("utf-8"))

        # Start the asynchronous operation to save the data into the file
        file.replace_contents_bytes_async(bytes, None, False, Gio.FileCreateFlags.NONE, None, self.save_file_complete)

    # Function called when the file contents finish saving
    def save_file_complete(self, file, result):
        res = file.replace_contents_finish(result)
        info = file.query_info("standard::display-name", Gio.FileQueryInfoFlags.NONE)
        if info:
            display_name = info.get_attribute_string("standard::display-name")
        else:
            display_name = file.get_basename()

        code_view = self.tab_view.get_selected_page().get_child().get_child()
        code_view.file = file

        current_page = self.tab_view.get_selected_page()
        current_page.set_title(file.get_basename())
        current_page.set_tooltip(file.get_path())

    # Open file action callback
    def open_file_dialog(self, action, parameter):
        # Create a new file selection dialog, using the "open" mode
        # and keep a reference to it
        self._native = Gtk.FileChooserNative(
            title="Open file",
            transient_for=self,
            action=Gtk.FileChooserAction.OPEN,
            accept_label="_Open",
            cancel_label="_Cancel",
        )
        # Connect the "response" signal of the file selection dialog;
        # this signal is emitted when the user selects a file, or when
        # they cancel the operation
        self._native.connect("response", self.on_open_response)
        # Present the dialog to the user
        self._native.show()

    # Called when the file chooser dialog is closed
    def on_open_response(self, dialog, response):
        # If the user selected a file...
        if response == Gtk.ResponseType.ACCEPT:
            # ... retrieve the location from the dialog and open it
            self.open_file(dialog.get_file())
        # Release the reference on the file selection dialog now that we
        # do not need it any more
        self._native = None

    # Function to open a file asynchronously
    def open_file(self, file):
        file_path = Path(file.get_path())
        if file_path.is_dir():
            start = time.perf_counter()
            self.open_folder(file_path)
            print(f"Completed Execution in {time.perf_counter() - start} seconds")
        else:
            # Load the file contents asynchronously
            file.load_contents_async(None, self.open_file_complete)

    # Function called when the file contents finish loading
    def open_file_complete(self, file, result):
        contents = file.load_contents_finish(result)

        # Try to open the file
        if not contents[0]:
            path = file.peek_path()

        # Check if the file is a text file and UTF-8 encoding
        try:
            text = contents[1].decode("utf-8")
        except UnicodeError as err:
            path = file.peek_path()
            return

        # Create a new editor widget
        new_gtksource_view = Codeview()
        new_gtksource_view.file = file
        new_gtksource_view.grab_focus()

        # Load the file contents into the editor instance
        buffer = new_gtksource_view.get_buffer()
        buffer.set_text(text)

        # Place the cursor at the beginning of the file
        start = buffer.get_start_iter()
        buffer.place_cursor(start)

        # Create a new scrolled window to hold the editor
        new_scrolleable_window = Gtk.ScrolledWindow()
        new_scrolleable_window.set_child(new_gtksource_view)
        new_scrolleable_window.set_vexpand(True)

        # Create a new tab and add it to the tabview
        newly_created_page = self.tab_view.append(new_scrolleable_window)
        newly_created_page.set_title(file.get_basename())
        newly_created_page.set_tooltip(file.get_path())

        new_gtksource_view.grab_focus()

    # Open folder action callback
    def open_folder_dialog(self, action, parameter):
        self._native = Gtk.FileChooserNative(
            title="Open folder",
            transient_for=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            accept_label="_Open",
            cancel_label="_Cancel",
        )
        self._native.connect("response", self.on_open_folder_response)
        self._native.show()

    # Called when the folder chooser dialog is closed
    def on_open_folder_response(self, dialog, response):
        # If the user selected a file...
        if response == Gtk.ResponseType.ACCEPT:
            # ... retrieve the location from the dialog and open it
            self.open_folder_button.set_visible(False)
            self.file_explorer_list.set_visible(True)
            list_has_rows = self.file_explorer_list.get_row_at_index(0)
            while list_has_rows != None:
                self.file_explorer_list.remove(self.file_explorer_list.get_row_at_index(0))
                list_has_rows = self.file_explorer_list.get_row_at_index(0)

            folder_path = Path(dialog.get_file().get_path())
            self.window_title.set_title(folder_path.name.title())

            self.open_file(dialog.get_file())
        # Release the reference on the file selection dialog now that we
        # do not need it any more
        self._native = None

    def open_folder(self, folder_path: Path, parent_folder_row=None):
        # Create side bar entries for each file in the folder
        for file in folder_path.iterdir():
            if file.name.startswith("."):
                continue
            elif file.is_dir():
                new_folder_row = FolderRow(file)
                if parent_folder_row:
                    parent_folder_row.add_row(new_folder_row)
                else:
                    self.file_explorer_list.append(new_folder_row)
                self.open_folder(file, new_folder_row)

            elif file.is_file():
                new_file_row = FileRow(file)
                new_file_row.connect("activated", self.on_file_selected)
                if parent_folder_row:
                    parent_folder_row.add_row(new_file_row)
                else:
                    self.file_explorer_list.append(new_file_row)

    # New file action callback
    def on_new_file(self, action, parameter):
        # Create a new editor widget
        new_gtksource_view = Codeview()

        # Create a new scrolled window to hold the editor
        new_scrolleable_window = Gtk.ScrolledWindow()
        new_scrolleable_window.set_child(new_gtksource_view)
        new_scrolleable_window.set_vexpand(True)

        # Create a new tab and add it to the tabview
        newly_created_page = self.tab_view.append(new_scrolleable_window)
        newly_created_page.set_title("Untitled")
        newly_created_page.set_tooltip("Untitled")

        new_gtksource_view.grab_focus()

    # File selected callback
    def on_file_selected(self, action_row: Adw.ActionRow) -> None:
        gfile = Gio.File.new_for_path(str(action_row.file_path))
        self.open_file(gfile)


class AboutDialog(Gtk.AboutDialog):
    def __init__(self, parent):
        Gtk.AboutDialog.__init__(self)
        self.props.program_name = "Code"
        self.props.version = "0.0.1"
        self.props.authors = ["Eglenelid Gamaliel Gutierrez Hernandez"]
        self.props.copyright = "2022 Eglenelid Gamaliel Gutierrez Hernandez"
        self.props.logo_icon_name = "dev.eglenelidgamaliel.code"
        self.props.modal = True
        self.set_transient_for(parent)
