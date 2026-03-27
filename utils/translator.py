LEVELS = {
    "ابتدائي": {
        "التحضيري": "0ap",
        "الاولى": "1ap",
        "الثانية": "2ap",
        "الثالثة": "3ap",
        "الرابعة": "4ap",
        "الخامسة": "5ap",
    },
    "متوسط": {
        "الاولى": "1am",
        "الثانية": "2am",
        "الثالثة": "3am",
        "الرابعة": "4am",
    },
    "ثانوي": {
        "الاولى": "1as",
        "الثانية": "2as",
        "الثالثة": "3as",
    },
    "شهادات": {
        "شهادة التعليم الابتدائي": "bep",
        "شهادة التعليم المتوسط": "bem",
        "شهادة البكالوريا": "bac",
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
    "فروض الفصل الاول": "d1",
    "اختبارات الفصل الاول": "e1",
    "فروض الفصل الثاني": "d2",
    "اختبارات الفصل الثاني": "e2",
    "فروض الفصل الثالث": "d3",
    "اختبارات الفصل الثالث": "e3",
    "دروس وملخصات": "cours",
    "تمارين وتطبيقات": "exercices",
}

BASE_URL = "https://www.dzexams.com"


def build_subject_url(level_code, subject_slug):
    return f"{BASE_URL}/ar/{level_code}/{subject_slug}"


def build_category_url(level_code, subject_slug, category_code):
    return f"{BASE_URL}/ar/{level_code}/{subject_slug}/{category_code}"
