from pyi18n import PyI18n

# Guild Locale on startup, should be guild_local[guild_id] = lang
guild_locale = {}
available_locales = ('en', 'ja')
default_locale = 'en'

class Locale:
    _instance = None
    _locale = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            i18n: PyI18n = PyI18n(available_locales=available_locales)
            cls._locale = i18n.gettext

        return cls._instance

    def get_text(self, guild_id: int, string: str, **kwargs) -> str:
        lang = guild_locale.get(guild_id, default_locale)
        return self._instance._locale(lang, string, **kwargs)

    def t(self, guild_id: int, string: str, **kwargs) -> str:
        lang = guild_locale.get(guild_id, default_locale)
        return self._instance._locale(lang, string, **kwargs)
