from __future__ import annotations


class Forbidden(Exception):
    pass


class HTTPException(Exception):
    pass


class NotFound(Exception):
    pass


class _FakeEmbedPart:
    def __init__(self, **attrs: object) -> None:
        for key, val in attrs.items():
            setattr(self, key, val)


class FakeEmbed:
    def __init__(
        self,
        *,
        title: str | None = None,
        description: str | None = None,
        url: str | None = None,
        colour: int | None = None,
        color: int | None = None,
        timestamp: object = None,
    ) -> None:
        self.title = title
        self.description = description
        self.url = url
        self.colour = colour if colour is not None else color
        self.color = self.colour
        self.timestamp = timestamp
        self.fields: list[_FakeEmbedPart] = []
        self.footer = _FakeEmbedPart(text="", icon_url=None)
        self.image = _FakeEmbedPart(url="")
        self.thumbnail = _FakeEmbedPart(url="")
        self.author: _FakeEmbedPart | None = None

    def set_footer(self, *, text: str | None = None, icon_url: str | None = None) -> None:
        self.footer = _FakeEmbedPart(text=text or "", icon_url=icon_url)

    def set_image(self, *, url: str | None = None) -> None:
        self.image = _FakeEmbedPart(url=url or "")

    def set_thumbnail(self, *, url: str | None = None) -> None:
        self.thumbnail = _FakeEmbedPart(url=url or "")

    def set_author(self, *, name: str | None = None, url: str | None = None, icon_url: str | None = None) -> None:
        self.author = _FakeEmbedPart(name=name, url=url, icon_url=icon_url)

    def add_field(self, *, name: str, value: str, inline: bool = False) -> None:
        self.fields.append(_FakeEmbedPart(name=name, value=value, inline=inline))

    def set_field_at(self, index: int, *, name: str, value: str, inline: bool = False) -> None:
        self.fields[index] = _FakeEmbedPart(name=name, value=value, inline=inline)

    def remove_field(self, index: int) -> None:
        del self.fields[index]
