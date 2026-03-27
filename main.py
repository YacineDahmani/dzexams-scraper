import sys
from pathlib import Path

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
    subtitle = display_text(" تحميل جميع الفروض والاختبارات")
    panel = Panel(
        f"[bold cyan]{title}[/bold cyan]\n[white]{subtitle}[/white]",
        box=box.ROUNDED,
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel)


def _show_error(message):
    console.print(f"[bold red]{display_text('خطا:')}[/bold red] [red]{display_text(message)}[/red]")


def _show_warning(message):
    console.print(f"[bold yellow]{display_text('تنبيه:')}[/bold yellow] [yellow]{display_text(message)}[/yellow]")


def _show_info(message):
    console.print(f"[bold blue]{display_text('معلومة:')}[/bold blue] [white]{display_text(message)}[/white]")


def _show_success(message):
    console.print(f"[bold green]{display_text('نجاح:')}[/bold green] [green]{display_text(message)}[/green]")


def _select(options, label):
    if not options:
        raise ValueError("لا توجد خيارات متاحة")

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
    answer = questionary.confirm(
        message=display_text(prompt),
        default=default,
        qmark="",
    ).ask()
    if answer is None:
        raise UserAbortError
    return answer


def _ask_positive_int(prompt):
    while True:
        value = _ask_text(prompt)
        if not value:
            return None
        if value.isdigit() and int(value) > 0:
            return int(value)
        _show_warning("ادخل رقما صحيحا اكبر من صفر او اتركه فارغا")


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


def _show_summary(level_name, year_name, subject_name, category_name, year_filter, limit, dest):
    table = Table(box=box.SIMPLE_HEAVY, show_header=False, expand=False)
    table.add_column(display_text("الحقل"), style="cyan")
    table.add_column(display_text("القيمة"), style="white")

    table.add_row(display_text("المرحلة"), display_text(level_name))
    table.add_row(display_text("السنة"), display_text(year_name))
    table.add_row(display_text("المادة"), display_text(subject_name))
    table.add_row(display_text("القسم"), display_text(category_name))
    table.add_row(display_text("فلترة السنوات"), display_text(year_filter or "بدون فلترة"))
    table.add_row(display_text("العدد"), display_text(str(limit) if limit else "الكل"))
    table.add_row(display_text("الحفظ في"), str(dest))

    console.print(Panel(table, title=display_text("ملخص الخيارات"), border_style="blue", box=box.ROUNDED))


def main():
    configure_console_encoding()
    _show_header()

    session = get_session()

    stage_names = list(LEVELS.keys())
    stage_idx = _select(stage_names, "اختر المرحلة الدراسية")
    stage = stage_names[stage_idx]

    year_names = list(LEVELS[stage].keys())
    year_idx = _select(year_names, "اختر السنة")
    level_code = LEVELS[stage][year_names[year_idx]]

    _show_info(f"جاري تحميل المواد لـ {level_code}...")
    subjects = get_subjects(session, level_code)

    if not subjects:
        _show_error("لم يتم العثور على مواد")
        return

    subject_names = [s["name"] for s in subjects]
    subj_idx = _select(subject_names, "اختر المادة")
    subject_slug = subjects[subj_idx]["slug"]

    _show_info("جاري تحميل الاقسام...")
    categories = get_categories(session, level_code, subject_slug)

    if not categories:
        _show_error("لم يتم العثور على اقسام")
        return

    cat_names = [c["name"] for c in categories]
    cat_idx = _select(cat_names, "اختر القسم")
    category_code = categories[cat_idx]["code"]

    year_filter = _ask_year_filter("ادخل السنة للفلترة (مثلا 2024 او 2022-2024) او اتركها فارغة")
    limit = _ask_positive_int("عدد الملفات المراد تحميلها (اتركها فارغة للكل)")
    dest = build_dest_folder(level_code, subject_slug, category_code)

    _show_summary(
        level_name=stage,
        year_name=year_names[year_idx],
        subject_name=subject_names[subj_idx],
        category_name=cat_names[cat_idx],
        year_filter=year_filter,
        limit=limit,
        dest=dest,
    )

    if not _ask_confirm("هل تريد بدء التحميل الان؟", default=True):
        _show_warning("تم الغاء العملية من طرف المستخدم")
        return

    _show_info("جاري البحث عن الامتحانات...")
    exams = get_exam_links(session, level_code, subject_slug, category_code, year_filter, limit)

    if not exams:
        _show_error("لم يتم العثور على امتحانات")
        return

    _show_success(f"تم العثور على {len(exams)} ملف(ات)")
    ok_count = 0
    failed_count = 0

    for i, exam in enumerate(exams, 1):
        sol = display_text("مع الحل") if exam["has_solution"] else display_text("بدون حل")
        console.print(
            display_text(f"\n[{i}/{len(exams)}] {exam['title']} ({exam['year'] or '?'}) - {sol}"),
            style="bold white",
        )

        pdf_url = get_pdf_url(session, exam["url"])
        if not pdf_url:
            failed_count += 1
            _show_error("لم يتم العثور على رابط PDF")
            continue

        downloaded = download_pdf(session, pdf_url, dest)
        if downloaded:
            ok_count += 1
        else:
            failed_count += 1

    summary = Table(box=box.SIMPLE_HEAVY, show_header=False)
    summary.add_column(display_text("البند"), style="cyan")
    summary.add_column(display_text("القيمة"), style="white")
    summary.add_row(display_text("التحميلات الناجحة"), str(ok_count))
    summary.add_row(display_text("التحميلات الفاشلة"), str(failed_count))
    summary.add_row(display_text("المسار"), str(Path(dest)))

    console.print(Panel(summary, title=display_text("تم الانتهاء"), border_style="green", box=box.ROUNDED))


if __name__ == "__main__":
    try:
        main()
    except UserAbortError:
        console.print(display_text("\nتم الخروج من البرنامج"), style="bold yellow")
        sys.exit(0)
    except KeyboardInterrupt:
        console.print(display_text("\nتم ايقاف البرنامج من لوحة المفاتيح"), style="bold yellow")
        sys.exit(0)
    except Exception as exc:
        log.exception(display_text(f"حدث خطأ غير متوقع: {exc}"))
        sys.exit(1)
