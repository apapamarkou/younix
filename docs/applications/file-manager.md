## 📁 `nnn` File Manager Keybindings

nnn is a highly efficient, minimalist terminal file manager. The following keybindings cover the most common file and folder operations.

### 1. Selection and Cutbuffer

nnn uses a "cutbuffer" (selection) to stage files for copy and move operations across its contexts (tabs).

| Action | Keybinding | Description |
| :--- | :--- | :--- |
| **Select/Deselect Item** | `Space` | Toggles the selection status of the highlighted item (indicated by a `+`). |
| **Select a Range** | `m` (Start) then `m` (End) | Marks the beginning and end of a range to select multiple consecutive items. |
| **Select All** | `a` | Selects all files and folders in the current directory. |
| **Clear Selection** | `A` | Inverts the selection, effectively clearing it if all items are deselected. |

### 2. Copy and Move Files/Folders

Once items are selected, you paste them into the target directory.

| Action | Keybinding | Steps |
| :--- | :--- | :--- |
| **Copy Selected Items** | `p` | 1. Select items. 2. Navigate to the destination directory (use contexts for speed). 3. Press `p` to copy. |
| **Move Selected Items** | `v` | 1. Select items. 2. Navigate to the destination directory. 3. Press `v` to move (i.e., cut and paste). |

> 💡 **Tip: Using Contexts for Transfers**
>
> Use the numbered keys **`1`**, **`2`**, **`3`**, and **`4`** to switch between the four available contexts (tabs). This allows you to select files in one context, switch to another context's directory, and then execute the copy or move command.

### 3. Create, Delete, and Rename

These operations apply to the currently highlighted item or prompt for input.

| Action | Keybinding | Function |
| :--- | :--- | :--- |
| **Create Directory** | `D` | Prompts you to enter a new directory name. |
| **Create File/Folder** | `n` | Prompts you to choose file or folder and then to give a name. |
| **Rename** (Highlighted) | `^R` (Ctrl + `r`) | Prompts to rename the currently highlighted file or folder. |
| **Delete** (Selected/Highlighted) | `^X` (Ctrl + `x`) | Prompts for confirmation to permanently delete the selected or highlighted item(s). |

### 4. Navigation and Help

| Action | Keybinding | Description |
| :--- | :--- | :--- |
| **Enter Directory/Open File** | `Enter` or `l` | Enters a directory or opens a file with the associated program. |
| **Go Up Directory** | `Left Arrow` or `h` | Moves one level up in the directory structure. |
| **Show Help/Keybinds** | `?` | Displays a quick reference guide of all nnn keybindings. |
| **Run Shell Command** | `]` | Prompts for a shell command to execute in the current directory. |
| **Run Shell Command** | `!` | Opens a shell in the current directory. |
