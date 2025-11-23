import tkinter as tk
from tkinter import filedialog, ttk, Toplevel
import os
import json
import csv
from pathlib import Path
import platform
import time
from datetime import datetime
import zipfile

# --- Theme Definitions ---
LIGHT_THEME = {
    'bg': '#f0f0f0',        # General background (light gray)
    'fg': 'black',          # General text color
    'text_bg': 'white',     # Textbox background
    'text_fg': 'black',     # Textbox foreground
    'status_fg_ok': 'green',
    'status_fg_error': 'red',
    'button_bg': '#e0e0e0', # Button default bg (light gray)
    'button_active_bg': '#c0c0c0' # Button active bg
}
DARK_THEME = {
    'bg': '#2b2b2b',        # General background (dark gray)
    'fg': 'white',          # General text color (white)
    'text_bg': '#3c3f41',   # Textbox background (slightly darker gray)
    'text_fg': 'white',     # Textbox foreground
    'status_fg_ok': '#a8ff78', # Light green for success
    'status_fg_error': '#ff6347', # Light red for error
    'button_bg': '#4a4a4a', # Button default bg (darker gray)
    'button_active_bg': '#606060' # Button active bg
}

# --- Common Launcher Path Definitions ---
LAUNCHER_PATHS = {
    "Windows": {
        "Default Minecraft (.minecraft)": r"%APPDATA%\.minecraft\mods", # Final folder
        "Prism Launcher (Instances)": r"%APPDATA%\PrismLauncher\instances", # Instance root
        "MultiMC (Instances)": r"%APPDATA%\MultiMC\instances", # Instance root
        "Modrinth App (Instances)": r"%APPDATA%\Modrinth\instances", # Instance root
        "CurseForge (Legacy Overwolf)": r"%APPDATA%\CurseForge\Minecraft\Instances", # Instance root
        "FTB App (Instances)": r"%APPDATA%\ftblauncher\instances", # Instance root
        "GDLauncher (Instances)": r"%APPDATA%\gdlauncher\instances", # Instance root
        "Technic Launcher (Modpacks)": r"%APPDATA%\.technic\modpacks", # Instance root
        "ATLauncher (Instances)": r"%APPDATA%\ATLauncher\Instances", # Instance root
    },
    "Linux": {
        "Default Minecraft (.minecraft)": "~/.minecraft/mods", # Final folder
        "Prism Launcher (Instances)": "~/.local/share/PrismLauncher/instances", # Instance root
        "MultiMC (Instances)": "~/.local/share/multimc/instances", # Instance root
        "PolyMC (Instances)": "~/.local/share/polymc/instances", # Instance root
        "Modrinth App (Instances)": "~/.local/share/modrinth-app/instances", # Instance root
        "GDLauncher / GTK-L (Instances) (1)": "~/.local/share/gdlauncher/instances", # Instance root
        "GDLauncher / GTK-L (Instances) (2 - Alternative)": "~/gdlauncher/instances", # Instance root
        "ATLauncher (Instances) (1)": "~/ATLauncher/Instances", # Instance root
        "ATLauncher (Instances) (2 - Local Share)": "~/.local/share/atlauncher/instances", # Instance root
        "FTB App (Flatpak/Snap)": "~/.var/app/com.feed-the-beast.ftb-app/data/ftblauncher/instances", # Instance root
        "XMinecraft Launcher (Instances)": "~/.minecraftx/instances", # Instance root
    },
    "Darwin": { # macOS
        "Default Minecraft": "~/Library/Application Support/minecraft/mods", # Final folder
        "Prism Launcher (Instances)": "~/Library/Application Support/PrismLauncher/instances", # Instance root
        "MultiMC (Instances)": "~/Library/Application Support/MultiMC/instances", # Instance root
        "Modrinth App (Instances)": "~/Library/Application Support/Modrinth/instances", # Instance root
        "CurseForge (Overwolf)": "~/Library/Application Support/CurseForge/Minecraft/Instances", # Instance root
        "FTB App (Instances)": "~/Library/Application Support/ftblauncher/instances", # Instance root
    }
}

class ModlistExporterApp:
    """
    A GUI application for scanning a directory for .jar files, extracting metadata
    and links, and exporting the list in multiple formats.
    """

    def __init__(self, master):
        self.master = master
        master.title("Minecraft Modlist Exporter v4.5 (Rich Instance Selection)")
        master.geometry("700x550")
        master.resizable(True, True)

        # --- State Variables ---
        self.scanned_mods = []
        self.current_scan_path = ""
        self.current_theme_name = "light"
        self.current_theme = LIGHT_THEME
        self.os_system = platform.system()
        self.launcher_popup = None      # Stores the first (Launcher Root) popup
        self.instance_popup = None      # Stores the second (Instance List) popup

        # --- Central Centering Frame (Grid) ---
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        self.content_wrapper = ttk.Frame(master, padding="15")
        self.content_wrapper.grid(row=0, column=0, sticky="nsew")

        # --- Setup Style (Use 'clam' base) ---
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Configure initial default styles (Light Theme)
        self.style.configure('TFrame', background=LIGHT_THEME['bg'])
        self.style.configure('TLabel', background=LIGHT_THEME['bg'], foreground=LIGHT_THEME['fg'], font=('Inter', 10))
        self.style.configure('TButton', font=('Inter', 10, 'bold'), padding=8, background=LIGHT_THEME['button_bg'], foreground=LIGHT_THEME['fg'])
        self.style.map('TButton',
                       background=[('active', LIGHT_THEME['button_active_bg']), ('!disabled', LIGHT_THEME['button_bg'])],
                       foreground=[('active', LIGHT_THEME['fg']), ('!disabled', LIGHT_THEME['fg'])])

        # --- Theme Toggle Button ---
        self.theme_button_frame = ttk.Frame(self.content_wrapper)
        self.theme_button_frame.pack(fill='x', pady=(0, 10))

        self.theme_button = ttk.Button(self.theme_button_frame,
                                       text="🌑 Dark Mode",
                                       command=self.toggle_theme)
        self.theme_button.pack(side='right')

        # --- Main Layout Frame (Pack) ---
        self.main_frame = ttk.Frame(self.content_wrapper, padding="15")
        self.main_frame.pack(fill='both', expand=True, anchor='center')

        # --- Input Section ---
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(pady=10, fill='x')

        self.label_scan = ttk.Label(input_frame, text="1. Scan Options:", font=('Inter', 12, 'bold'))
        self.label_scan.pack(anchor='w', pady=(0, 5))

        # Buttons for scanning
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill='x', pady=(0, 10))

        ttk.Button(button_frame, text="🚀 Quick Scan (Default)", command=self.quick_scan).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="🔗 Select Launcher Instance", command=self.show_launcher_paths).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="📂 Select Custom Folder", command=self.select_custom_folder).pack(side='left')

        # Current Path Display
        self.path_label = ttk.Label(self.main_frame, text="No folder selected.", wraplength=1000)
        self.path_label.pack(anchor='w', fill='x', pady=(5, 10))

        # --- Scan Results Section ---
        self.label_results = ttk.Label(self.main_frame, text="2. Found Mods (Name, Version, Links):", font=('Inter', 12, 'bold'))
        self.label_results.pack(anchor='w', pady=(5, 5))

        # Text area for showing results
        self.results_text = tk.Text(self.main_frame, height=15, state='disabled', wrap='word',
                                    font=('Consolas', 9), relief=tk.SUNKEN, borderwidth=1)
        self.results_text.pack(fill='both', expand=True, pady=(0, 10))

        # --- Output Section ---
        output_frame = ttk.Frame(self.main_frame)
        output_frame.pack(fill='x')

        self.export_button = ttk.Button(output_frame, text="💾 Export Full Report (6 Files)", command=self.export_modlist, state='disabled')
        self.export_button.pack(side='left', padx=(0, 10))

        # Status Label
        self.status_label = ttk.Label(output_frame, text="Ready.", font=('Inter', 10, 'italic'))
        self.status_label.pack(side='left')

        # Apply initial theme
        self.apply_theme(LIGHT_THEME, "light")

    def resolve_path(self, path_template):
        """Resolves OS-specific path variables like ~ and %APPDATA%."""
        if self.os_system == "Windows":
            path = path_template.replace("%APPDATA%", os.environ.get('APPDATA', ''))
        else:
            path = os.path.expanduser(path_template)
        return path

    def show_launcher_paths(self):
        """Creates the first pop-up window (Launcher Root Selection)."""

        if self.os_system == "Windows":
            path_set = LAUNCHER_PATHS["Windows"]
        elif self.os_system == "Darwin":
            path_set = LAUNCHER_PATHS["Darwin"]
        else:
            path_set = LAUNCHER_PATHS["Linux"]

        if self.launcher_popup and self.launcher_popup.winfo_exists():
            self.launcher_popup.lift()
            return

        self.launcher_popup = Toplevel(self.master)
        self.launcher_popup.title(f"Select Launcher Root ({self.os_system})")
        self.launcher_popup.geometry("550x450")
        self.launcher_popup.resizable(False, False)
        self.launcher_popup.config(bg=self.current_theme['bg'])

        popup_frame = ttk.Frame(self.launcher_popup, padding="15")
        popup_frame.pack(fill='both', expand=True)

        ttk.Label(popup_frame,
                  text="1. Select the Launcher's root instance folder (e.g., '.../instances'):",
                  font=('Inter', 11, 'bold')).pack(pady=(0, 10), anchor='w')

        # Scrollable Frame setup
        canvas = tk.Canvas(popup_frame, bg=self.current_theme['bg'], highlightthickness=0)
        vscrollbar = ttk.Scrollbar(popup_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=vscrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        vscrollbar.pack(side="right", fill="y")

        # Add Launcher Buttons
        for name, path_template in path_set.items():

            path_button = ttk.Button(
                scrollable_frame,
                text=f"📂 {name}",
                command=lambda n=name, p=path_template: self.select_launcher_path(n, p)
            )
            path_button.pack(fill='x', pady=5)

            # Display the path template
            path_label = ttk.Label(scrollable_frame,
                                   text=path_template,
                                   font=('Consolas', 8),
                                   foreground='#888888')
            path_label.pack(fill='x', padx=10, anchor='w')

        self.apply_theme_to_toplevel(self.launcher_popup, scrollable_frame)

    def select_launcher_path(self, path_name, path_template):
        """Handles the selection from the first pop-up."""
        resolved_path = self.resolve_path(path_template)

        # Close the launcher root selection pop-up
        if self.launcher_popup:
            self.launcher_popup.destroy()
            self.launcher_popup = None

        if "Default Minecraft" in path_name:
            # If it's the default path, it already points to the /mods folder. Scan directly.
            self.scan_for_jar_files(resolved_path)
        else:
            # It's an instance root, show the second selector.
            self.show_instance_selection(path_name, resolved_path)

    def get_instance_metadata(self, instance_path):
        """Attempts to read metadata from common instance files."""
        # 1. Check for XMinecraft Launcher (instance.json)
        xmcl_path = Path(instance_path) / "instance.json"
        if xmcl_path.exists():
            try:
                with open(xmcl_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    runtime = data.get('runtime', {})

                    # Construct a descriptive runtime string
                    runtime_parts = [f"MC: {runtime.get('minecraft') or 'N/A'}"]
                    if runtime.get('fabricLoader'): runtime_parts.append(f"Fabric: {runtime['fabricLoader']}")
                    if runtime.get('forge'): runtime_parts.append(f"Forge: {runtime['forge']}")
                    if runtime.get('quiltLoader'): runtime_parts.append(f"Quilt: {runtime['quiltLoader']}")
                    if runtime.get('neoForged'): runtime_parts.append(f"NeoForge: {runtime['neoForged']}")

                    return {
                        'name': data.get('name', Path(instance_path).name),
                        'description': data.get('description', 'No description.'),
                        'runtime': ", ".join(runtime_parts)
                    }
            except Exception as e:
                # print(f"Error reading XMinecraft JSON: {e}")
                pass # Continue to fallbacks

        # 2. Add other launcher specific metadata checks here (e.g., Prism/MultiMC's instance.cfg)
        # For now, we'll use a simple name fallback if JSON read fails or doesn't exist.

        # Fallback metadata
        return {
            'name': Path(instance_path).name,
            'description': 'Metadata unavailable or could not be read.',
            'runtime': 'N/A'
        }

    def show_instance_selection(self, launcher_name, instance_root_path):
        """Creates the second pop-up window (Instance Selection) with rich metadata."""

        if not Path(instance_root_path).is_dir():
             self._update_status(f"Error: Instance root not found at {instance_root_path}. Please check installation.", 'status_fg_error')
             return

        if self.instance_popup and self.instance_popup.winfo_exists():
            self.instance_popup.lift()
            return

        self.instance_popup = Toplevel(self.master)
        self.instance_popup.title(f"2. Select Instance for {launcher_name}")
        self.instance_popup.geometry("650x500") # Increased size for metadata
        self.instance_popup.resizable(False, False)
        self.instance_popup.config(bg=self.current_theme['bg'])

        popup_frame = ttk.Frame(self.instance_popup, padding="15")
        popup_frame.pack(fill='both', expand=True)

        ttk.Label(popup_frame,
                  text=f"Select the Modpack Instance (Folder) to scan its /mods directory:",
                  font=('Inter', 11, 'bold')).pack(pady=(0, 10), anchor='w')

        # Scrollable Frame setup for instances
        canvas = tk.Canvas(popup_frame, bg=self.current_theme['bg'], highlightthickness=0)
        vscrollbar = ttk.Scrollbar(popup_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=vscrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        vscrollbar.pack(side="right", fill="y")

        # List instances (directories) inside the root
        try:
            instance_dirs = sorted([d for d in os.listdir(instance_root_path)
                                   if (Path(instance_root_path) / d).is_dir() and not d.startswith('.')])
        except Exception as e:
            ttk.Label(scrollable_frame, text=f"Error reading directory: {e}", foreground='red').pack(pady=10)
            instance_dirs = []

        if not instance_dirs:
            ttk.Label(scrollable_frame, text="No instances found here. Please check the launcher path.", foreground='red').pack(pady=10)
        else:
            for instance_folder_name in instance_dirs:
                full_instance_path = Path(instance_root_path) / instance_folder_name
                final_mods_path = full_instance_path / "mods"

                metadata = self.get_instance_metadata(full_instance_path)

                # --- Instance Display Frame ---
                instance_display_frame = ttk.Frame(scrollable_frame, padding=10, relief='groove', borderwidth=1)
                instance_display_frame.pack(fill='x', pady=5, padx=5)

                # Use a grid layout inside the instance frame for better alignment
                instance_display_frame.columnconfigure(0, weight=1) # Name/Description column
                instance_display_frame.columnconfigure(1, weight=0) # Button column

                # 1. Title/Name
                ttk.Label(instance_display_frame,
                          text=metadata['name'],
                          font=('Inter', 11, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 2))

                # 2. Runtime Info (Smaller text)
                ttk.Label(instance_display_frame,
                          text=f"Runtime: {metadata['runtime']}",
                          font=('Inter', 9, 'italic'),
                          foreground='#4a4a4a' if self.current_theme_name == 'light' else '#a0a0a0'
                          ).grid(row=1, column=0, sticky='w')

                # 3. Description (Wrap text)
                ttk.Label(instance_display_frame,
                          text=metadata['description'],
                          wraplength=450).grid(row=2, column=0, sticky='w', pady=(5, 5))

                # 4. Scan Button
                scan_button_text = f"Scan /mods ({'Exists' if final_mods_path.is_dir() else 'Missing'})"
                ttk.Button(
                    instance_display_frame,
                    text=scan_button_text,
                    command=lambda p=final_mods_path: self.scan_and_close_instance_popup(p)
                ).grid(row=1, column=1, rowspan=2, padx=(10, 0), sticky='nse')

        self.apply_theme_to_toplevel(self.instance_popup, scrollable_frame)

    def scan_and_close_instance_popup(self, mods_path):
        """Closes the instance pop-up and starts the scan."""
        if self.instance_popup:
            self.instance_popup.destroy()
            self.instance_popup = None

        self.scan_for_jar_files(mods_path)

    def apply_theme_to_toplevel(self, toplevel, inner_frame):
        """Applies the current theme to the Toplevel window and its contents."""
        theme = self.current_theme
        toplevel.config(bg=theme['bg'])

        # Frames
        inner_frame.config(style='TFrame')

        # Labels and Canvas
        for widget in toplevel.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.config(style='TFrame')
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label):
                        child.config(style='TLabel')
                    elif isinstance(child, tk.Canvas):
                        child.config(bg=theme['bg'])
                        if child.winfo_children():
                            self.apply_theme_to_toplevel(toplevel, child.winfo_children()[0])
            elif isinstance(widget, ttk.Label):
                widget.config(style='TLabel')

    def apply_theme(self, theme, theme_name):
        """Applies the selected color theme to all main window widgets."""
        self.current_theme = theme
        self.current_theme_name = theme_name

        # 1. Update Root and Wrapper Backgrounds
        self.master.config(bg=theme['bg'])

        # Configure styles for ttk widgets
        self.style.configure('TFrame', background=theme['bg'])
        self.style.configure('TLabel', background=theme['bg'], foreground=theme['fg'])
        self.style.configure('TButton', background=theme['button_bg'], foreground=theme['fg'])

        # Use style map for button states (active, disabled)
        self.style.map('TButton',
                       background=[('active', theme['button_active_bg']), ('!disabled', theme['button_bg'])],
                       foreground=[('active', theme['fg']), ('!disabled', theme['fg'])])

        # 2. Update Text Widgets (Non-ttk)
        self.results_text.config(
            bg=theme['text_bg'],
            fg=theme['text_fg'],
            insertbackground=theme['text_fg'] # Cursor color
        )

        # 3. Update Theme Button Text
        if theme_name == "dark":
            self.theme_button.config(text="☀️ Light Mode")
        else:
            self.theme_button.config(text="🌑 Dark Mode")

        # 4. Update status label color
        current_fg = self.status_label.cget("foreground")
        if current_fg not in (LIGHT_THEME['status_fg_ok'], LIGHT_THEME['status_fg_error'],
                              DARK_THEME['status_fg_ok'], DARK_THEME['status_fg_error']):
             self.status_label.config(foreground=theme['fg'])


    def toggle_theme(self):
        """Switches between light and dark themes."""
        if self.current_theme_name == "light":
            self.apply_theme(DARK_THEME, "dark")
        else:
            self.apply_theme(LIGHT_THEME, "light")

    def _update_status(self, message, color_key='fg'):
        """Updates the status bar with a message and theme-appropriate color."""
        theme = self.current_theme
        color = theme.get(color_key, theme['fg'])
        self.status_label.config(text=message, foreground=color)
        self.master.update()

    def find_minecraft_mods_folder(self):
        """Attempts to find the default Minecraft mods folder based on OS."""
        path_key = "Default Minecraft (.minecraft)"

        if self.os_system == "Windows":
            path_template = LAUNCHER_PATHS["Windows"][path_key]
        elif self.os_system == "Darwin":
            path_template = LAUNCHER_PATHS["Darwin"][path_key]
        else:
            path_template = LAUNCHER_PATHS["Linux"][path_key]

        mods_path = self.resolve_path(path_template)
        return mods_path if Path(mods_path).is_dir() else None

    def extract_mod_info(self, jar_path, filename):
        """
        Extracts mod metadata (name, version, links) from fabric.mod.json or mcmod.info inside the JAR.
        """
        fallback_data = {
            'filename': filename,
            'name': filename.replace('.jar', ''),
            'version': 'N/A',
            'description': 'Could not extract metadata (Not a Fabric/Forge/Quilt mod, or JSON invalid).',
            'links': {}
        }

        try:
            with zipfile.ZipFile(jar_path, 'r') as zf:

                # 1. Try Fabric/Quilt metadata (fabric.mod.json)
                try:
                    with zf.open('fabric.mod.json') as f:
                        data = json.loads(f.read().decode('utf-8'))

                        links = {
                            'Homepage': data.get('contact', {}).get('homepage'),
                            'Sources': data.get('contact', {}).get('sources'),
                            'Issues': data.get('contact', {}).get('issues')
                        }

                        modmenu_links = data.get('custom', {}).get('modmenu', {}).get('links', {})
                        for key, url in modmenu_links.items():
                            clean_key = key.replace('modmenu.', '').replace('_', ' ').title()
                            links[clean_key] = url

                        cleaned_links = {k: v for k, v in links.items() if v and v.strip()}

                        return {
                            'filename': filename,
                            'name': data.get('name', filename.replace('.jar', '')),
                            'version': data.get('version', 'N/A'),
                            'description': data.get('description', 'No description provided.'),
                            'links': cleaned_links
                        }
                except KeyError:
                    pass

                # 2. Try Forge/Neoforge metadata (mcmod.info - legacy, or mods.toml)
                try:
                    with zf.open('mcmod.info') as f:
                        # mcmod.info is usually an array, containing one mod entry
                        data = json.loads(f.read().decode('utf-8'))[0]

                        links = {}
                        if 'url' in data: links['Homepage'] = data['url']

                        return {
                            'filename': filename,
                            'name': data.get('name', filename.replace('.jar', '')),
                            'version': data.get('version', 'N/A'),
                            'description': data.get('description', 'Forge mod metadata found (mcmod.info).'),
                            'links': links
                        }
                except KeyError:
                    pass # Failed both fabric.mod.json and mcmod.info

        except zipfile.BadZipFile:
            fallback_data['description'] = 'Not a valid JAR/ZIP file.'
        except Exception as e:
            fallback_data['description'] = f'Error during extraction: {e}'

        return fallback_data

    def scan_for_jar_files(self, directory):
        """Scans the given directory and its subdirectories for .jar files and extracts info."""
        self.scanned_mods = []

        # Check if the path exists before starting the walk
        if not os.path.isdir(directory):
            self._update_status(f"Error: Mods directory not found at: {directory}", 'status_fg_error')
            self.update_results_display()
            self.export_button.config(state='disabled')
            return

        self.current_scan_path = directory
        self._update_status(f"Scanning mods in: {Path(directory).name}...", 'fg')

        # Recursive scan (for nested mod folders, e.g., optional or disabled subfolders)
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.jar'):
                    full_path = Path(root) / file
                    mod_data = self.extract_mod_info(full_path, file)
                    self.scanned_mods.append(mod_data)

        self.scanned_mods.sort(key=lambda x: x['name'].lower())

        self.update_results_display()

        if self.scanned_mods:
            valid_mods = [m for m in self.scanned_mods if 'Could not extract metadata' not in m['description']]
            self._update_status(f"Scan complete. Found {len(valid_mods)} mods with metadata, {len(self.scanned_mods) - len(valid_mods)} fallback entries. Ready to export.", 'status_fg_ok')
            self.export_button.config(state='normal')
        else:
            self._update_status(f"Scan complete. No .jar files found in the directory. (Path: {self.current_scan_path})", 'fg')
            self.export_button.config(state='disabled')

        self.path_label.config(text=f"Current Scan Path: {self.current_scan_path}")

    def quick_scan(self):
        """Initiates a scan on the detected default Minecraft mods folder."""
        self._update_status("Attempting Quick Scan...")
        mods_folder = self.find_minecraft_mods_folder()

        if mods_folder and Path(mods_folder).is_dir():
            self.scan_for_jar_files(mods_folder)
        else:
            self._update_status("Error: Could not automatically find the default .minecraft/mods folder.", 'status_fg_error')
            self.update_results_display()
            self.export_button.config(state='disabled')

    def select_custom_folder(self):
        """Opens a dialog for the user to select a custom folder to scan."""
        folder_selected = filedialog.askdirectory(title="Select Mods Folder")
        if folder_selected:
            self.scan_for_jar_files(folder_selected)
        else:
            self._update_status("Folder selection cancelled.", 'fg')

    def update_results_display(self):
        """Clears and updates the text area with the list of found files."""
        self.results_text.config(state='normal')
        self.results_text.delete('1.0', tk.END)

        if not self.scanned_mods:
            self.results_text.insert(tk.END, "No files to display. Please perform a scan.")
        else:
            for i, mod in enumerate(self.scanned_mods):
                self.results_text.insert(tk.END, f"{i+1}. {mod['name']} ({mod['version']})\n")

                links = mod['links']
                if links:
                    for key, url in links.items():
                        self.results_text.insert(tk.END, f"   - {key}: {url}\n")
                else:
                     self.results_text.insert(tk.END, "   - No automatic links found.\n")

                if 'Could not extract metadata' in mod['description']:
                    self.results_text.insert(tk.END, f"   [WARNING] {mod['description']}\n")

                self.results_text.insert(tk.END, "\n") # Spacer

        self.results_text.config(state='disabled')

    # --- Helper Functions for Export ---

    def _get_system_info(self):
        """Gathers system information for info.txt."""
        info = []
        info.append("--- System Information ---\n")
        info.append(f"Date and Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        system = platform.system()
        # Custom note for the user's environment
        if system == "Linux":
            info.append(f"Operating System: Linux (Arch Linux/KDE - Inferred from user environment)\n")
        else:
             info.append(f"Operating System: {system} {platform.release()} ({platform.version()})\n")

        info.append(f"System Architecture: {platform.machine()}\n")
        info.append(f"Python Version: {platform.python_version()}\n")
        info.append(f"Current Scan Path: {self.current_scan_path}\n")
        info.append("\n--- Disclaimer ---\n")
        info.append("Detailed hardware information (like RAM usage or GPU model) requires external, non-standard Python libraries and is therefore omitted.")
        return "\n".join(info)

    def export_info_file(self, export_dir, base_filename):
        """Creates the info.txt file with system details."""
        info_content = self._get_system_info()
        info_path = export_dir / f"{base_filename}.info.txt"
        try:
            with open(info_path, 'w', encoding='utf-8') as f:
                f.write(info_content)
            return True
        except IOError as e:
            self._update_status(f"Error writing info.txt: {e}", 'status_fg_error')
            return False

    def export_modlinks_automatic_file(self, export_dir, base_filename):
        """Creates the modlinks.txt file with ALL unique extracted URLs."""
        all_links = set()

        for mod in self.scanned_mods:
            for url in mod['links'].values():
                all_links.add(url)

        links_path = export_dir / f"{base_filename}.modlinks.txt"

        try:
            with open(links_path, 'w', encoding='utf-8') as f:
                f.write("--- Automatically Extracted Mod Links ---\n")
                f.write(f"Total unique links found: {len(all_links)}\n\n")
                if all_links:
                    for url in sorted(list(all_links)):
                        f.write(f"{url}\n")
                else:
                    f.write("No links (homepage, sources, modrinth, etc.) were found in the mod metadata files.\n")
            return True
        except IOError as e:
            self._update_status(f"Error writing modlinks.txt: {e}", 'status_fg_error')
            return False

    # --- Main Export Function ---

    def export_modlist(self):
        """Exports the list of mod data into 6 formats."""
        if not self.scanned_mods:
            self._update_status("Error: No mods scanned to export.", 'status_fg_error')
            return

        desktop_path = Path.home() / "Desktop"
        export_dir = desktop_path / "modlist"

        try:
            os.makedirs(export_dir, exist_ok=True)
        except OSError as e:
            self._update_status(f"Error creating export directory: {e}", 'status_fg_error')
            return

        base_filename = f"modlist-{time.strftime('%Y%m%d-%H%M%S')}"

        exported_count = 0

        def write_file(filepath, content=None, json_data=None, csv_rows=None):
            nonlocal exported_count
            try:
                if json_data is not None:
                     with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=4)
                elif csv_rows is not None:
                    with open(filepath, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Index', 'Mod Name', 'Version', 'Filename', 'Homepage', 'Sources'])
                        for i, mod in enumerate(self.scanned_mods):
                            writer.writerow([
                                i + 1,
                                mod['name'],
                                mod['version'],
                                mod['filename'],
                                mod['links'].get('Homepage', ''),
                                mod['links'].get('Sources', '')
                            ])
                else:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                exported_count += 1
            except IOError as e:
                self._update_status(f"Error writing file {filepath.name}: {e}", 'status_fg_error')

        # --- 1. Markdown (.md) - Detailed Rich Format ---
        md_content = f"# Minecraft Modlist Export\n\n"
        md_content += f"Scanned Directory: `{self.current_scan_path}`\n"
        md_content += f"Total Mods: **{len(self.scanned_mods)}**\n\n---\n\n"

        for i, mod in enumerate(self.scanned_mods):
            md_content += f"### {i+1}. {mod['name']} (`{mod['version']}`)\n"
            md_content += f"**File:** `{mod['filename']}`\n\n"
            md_content += f"**Description:** {mod['description']}\n\n"

            if mod['links']:
                md_content += "**Links:**\n"
                for key, url in mod['links'].items():
                    md_content += f"* [{key}]({url})\n"
            else:
                md_content += "* No links found in metadata.\n"
            md_content += "\n"

        write_file(export_dir / f"{base_filename}.md", content=md_content)

        # --- 2. Plain Text (.txt) ---
        txt_content = f"Minecraft Modlist Export\nScanned Directory: {self.current_scan_path}\nTotal Mods: {len(self.scanned_mods)}\n" + ("=" * 50) + "\n\n"
        for mod in self.scanned_mods:
            txt_content += f"MOD: {mod['name']} ({mod['version']})\n"
            txt_content += f"FILE: {mod['filename']}\n"
            for key, url in mod['links'].items():
                txt_content += f" {key}: {url}\n"
            txt_content += "-" * 50 + "\n"

        write_file(export_dir / f"{base_filename}.txt", content=txt_content)

        # --- 3. JSON (.json) - Raw Data ---
        json_data = {
            "scan_path": self.current_scan_path,
            "total_mods": len(self.scanned_mods),
            "mods": self.scanned_mods
        }
        write_file(export_dir / f"{base_filename}.json", json_data=json_data)

        # --- 4. CSV (.csv) - Spreadsheet friendly ---
        write_file(export_dir / f"{base_filename}.csv", csv_rows=self.scanned_mods)

        # --- 5. System Info (info.txt) ---
        self.export_info_file(export_dir, base_filename)

        # --- 6. Automatic Mod Links (modlinks.txt) ---
        self.export_modlinks_automatic_file(export_dir, base_filename)

        final_count = 6

        self._update_status(f"Successfully exported {final_count} files to: {export_dir}", 'status_fg_ok')


# Run the application
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ModlistExporterApp(root)
        root.mainloop()
    except tk.TclError:
        print("Error: Tkinter GUI environment could not be initialized.")
        print("Please ensure Python is running in a desktop environment and the 'tkinter' library is installed and configured.")
