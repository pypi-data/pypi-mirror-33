from typing import Generic, TypeVar

from amino import do, Do, IO, List, Dat, Lists, ADT

from ribosome.config.setting import StrictSetting

A = TypeVar('A')


class DocMeta(Generic[A], ADT['DocMeta[A]']):
    pass


class Headline(Generic[A], DocMeta[A]):
    pass


class CustomDocMeta(Generic[A], DocMeta[A]):
    pass


class DocLine(Generic[A], Dat['DocLine']):

    @staticmethod
    def cons(
            text: str,
    ) -> 'DocLine':
        return DocLine(
            text,
        )

    def __init__(self, text: str) -> None:
        self.text = text


def setting_doc(setting: StrictSetting) -> IO[List[DocLine]]:
    return IO.pure((List(setting.desc) + Lists.lines(setting.help)).map(DocLine))


def settings_doc(settings: List[StrictSetting]) -> IO[List[DocLine]]:
    return settings.traverse(setting_doc, IO)


@do(IO[int])
def generate_doc(settings: List[StrictSetting]) -> Do:
    yield settings_doc(settings)


__all__ = ('generate_doc',)
