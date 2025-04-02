
!!! tip "**Package** manager cache: "
    === ":simple-astral: uv"
        Either run `uv cache prune` or `uv cache dir` to locate wheel downloads caches, should be at:
        <table>
            <tbody class="slim-table">
                <tr>
                    <td style="width: 20%">:material-microsoft: Windows</td>
                    <td><kbd>C:\\\\Users\\(...)\\AppData\\Local\\uv</kbd></td>
                </tr>
                <tr>
                    <td>:simple-apple: MacOS</td>
                    <td><kbd>~/Library/Caches/uv</kbd></td>
                </tr>
                <tr>
                    <td>:simple-linux: Linux</td>
                    <td><kbd>~/.cache/uv</kbd></td>
                </tr>
            </tbody>
        </table>
    === ":simple-python: Pip"
        Either run `pip cache purge` or `pip cache dir` to locate wheel download caches, should be at:
        <table>
            <tbody class="slim-table">
                <tr>
                    <td style="width: 20%">:material-microsoft: Windows</td>
                    <td><kbd>C:\\\\Users\\(...)\\AppData\\Local\\pip</kbd></td>
                </tr>
                <tr>
                    <td>:simple-apple: MacOS</td>
                    <td><kbd>~/Library/Caches/pip</kbd></td>
                </tr>
                <tr>
                    <td>:simple-linux: Linux</td>
                    <td><kbd>~/.cache/pip</kbd></td>
                </tr>
            </tbody>
        </table>
    === ":simple-poetry: Poetry"
        Either run `poetry cache clear` or `poetry cache list` to locate caches and venvs, should be at:
        <table>
            <tbody class="slim-table">
                <tr>
                    <td style="width: 20%">:material-microsoft: Windows</td>
                    <td><kbd>C:\\\\Users\\(...)\\AppData\\Local\\pypoetry</kbd></td>
                </tr>
                <tr>
                    <td>:simple-apple: MacOS</td>
                    <td><kbd>~/Library/Caches/pypoetry</kbd></td>
                </tr>
                <tr>
                    <td>:simple-linux: Linux</td>
                    <td><kbd>~/.cache/pypoetry</kbd></td>
                </tr>
            </tbody>
        </table>
    === ":simple-pdm: PDM"
        Either run `pdm cache clear` or `pdm cache list` to locate wheel downloads caches, should be at:
        <table>
            <tbody class="slim-table">
                <tr>
                    <td style="width: 20%">:material-microsoft: Windows</td>
                    <td><kbd>C:\\\\Users\\(...)\\AppData\\Local\\pdm</kbd></td>
                </tr>
                <tr>
                    <td>:simple-apple: MacOS</td>
                    <td><kbd>~/Library/Caches/pdm</kbd></td>
                </tr>
                <tr>
                    <td>:simple-linux: Linux</td>
                    <td><kbd>~/.cache/pdm</kbd></td>
                </tr>
            </tbody>
        </table>
