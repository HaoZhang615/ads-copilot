import base64
import re


# Abbreviations that should not trigger sentence splits
_ABBREVIATIONS = re.compile(
    r"\b(?:Mr|Mrs|Ms|Dr|Prof|Sr|Jr|Inc|Ltd|Corp|etc|vs|approx|dept|est|govt|vol)\.$",
    re.IGNORECASE,
)

_ELLIPSIS = re.compile(r"\.{2,}")


def detect_sentence_boundaries(text: str) -> list[str]:
    """Split text on sentence-ending punctuation while respecting abbreviations and ellipsis."""
    sentences: list[str] = []
    current: list[str] = []

    i = 0
    chars = list(text)
    length = len(chars)

    while i < length:
        char = chars[i]
        current.append(char)

        if char in ".?!":
            current_text = "".join(current)

            if char == "." and _ELLIPSIS.search(current_text):
                i += 1
                continue

            if char == "." and _ABBREVIATIONS.search(current_text):
                i += 1
                continue

            is_end = (i + 1 >= length) or (i + 1 < length and chars[i + 1] == " ")

            if is_end:
                sentence = current_text.strip()
                if sentence:
                    sentences.append(sentence)
                current = []
                if i + 1 < length and chars[i + 1] == " ":
                    i += 1

        i += 1

    remainder = "".join(current).strip()
    if remainder:
        sentences.append(remainder)

    return sentences


def base64_encode_audio(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def base64_decode_audio(data: str) -> bytes:
    return base64.b64decode(data)
