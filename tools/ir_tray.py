#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import subprocess
import time

import gi

gi.require_version(
    "Gtk",
    "3.0",
)

gi.require_version(
    "AyatanaAppIndicator3",
    "0.1",
)

from gi.repository import (  # noqa: E402
    AyatanaAppIndicator3 as AppIndicator,
)
from gi.repository import Gio, GLib, Gtk  # noqa: E402

SERVICE = "ir.service"
POLL_SECONDS = 2

ICON_DIR = "/home/ron/Проекты/ARGO/ARGO_MVP_0_1/assets/tray"

ICON_ON = "ir-on"


def wait_for_status_notifier_watcher(
    timeout_seconds: float = 15.0,
) -> bool:
    """Wait until Cinnamon's StatusNotifier watcher owns its D-Bus name."""
    try:
        bus = Gio.bus_get_sync(
            Gio.BusType.SESSION,
            None,
        )
    except GLib.Error:
        return False

    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        try:
            result = bus.call_sync(
                "org.freedesktop.DBus",
                "/org/freedesktop/DBus",
                "org.freedesktop.DBus",
                "NameHasOwner",
                GLib.Variant(
                    "(s)",
                    ("org.kde.StatusNotifierWatcher",),
                ),
                GLib.VariantType("(b)"),
                Gio.DBusCallFlags.NONE,
                1000,
                None,
            )

            if result.unpack()[0]:
                return True

        except GLib.Error:
            pass

        time.sleep(0.2)

    return False


def run_systemctl(
    *args: str,
) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            [
                "systemctl",
                "--user",
                *args,
                SERVICE,
            ],
            text=True,
            capture_output=True,
            timeout=10,
        )
    except (
        OSError,
        subprocess.TimeoutExpired,
    ):
        return None


def service_state(
    command: str,
    expected: str,
) -> bool:
    process = run_systemctl(command)

    return process is not None and process.stdout.strip() == expected


def notify(
    text: str,
) -> None:
    with contextlib.suppress(OSError, subprocess.TimeoutExpired):
        subprocess.run(
            [
                "notify-send",
                "--app-name=IR",
                "--expire-time=2500",
                "IR",
                text,
            ],
            check=False,
            timeout=5,
        )


class IRTray:
    def __init__(
        self,
    ) -> None:
        Gtk.IconTheme.get_default().append_search_path(ICON_DIR)

        self.indicator = AppIndicator.Indicator.new(
            "ir-tray",
            ICON_ON,
            AppIndicator.IndicatorCategory.APPLICATION_STATUS,
        )

        wait_for_status_notifier_watcher()

        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)

        self.indicator.set_title("IR")

        self.indicator.set_icon_theme_path(ICON_DIR)

        self.menu = Gtk.Menu()

        self.status_item = self._add_item(
            "IR: проверяю…",
            sensitive=False,
        )

        self.autostart_item = self._add_item(
            "Автозапуск: проверяю…",
            sensitive=False,
        )

        self.menu.append(Gtk.SeparatorMenuItem())

        self.start_item = self._add_action(
            "Включить IR",
            "start",
        )

        self.stop_item = self._add_action(
            "Выключить IR",
            "stop",
        )

        self.restart_item = self._add_action(
            "Перезапустить IR",
            "restart",
        )

        self.menu.append(Gtk.SeparatorMenuItem())

        self.enable_item = self._add_action(
            "Включить автозапуск",
            "enable",
        )

        self.disable_item = self._add_action(
            "Отключить автозапуск",
            "disable",
        )

        self.menu.append(Gtk.SeparatorMenuItem())

        self.menu.show_all()

        self.indicator.set_menu(self.menu)

        self.refresh()

        GLib.timeout_add_seconds(
            POLL_SECONDS,
            self.tick,
        )

    def _add_item(
        self,
        label: str,
        *,
        sensitive: bool = True,
    ):
        item = Gtk.MenuItem(label=label)

        item.set_sensitive(sensitive)

        self.menu.append(item)

        return item

    def _add_action(
        self,
        label: str,
        action: str,
    ):
        item = self._add_item(label)

        item.connect(
            "activate",
            self.service_action,
            action,
        )

        return item

    def refresh(
        self,
    ) -> None:
        active = service_state(
            "is-active",
            "active",
        )

        enabled = service_state(
            "is-enabled",
            "enabled",
        )

        self.indicator.set_icon_full(
            ICON_ON,
            "IR работает" if active else "IR выключена",
        )

        self.status_item.set_label("● IR: работает" if active else "○ IR: выключена")

        self.autostart_item.set_label("Автозапуск: включён" if enabled else "Автозапуск: выключен")

        self.start_item.set_sensitive(not active)

        self.stop_item.set_sensitive(active)

        self.restart_item.set_sensitive(active)

        self.enable_item.set_sensitive(not enabled)

        self.disable_item.set_sensitive(enabled)

    def tick(
        self,
    ) -> bool:
        self.refresh()
        return True

    def service_action(
        self,
        _item,
        action: str,
    ) -> None:
        process = run_systemctl(action)

        if process is None or process.returncode != 0:
            message = f"Не удалось выполнить: {action}"
        else:
            message = {
                "start": "IR включена",
                "stop": "IR выключена",
                "restart": "IR перезапускается",
                "enable": "Автозапуск IR включён",
                "disable": "Автозапуск IR отключён",
            }.get(action)

        if message:
            notify(message)

        GLib.timeout_add_seconds(
            1,
            self.refresh_once,
        )

    def refresh_once(
        self,
    ) -> bool:
        self.refresh()
        return False


IRTray()
Gtk.main()
