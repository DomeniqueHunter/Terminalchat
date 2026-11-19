const log = () => document.getElementById("log");
const root = document.documentElement;

function store(key, value) {
  try {
    if (value === undefined) return localStorage.getItem(key);
    localStorage.setItem(key, value);
  } catch (e) { return null; }
}

const CHARACTER_TABS = ["character", "inventory", "family", "mail",
  "contacts", "settings"];

function showTab(name) {
  const group = CHARACTER_TABS.includes(name);
  document.querySelectorAll("#tabs button").forEach(
    (button) => button.classList.toggle(
      "on", button.dataset.tab === (group ? "character" : name)));
  document.querySelectorAll("#subtabs button").forEach(
    (button) => button.classList.toggle("on", button.dataset.tab === name));
  document.getElementById("subtabs").hidden = !group;
  document.querySelectorAll(".tab").forEach(
    (tab) => tab.classList.toggle("on", tab.id === `tab-${name}`));
  store("tab", name);
  if (group) store("sub", name);
}

function setTheme(name) {
  root.dataset.theme = name;
  store("theme", name);
  const label = name === "dark" ? "Light mode" : "Dark mode";
  document.getElementById("theme-button").textContent = label;
}

function toggleTheme() {
  setTheme(root.dataset.theme === "dark" ? "light" : "dark");
}

document.getElementById("tabs").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-tab]");
  if (!button) return;
  const name = button.dataset.tab;
  showTab(name === "character" ? store("sub") || name : name);
});
document.getElementById("subtabs").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-tab]");
  if (button) showTab(button.dataset.tab);
});
document.getElementById("theme-button").addEventListener("click", toggleTheme);
document.getElementById("theme-setting").addEventListener("click", toggleTheme);
const clear = document.getElementById("clear-log");
if (clear) clear.addEventListener("click", () => { log().innerHTML = ""; });

document.body.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-fill]");
  if (!button) return;
  const input = document.getElementById("say-input");
  input.value = button.dataset.fill;
  input.focus();
});

document.body.addEventListener("htmx:oobAfterSwap", () => {
  const box = log();
  if (box) box.scrollTop = box.scrollHeight;
});

document.body.addEventListener("htmx:wsAfterSend", () => {
  const input = document.getElementById("say-input");
  if (input && document.activeElement !== null
      && (document.activeElement === input
          || document.activeElement.id === "send")) {
    input.value = "";
  }
});

const kept = {};

function remember(event) {
  const box = event.target.closest("[data-keep]");
  if (box) kept[box.dataset.keep] = event.target.value;
}

document.body.addEventListener("change", remember);
document.body.addEventListener("input", remember);

function restoreChoices() {
  document.querySelectorAll("[data-keep]").forEach((box) => {
    const value = kept[box.dataset.keep];
    if (value === undefined) return;
    box.querySelectorAll("input, select, textarea").forEach((input) => {
      if (input.type === "radio") input.checked = input.value === value;
      else input.value = value;
    });
  });
}

document.body.addEventListener("htmx:oobAfterSwap", restoreChoices);

const MAIL_FIELDS = ["mail_subject", "mail_body", "mail_gold", "mail_item"];

document.addEventListener("click", (event) => {
  const button = event.target.closest("#tab-mail button");
  if (!button || button.textContent.trim() !== "Send") return;
  if (!kept.mail_subject || !kept.mail_body) return;
  setTimeout(() => MAIL_FIELDS.forEach((name) => delete kept[name]), 50);
});

document.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-arm]");
  if (!button) return;
  if (button.dataset.armed === "1") return;
  event.stopPropagation();
  event.preventDefault();
  button.dataset.armed = "1";
  button.dataset.label = button.textContent;
  button.textContent = button.dataset.arm;
  setTimeout(() => {
    button.dataset.armed = "";
    button.textContent = button.dataset.label;
  }, 5000);
}, true);

const paneOf = {};

function showPane(box, index) {
  box.querySelectorAll(":scope > .strip > button").forEach(
    (button, i) => button.classList.toggle("on", i === index));
  box.querySelectorAll(":scope > .pane").forEach(
    (pane, i) => pane.classList.toggle("on", i === index));
}

document.body.addEventListener("click", (event) => {
  const button = event.target.closest(".strip > button[data-pane]");
  if (!button) return;
  const box = button.closest(".subtabs");
  const index = Number(button.dataset.pane);
  paneOf[box.dataset.tabs] = index;
  showPane(box, index);
});

function restorePanes() {
  document.querySelectorAll(".subtabs").forEach((box) => {
    const index = paneOf[box.dataset.tabs];
    if (index !== undefined) showPane(box, index);
  });
}

document.body.addEventListener("htmx:oobAfterSwap", restorePanes);

const shown = {};

function watchTabs() {
  ["visit", "sex"].forEach((name) => {
    const button = document.getElementById(`tabbtn-${name}`);
    if (!button) return;
    const visible = !button.hidden;
    if (visible && !shown[name]) showTab(name);
    if (!visible && shown[name] && store("tab") === name) {
      showTab("character");
    }
    shown[name] = visible;
  });
  const shop = Boolean(document.getElementById("run-shop"));
  if (shop && !shown.shop) showTab("location");
  shown.shop = shop;
}

document.body.addEventListener("htmx:oobAfterSwap", watchTabs);

setTheme(root.dataset.theme || "dark");
showTab(store("tab") || "character");

(function () {
  var button = document.getElementById("logout");
  if (button) {
    button.addEventListener("click", function () {
      fetch("/logout", {method: "POST"}).then(function () {
        window.location.href = "/";
      });
    });
  }
})();

(function () {
  const dialog = document.getElementById("create-dialog");
  if (!dialog) return;
  const HUNG = ["Male", "Herm", "Shemale", "Male-Herm", "Transgender"];
  const field = (name) => dialog.querySelector(`[name="${name}"]`);

  function syncHung() {
    const gender = field("cf_gender").value;
    document.getElementById("cf-hung").hidden = !HUNG.includes(gender);
  }

  function refresh() {
    syncHung();
    htmx.trigger(document.getElementById("cf-fields"), "change");
  }

  document.getElementById("new-character").addEventListener("click", () => {
    dialog.showModal();
    refresh();
  });
  document.getElementById("cf-cancel").addEventListener(
    "click", () => dialog.close());
  dialog.addEventListener("change", (event) => {
    if (event.target.id === "cf-gender") syncHung();
  });
  dialog.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-for]");
    if (!button) return;
    const input = field(button.dataset.for);
    input.value = Math.max(0, Number(input.value || 0) + Number(button.dataset.step));
    htmx.trigger(document.getElementById("cf-fields"), "change");
  });
  document.body.addEventListener("htmx:oobAfterSwap", () => {
    const done = document.querySelector("#cf-close[data-done]");
    if (done) {
      done.removeAttribute("data-done");
      dialog.close();
    }
  });
})();

(function () {
  document.body.addEventListener("htmx:oobAfterSwap", () => {
    const marker = document.getElementById("cf-invalid");
    const dialog = document.getElementById("create-dialog");
    if (!marker || !dialog) return;
    const bad = (marker.dataset.fields || "").split(",");
    dialog.querySelectorAll("input, select, textarea").forEach((item) => {
      item.classList.toggle("invalid", bad.includes(item.name));
    });
  });
})();

(function () {
  const input = document.getElementById("say-input");
  if (!input) return;
  const KEY = "history";
  const LIMIT = 50;
  let position = -1;
  let draft = "";

  function load() {
    try { return JSON.parse(store(KEY) || "[]"); } catch (e) { return []; }
  }

  function remember(text) {
    text = text.trim();
    position = -1;
    if (!text) return;
    const items = load();
    if (items[items.length - 1] === text) return;
    items.push(text);
    store(KEY, JSON.stringify(items.slice(-LIMIT)));
  }

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") { remember(input.value); return; }
    if (event.key !== "ArrowUp" && event.key !== "ArrowDown") return;
    const items = load();
    if (!items.length) return;
    event.preventDefault();
    if (position === -1) draft = input.value;
    if (event.key === "ArrowUp") {
      position = position === -1 ? items.length - 1 : Math.max(0, position - 1);
    } else if (position !== -1) {
      position += 1;
      if (position >= items.length) position = -1;
    }
    input.value = position === -1 ? draft : items[position];
  });
  document.getElementById("send").addEventListener(
    "click", () => remember(input.value));
})();

(function () {
  const clock = () => document.getElementById("world-clock");

  function pad(value) { return String(value).padStart(2, "0"); }

  function draw() {
    const el = clock();
    if (!el || el.dataset.day === undefined) return;
    if (!el.dataset.at) el.dataset.at = Date.now();
    const length = Number(el.dataset.length) || 3600;
    const seconds = Number(el.dataset.elapsed)
      + (Date.now() - Number(el.dataset.at)) / 1000;
    const day = Number(el.dataset.day) + Math.floor(seconds / length);
    const minutes = Math.floor(((seconds % length) / length) * 1440);
    const hour = Math.floor(minutes / 60);
    const icon = hour >= 6 && hour < 18 ? "☀" : "🌙";
    const yearDays = Number(el.dataset.yearDays) || 365;
    const names = (el.dataset.weekdays || "").split(",");
    const weekday = names[day % names.length] || "";
    const dayOfYear = (day % yearDays) + 1;
    const year = Math.floor(day / yearDays) + 1;
    el.textContent = `${icon} ${weekday} · Day ${dayOfYear}, Year ${year}`
      + ` · ${pad(hour)}:${pad(minutes % 60)}`;
  }

  document.body.addEventListener("htmx:oobAfterSwap", (event) => {
    const el = event.target;
    if (el && el.id === "world-clock") {
      el.dataset.at = Date.now();
      draw();
    }
  });
  setInterval(draw, 1000);
})();

(function () {
  const KEYS = {h: "!hit", c: "!cast", f: "!force", d: "!dodge", g: "!guard",
                p: "!potion", e: "!enter"};

  document.addEventListener("keydown", (event) => {
    if (event.ctrlKey || event.altKey || event.metaKey) return;
    const active = document.activeElement;
    if (active && /^(INPUT|SELECT|TEXTAREA)$/.test(active.tagName)) return;
    const command = KEYS[event.key.toLowerCase()];
    if (!command) return;
    const button = document.querySelector(
      `button[hx-vals*='"${command}"']:not([disabled])`);
    if (!button) return;
    event.preventDefault();
    button.click();
  });
})();

document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  const close = document.getElementById("house-close")
    || document.getElementById("stash-close")
    || document.getElementById("lobby-close");
  if (close) close.click();
});

document.body.addEventListener("click", (event) => {
  const closers = {"lobby-backdrop": "lobby-close",
                   "stash-backdrop": "stash-close",
                   "house-backdrop": "house-close"};
  const target = closers[event.target.id];
  if (!target) return;
  const close = document.getElementById(target);
  if (close) close.click();
});

(function () {
  const input = document.getElementById("say-input");
  let cycle = null;

  function names() {
    const box = document.getElementById("w-names");
    try { return JSON.parse(box.dataset.names || "[]"); } catch (e) { return []; }
  }

  function matches(fragment) {
    const wanted = fragment.toLowerCase();
    const all = names();
    const starts = all.filter((n) => n.toLowerCase().startsWith(wanted));
    const words = all.filter((n) => !starts.includes(n)
      && n.toLowerCase().split(" ").some((w) => w.startsWith(wanted)));
    return [...starts, ...words];
  }

  input.addEventListener("keydown", (event) => {
    if (event.key !== "Tab" || event.shiftKey) return;
    const found = /^(!w\s+)([^:]*)$/i.exec(input.value);
    if (!found && !cycle) return;
    if (cycle && input.value !== cycle.shown) cycle = null;
    if (!cycle) {
      if (!found) return;
      const list = matches(found[2].trim());
      if (!list.length) return;
      cycle = {prefix: found[1], list, index: -1, shown: ""};
    }
    event.preventDefault();
    cycle.index = (cycle.index + 1) % cycle.list.length;
    cycle.shown = `${cycle.prefix}${cycle.list[cycle.index]}: `;
    input.value = cycle.shown;
  });

  input.addEventListener("input", () => {
    if (cycle && input.value !== cycle.shown) cycle = null;
  });
})();
