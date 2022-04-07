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

from gi.repository import Adw, Gtk, GtkSource


# Subclass GtkSource.View to add custom features.
class Codeview(GtkSource.View):
    def __init__(self) -> None:
        super().__init__()
        self.set_show_line_numbers(True)
        self.set_auto_indent(True)
        self.set_highlight_current_line(True)
        self.set_monospace(True)
        self.set_top_margin(10)
        self.set_bottom_margin(10)

        self.file = None


# Subclass Adw.ActionRow to add custom features.
class FileRow(Adw.ActionRow):
    def __init__(self, file_path: Path) -> Gtk.Widget:
        super().__init__()
        self.file_path = file_path
        self.set_title(file_path.name)
        self.set_icon_name("emblem-documents-symbolic")
        self.set_activatable(True)
        self.set_selectable(False)


# Subclass Adw.ActionRow to add custom features.
class FolderRow(Adw.ExpanderRow):
    def __init__(self, folder_path: Path) -> Gtk.Widget:
        super().__init__()
        self.file_path = folder_path
        self.set_title(folder_path.name)
        self.set_icon_name("folder-visiting-symbolic")
        self.set_activatable(True)
        self.set_selectable(False)
