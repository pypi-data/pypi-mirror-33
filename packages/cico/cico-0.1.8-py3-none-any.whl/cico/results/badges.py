from anybadge import Badge as AnyBadge
import cairosvg

from .results import Result


class Badge(Result):
    def __init__(self, filename, png=False, **any_badge_kwargs):
        self.badge = AnyBadge(**any_badge_kwargs)
        self.filename = filename
        self.png = png

    def _to(self, dest):
        badge_path = dest / "{}.svg".format(self.filename)
        self.badge.write_badge(str(badge_path), overwrite=True)
        badges = [badge_path]
        if self.png:
            png_path = dest / "{}.png".format(self.filename)
            cairosvg.svg2png(url=str(badge_path), write_to=str(png_path))
            badges.append(png_path)
        return badges
