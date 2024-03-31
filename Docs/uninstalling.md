# ♻️ Uninstalling

There is a partially implemented command for uninstalling, but it doesn't exist for release versions yet:
- `broken uninstall`

For now, you can just delete the directories we use below:

!!! tip "Project Workspaces"
    The main Library uses [**AppDirs**](https://pypi.org/project/appdirs) to decide per-platform directories

    For unification, all project's Workspaces are located at the User Data directory, followed by a **AppAuthor** and **AppName** subdirectories which will be <kbd>BrokenSource</kbd> and <kbd>ProjectName</kbd> in most cases

    - **Linux**: `~/.local/share/AppAuthor/AppName/*`

    - **Windows**: `%applocaldata%\AppAuthor\AppName\*`

    - **MacOS**: `~/Library/Application Support/AppAuthor/AppName/*`

!!! tip "Python Virtual Environment"
    **Rye** creates Virtual Environments on the `.venv` directory on the Monorepo root

    The download cache if you chose `uv` instead of `pip-tools` is located at:

    - **Linux**: `~/.cache/uv/*`

    - **Windows**: `%localappdata%\uv\*`

    - **MacOS**: `~/Library/Caches/uv/*`

!!! tip "Releases Virtual Environment"
    We use [**PyApp**](https://github.com/ofek/pyapp) to make the releases. It unpacks itself on:

    - **Linux**: `~/.local/share/pyapp`

    - **Windows**: `%applocaldata%\pyapp`

    - **MacOS**: `~/Library/Application Support/pyapp`
