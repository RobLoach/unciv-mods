# Unciv Mods

Lists all the available Unciv mods, in a website, and a mods.json manifest file.

## Development

1. Install mkdocs
    ```
    sudo apt install mkdocs
    ```

2. Install dependencies
    ```
    pip install mkdocs-material mkdocs-awesome-pages-plugin
    ```

3. Generate a [GitHub Token](https://github.com/settings/personal-access-tokens/new?name=Unciv-Mods-GitHub-Pages)

4. Run the build process
    ```
    GITHUB_TOKEN=github_pat_abc python3 build.py
    ```

5. Test the docs
    ```
    mkdocs serve
    ```

6. Deploy
    ```
    mkdocs gh-deploy
    ```
