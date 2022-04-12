# widgets.py
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

from gi.repository import Gio, Gtk, GtkSource


# Subclass GtkSource.View to add custom features.
class Codeview(GtkSource.View):
    def __init__(self) -> None:
        super().__init__()

        # Get the application settings
        self.settings = Gio.Settings(schema_id="dev.eglenelidgamaliel.code")

        # Connect to the settings style-scheme change signal
        self.settings.connect("changed::code-view-style-scheme", self.on_style_scheme_changed)
        self.on_style_scheme_changed(self.settings, "code-view-style-scheme")

        # Set GtkSource.View properties
        self.set_show_line_numbers(True)
        self.set_auto_indent(True)
        self.set_highlight_current_line(True)
        self.set_monospace(True)
        self.set_top_margin(10)
        self.set_bottom_margin(10)

        self.file = None

    def on_style_scheme_changed(self, settings: Gio.Settings, key: str) -> None:
        style_scheme_id = settings.get_string("code-view-style-scheme")
        style_scheme = GtkSource.StyleSchemeManager.get_default().get_scheme(style_scheme_id)
        self.get_buffer().set_style_scheme(style_scheme)


# Subclass Gtk.TreeStore to add custom features.
class FileExplorerTreeStore(Gtk.TreeStore):
    def __init__(self, folder) -> Gtk.TreeStore:
        super().__init__(str, str)
        self.create_folder_files(Path(folder.get_path()))

    def create_folder_files(self, folder_path: Path, parent=None):
        for file in folder_path.iterdir():
            if file.name.startswith("."):
                continue
            elif file.is_dir():
                sub_folder = self.append(parent, [file.name, str(file)])
                self.create_folder_files(file, sub_folder)
            elif file.is_file():
                self.append(parent, [file.name, str(file)])


# Subclass Gtk.TreeView to add custom features.
class FileExplorerView(Gtk.TreeView):
    def __init__(self, folder) -> Gtk.TreeView:
        self.model = FileExplorerTreeStore(folder)

        super().__init__(model=self.model)

        self.set_enable_tree_lines(True)
        self.set_headers_visible(False)
        self.set_fixed_height_mode(True)

        self.get_style_context().add_class("navigation-sidebar")

        for i, column_title in enumerate(["Files"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.set_property("sizing", Gtk.TreeViewColumnSizing.FIXED)
            self.append_column(column)
