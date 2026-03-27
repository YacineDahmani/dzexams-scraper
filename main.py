import sys

import questionary
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

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
    console.print(f"[bold red]{display_text(message)}[/bold red]")


def _show_warning(message):
    console.print(f"[bold yellow]{display_text(message)}[/bold yellow]")


def _show_success(message):
    console.print(f"[bold green]{display_text(message)}[/bold green]")


def _run_step(label, action, *args, **kwargs):
    with console.status(f"[cyan]{display_text(label)}[/cyan]", spinner="dots"):
        return action(*args, **kwargs)


def _show_download_plan(level_code, subject_name, category_name, year_filter, limit, dest):
    table = Table(box=box.SIMPLE, show_header=False, pad_edge=False)
    table.add_column(style="bold cyan")
    table.add_column(style="white")
    table.add_row(display_text("Niveau / المرحلة"), display_text(level_code))
    table.add_row(display_text("Matiere / المادة"), display_text(subject_name))
    table.add_row(display_text("Categorie / القسم"), display_text(category_name))
    table.add_row(display_text("Filtre annee / فلترة السنة"), display_text(year_filter or "Aucun / بدون"))
    table.add_row(display_text("Limite / العدد"), display_text("Tous / الكل" if limit is None else str(limit)))
    table.add_row(display_text("Dossier / المجلد"), display_text(str(dest)))

    console.print(
        Panel(
            table,
            title=display_text("Resume / الملخص"),
            border_style="cyan",
            box=box.ROUNDED,
            padding=(0, 1),
        )
    )


def _show_download_summary(total, completed, failed, dest):
    table = Table(box=box.SIMPLE, show_header=False, pad_edge=False)
    table.add_column(style="bold cyan")
    table.add_column(style="white")
    table.add_row(display_text("Total"), str(total))
    table.add_row(display_text("Reussis / نجح"), str(completed))
    table.add_row(display_text("Echoues / فشل"), str(failed))
    table.add_row(display_text("Dossier / المجلد"), display_text(str(dest)))

    console.print(
        Panel(
            table,
            title=display_text("Telechargement termine / انتهى التحميل"),
            border_style="green",
            box=box.ROUNDED,
            padding=(0, 1),
        )
    )


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

        subjects = _run_step(
            f"Chargement des matieres pour {level_code}... / تحميل المواد",
            get_subjects,
            session,
            level_code,
        )

        if not subjects:
            _show_error("Aucune matiere trouvee / لم يتم العثور على مواد")
            if _ask_confirm("Reessayer ? / هل تريد المحاولة مرة اخرى؟", default=True):
                continue
            return

        subject_names = [s["name"] for s in subjects]
        subj_idx = _select(subject_names, "Choisissez la matiere / اختر المادة")
        subject_slug = subjects[subj_idx]["slug"]

        categories = _run_step(
            "Chargement des categories... / تحميل الاقسام",
            get_categories,
            session,
            level_code,
            subject_slug,
        )

        if not categories:
            _show_error("Aucune categorie trouvee / لم يتم العثور على أقسام")
            if _ask_confirm("Reessayer ? / هل تريد المحاولة مرة اخرى؟", default=True):
                continue
            return

        cat_names = [c["name"] for c in categories]
        cat_idx = _select(cat_names, "Choisissez la categorie / اختر القسم")
        category_code = categories[cat_idx]["code"]
        category_name = categories[cat_idx]["name"]

        year_filter = _ask_year_filter("Entrez un filtre d'annees (exemple 2024 ou 2022-2024), ou laissez vide / ادخل السنة للفلترة او اتركها فارغة")
        limit = _ask_download_limit("Combien de fichiers telecharger ? (defaut: 1, ecrire 'tous' pour tout) / عدد الملفات المراد تحميلها (الافتراضي 1، اكتب tous للكل)")
        dest = build_dest_folder(level_code, subject_slug, category_code)
        _show_download_plan(level_code, subject_names[subj_idx], category_name, year_filter, limit, dest)

        if not _ask_confirm("Demarrer le telechargement maintenant ? / هل تريد بدء التحميل الان؟", default=True):
            _show_warning("Operation annulee par l'utilisateur / تم إلغاء العملية من طرف المستخدم")
            if _ask_confirm("Retour au menu ? / العودة للقائمة؟", default=True):
                continue
            return

        exams = _run_step(
            "Recherche des sujets... / البحث عن المواضيع",
            _get_exam_links_with_retries,
            session,
            level_code,
            subject_slug,
            category_code,
            year_filter,
            limit,
            3,
        )

        if not exams:
            _show_error("Aucun sujet trouve / لم يتم العثور على مواضيع")
            if _ask_confirm("Aucun sujet trouve. Refaire une recherche ? / لم يتم العثور على مواضيع. هل تريد المحاولة مجددا؟", default=True):
                continue
            return

        _show_success(f"{len(exams)} sujet(s) trouve(s) / تم العثور على مواضيع")

        completed = 0
        failed = 0

        for i, exam in enumerate(exams, 1):
            sol = display_text("avec correction / مع الحل") if exam["has_solution"] else display_text("sans correction / بدون حل")
            console.print(
                display_text(f"[{i}/{len(exams)}] {exam['title']} ({exam['year'] or '?'}) - {sol}"),
                style="white",
            )

            pdf_url = _get_pdf_url_with_retries(session, exam["url"], max_attempts=3)
            if not pdf_url:
                failed += 1
                _show_warning(f"Lien PDF introuvable: {exam['title']} / رابط PDF غير موجود")
                continue

            downloaded = download_pdf(session, pdf_url, dest, max_retries=3)
            if downloaded:
                completed += 1
            else:
                failed += 1
                _show_warning(f"Echec du telechargement: {exam['title']} / فشل التحميل")

        _show_download_summary(len(exams), completed, failed, dest)

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
