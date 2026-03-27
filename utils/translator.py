LEVELS = {
    "Primaire / ابتدائي": {
        "Preparatoire / التحضيري": "0ap",
        "1re annee / الاولى": "1ap",
        "2e annee / الثانية": "2ap",
        "3e annee / الثالثة": "3ap",
        "4e annee / الرابعة": "4ap",
        "5e annee / الخامسة": "5ap",
    },
    "Moyen / متوسط": {
        "1re annee / الاولى": "1am",
        "2e annee / الثانية": "2am",
        "3e annee / الثالثة": "3am",
        "4e annee / الرابعة": "4am",
    },
    "Secondaire / ثانوي": {
        "1re annee / الاولى": "1as",
        "2e annee / الثانية": "2as",
        "3e annee / الثالثة": "3as",
    },
    "Examens officiels / شهادات": {
        "5eme / شهادة التعليم الابتدائي": "bep",
        "BEM / شهادة التعليم المتوسط": "bem",
        "BAC / شهادة البكالوريا": "bac",
    },
}

SUBJECTS = {
    "الرياضيات": "mathematiques",
    "اللغة العربية": "arabe",
    "اللغة الفرنسية": "francais",
    "اللغة الانجليزية": "anglais",
    "التاريخ والجغرافيا": "histoire-geographie",
    "العلوم الفيزيائية": "physique",
    "علوم الطبيعة والحياة": "sciences-naturelles",
    "التربية الاسلامية": "tarbia-islamia",
    "التربية المدنية": "tarbia-madania",
    "الاعلام الالي": "informatique",
    "الفلسفة": "philosophie",
    "الهندسة الميكانيكية": "genie-mecanique",
    "الهندسة الكهربائية": "genie-electrique",
    "الهندسة المدنية": "genie-civil",
    "المحاسبة": "comptabilite",
    "الاقتصاد": "economie",
    "القانون": "droit",
    "التسيير المحاسبي والمالي": "gestion",
    "اللغة الامازيغية": "tamazight",
    "التربية الفنية": "dessin",
    "التربية الموسيقية": "musique",
    "العلوم الاسلامية": "sciences-islamiques",
}

CATEGORIES = {
    "Devoirs T1 / فروض الفصل الاول": "d1",
    "Examens T1 / اختبارات الفصل الاول": "e1",
    "Devoirs T2 / فروض الفصل الثاني": "d2",
    "Examens T2 / اختبارات الفصل الثاني": "e2",
    "Devoirs T3 / فروض الفصل الثالث": "d3",
    "Examens T3 / اختبارات الفصل الثالث": "e3",
    "Cours et resumes / دروس وملخصات": "cours",
    "Exercices et applications / تمارين وتطبيقات": "exercices",
}

BASE_URL = "https://www.dzexams.com"


SUBJECT_LABELS = {
    "الرياضيات": "Mathematiques / الرياضيات",
    "اللغة العربية": "Langue arabe / اللغة العربية",
    "اللغة الفرنسية": "Langue francaise / اللغة الفرنسية",
    "اللغة الانجليزية": "Langue anglaise / اللغة الانجليزية",
    "التاريخ والجغرافيا": "Histoire-Geographie / التاريخ والجغرافيا",
    "العلوم الفيزيائية": "Sciences physiques / العلوم الفيزيائية",
    "علوم الطبيعة والحياة": "Sciences de la nature et de la vie / علوم الطبيعة والحياة",
    "التربية الاسلامية": "Education islamique / التربية الاسلامية",
    "التربية المدنية": "Education civique / التربية المدنية",
    "الاعلام الالي": "Informatique / الاعلام الالي",
    "الفلسفة": "Philosophie / الفلسفة",
    "الهندسة الميكانيكية": "Genie mecanique / الهندسة الميكانيكية",
    "الهندسة الكهربائية": "Genie electrique / الهندسة الكهربائية",
    "الهندسة المدنية": "Genie civil / الهندسة المدنية",
    "المحاسبة": "Comptabilite / المحاسبة",
    "الاقتصاد": "Economie / الاقتصاد",
    "القانون": "Droit / القانون",
    "التسيير المحاسبي والمالي": "Gestion comptable et financiere / التسيير المحاسبي والمالي",
    "اللغة الامازيغية": "Langue amazighe / اللغة الامازيغية",
    "التربية الفنية": "Education artistique / التربية الفنية",
    "التربية الموسيقية": "Education musicale / التربية الموسيقية",
    "العلوم الاسلامية": "Sciences islamiques / العلوم الاسلامية",
}


CATEGORY_LABELS = {
    "فروض الفصل الاول": "Devoirs T1 / فروض الفصل الاول",
    "اختبارات الفصل الاول": "Examens T1 / اختبارات الفصل الاول",
    "فروض الفصل الثاني": "Devoirs T2 / فروض الفصل الثاني",
    "اختبارات الفصل الثاني": "Examens T2 / اختبارات الفصل الثاني",
    "فروض الفصل الثالث": "Devoirs T3 / فروض الفصل الثالث",
    "اختبارات الفصل الثالث": "Examens T3 / اختبارات الفصل الثالث",
    "دروس وملخصات": "Cours et resumes / دروس وملخصات",
    "تمارين وتطبيقات": "Exercices et applications / تمارين وتطبيقات",
    "All exams": "Tous les sujets / جميع المواضيع",
}


def translate_subject_name(name):
    normalized = " ".join(str(name).split())
    return SUBJECT_LABELS.get(normalized, normalized)


def translate_category_name(name):
    normalized = " ".join(str(name).split())
    return CATEGORY_LABELS.get(normalized, normalized)


def build_subject_url(level_code, subject_slug):
    return f"{BASE_URL}/ar/{level_code}/{subject_slug}"


def build_category_url(level_code, subject_slug, category_code):
    return f"{BASE_URL}/ar/{level_code}/{subject_slug}/{category_code}"
