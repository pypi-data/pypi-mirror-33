import enum


class SIZE(enum.Enum):
    X_SMALL = "X_SMALL"
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"
    X_LARGE = "X_LARGE"


class ImageSource(object):

    def __init__(self, url, size=None, width_pixels=None, height_pixels=None):
        if not url:
            raise ValueError('"url" must not be None.')
        self.url = url
        self.size = size
        if self.size:
            self.size = SIZE(self.size)
        self.width_pixels = width_pixels
        self.heigh_pixels = height_pixels

    def prepare(self):
        source = {'url': self.url}
        if self.size:
            source['size'] = self.size.value
        if self.width_pixels and self.heigh_pixels:
            source['widthPixels'] = self.width_pixels
            source['heightPixels'] = self.heigh_pixels
        return source

class Image(object):

    def __init__(self, content_description, sources=None):
        self.content_description = content_description
        self.sources = []
        if sources:
            self.sources.extend(sources)

    def add_source(self, url, size=None, width_pixels=None, height_pixels=None):
        self.sources.append(ImageSource(url=url, size=size, width_pixels=width_pixels, height_pixels=height_pixels))
        return self

    def with_source(self, source):
        if source:
            self.sources.append(source)
        return self

    def prepare(self):
        if not self.sources:
            raise RuntimeError('No sources for image.')
        return {
            'contentDescription': self.content_description,
            'sources': [s.prepare() for s in self.sources]
        }
