from kwiq.core.app import App

from translate_non_english_code.apply_translation import ApplyTranslation
from translate_non_english_code.prepare_translation import PrepareForTranslation
from translate_non_english_code.translate import Translate


def main():
    app = App(name="translate-non-english-code")
    app.register_flow(ApplyTranslation())
    app.register_flow(PrepareForTranslation())
    app.register_flow(Translate())

    app.main()


if __name__ == '__main__':
    main()
