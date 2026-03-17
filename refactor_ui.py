import os
import re
import shutil

ui_dir = "c:/Users/c/Desktop/GichanFormant/ui"
base_dir = "c:/Users/c/Desktop/GichanFormant"

mapping = {
    "main_window": "windows",
    "popup_plot": "windows",
    "compare_plot": "windows",
    "vowel_analysis_dialog": "dialogs",
    "file_guide": "dialogs",
    "canvas_fixed": "widgets",
    "design_panel": "widgets",
    "draw_design_panel": "widgets",
    "filter_panel": "widgets",
    "icon_widgets": "widgets",
    "layer_dock": "widgets",
    "layer_row_widgets": "widgets",
    "tab_draw_view": "widgets",
    "tab_label_view": "widgets",
    "tool_indicator": "widgets",
    "display_utils": "widgets",
    "draw_manager": "widgets",
    "label_manager": "widgets",
    "layer_logic": "widgets",
    "layout_constants": "widgets",
}

for root, _, files in os.walk(base_dir):
    if ".venv" in root or ".git" in root or "__pycache__" in root:
        continue
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Replace string references or imports
            for mod, folder in mapping.items():
                content = re.sub(
                    rf"from\s+ui\.{mod}\s+import",
                    f"from ui.{folder}.{mod} import",
                    content,
                )
                content = re.sub(
                    rf"import\s+ui\.{mod}\b", f"import ui.{folder}.{mod}", content
                )

            # In the UI files, replace relative imports 'from .X import Y' -> 'from ui.folder.X import Y'
            if "ui" in root.replace("\\", "/").split("/"):
                for mod, folder in mapping.items():
                    content = re.sub(
                        rf"from\s+\.{mod}\s+import",
                        f"from ui.{folder}.{mod} import",
                        content,
                    )

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

# Move the files
for folder in ["windows", "dialogs", "widgets"]:
    fpath = os.path.join(ui_dir, folder)
    os.makedirs(fpath, exist_ok=True)
    with open(os.path.join(fpath, "__init__.py"), "w", encoding="utf-8") as f:
        pass

for mod, folder in mapping.items():
    src = os.path.join(ui_dir, f"{mod}.py")
    dst = os.path.join(ui_dir, folder, f"{mod}.py")
    if os.path.exists(src):
        try:
            shutil.move(src, dst)
        except Exception as e:
            print(f"Failed to move {src}: {e}")

print("Done Refactoring!")
