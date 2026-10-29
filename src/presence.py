from typing import Callable


FRIENDS = "friends"


class Presence:

    def __init__(self, on_change:Callable[[str], None]) -> None:
        self.on_change = on_change
        self.online: dict[str, str] = {}
        self.status: dict[str, str] = {}
        self.friends: set[str] = set()
        self.members: dict[str, dict[str, str]] = {}
        self.ops: dict[str, set[str]] = {}

    def _changed_for(self, key:str) -> None:
        if key in self.friends:
            self.on_change(FRIENDS)
        for code, members in self.members.items():
            if key in members:
                self.on_change(code)

    def set_online(self, name:str, status:str="online") -> None:
        key = name.lower()
        self.online[key] = name
        self.status[key] = status or "online"
        self._changed_for(key)

    def set_offline(self, name:str) -> None:
        key = name.lower()
        self.online.pop(key, None)
        self.status.pop(key, None)
        self._changed_for(key)
        for members in self.members.values():
            members.pop(key, None)

    def set_status(self, name:str, status:str) -> None:
        key = name.lower()
        if key in self.online:
            self.status[key] = status or "online"
            self._changed_for(key)

    def find_online(self, name:str) -> str | None:
        return self.online.get(name.strip().lower())

    def set_friends(self, names:list[str]) -> None:
        self.friends = {name.lower() for name in names}
        self.on_change(FRIENDS)

    def _ensure_online(self, name:str) -> None:
        key = name.lower()
        if key not in self.online:
            self.online[key] = name
            self.status.setdefault(key, "online")

    def set_members(self, code:str, names:list[str]) -> None:
        for name in names:
            self._ensure_online(name)
        self.members[code] = {name.lower(): name for name in names}
        self.on_change(code)

    def add_member(self, code:str, name:str) -> None:
        self._ensure_online(name)
        self.members.setdefault(code, {})[name.lower()] = name
        self.on_change(code)

    def remove_member(self, code:str, name:str) -> None:
        if self.members.get(code, {}).pop(name.lower(), None) is not None:
            self.on_change(code)

    def drop_channel(self, code:str) -> None:
        self.members.pop(code, None)
        self.ops.pop(code, None)
        self.on_change(code)

    def set_ops(self, code:str, names:list[str]) -> None:
        self.ops[code] = {name.lower() for name in names if name}
        self.on_change(code)

    def add_op(self, code:str, name:str) -> None:
        self.ops.setdefault(code, set()).add(name.lower())
        self.on_change(code)

    def remove_op(self, code:str, name:str) -> None:
        self.ops.get(code, set()).discard(name.lower())
        self.on_change(code)

    def online_friends(self) -> list[tuple[str, str, bool]]:
        entries = [(self.online[key], self.status.get(key, "online"), False) for key in self.friends if key in self.online]
        return sorted(entries, key=lambda entry: entry[0].lower())

    def channel_members(self, code:str) -> list[tuple[str, str, bool]] | None:
        if code not in self.members:
            return None
        ops = self.ops.get(code, set())
        entries = [(name, self.status.get(key, "online"), key in ops) for key, name in self.members[code].items()]
        return sorted(entries, key=lambda entry: (not entry[2], entry[0].lower()))


def main() -> None:
    presence = Presence(lambda key: print("changed:", key))
    presence.set_friends(["Alice"])
    presence.set_online("Alice", "looking")
    presence.set_members("Development", ["Alice", "Bob"])
    presence.set_ops("Development", ["Bob"])
    print(presence.online_friends(), presence.channel_members("Development"))


if __name__ == "__main__":
    main()
