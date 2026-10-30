# terminalchat

A terminal client for [F-Chat](https://www.f-list.net/chat3/), the chat of f-list.net, built with [Textual](https://textual.textualize.io/).

Features:

- Public and private channels, private messages
- Channel browser with live search
- Sidebar with online friends and channel users
- BBCode rendering (bold, italic, colors, `[user]`, links, ...)
- Character names colored by gender
- Eicons shown as (animated) images directly in the chat
- Pinned chats that are restored on startup
- Console with global events and friends going online/offline
- Login screen and character switching
- Status and status message, remembered per character
- Input history (arrow keys)
- Local chat logs per character
- Respects `NO_COLOR`
- Keeps running in the background (`/minimize`, re-attach with `terminalchat`)

## Requirements

- Python 3.10 or newer
- tmux (optional, for running in the background). For sharp eicons inside the launcher's tmux session, tmux 3.4+ built with Sixel support is needed; otherwise eicons fall back to block graphics.
- A terminal with Sixel or Kitty graphics support for sharp eicons (e.g. Konsole, WezTerm, foot, Kitty, iTerm2). Other terminals fall back to coarse block graphics.

## Installation

```bash
git clone <repository-url> terminalchat
cd terminalchat
./setup.sh
```

`setup.sh` installs the system packages (tmux, Python with venv support) using your distribution's package manager (pacman, apt, dnf, zypper or Homebrew) after asking for confirmation, creates `venv/` and installs the Python requirements. It can be run again at any time, e.g. after a Python update broke the venv.

| Option | Description |
|---|---|
| `--skip-packages` | Only set up the Python environment |
| `--recreate-venv` | Delete and recreate `venv/` |
| `-y`, `--yes` | Do not ask before installing system packages |

Manual installation:

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

To start the client from anywhere, link the launcher into your `PATH`:

```bash
ln -s "$(pwd)/terminalchat" ~/.local/bin/terminalchat
```

## Running

```bash
terminalchat
```

The launcher runs the client inside its own [tmux](https://github.com/tmux/tmux) session (separate tmux server, so your own tmux setup is not touched). This allows the chat to keep running in the background:

- `/minimize` detaches your terminal; the client stays connected, keeps receiving messages and writing logs.
- Closing the terminal or losing the SSH connection has the same effect.
- Running `terminalchat` again re-attaches to the running session.
- `/quit` (or `ctrl+q`) ends the client and the session.

Without tmux installed the launcher starts the client in the foreground; `/minimize` is then unavailable.

To run the client directly without the launcher (e.g. for debugging, as error messages then stay visible):

```bash
venv/bin/python src/terminalchat.py
```

On the first start (or if account, password or character are missing) a login screen appears. Enter your f-list account and password, then pick a character. Check "Remember password" if the password should be stored in `config.json`.

## Commands

Type commands into the input line.

| Command | Description |
|---|---|
| `/join <channel>` | Join a channel by name or code (e.g. `/join Development`, `/join ADH-...`) |
| `/leave` | Leave or close the current chat (alias: `/close`) |
| `/priv <character>` | Open a private chat with an online character |
| `/invite <character>` | Invite a character into the current (private) channel; when you are invited, a notification shows how to join |
| `/me <text>` | Send an emote to the current chat |
| `/ad <text>` | Post a role play ad in the current channel. The server allows one ad per channel every few minutes (default 10); the client tells you how long to wait |
| `/roll [dice]` | Roll dice on the server, visible to everyone in the chat (e.g. `/roll 1d20`, `/roll 2d6+3`); default `1d6` |
| `/bottle` | Spin the bottle (channels only) |
| `/channels` | Open the channel browser |
| `/users` | Show or hide the sidebar with online friends and channel users |
| `/pin` | Pin the current chat; pinned chats are restored on startup |
| `/unpin` | Unpin the current chat |
| `/pins` | Show all pinned chats |
| `/status [status] [message]` | Set your status (`online`, `looking`, `busy`, `dnd`, `idle`, `away`) and an optional message (max. 255 characters). If the first word is not a status, the whole text becomes the message and the status is kept (`/status back in 5`); without arguments the current status is shown. The status is stored per character and restored after every login; `/status online` resets it |
| `/status:flag <status>` | Change only the status, keep the message |
| `/status:message [text]` | Change only the message, keep the status; without text the message is cleared |
| `/ads [on\|off]` | Show or hide ads (role play ads) in the current channel; hidden ads are still logged and reappear with `/ads on`. Stored per channel and character |
| `/gif [on\|off]` | Turn eicon animation on or off; without argument it toggles |
| `/char [name]` | Switch character; without a name a character picker opens |
| `/logout` | Disconnect, forget the stored password and show the login screen |
| `/minimize` | Detach and keep running in the background (alias: `/detach`, needs the launcher) |
| `/help` | Show the command list |
| `/quit` | Exit |

While typing a `/`, a list of matching commands with a short description appears above the input line. Press `tab` to complete the command as far as it is unambiguous.

Names and channel titles containing spaces work without quotes (`/priv Domenique Hunter`); quotes are accepted as well.

### Channel management

These commands act on the open channel. The server decides whether you are allowed to use them (channel owner or operator); if not, its error message is shown.

| Command | Description |
|---|---|
| `/code` | Copy the open channel as `[session=Title]code[/session]` link to the clipboard (also shown as notification) |
| `/makeroom <title>` | Create a private channel and open it (alias: `/create`) |
| `/openroom` | List the private channel publicly |
| `/closeroom` | Make the private channel invite-only again |
| `/kick <name>` | Kick a character |
| `/ban <name>` / `/unban <name>` | Ban / unban a character |
| `/banlist` | Show the ban list |
| `/timeout <name> <minutes>` | Time out a character |
| `/op <name>` / `/deop <name>` | Give / remove operator rights |
| `/setowner <name>` | Hand the channel over |
| `/setdescription <text>` | Set the channel description |
| `/setmode <chat\|ads\|both>` | Allow chat messages, ads or both |

Kicks, bans and timeouts announced by the server appear as system lines in the channel.

## Key bindings

| Key | Action |
|---|---|
| `ctrl+o` | Open the channel browser |
| `ctrl+l` | Leave / close the current chat |
| `ctrl+f` | Show or hide the sidebar (friends / channel users) |
| `ctrl+t` | Minimize: detach and keep running in the background (needs the launcher) |
| `enter` | Send the message |
| `shift+enter` / `ctrl+enter` / `ctrl+j` / `alt+enter` | New line in the message (multi-line messages, e.g. eicon grids). `shift+enter` and `ctrl+enter` only work in terminals that report it separately (e.g. kitty, WezTerm, foot); `ctrl+j` works everywhere |
| `up` / `down` | Move between lines; on the first / last line browse previously sent input |
| `tab` | Complete a command |
| `ctrl+p` | Command palette |
| `ctrl+q` | Quit |
| `escape` | Close a dialog |

The title bar shows your status and character (`Terminal Chat — looking — as <character>`). Click it to expand it and show your status message below; click again to collapse it.

In the chat list on the left, the console (`>`) is at the top, followed by channels (`#`) and private chats (`@`). A `*` marks unread messages, a `+` marks pinned chats.

Click a link to open it in your browser. When the client runs over SSH or without a graphical session, the link is copied to the clipboard instead (OSC 52; needs a terminal that supports it, e.g. Konsole, kitty, WezTerm) and shown as a notification.

The console collects global events: connection, server messages and errors, broadcasts, site events, invitations and friends going online or offline. It is read-only and cannot be closed. Channel related events (kicks, bans, timeouts, operator changes, channel notices) are shown in the affected channel instead.

The sidebar on the right has two tabs: *Friends* lists your friends that are online, *Channel* lists the users of the open channel (channel operators first, marked with `@`). It switches to the matching tab when you change chats. Press `enter` on a name to open a private chat. Status symbols: `+` looking, `•` online, `~` idle/away, `-` busy, `x` do not disturb.

## Configuration

The configuration is stored in `~/.config/terminalchat/config.json` and created on the first login. `src/config.json.example` shows all options:

| Option | Default | Description |
|---|---|---|
| `account` | `""` | f-list account name |
| `password` | `""` | Stored only if `remember_password` is `true` |
| `character` | `""` | Character to log in with |
| `remember_password` | `true` | Store the password in `config.json` |
| `default_channels` | `[]` | Channels joined on every start |
| `data_dir` | `~/.local/share/terminalchat` | Where logs and per-character data are stored |
| `show_sidebar` | `false` | Show the sidebar on startup |
| `show_ads` | `true` | Show ads in channels without an own `/ads` setting |
| `log_keep_days` | `0` | Delete daily log files older than this many days (including today); `0` keeps everything |
| `eicons` | `"inline"` | `"inline"` shows eicons as images, `"off"` shows them as `:name:` links |
| `eicon_height` | `4` | Eicon height in text lines |
| `eicon_animate` | `true` | Animate eicons on startup (see `/gif`) |
| `eicon_max_age_hours` | `24` | After this time cached eicons are checked for changes |
| `protocol`, `server`, `endpoint` | f-list chat server | Connection settings, usually left unchanged |

Colors can be adjusted in `src/color_config.py`, including the gender colors (`GENDER_STYLES`). Names with unknown gender keep the default color.

### Locations

The client follows the XDG base directory specification and respects `XDG_CONFIG_HOME`, `XDG_DATA_HOME` and `XDG_CACHE_HOME`.

| Purpose | Default | Override (highest priority first) |
|---|---|---|
| Configuration | `~/.config/terminalchat/config.json` | `TERMINALCHAT_CONFIG` |
| Data (logs, pins, status, ...) | `~/.local/share/terminalchat/` | `TERMINALCHAT_DATA`, then `data_dir` in the config |
| Cache (eicons) | `~/.cache/terminalchat/` | `XDG_CACHE_HOME` |

The console shows the paths in use on every start. When you change `data_dir`, existing data is not moved; move the folder yourself.

Older versions stored `config.json` and `chats/` inside `src/`. On the first start they are moved to the new locations automatically and the console reports it. If something already exists at the target, the old files are left untouched.

## Files

| Path | Content |
|---|---|
Paths below `<data>` refer to the data directory (default `~/.local/share/terminalchat`).

| Path | Content |
|---|---|
| `~/.config/terminalchat/config.json` | Configuration and credentials (permissions `600`) |
| `<data>/chats/<character>/<name>/YYYY-MM-DD.log` | Private chat logs, one file per day |
| `<data>/chats/<character>/channels/<code>/YYYY-MM-DD.log` | Channel logs, one file per day |
| `<data>/chats/<character>/_console/YYYY-MM-DD.log` | Console history, one file per day |
| `<data>/chats/<character>/pins.json` | Pinned chats |
| `<data>/chats/<character>/status.json` | Your status and status message |
| `<data>/chats/<character>/ads.json` | Per-channel ad visibility |
| `<data>/chats/genders.json` | Known genders of other characters, used for name colors |
| `<data>/debug.log` | Debug output |
| `~/.cache/terminalchat/eicons/` | Eicon cache |
| `tmux.conf` | Settings for the launcher's tmux server |

Older single-file logs (`chat.log`, `console.log`) are split into daily files automatically the first time a chat is opened; the original is kept as `chat.log.bak` / `console.log.bak` and can be deleted afterwards.

## Security note

If "Remember password" is enabled, the password is stored in plain text in `~/.config/terminalchat/config.json`. The file is created with permissions `600` (readable only by you).

## Disabling colors

Set the `NO_COLOR` environment variable to remove all colors. Bold, italic and underline are kept:

```bash
NO_COLOR=1 ./terminalchat
```
