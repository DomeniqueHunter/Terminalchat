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

To run the client directly without the launcher, start it from inside `src/`, because `config.json`, logs and chat history are read relative to the working directory:

```bash
cd src
python3 terminalchat.py
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
| `/gif [on\|off]` | Turn eicon animation on or off; without argument it toggles |
| `/char [name]` | Switch character; without a name a character picker opens |
| `/logout` | Disconnect, forget the stored password and show the login screen |
| `/minimize` | Detach and keep running in the background (alias: `/detach`, needs the launcher) |
| `/help` | Show the command list |
| `/quit` | Exit |

While typing a `/`, a list of matching commands with a short description appears above the input line. The best match is suggested in grey: press `→` to accept it, or `tab` to complete the command as far as it is unambiguous.

Names and channel titles containing spaces work without quotes (`/priv Domenique Hunter`); quotes are accepted as well.

### Channel management

These commands act on the open channel. The server decides whether you are allowed to use them (channel owner or operator); if not, its error message is shown.

| Command | Description |
|---|---|
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
| `up` / `down` | Browse previously sent input |
| `ctrl+p` | Command palette |
| `ctrl+q` | Quit |
| `escape` | Close a dialog |

The title bar shows your status and character (`Terminal Chat — looking — as <character>`). Click it to expand it and show your status message below; click again to collapse it.

In the chat list on the left, channels (`#`) are listed above private chats (`@`). A `*` marks unread messages, a `+` marks pinned chats.

The sidebar on the right has two tabs: *Friends* lists your friends that are online, *Channel* lists the users of the open channel (channel operators first, marked with `@`). It switches to the matching tab when you change chats. Press `enter` on a name to open a private chat. Status symbols: `+` looking, `•` online, `~` idle/away, `-` busy, `x` do not disturb.

## Configuration

`src/config.json` is created on the first login. `src/config.json.example` shows all options:

| Option | Default | Description |
|---|---|---|
| `account` | `""` | f-list account name |
| `password` | `""` | Stored only if `remember_password` is `true` |
| `character` | `""` | Character to log in with |
| `remember_password` | `true` | Store the password in `config.json` |
| `default_channels` | `[]` | Channels joined on every start |
| `show_sidebar` | `false` | Show the sidebar on startup |
| `eicons` | `"inline"` | `"inline"` shows eicons as images, `"off"` shows them as `:name:` links |
| `eicon_height` | `4` | Eicon height in text lines |
| `eicon_animate` | `true` | Animate eicons on startup (see `/gif`) |
| `eicon_max_age_hours` | `24` | After this time cached eicons are checked for changes |
| `protocol`, `server`, `endpoint` | f-list chat server | Connection settings, usually left unchanged |

Colors can be adjusted in `src/color_config.py`, including the gender colors (`GENDER_STYLES`). Names with unknown gender keep the default color.

## Files

| Path | Content |
|---|---|
| `src/config.json` | Configuration and credentials (permissions `600`) |
| `src/chats/<character>/` | Chat logs per character, private chats and `channels/` |
| `src/chats/<character>/pins.json` | Pinned chats |
| `src/chats/<character>/status.json` | Your status and status message |
| `src/chats/genders.json` | Known genders of other characters, used for name colors |
| `~/.cache/terminalchat/eicons/` | Eicon cache (respects `XDG_CACHE_HOME`) |
| `src/debug.log` | Debug output |
| `tmux.conf` | Settings for the launcher's tmux server |

## Security note

If "Remember password" is enabled, the password is stored in plain text in `config.json`. The file is created with permissions `600` (readable only by you). Do not commit it; it is listed in `.gitignore`.

## Disabling colors

Set the `NO_COLOR` environment variable to remove all colors. Bold, italic and underline are kept:

```bash
NO_COLOR=1 python3 terminalchat.py
```
