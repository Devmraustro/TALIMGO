"""Locale resolution and the server-side phrase table.

Rule (documented so it cannot drift): **educational content is returned in the learner's saved
locale**, falling back to English when that translation is missing. The fallback lives in
``app.curriculum.registry.localised`` for content fields, and in :func:`translate` here for
sentences the *server* composes (next actions, evidence explanations, blockers, placement notes).

Public routes have no learner profile yet, so they accept ``?locale=`` first and ``Accept-Language``
second, both defaulting to English. Authenticated routes always prefer the profile — a learner who
set Arabic does not have to pass a query parameter to get Arabic lessons.
"""

from __future__ import annotations

from typing import Any

SUPPORTED_LOCALES = ("en", "ar")
DEFAULT_LOCALE = "en"
RTL_LOCALES = frozenset({"ar"})


def normalise_locale(value: str | None) -> str | None:
    """``ar-DZ`` → ``ar``; returns ``None`` when the value is not a language we ship."""
    if not value:
        return None
    base = value.strip().lower().replace("_", "-").split("-", 1)[0]
    return base if base in SUPPORTED_LOCALES else None


def locale_from_accept_language(header: str | None) -> str | None:
    """First supported language from an ``Accept-Language`` header, honouring q-weights loosely."""
    if not header:
        return None
    candidates: list[tuple[float, int, str]] = []
    for position, part in enumerate(header.split(",")):
        piece = part.strip()
        if not piece:
            continue
        tag, _, params = piece.partition(";")
        weight = 1.0
        if params.strip().startswith("q="):
            try:
                weight = float(params.strip()[2:])
            except ValueError:
                weight = 0.0
        candidates.append((-weight, position, tag.strip()))
    for _weight, _position, tag in sorted(candidates):
        resolved = normalise_locale(tag)
        if resolved is not None:
            return resolved
    return None


def request_locale(query_locale: str | None, accept_language: str | None) -> str:
    """Locale for a public route: explicit query parameter wins, then the header, then English."""
    return normalise_locale(query_locale) or locale_from_accept_language(accept_language) or DEFAULT_LOCALE


def is_rtl(locale: str) -> bool:
    return locale in RTL_LOCALES


PHRASES: dict[str, dict[str, str]] = {
    "en": {
        "action.no_goal.title": "Define your learning goal",
        "action.no_goal.rationale": ("TALIMGO plans from a goal: tell it what you want to be able to do."),
        "action.no_goal.basis": "No active goal on this account.",
        "action.diagnostic.title": "Take the starting check",
        "action.diagnostic.rationale": (
            "A short adaptive check places you correctly and keeps you from re-learning what you "
            "already know."
        ),
        "action.diagnostic.basis": "No diagnostic evidence recorded for this goal yet.",
        "action.generate_plan.title": "Generate your roadmap",
        "action.generate_plan.rationale": (
            "Your placement is recorded; the next step is a plan built from it."
        ),
        "action.generate_plan.basis": "Diagnostic complete, no active plan.",
        "action.continue.rationale": "This is the task you started.",
        "action.review_due.rationale": (
            "You confirmed this earlier and recall has faded — a short review keeps it."
        ),
        "action.review_unplanned.rationale": (
            "Everything in your plan is done; this confirmed objective is due for review."
        ),
        "action.next_step.rationale": "It is the next unfinished step in your plan.",
        "action.review.title": "Review: {title}",
        "action.all_done.title": "Your plan is complete",
        "action.all_done.rationale": (
            "Every planned step is finished. Measure again, or set a harder goal to continue."
        ),
        "action.all_done.basis": "{n} objective(s) with recorded evidence.",
        "evidence.none": "No evidence recorded for this objective yet.",
        "evidence.no_unassisted": ("{title} is still being learned: no unassisted correct answers yet."),
        "evidence.acquiring": "{title} is being learned. To confirm it, you still need: {missing}.",
        "evidence.missing_successes": "{n} more unassisted correct answer(s)",
        "evidence.missing_delayed": "a correct answer at least 3 days later",
        "evidence.retaining_below": (
            "{title} was confirmed after {n} unassisted correct answers, but {percent}% recall is "
            "below the review threshold — a short review is due."
        ),
        "evidence.retaining_ok": (
            "{title} is confirmed: {n} unassisted correct answers, estimated {percent}% recall right now."
        ),
        "evidence.recall_suffix": " Current estimated recall: {percent}%.",
        "blocker.no_plan": "No roadmap yet — generate one from your goal.",
        "blocker.low_budget": "Your weekly time budget is under an hour; progress will be slow.",
        "placement.note": (
            "Placement is provisional: it reflects one short check and will be revised by your "
            "practice evidence."
        ),
        "placement.rule": (
            "Each answer is counted. Any incorrect answer leaves the objective at needs_work for "
            "this check; with only correct answers it is assumed_known when the hardest correct "
            "item was difficulty 3 or more, and likely_known when every answered item was easy."
        ),
    },
    "ar": {
        "action.no_goal.title": "حدّد هدفك التعليمي",
        "action.no_goal.rationale": (
            "تبني TALIMGO خطتها انطلاقاً من هدف: أخبرنا بما تريد أن تكون قادراً على فعله."
        ),
        "action.no_goal.basis": "لا يوجد هدف نشط في هذا الحساب.",
        "action.diagnostic.title": "ابدأ الاختبار التشخيصي",
        "action.diagnostic.rationale": (
            "اختبار قصير ومتدرّج يحدّد مستواك ويمنعك من إعادة تعلّم ما تعرفه بالفعل."
        ),
        "action.diagnostic.basis": "لا توجد أدلة تشخيصية مسجّلة لهذا الهدف بعد.",
        "action.generate_plan.title": "أنشئ خطتك التعليمية",
        "action.generate_plan.rationale": "تم تسجيل مستواك، والخطوة التالية هي بناء خطة انطلاقاً منه.",
        "action.generate_plan.basis": "اكتمل الاختبار التشخيصي ولا توجد خطة نشطة.",
        "action.continue.rationale": "هذه هي المهمة التي بدأتها.",
        "action.review_due.rationale": "أكّدت هذا الهدف سابقاً وتراجع تذكّرك؛ مراجعة قصيرة تحافظ عليه.",
        "action.review_unplanned.rationale": "أنجزت كل ما في خطتك؛ وهذا الهدف المؤكَّد حان وقت مراجعته.",
        "action.next_step.rationale": "إنها الخطوة التالية غير المكتملة في خطتك.",
        "action.review.title": "مراجعة: {title}",
        "action.all_done.title": "اكتملت خطتك",
        "action.all_done.rationale": "انتهت كل الخطوات المخطَّطة. أعد القياس أو ضع هدفاً أصعب للمتابعة.",
        "action.all_done.basis": "{n} هدف/أهداف لديها أدلة مسجّلة.",
        "evidence.none": "لا توجد أدلة مسجّلة لهذا الهدف بعد.",
        "evidence.no_unassisted": "لا يزال «{title}» قيد التعلّم: لا توجد إجابات صحيحة دون مساعدة حتى الآن.",
        "evidence.acquiring": "«{title}» قيد التعلّم. لتأكيده ما زلت تحتاج إلى: {missing}.",
        "evidence.missing_successes": "{n} إجابات صحيحة إضافية دون مساعدة",
        "evidence.missing_delayed": "إجابة صحيحة بعد ثلاثة أيام على الأقل",
        "evidence.retaining_below": (
            "تم تأكيد «{title}» بعد {n} إجابات صحيحة دون مساعدة، لكن نسبة التذكّر {percent}% "
            "أقل من حد المراجعة؛ حان وقت مراجعة قصيرة."
        ),
        "evidence.retaining_ok": (
            "«{title}» مؤكَّد: {n} إجابات صحيحة دون مساعدة، والتذكّر المقدَّر الآن {percent}%."
        ),
        "evidence.recall_suffix": " التذكّر المقدَّر حالياً: {percent}%.",
        "blocker.no_plan": "لا توجد خطة بعد — أنشئ خطة من هدفك.",
        "blocker.low_budget": "ميزانيتك الزمنية الأسبوعية أقل من ساعة؛ سيكون التقدّم بطيئاً.",
        "placement.note": "التوزيع مبدئي: يعكس اختباراً قصيراً واحداً وستعدّله أدلة تدريبك لاحقاً.",
        "placement.rule": (
            "تُحتسب كل إجابة. أي إجابة خاطئة تُبقي الهدف في وضع needs_work خلال هذا الاختبار؛ "
            "ومع الإجابات الصحيحة فقط يصبح الهدف assumed_known إذا كانت أصعب إجابة صحيحة من "
            "مستوى صعوبة 3 أو أكثر، وlikely_known إذا كانت كل الأسئلة المُجابة سهلة."
        ),
    },
}


def translate(key: str, locale: str, **params: Any) -> str:
    """Look a sentence up in ``locale``, falling back to English, then to the key itself."""
    resolved = normalise_locale(locale) or DEFAULT_LOCALE
    template = PHRASES.get(resolved, {}).get(key) or PHRASES[DEFAULT_LOCALE].get(key) or key
    if not params:
        return template
    try:
        return template.format(**params)
    except (KeyError, IndexError):  # a missing parameter must not break a learner's dashboard
        return PHRASES[DEFAULT_LOCALE].get(key, template).format(**params)
