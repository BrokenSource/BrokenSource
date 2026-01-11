<div align="center">
  <a href="https://brokensrc.dev"><img src="https://raw.githubusercontent.com/BrokenSource/BrokenSource/main/broken/resources/images/logo.png" width="200"></a>
  <h2 style="margin-top: 0">Broken Source Software</h2>
  <a href="https://pypi.org/project/broken-source/"><img src="https://img.shields.io/pypi/v/broken-source?label=PyPI&color=blue"></a>
  <a href="https://pypi.org/project/broken-source/"><img src="https://img.shields.io/pypi/dw/broken-source?label=Installs&color=blue"></a>
  <a href="https://github.com/BrokenSource/BrokenSource"><img src="https://img.shields.io/github/v/tag/BrokenSource/BrokenSource?label=GitHub&color=orange"></a>
  <a href="https://github.com/BrokenSource/BrokenSource/stargazers"><img src="https://img.shields.io/github/stars/BrokenSource/BrokenSource?label=Stars&style=flat&color=orange"></a>
  <a href="https://discord.gg/KjqvcYwRHm"><img src="https://img.shields.io/discord/1184696441298485370?label=Discord&style=flat&color=purple"></a>
</div>

<br>

> [!NOTE]
> This repository is the main development environment for all my professional and personal projects, including libraries, applications, infrastructure and some private components.
>
> <sup><b>Warning:</b> Expect a developer-centric experience within a complex monorepo structure 🙂</sup>

Always evolving code, a wisdom rabbit hole to know the ins and outs of the system as a whole. I could only hope to ever have it all properly documented, as the focus is always on the code itself.

- This readme is intentionally vague in a sense, as there's just too much going on. Instead of talking about everything and nothing at the same time, go exploring the self-documented codebase!
- Feel free to get in touch to learn how it works or python monorepos advice.


## 📦 Structure

Roughly speaking, the important parts are:

### ♻️ Common

- [`📁/.github`](./.github): Workflows, readmes + [special](https://github.com/BrokenSource/.github) organization repository
- [`📁/website`](./website): Mkdocs documentation derived from [`mkdocs-base.yml`](./mkdocs-base.yml)

### 🗿 Monorepo

- [`📁/docker`](./docker): Everything docker for all projects
- `📁/meta`: Optional directory to link off-branch projects
- [`📁/projects`](./projects): Application projects (has entry points)
- [`📁/packages`](./packages): Library projects (
- [`action.yml`](./action.yml): Setup workflow

### 🐍 Python

- `📁/.venv`: Global venv from [uv](https://github.com/astral-sh/uv)
- [`📁/broken`](./broken): Main shared library
- `📁/dist`: Common build directory

### 🦀 Rust

- [`📁/crates`](./crates): Library projects
- `📁/target`: Build directory


## 💡 Tips

- Export `PYTHONPYCACHEPREFIX=/tmp/__pycache__` in `/etc/environment` to avoid `*.pyc` clutter
- Always run `uv sync --all-packages` or `uv sync --package (name)` for select projects
- Use `docker compose run --rm --build (service)` from [`docker-compose.yml`](./docker-compose.yml)
- Add `root="/tmp/containerd"` in `/etc/containerd/config.toml ` if you got the RAM to save SSD in Docker
