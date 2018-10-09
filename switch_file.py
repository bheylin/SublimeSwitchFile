import os.path
import platform

import sublime
import sublime_plugin

class SwitchFileCommand(sublime_plugin.WindowCommand):
    def run(self):
        if not self.window.active_view():
            return

        fname = self.window.active_view().file_name()
        if not fname:
            return

        file_path, ext = os.path.splitext(fname)

        if ext == "":
            return

        settings = sublime.load_settings("SwitchFile.sublime-settings")
        header_extensions = settings.get("switch_file.header_extensions");
        impl_extensions = settings.get("switch_file.impl_extensions");
        paths = settings.get("switch_file.paths");

        ext = ext[1:]
        is_source_file_an_impl = ext in impl_extensions
        partner_extensions = header_extensions if is_source_file_an_impl else impl_extensions

        file_opened = self.try_all_paths(paths, partner_extensions, file_path)

        if not file_opened:
            file_opened = self.try_package_layout(paths, partner_extensions, file_path)

        # if no file can be found, try feeding the filename to the Goto Anything system
        if not file_opened:
            file_base_path, file_name = os.path.split(file_path)
            file_name_base, ext = os.path.splitext(file_name)
            print('file_name_base: {}'.format(file_name_base))
            search_file_name = file_name_base + (".h" if is_source_file_an_impl else ".cpp")
            self.window.run_command("show_overlay", {"overlay": "goto", "show_files": True, "text": search_file_name})

    def parent_dir(self, path):
        return os.path.abspath(os.path.join(path, os.pardir))

    def try_package_layout(self, paths, partner_extensions, file_path):
        file_opened = False
        package_path = self.parent_dir(file_path)
        _, package_dir_name = os.path.split(package_path)
        base_path = self.parent_dir(package_path)
        for path in paths:
            folder_path = os.path.join(base_path, path, package_dir_name)
            file_opened = self.try_open_file_at(folder_path, file_path, partner_extensions)
            if file_opened:
                break
        return file_opened

    def try_all_paths(self, paths, partner_extensions, file_path):
        file_opened = False
        for path in paths:
            file_opened = self.try_open_file_at(path, file_path, partner_extensions)
            if file_opened:
                break
        return file_opened

    def try_open_file_at(self, base_path, file_path, extensions):
        file_opened = False
        file_base_path, file_name = os.path.split(file_path)
        for ext in extensions:
            partner_path = os.path.join(file_base_path, base_path, file_name + '.' + ext)
            if os.path.exists(partner_path):
                self.window.open_file(partner_path, flags=sublime.FORCE_GROUP)
                file_opened = True

        return file_opened
