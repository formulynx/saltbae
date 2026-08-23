# saltbae

> *"Cooked through? Now, folks — it's saltbae time."*

`/saltbae` is a commit-serving skill for [Claude Code](https://claude.com/product/claude-code). 

## Usage

```
/saltbae
```

You can also bump the version (auto-incrementing the patch, or to the version given),
commits, and tags the release.

```
/saltbae bump
/saltbae bump 4.2.1
```

Commits from this skill never carry an AI-attribution string (no
`Co-Authored-By: Claude ...`, no "Generated with Claude Code", no
Anthropic/Claude/AI mention) — this overrides any default trailer behavior.

## Install

```sh
# macOS / Linux / WSL / Git Bash (any POSIX shell)
curl -fsSL https://cdn.jsdelivr.net/gh/formulynx/saltbae@v0.1.9/install.sh | bash

# Native Windows (PowerShell or cmd, no POSIX shell)
irm https://cdn.jsdelivr.net/gh/formulynx/saltbae@v0.1.9/install.ps1 | iex
```

- Copies `skills/saltbae/SKILL.md` into `~/.claude/skills/saltbae/SKILL.md`, pinned to a release tag
- Use `@main` for latest dev code
- For dev, git clone and run `saltbae/install.sh` (symlinks instead of copies)
- Uninstall with `--uninstall` (`-Uninstall` on the `.ps1`)

## Update

- Re-run the one-liner with a newer tag (or `@main`)
- Git-clone installs: `git -C saltbae pull`

## Why "saltbae"?

Named for the meme chef's dramatic tableside cut and salt flourish.  
Without a proper cut (splitting the diff into logical commits) and seasoning (a clear commit log),
a reviewer can't chew through the change despite your tireless effort.  
You focus on the code, `/saltbae` handles the plating.

[`/grilling`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling) (Thanks to Matt Pocock)
stress-tests a plan before anything is built.  
`/saltbae` picks up once the changes exist, carving and seasoning them into a reviewable history.

```
⠀⠀⠀⠀⣀⡀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⢀⡔⠁⠴⠋⡿⠀⠀⠁⠀⠓⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⡇⢸⢀⠇⢹⣠⢤⡀⠀⠀⠀⢠⠎⠀⠀⠀⢠⡀⡀⠀⠀⠀⠙⠎⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣖⠢⡀⠀⡇⠀⠿⠀⠘⡠⠊⡣⠀⠀⢠⠇⠀⡴⠒⠠⠤⣤⡐⠂⠈⠁⠉⠀⠸⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠈⢢⡈⠢⠽⠀⠘⠠⠀⢢⠀⢹⡀⠀⣾⠀⣺⠁⠀⠀⠀⠀⠉⠒⠢⡔⠒⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠑⢄⠀⠀⠀⠀⠐⠀⠂⠄⢳⠀⢻⣷⡁⠀⠀⠀⠀⠀⠀⠀⠀⠈⢟⠳⡞⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠈⢦⠀⠀⠀⠀⠀⠀⠀⢸⠀⢸⡇⢣⡒⣶⣤⡀⠀⠀⠀⠀⠀⠀⡼⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠱⡄⠀⠀⠀⠀⢀⡞⠀⠀⡇⠀⣿⣿⣿⣿⠖⢤⣾⣿⣾⣽⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⡼⠈⠉⡉⠀⢸⠀⠀⠀⣧⠀⠈⠙⠛⠁⠀⠘⠻⠿⢿⣧⣄⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢹⠀⠀⢈⢧⣼⣠⠖⢶⡉⢦⢀⣀⣀⣦⣤⡔⢀⣠⠋⢢⡀⠀⠀⠉⠑⣄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⠀⢀⠶⠁⠈⡇⠀⠀⠉⠢⣧⡈⠉⢉⡍⢉⡝⠁⠀⠀⠙⢆⠀⠀⠀⠘⡆⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⡾⠀⠀⠈⠂⠀⠘⡄⠀⠀⠀⠀⠙⠦⣤⠴⠋⠀⠀⠀⠀⠀⠀⢳⡀⠀⠀⣽⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢠⡇⠀⢠⠀⠀⠀⠀⠹⡀⠀⠀⠀⠀⠀⠈⠓⢤⡀⠀⠀⠀⠀⠀⠀⡇⠀⠀⢾⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢸⠁⠀⠀⠀⠀⠀⠀⠀⢳⡄⠀⠀⠀⠀⠀⠀⠀⠉⠓⠦⢄⣀⡠⠞⠀⠀⠀⠘⡄⠀⠀⠀
⠀⠀⠀⠈⠀⡾⠀⠀⠀⠀⠠⠀⠀⠀⠈⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⢇⠀⠀⠀
⠀⠀⠀⠀⠀⡇⠀⠄⢀⠀⠀⢃⠀⠀⠀⢹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠈⢆⠀⠀
⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠠⠀⠀⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡏⠀⠈⡆⠀
⠀⠀⠀⠀⠂⢱⡀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢧⠀⠀⢣⠀
⠀⠀⢡⠀⠀⠀⠑⢄⠠⠄⠀⡀⣀⣠⠔⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠘⡄
⠄⠀⠀⠂⠀⠀⠤⡈⠓⠶⠈⠙⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡀⠀⠀⣇
⠀⠀⠀⠀⠉⠀⠀⠐⠀⠀⠀⠀⠘⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⢻
```

## License

MIT. See [LICENSE](LICENSE).
