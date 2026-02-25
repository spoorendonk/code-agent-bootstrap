#!/usr/bin/env python3
"""Bootstrap CLAUDE.md into the current project directory."""

import os
import platform
import re
import subprocess
import sys
import tempfile
import urllib.request

TEMPLATE_URL = (
    "https://raw.githubusercontent.com/spoorendonk/code-agent-bootstrap"
    "/master/CLAUDE.md.template"
)

WORKFLOW_SECTIONS = [
    "## Workflow: Plan → Grind",
    "### Plan (default)",
    "### Grind (on approval)",
    "### Fullgate",
    "### Claiming Work (GitHub)",
    "### Teams",
]


def download_template():
    """Download CLAUDE.md.template from GitHub and return its contents."""
    print("Downloading CLAUDE.md.template …")
    with urllib.request.urlopen(TEMPLATE_URL) as resp:
        return resp.read().decode()


def detect_project_type():
    """Return (language, build_cmd, test_cmd) based on project files."""
    if os.path.exists("CMakeLists.txt"):
        return "C++", "cmake --build build", "ctest --test-dir build"
    if os.path.exists("Cargo.toml"):
        return "Rust", "cargo build", "cargo test"
    if os.path.exists("pyproject.toml") or os.path.exists("setup.py"):
        return "Python", "pip install -e .", "pytest"
    if os.path.exists("package.json"):
        return "Node", "npm run build", "npm test"
    if os.path.exists("go.mod"):
        return "Go", "go build ./...", "go test ./..."
    return None, "make", "make test"


def detect_project_name():
    """Guess the project name from README heading, git remote, or folder."""
    if os.path.exists("README.md"):
        with open("README.md") as f:
            for line in f:
                m = re.match(r"^#\s+(.+)", line)
                if m:
                    return m.group(1).strip()

    if os.path.isdir(".git"):
        try:
            url = subprocess.check_output(
                ["git", "remote", "get-url", "origin"],
                stderr=subprocess.DEVNULL,
            ).decode().strip()
            name = url.rstrip("/").rsplit("/", 1)[-1]
            return name.removesuffix(".git")
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    return os.path.basename(os.getcwd())


def prompt(label, default):
    """Prompt the user for a value with a default."""
    answer = input(f"{label} [{default}]: ").strip()
    return answer or default


def merge_into(existing_path, template):
    """Append missing workflow sections from template into existing file."""
    with open(existing_path) as f:
        existing = f.read()

    # Find the start of the workflow block in the template
    first_section = WORKFLOW_SECTIONS[0]
    idx = template.find(first_section)
    if idx == -1:
        print("Template has no workflow sections — nothing to merge.")
        return

    workflow_block = template[idx:]
    added = []

    for heading in WORKFLOW_SECTIONS:
        if heading not in existing:
            # Extract everything from this heading until the next ##
            start = workflow_block.find(heading)
            if start == -1:
                continue
            end = workflow_block.find("\n## ", start + 1)
            if end == -1:
                end = len(workflow_block)
            else:
                # Also check for ### at the same or higher level
                end2 = workflow_block.find("\n" + "#" * heading.count("#") + " ", start + len(heading))
                if end2 != -1 and end2 < end:
                    end = end2
                # Recalculate: find next heading at same or higher level
                pass
            # Simpler: just grab from heading to next same-or-higher-level heading
            level = len(heading) - len(heading.lstrip("#"))
            search_start = start + len(heading)
            end = len(workflow_block)
            for m in re.finditer(r"\n(#{1," + str(level) + r"})\s", workflow_block[search_start:]):
                end = search_start + m.start()
                break
            section = workflow_block[start:end].rstrip() + "\n"
            added.append(section)

    if not added:
        print("All workflow sections already present — nothing to merge.")
        return

    with open(existing_path, "a") as f:
        f.write("\n")
        for section in added:
            f.write("\n" + section)

    print(f"Merged {len(added)} section(s) into {existing_path}.")


def create_agents_symlink():
    """Create AGENTS.md as a symlink (or copy on Windows)."""
    if os.path.exists("AGENTS.md"):
        print("AGENTS.md already exists — skipping.")
        return
    if platform.system() == "Windows":
        import shutil
        shutil.copy2("CLAUDE.md", "AGENTS.md")
        print("Created AGENTS.md (copy).")
    else:
        os.symlink("CLAUDE.md", "AGENTS.md")
        print("Created AGENTS.md → CLAUDE.md symlink.")


def main():
    template = download_template()

    # Check for existing files
    claude_exists = os.path.exists("CLAUDE.md")
    choice = None
    if claude_exists:
        print("\nCLAUDE.md already exists.")
        choice = input("  (o)verwrite / (m)erge workflow sections / (c)ancel? [c]: ").strip().lower()
        if choice in ("c", ""):
            print("Cancelled.")
            sys.exit(0)
        if choice == "m":
            # Still need to fill placeholders for merge content
            pass

    # Detect defaults
    lang, default_build, default_test = detect_project_type()
    default_name = detect_project_name()

    if lang:
        print(f"\nDetected {lang} project.")

    # Interactive prompts
    name = prompt("Project name", default_name)
    build = prompt("Build command", default_build)
    test = prompt("Test command", default_test)

    # Fill template
    filled = template
    filled = filled.replace("{{PROJECT_NAME}}", name)
    filled = filled.replace("{{BUILD_COMMAND}}", build)
    filled = filled.replace("{{TEST_COMMAND}}", test)

    if choice == "m":
        merge_into("CLAUDE.md", filled)
    else:
        with open("CLAUDE.md", "w") as f:
            f.write(filled)
        print(f"\nWrote CLAUDE.md for '{name}'.")

    # AGENTS.md symlink (skip on merge if it already exists)
    if not (choice == "m" and os.path.exists("AGENTS.md")):
        create_agents_symlink()

    print("Done.")


if __name__ == "__main__":
    main()
