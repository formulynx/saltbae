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

## AI attribution

Commits from `/saltbae` follow Claude Code's `attribution` setting. When it is
unset, Claude Code appends its default `Co-Authored-By` trailer. An empty
string hides the attribution, and any other string replaces it.

Add `attribution` as a top-level key, next to your existing settings,
in `~/.claude/settings.json` for all projects or in `.claude/settings.json`
for one project:

```jsonc
{
  "permissions": { ... },  // your existing settings stay as they are
  "model": "...",
  "attribution": {
    "commit": "",
    "pr": ""
  }
}
```

Mind the comma after the key that precedes `attribution`. See the
[Claude Code settings docs](https://code.claude.com/docs/en/settings) for details.

## Install

saltbae ships as a Claude Code plugin. Add the marketplace once, then install:

```sh
claude plugin marketplace add formulynx/saltbae
claude plugin install saltbae@saltbae
```

- Uninstall with `claude plugin uninstall saltbae@saltbae`
- For dev, `claude plugin marketplace add /path/to/clone` and install from
  there, or run `claude --plugin-dir /path/to/clone`
- Update with `/plugin` -> marketplace -> `saltbae` -> `Update marketplace` or `Enable auto-update`

## Why "saltbae"?

Named for the meme chef's dramatic tableside cut and salt flourish.  
Without a proper cut (splitting the diff into logical commits) and seasoning (a clear commit log),
a reviewer can't chew through the change despite your tireless effort.  
You focus on the code, `/saltbae` handles the plating.

🔥🥩 [`/grilling`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling) 
stress-tests a plan before anything is built. (Thanks to Matt Pocock) 
🍽️🍖 `/saltbae` picks up once the changes exist, carving and seasoning them into a reviewable history.

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

MIT / See [LICENSE](LICENSE)
