import sys

import questionary
from rich import box
from rich.console import Console
from rich.panel import Panel

from engine.parser import (
    get_session,
    get_subjects,
    get_categories,
    get_exam_links,
    get_pdf_url,
    normalize_year_filter,
)
from engine.downloader import download_pdf, build_dest_folder
from utils.arabic_display import configure_console_encoding, display_prompt, display_text
from utils.translator import LEVELS
from utils.logger import log

console = Console()


class UserAbortError(Exception):
    """Raised when the user aborts an interactive prompt."""


def _show_header():
    title = display_text("DZExams Scraper")
    subtitle = display_text("Telecharger tous les devoirs et examens / تحميل جميع الفروض والاختبارات")
    panel = Panel(
        f"[bold cyan]{title}[/bold cyan]\n[white]{subtitle}[/white]",
        box=box.ROUNDED,
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel)


def _show_error(message):
    console.print(f"[bold red]{display_text('Erreur / خطأ:')}[/bold red] [red]{display_text(message)}[/red]")


def _show_warning(message):
    console.print(f"[bold yellow]{display_text('Avertissement / تنبيه:')}[/bold yellow] [yellow]{display_text(message)}[/yellow]")


def _show_info(message):
    console.print(f"[bold blue]{display_text('Info / معلومات:')}[/bold blue] [white]{display_text(message)}[/white]")


def _select(options, label):
    if not options:
        raise ValueError("Aucune option disponible / لا توجد خيارات متاحة")

    rendered = [display_text(str(opt)) for opt in options]
    answer = questionary.select(
        message=display_text(label),
        choices=rendered,
        qmark="",
        use_indicator=True,
        style=questionary.Style(
            [
                ("pointer", "fg:#00AEEF bold"),
                ("highlighted", "fg:#00AEEF bold"),
                ("question", "fg:#E2E8F0 bold"),
                ("answer", "fg:#10B981 bold"),
            ]
        ),
    ).ask()

    if answer is None:
        raise UserAbortError

    return rendered.index(answer)


def _ask_text(prompt, default=None):
    message = display_text(prompt)
    if default is not None:
        message = f"{message} [{default}]"

    answer = questionary.text(
        message=message,
        default=default or "",
        qmark="",
    ).ask()

    if answer is None:
        raise UserAbortError

    value = answer.strip()
    return value if value else default


def _ask_confirm(prompt, default=True):
    yes_label = display_text("Oui / نعم")
    no_label = display_text("Non / لا")
    choices = [yes_label, no_label] if default else [no_label, yes_label]

    answer = questionary.select(
        message=display_text(prompt),
        choices=choices,
        qmark="",
        use_indicator=True,
        style=questionary.Style(
            [
                ("pointer", "fg:#00AEEF bold"),
                ("highlighted", "fg:#00AEEF bold"),
                ("question", "fg:#E2E8F0 bold"),
                ("answer", "fg:#10B981 bold"),
            ]
        ),
    ).ask()

    if answer is None:
        raise UserAbortError
    return answer == yes_label


def _ask_download_limit(prompt, default=1):
    while True:
        value = _ask_text(prompt, default=str(default))
        if not value:
            return default

        lowered = value.strip().lower()
        if lowered in ("tous", "tout", "all", "*"):
            return None

        if value.isdigit() and int(value) > 0:
            return int(value)
        _show_warning("Entrez un nombre (>0) ou 'tous' pour tout telecharger / ادخل رقما صحيحا او 'tous' لتحميل الكل")


def _ask_year_filter(prompt):
    while True:
        value = _ask_text(prompt)
        if not value:
            return None
        try:
            normalize_year_filter(value)
            return value
        except ValueError as exc:
            _show_warning(str(exc))


def _get_exam_links_with_retries(session, level_code, subject_slug, category_code, year_filter, limit, max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        exams = get_exam_links(session, level_code, subject_slug, category_code, year_filter, limit)
        if exams:
            return exams
        if attempt < max_attempts:
            _show_warning(f"Aucun sujet trouve, nouvelle tentative ({attempt}/{max_attempts}) / لم يتم العثور على مواضيع، إعادة المحاولة")
    return []


def _get_pdf_url_with_retries(session, exam_url, max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        pdf_url = get_pdf_url(session, exam_url)
        if pdf_url:
            return pdf_url
        if attempt < max_attempts:
            _show_warning(f"Lien PDF introuvable, nouvelle tentative ({attempt}/{max_attempts}) / رابط PDF غير موجود، إعادة المحاولة")
    return None


def main():
    configure_console_encoding()
    _show_header()

    session = get_session()

    while True:
        stage_names = list(LEVELS.keys())
        stage_idx = _select(stage_names, "Choisissez le niveau scolaire / اختر المرحلة الدراسية")
        stage = stage_names[stage_idx]

        year_names = list(LEVELS[stage].keys())
        year_idx = _select(year_names, "Choisissez l'annee scolaire / اختر السنة")
        level_code = LEVELS[stage][year_names[year_idx]]

        _show_info(f"Chargement des matieres pour {level_code}... / تحميل المواد")
        subjects = get_subjects(session, level_code)

        if not subjects:
            _show_error("Aucune matiere trouvee / لم يتم العثور على مواد")
            if _ask_confirm("Reessayer ? / هل تريد المحاولة مرة اخرى؟", default=True):
                continue
            return

        subject_names = [s["name"] for s in subjects]
        subj_idx = _select(subject_names, "Choisissez la matiere / اختر المادة")
        subject_slug = subjects[subj_idx]["slug"]

        _show_info("Chargement des categories... / تحميل الاقسام")
        categories = get_categories(session, level_code, subject_slug)

        if not categories:
            _show_error("Aucune categorie trouvee / لم يتم العثور على أقسام")
            if _ask_confirm("Reessayer ? / هل تريد المحاولة مرة اخرى؟", default=True):
                continue
            return

        cat_names = [c["name"] for c in categories]
        cat_idx = _select(cat_names, "Choisissez la categorie / اختر القسم")
        category_code = categories[cat_idx]["code"]

        year_filter = _ask_year_filter("Entrez un filtre d'annees (exemple 2024 ou 2022-2024), ou laissez vide / ادخل السنة للفلترة او اتركها فارغة")
        limit = _ask_download_limit("Combien de fichiers telecharger ? (defaut: 1, ecrire 'tous' pour tout) / عدد الملفات المراد تحميلها (الافتراضي 1، اكتب tous للكل)")
        dest = build_dest_folder(level_code, subject_slug, category_code)

        if not _ask_confirm("Demarrer le telechargement maintenant ? / هل تريد بدء التحميل الان؟", default=True):
            _show_warning("Operation annulee par l'utilisateur / تم إلغاء العملية من طرف المستخدم")
            if _ask_confirm("Retour au menu ? / العودة للقائمة؟", default=True):
                continue
            return

        _show_info("Recherche des sujets... / البحث عن المواضيع")
        exams = _get_exam_links_with_retries(session, level_code, subject_slug, category_code, year_filter, limit, max_attempts=3)

        if not exams:
            _show_error("Aucun sujet trouve / لم يتم العثور على مواضيع")
            if _ask_confirm("Aucun sujet trouve. Refaire une recherche ? / لم يتم العثور على مواضيع. هل تريد المحاولة مجددا؟", default=True):
                continue
            return

        _show_info(f"{len(exams)} sujet(s) trouve(s) / تم العثور على مواضيع")

        for i, exam in enumerate(exams, 1):
            sol = display_text("avec correction / مع الحل") if exam["has_solution"] else display_text("sans correction / بدون حل")
            console.print(
                display_text(f"\n[{i}/{len(exams)}] {exam['title']} ({exam['year'] or '?'}) - {sol}"),
                style="bold white",
            )

            downloaded = None
            for attempt in range(1, 4):
                pdf_url = _get_pdf_url_with_retries(session, exam["url"], max_attempts=2)
                if not pdf_url:
                    if attempt < 3:
                        _show_warning(f"Nouvelle tentative ({attempt}/3) : {exam['title']} / إعادة المحاولة")
                    continue

                downloaded = download_pdf(session, pdf_url, dest)
                if downloaded:
                    break

                if attempt < 3:
                    _show_warning(f"Echec du telechargement, nouvelle tentative ({attempt}/3) : {exam['title']} / فشل التحميل، إعادة المحاولة")

        _show_info(f"Telechargement termine. Dossier: {dest} / انتهى التحميل. المسار")

        if not _ask_confirm("Lancer un autre telechargement ? / هل تريد تنزيلات اخرى؟", default=False):
            return


if __name__ == "__main__":
    try:
        main()
    except UserAbortError:
        console.print(display_text("\nProgramme quitte / تم الخروج من البرنامج"), style="bold yellow")
        sys.exit(0)
    except KeyboardInterrupt:
        console.print(display_text("\nProgramme arrete depuis le clavier / تم ايقاف البرنامج من لوحة المفاتيح"), style="bold yellow")
        sys.exit(0)
    except Exception as exc:
        log.exception(display_text(f"Erreur inattendue: {exc} / خطأ غير متوقع"))
        sys.exit(1)
