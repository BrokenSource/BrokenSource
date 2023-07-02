from Broken import *


class BrokenSmart:
    def load_image(image: Union[PilImage, PathLike, URL], pixel="RGB", cache=True, echo=True) -> Option[PilImage, None]:
        """Smartly load 'SomeImage', a path, url or PIL Image"""

        # Nothing to do if already a PIL Image
        if isinstance(image, PilImage):
            return image

        try:
            # Load image if a path or url is supplied
            if any([isinstance(image, T) for T in (PathLike, str)]):
                if (path := true_path(image)).exists():
                    info(f"Loading image from path [{path}]", echo=echo)
                    return PIL.Image.open(path).convert(pixel)
                else:
                    info(f"Loading image from (maybe) url [{image}]", echo=echo)
                    try:
                        requests = BROKEN_REQUESTS_CACHE if cache else requests
                        return PIL.Image.open(BytesIO(requests.get(image).content)).convert(pixel)
                    except Exception as e:
                        error(f"Failed to load image from url [{image}]: {e}", echo=echo)
                        return None
            else:
                error(f"Unknown image parameter [{image}], must be a PIL Image, Path or URL", echo=echo)
                return None

        # Can't open file
        except PIL.UnidentifiedImageError as e:
            error(f"Failed to load image [{image}]: {e}", echo=echo)
            return None

        except Exception:
            return None