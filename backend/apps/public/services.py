"""US-12: bibliographic citation export for a published article."""

from apps.journal_settings.models import JournalSettings

GOST = "gost"
APA = "apa"
BIBTEX = "bibtex"
FORMATS = (GOST, APA, BIBTEX)


def _author_names(article):
    return [a.full_name for a in article.authors.all()]


def _pages_fragment(article, *, ru: bool) -> str:
    # No page-range field on Article (only a total pages_count) — approximate
    # with "С. N"/"pp. N" rather than a fabricated "start–end" range (see
    # plan decision #5).
    if not article.pages_count:
        return ""
    return f"С. {article.pages_count}" if ru else f"pp. {article.pages_count}"


def _build_gost(article) -> str:
    """ГОСТ Р 7.0.5-2008 — uses the Russian-language fields/journal name."""
    journal = JournalSettings.load()
    authors = ", ".join(_author_names(article))
    parts = [f"{authors} {article.title_ru}" if authors else article.title_ru]
    tail = f"// {journal.journal_name_ru}. — {article.published_at.year}."
    if article.issue_id:
        tail += f" — № {article.issue.number}."
    pages = _pages_fragment(article, ru=True)
    if pages:
        tail += f" — {pages}."
    if article.doi:
        tail += f" — DOI: {article.doi}."
    parts.append(tail)
    return " ".join(parts)


def _build_apa(article) -> str:
    """APA 7th ed. — uses the English-language fields/journal name."""
    journal = JournalSettings.load()
    authors = ", ".join(_author_names(article))
    year = article.published_at.year
    citation = f"{authors} ({year}). {article.title_en}. {journal.journal_name_en}"
    if article.issue_id:
        citation += f", {article.issue.number}"
    pages = _pages_fragment(article, ru=False)
    if pages:
        citation += f", {pages}"
    citation += "."
    if article.doi:
        citation += f" https://doi.org/{article.doi}"
    return citation


def _build_bibtex(article) -> str:
    journal = JournalSettings.load()
    authors = " and ".join(_author_names(article))
    citekey = f"vstu{article.published_at.year}{article.id.hex[:8]}"
    fields = {
        "author": authors,
        "title": article.title_en or article.title_ru,
        "journal": journal.journal_name_en or journal.journal_name_ru,
        "year": str(article.published_at.year),
    }
    if article.issue_id:
        fields["number"] = str(article.issue.number)
    if article.pages_count:
        fields["pages"] = str(article.pages_count)
    if article.doi:
        fields["doi"] = article.doi
    body = ",\n".join(f"  {key} = {{{value}}}" for key, value in fields.items())
    return f"@article{{{citekey},\n{body}\n}}"


_BUILDERS = {GOST: _build_gost, APA: _build_apa, BIBTEX: _build_bibtex}


def build_citation(article, fmt: str) -> str:
    if fmt not in _BUILDERS:
        raise ValueError("Неизвестный формат цитирования.")
    if not article.doi:
        raise ValueError("Ссылка формируется только для статей с присвоенным DOI.")
    return _BUILDERS[fmt](article)
