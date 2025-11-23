# ✨ Minecraft Modlist Exporter (v4.5)

**A Cross-Platform Graphical Utility for Cataloging Minecraft Mods**

*By © 2025 Minxify_ig*

## ⚠️ Disclaimer & Important Notes

Please read this before running the application:

  * **Performance:** The tool relies heavily on file I/O speed when reading mod archives. Scanning very large mod folders (e.g., 500+ mods) may take time, during which the GUI may appear unresponsive. **Please be patient.**

  * **Metadata Gaps:** If a mod file is malformed, encrypted, or uses a highly custom metadata format, the tool will only record the filename in the reports.

  * **Liability:** Use at your own risk. I am not responsible for any damage to your computer from executing this program. The full source code is available in this repository for review.

## 🖥️ Installation & Execution

This application requires Python 3.6+ and uses **only built-in modules** to ensure cross-platform compatibility without external dependencies.

1.  **Save the file:** Save the provided Python code as `modlistexportv3.py`.

2.  **Execute:** Open your terminal (**CMD** on Windows) and run the file directly:

    ```bash
    python3 modlistexportv3.py
    ```

## ⚙️ Usage Guide: Scanning & Exporting

The Exporter uses a simple, guided process to locate your mod files, extract the metadata, and generate a comprehensive report set.

### **Part 1: Selecting the Mod Directory**

The GUI offers three methods for locating the target mod folder:

1.  **Quick Scan (Default):** Instantly attempts to find the standard `.minecraft/mods` folder (ideal for vanilla or standard launcher installs).
2.  **Guided Instance Selection:** Allows selection of a specific modpack instance folder from supported third-party launchers (Prism, MultiMC, CurseForge, GDLauncher, etc.).
3.  **Select Custom Folder:** Opens your local file manager to manually choose any mod directory on your system.

### **Part 2: Reviewing and Generating the Report**

Once the directory is selected and the scan completes:

4.  **Review Results:** The central text area displays a summary of the scanned mods (names, versions, authors, and links).
5.  **Export:** Click the **"Export Full Report"** button. A new folder named `modlist` will be created on your Desktop containing all the generated report files, timestamped for easy organization (e.g., `modlist-20251123-101130.md`).

## 🚀 Key Features

  * **Robust Scanning:** Preset paths for popular third-party launchers (Prism, MultiMC, CurseForge, GDLauncher) across all major operating systems.
  * **Deep Metadata Extraction:** Accurately reads and processes metadata from both `fabric.mod.json` (Fabric/Quilt) and `mcmod.info` (Forge/NeoForge).
  * **Theme Toggle:** Supports switching between Light and Dark modes.
  * **Dependency-Free:** Uses **only built-in Python modules** (`tkinter`, `zipfile`, etc.).

### Multi-Format Reporting (6 Files)

The application generates a comprehensive report set tailored for different uses:

| Format | Purpose | Best For |
| :--- | :--- | :--- |
| **Markdown** (`.md`) | Highly readable, detailed list with links and descriptions. | Sharing on forums, documentation, or GitHub. |
| **CSV** (`.csv`) | Structured, delimited data for spreadsheet analysis. | Importing into **LibreOffice Calc** (your preferred office suite) for filtering and sorting. |
| **JSON** (`.json`) | Raw, structured data. | Programmatic use, automated tools, or developers. |
| **Plain Text** (`.txt`) | Simple, unformatted list. | Quick viewing or basic copy-paste into chat. |
| **Mod Links** (`.modlinks.txt`) | A consolidated, unique list of all URLs found. | Quickly accessing mod pages or verifying sources. |
| **System Info** (`.info.txt`) | Details about the host OS and Python environment. | Troubleshooting and providing context to support staff. |

## 🖼️ Look and Feel

  * **Intuitive Interface:** A user-friendly GUI built with `tkinter` that anyone can master in seconds.
  * **Theme Switching:** Easily toggle between Light and Dark mode for comfortable viewing.

## 💾 System Info & Verification

Each export session includes a detailed system information file:

`[base_filename].info.txt`

This file contains crucial details about the host OS, Python version, and execution time, which is essential when providing context for troubleshooting or bug reports.

## 🪩 License & Credits

© 2025 Minxify_ig. All rights reserved.
