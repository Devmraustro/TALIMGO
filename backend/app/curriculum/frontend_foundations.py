"""Authored curriculum: Front-end web development foundations (path id ``frontend-foundations``).

Content-as-data in the same shape as ``python_foundations``: objectives with prerequisites, one
lesson and verified items each, in English and Arabic. This is the second launch path of the
master reference (§15.3.1) — chosen because its pedagogical profile differs from Python's
(visual, artefact-based) and therefore proves the engine is not secretly Python-shaped.

Status: **PROPOSED content, not yet subject-reviewed** (implementation plan §4 keeps that gate:
a subject reviewer must pass this path before real learners are pointed at it). Answer keys are
hand-authored; numeric keys carry ``verify_expr`` arithmetic so a wrong key fails the build.
"""

from __future__ import annotations

from typing import Any

PATH: dict[str, Any] = {
    "id": "frontend-foundations",
    "title_en": "Front-end web development foundations",
    "title_ar": "أساسيات تطوير واجهات الويب",
    "summary_en": (
        "Build real web pages from zero: semantic HTML, CSS layout that survives a phone screen, "
        "and enough JavaScript to make a page respond — ending with a profile page you built."
    ),
    "summary_ar": (
        "ابنِ صفحات ويب حقيقية من الصفر: HTML دلالي، وتنسيق CSS يصمد على شاشة الهاتف، وقدر من "
        "JavaScript يجعل الصفحة تستجيب — وختاماً صفحة تعريف شخصية من بنائك."
    ),
    "objectives": [
        {
            "id": "fe:html-structure",
            "title_en": "The anatomy of an HTML document",
            "title_ar": "تشريح مستند HTML",
            "summary_en": "Doctype, head vs body, elements and nesting — the skeleton every page shares.",
            "summary_ar": "إعلان النوع، والرأس مقابل الجسم، والعناصر والتداخل — الهيكل المشترك لكل صفحة.",
            "kind": "concept",
            "bloom_level": "understand",
            "difficulty": 1,
            "prerequisites": [],
            "sequence": 10,
            "est_minutes": 25,
            "lesson": {
                "id": "fe:html-structure:lesson",
                "title_en": "Every page has the same skeleton",
                "title_ar": "كل صفحة لها نفس الهيكل",
                "est_minutes": 20,
                "body_md_en": (
                    "## The skeleton\n"
                    "```html\n"
                    "<!DOCTYPE html>\n"
                    '<html lang="en">\n'
                    "  <head>\n"
                    '    <meta charset="utf-8">\n'
                    "    <title>My page</title>\n"
                    "  </head>\n"
                    "  <body>\n"
                    "    <h1>Hello</h1>\n"
                    "    <p>Visible content lives here.</p>\n"
                    "  </body>\n"
                    "</html>\n"
                    "```\n\n"
                    "## Rules that matter\n"
                    "- `<head>` holds *metadata* (title, charset, links) — nothing the reader sees.\n"
                    "- `<body>` holds everything visible.\n"
                    "- Elements nest like boxes: what opens inside must close inside.\n"
                    "- A few elements are *void* and never close: `<meta>`, `<br>`, `<img>`, `<input>`.\n\n"
                    "> Try it: save the skeleton as `index.html`, change the heading, and open it in a browser."
                ),
                "body_md_ar": (
                    "## الهيكل\n"
                    "```html\n"
                    "<!DOCTYPE html>\n"
                    '<html lang="ar">\n'
                    "  <head>\n"
                    '    <meta charset="utf-8">\n'
                    "    <title>صفحتي</title>\n"
                    "  </head>\n"
                    "  <body>\n"
                    "    <h1>مرحباً</h1>\n"
                    "    <p>المحتوى المرئي يعيش هنا.</p>\n"
                    "  </body>\n"
                    "</html>\n"
                    "```\n\n"
                    "## قواعد مهمة\n"
                    "- يحتوي `<head>` على *بيانات وصفية* (العنوان والترميز والروابط) — لا شيء يراه القارئ.\n"
                    "- يحتوي `<body>` على كل ما هو مرئي.\n"
                    "- تتداخل العناصر كالصناديق: ما يُفتح في الداخل يجب أن يُغلق في الداخل.\n"
                    "- بعض العناصر *فارغة* ولا تُغلق أبداً: `<meta>` و`<br>` و`<img>` و`<input>`.\n\n"
                    "> جرّب: احفظ الهيكل باسم `index.html` وغيّر العنوان وافتحه في متصفح."
                ),
            },
            "items": [
                {
                    "id": "fe:html-structure:q1",
                    "kind": "mcq_single",
                    "prompt_en": "Where does the visible content of a page belong?",
                    "prompt_ar": "أين ينتمي المحتوى المرئي للصفحة؟",
                    "options": [
                        {"id": "a", "en": "Inside `<head>`", "ar": "داخل `<head>`"},
                        {"id": "b", "en": "Inside `<body>`", "ar": "داخل `<body>`"},
                        {"id": "c", "en": "Inside `<title>`", "ar": "داخل `<title>`"},
                        {"id": "d", "en": "After `</html>`", "ar": "بعد `</html>`"},
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "Everything the reader sees goes in `<body>`; `<head>` is metadata only.",
                    "explanation_ar": "كل ما يراه القارئ يوضع في `<body>`؛ أما `<head>` فبيانات وصفية فقط.",
                    "difficulty": 1,
                    "is_diagnostic": True,
                },
                {
                    "id": "fe:html-structure:q2",
                    "kind": "short_answer",
                    "prompt_en": "Which element marks the most important heading on a page? (tag name)",
                    "prompt_ar": "أي عنصر يُستخدم لأهم عنوان في الصفحة؟ (اسم الوسم)",
                    "options": None,
                    "answer_key": {"accepted": ["h1"]},
                    "explanation_en": "Headings run `<h1>` (most important) to `<h6>` (least).",
                    "explanation_ar": "تتدرج العناوين من `<h1>` (الأهم) إلى `<h6>` (الأقل أهمية).",
                    "difficulty": 1,
                    "is_diagnostic": True,
                },
                {
                    "id": "fe:html-structure:q3",
                    "kind": "true_false",
                    "prompt_en": "True or false: every HTML element must have a closing tag.",
                    "prompt_ar": "صواب أم خطأ: يجب أن يكون لكل عنصر HTML وسم إغلاق.",
                    "options": None,
                    "answer_key": {"value": False},
                    "explanation_en": "Void elements such as `<img>`, `<br>` and `<meta>` never have closing tags.",
                    "explanation_ar": "العناصر الفارغة مثل `<img>` و`<br>` و`<meta>` ليس لها وسوم إغلاق أبداً.",
                    "difficulty": 2,
                    "is_diagnostic": False,
                },
            ],
        },
        {
            "id": "fe:html-semantics",
            "title_en": "Semantic HTML and accessible forms",
            "title_ar": "HTML الدلالي والنماذج القابلة للوصول",
            "summary_en": "Elements that mean what they do: landmarks, real buttons, and labelled inputs.",
            "summary_ar": "عناصر تعني ما تفعله: معالم الصفحة، وأزرار حقيقية، وحقول موسومة.",
            "kind": "skill",
            "bloom_level": "apply",
            "difficulty": 2,
            "prerequisites": ["fe:html-structure"],
            "sequence": 20,
            "est_minutes": 30,
            "lesson": {
                "id": "fe:html-semantics:lesson",
                "title_en": "Say what it is, not how it looks",
                "title_ar": "قُل ما هو، لا كيف يبدو",
                "est_minutes": 20,
                "body_md_en": (
                    "## Landmarks\n"
                    "`<header>`, `<nav>`, `<main>`, `<article>`, `<footer>` tell browsers, search engines "
                    "and screen readers what each region *is*. A pile of `<div>`s says nothing.\n\n"
                    "## Interactive elements must be real\n"
                    "A `<button>` is focusable and keyboard-operable for free; a clickable `<div>` is "
                    "invisible to keyboard and screen-reader users until you rebuild all of that by hand.\n\n"
                    "## Every input needs a label\n"
                    "```html\n"
                    '<label for="email">Email</label>\n'
                    '<input id="email" type="email" name="email">\n'
                    "```\n"
                    "The `for`/`id` pair connects them: clicking the label focuses the field, and assistive "
                    "technology announces the label as the field's name."
                ),
                "body_md_ar": (
                    "## معالم الصفحة\n"
                    "تخبر عناصر `<header>` و`<nav>` و`<main>` و`<article>` و`<footer>` المتصفحات ومحركات "
                    "البحث وقارئات الشاشة بما *هي* كل منطقة. أما كومة `<div>` فلا تقول شيئاً.\n\n"
                    "## العناصر التفاعلية يجب أن تكون حقيقية\n"
                    "العنصر `<button>` قابل للتركيز والتشغيل بلوحة المفاتيح مجاناً؛ أما `<div>` القابل "
                    "للنقر فغير مرئي لمستخدمي لوحة المفاتيح وقارئ الشاشة ما لم تُعد بناء كل ذلك يدوياً.\n\n"
                    "## كل حقل يحتاج وسماً\n"
                    "```html\n"
                    '<label for="email">البريد</label>\n'
                    '<input id="email" type="email" name="email">\n'
                    "```\n"
                    "يربط زوج `for`/`id` بينهما: النقر على الوسم يركّز الحقل، وتقنية المساعدة تنطق الوسم اسماً للحقل."
                ),
            },
            "items": [
                {
                    "id": "fe:html-semantics:q1",
                    "kind": "mcq_multi",
                    "prompt_en": "Which of these elements are page landmarks? (choose all that apply)",
                    "prompt_ar": "أيٌّ من هذه العناصر تُعدّ معالم للصفحة؟ (اختر كل ما ينطبق)",
                    "options": [
                        {"id": "a", "en": "`<header>`", "ar": "`<header>`"},
                        {"id": "b", "en": "`<span>`", "ar": "`<span>`"},
                        {"id": "c", "en": "`<nav>`", "ar": "`<nav>`"},
                        {"id": "d", "en": "`<main>`", "ar": "`<main>`"},
                        {"id": "e", "en": "`<footer>`", "ar": "`<footer>`"},
                    ],
                    "answer_key": {"option_ids": ["a", "c", "d", "e"]},
                    "explanation_en": "header, nav, main and footer are landmarks; span is a generic inline wrapper.",
                    "explanation_ar": "العناصر header وnav وmain وfooter معالم؛ أما span فغلاف سطري عام.",
                    "difficulty": 2,
                    "is_diagnostic": True,
                },
                {
                    "id": "fe:html-semantics:q2",
                    "kind": "mcq_single",
                    "prompt_en": "How is a `<label>` connected to its input?",
                    "prompt_ar": "كيف يُربط `<label>` بالحقل التابع له؟",
                    "options": [
                        {
                            "id": "a",
                            "en": "The label's `for` equals the input's `id`",
                            "ar": "قيمة `for` في الوسم تساوي `id` الحقل",
                        },
                        {
                            "id": "b",
                            "en": "They only need to be on the same line",
                            "ar": "يكفي أن يكونا على السطر نفسه",
                        },
                        {
                            "id": "c",
                            "en": "The input's `name` equals the label text",
                            "ar": "قيمة `name` تساوي نص الوسم",
                        },
                        {"id": "d", "en": "Labels connect automatically", "ar": "تتصل الوسوم تلقائياً"},
                    ],
                    "answer_key": {"option_id": "a"},
                    "explanation_en": "`for` on the label must match `id` on the input (or the input is wrapped inside the label).",
                    "explanation_ar": "يجب أن تطابق `for` في الوسم قيمة `id` في الحقل (أو يُغلَّف الحقل داخل الوسم).",
                    "difficulty": 2,
                    "is_diagnostic": True,
                },
                {
                    "id": "fe:html-semantics:q3",
                    "kind": "true_false",
                    "prompt_en": "True or false: a `<div>` with a click handler is keyboard-accessible by default.",
                    "prompt_ar": "صواب أم خطأ: عنصر `<div>` مع معالج نقر يمكن تشغيله بلوحة المفاتيح افتراضياً.",
                    "options": None,
                    "answer_key": {"value": False},
                    "explanation_en": "Divs are not focusable or key-operable by default; use a real `<button>`.",
                    "explanation_ar": "عناصر div ليست قابلة للتركيز أو التشغيل بالمفاتيح افتراضياً؛ استخدم `<button>` حقيقياً.",
                    "difficulty": 2,
                    "is_diagnostic": False,
                },
            ],
        },
        {
            "id": "fe:css-selectors",
            "title_en": "CSS selectors and specificity",
            "title_ar": "محدّدات CSS والخصوصية",
            "summary_en": "Choosing elements with selectors, and predicting which rule wins when two disagree.",
            "summary_ar": "اختيار العناصر بالمحدّدات، والتنبؤ بأي قاعدة تفوز عند التعارض.",
            "kind": "concept",
            "bloom_level": "understand",
            "difficulty": 2,
            "prerequisites": ["fe:html-structure"],
            "sequence": 30,
            "est_minutes": 30,
            "lesson": {
                "id": "fe:css-selectors:lesson",
                "title_en": "Pointing at elements, and winning fights",
                "title_ar": "الإشارة إلى العناصر والفوز في التعارضات",
                "est_minutes": 20,
                "body_md_en": (
                    "## The three everyday selectors\n"
                    "```css\n"
                    "p       { }  /* every paragraph (element) */\n"
                    '.card   { }  /* class="card"                */\n'
                    '#main   { }  /* id="main" (once per page)   */\n'
                    "```\n\n"
                    "## Specificity: who wins?\n"
                    "When two rules set the same property, the more *specific* selector wins — "
                    "element < class < id < inline `style=`. Equal specificity: the later rule wins. "
                    "`!important` overrides all of this and is a smell: it makes the next fight unwinnable."
                ),
                "body_md_ar": (
                    "## المحدّدات الثلاثة اليومية\n"
                    "```css\n"
                    "p       { }  /* كل فقرة (عنصر) */\n"
                    '.card   { }  /* class="card" */\n'
                    '#main   { }  /* id="main" (مرة في الصفحة) */\n'
                    "```\n\n"
                    "## الخصوصية: من يفوز؟\n"
                    "عندما تضبط قاعدتان الخاصية نفسها، يفوز المحدّد *الأكثر خصوصية*: عنصر < صنف < معرّف < "
                    "النمط السطري `style=`. وعند التساوي تفوز القاعدة اللاحقة. وتجاوز `!important` كل ذلك "
                    "وهو رائحة سيئة: يجعل التعارض التالي غير قابل للفوز."
                ),
            },
            "items": [
                {
                    "id": "fe:css-selectors:q1",
                    "kind": "ordering",
                    "prompt_en": "Order these from weakest to strongest specificity.",
                    "prompt_ar": "رتّب التالي من الأضعف إلى الأقوى في الخصوصية.",
                    "options": [
                        {"id": "a", "en": "Element selector `p`", "ar": "محدّد عنصر `p`"},
                        {"id": "b", "en": "Class selector `.card`", "ar": "محدّد صنف `.card`"},
                        {"id": "c", "en": "ID selector `#main`", "ar": "محدّد معرّف `#main`"},
                        {"id": "d", "en": "Inline `style=` attribute", "ar": "سمة `style=` السطرية"},
                    ],
                    "answer_key": {"option_ids": ["a", "b", "c", "d"]},
                    "explanation_en": "Specificity grows element → class → ID → inline style.",
                    "explanation_ar": "تكبر الخصوصية من العنصر ثم الصنف ثم المعرّف ثم النمط السطري.",
                    "difficulty": 3,
                    "is_diagnostic": True,
                },
                {
                    "id": "fe:css-selectors:q2",
                    "kind": "mcq_single",
                    "prompt_en": 'Which selector targets elements with `class="card"`?',
                    "prompt_ar": 'أي محدّد يستهدف العناصر ذات `class="card"`؟',
                    "options": [
                        {"id": "a", "en": "`#card`", "ar": "`#card`"},
                        {"id": "b", "en": "`.card`", "ar": "`.card`"},
                        {"id": "c", "en": "`card`", "ar": "`card`"},
                        {"id": "d", "en": "`*card`", "ar": "`*card`"},
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "A dot selects a class; `#` selects an id; a bare word selects an element type.",
                    "explanation_ar": "النقطة لمحدّد الصنف، و`#` للمعرّف، والكلمة المجردة لنوع عنصر.",
                    "difficulty": 1,
                    "is_diagnostic": True,
                },
                {
                    "id": "fe:css-selectors:q3",
                    "kind": "short_answer",
                    "prompt_en": 'Write the selector that targets the element with `id="main"`.',
                    "prompt_ar": 'اكتب المحدّد الذي يستهدف العنصر ذا `id="main"`.',
                    "options": None,
                    "answer_key": {"accepted": ["#main"]},
                    "explanation_en": "`#main` selects the (single) element whose id is main.",
                    "explanation_ar": "المحدّد `#main` يختار العنصر (الوحيد) الذي معرّفه main.",
                    "difficulty": 1,
                    "is_diagnostic": False,
                },
            ],
        },
        {
            "id": "fe:css-box",
            "title_en": "The CSS box model",
            "title_ar": "نموذج الصندوق في CSS",
            "summary_en": "Content, padding, border, margin — and why `box-sizing` decides what `width` means.",
            "summary_ar": "المحتوى والحشو والحد والهامش — ولماذا تحدّد `box-sizing` معنى `width`.",
            "kind": "concept",
            "bloom_level": "understand",
            "difficulty": 3,
            "prerequisites": ["fe:css-selectors"],
            "sequence": 40,
            "est_minutes": 30,
            "lesson": {
                "id": "fe:css-box:lesson",
                "title_en": "Four layers around every element",
                "title_ar": "أربع طبقات حول كل عنصر",
                "est_minutes": 20,
                "body_md_en": (
                    "## Inside → out\n"
                    "**content** (the text/image) → **padding** (space inside the border) → **border** → "
                    "**margin** (space between this box and its neighbours).\n\n"
                    "## What does `width: 200px` measure?\n"
                    "- Default `box-sizing: content-box`: the 200px is *content only*; padding and border "
                    "are added on top (200 + 2×10 padding + 2×2 border = 224px on screen).\n"
                    "- `box-sizing: border-box`: the 200px *includes* padding and border. Most projects "
                    "set this once for everything: `* { box-sizing: border-box; }`."
                ),
                "body_md_ar": (
                    "## من الداخل إلى الخارج\n"
                    "**المحتوى** (النص/الصورة) ← **الحشو** (مساحة داخل الحد) ← **الحد** ← **الهامش** "
                    "(المسافة بين هذا الصندوق وجيرانه).\n\n"
                    "## ماذا تقيس `width: 200px`؟\n"
                    "- الافتراضي `box-sizing: content-box`: الـ200 بكسل *للمحتوى فقط*؛ يُضاف الحشو والحد "
                    "فوقه (200 + حشو 2×10 + حد 2×2 = 224 بكسل على الشاشة).\n"
                    "- أما `box-sizing: border-box`: فالـ200 بكسل *تتضمن* الحشو والحد. تضبطه معظم المشاريع "
                    "مرة واحدة لكل شيء: `* { box-sizing: border-box; }`."
                ),
            },
            "items": [
                {
                    "id": "fe:css-box:q1",
                    "kind": "ordering",
                    "prompt_en": "Order the box-model layers from the inside out.",
                    "prompt_ar": "رتّب طبقات نموذج الصندوق من الداخل إلى الخارج.",
                    "options": [
                        {"id": "a", "en": "content", "ar": "المحتوى"},
                        {"id": "b", "en": "padding", "ar": "الحشو"},
                        {"id": "c", "en": "border", "ar": "الحد"},
                        {"id": "d", "en": "margin", "ar": "الهامش"},
                    ],
                    "answer_key": {"option_ids": ["a", "b", "c", "d"]},
                    "explanation_en": "Content is wrapped by padding, then the border, then margin on the outside.",
                    "explanation_ar": "المحتوى يغلّفه الحشو ثم الحد ثم الهامش في الخارج.",
                    "difficulty": 2,
                    "is_diagnostic": True,
                },
                {
                    "id": "fe:css-box:q2",
                    "kind": "numeric",
                    "prompt_en": "With the default `content-box`, an element is `width: 200px; padding: 10px; border: 2px solid`. How many px wide is it on screen?",
                    "prompt_ar": "بالوضع الافتراضي `content-box`، عنصر بخواص `width: 200px; padding: 10px; border: 2px solid`. كم عرضه بالبكسل على الشاشة؟",
                    "options": None,
                    "answer_key": {"value": 224},
                    "verify_expr": "200 + 2*10 + 2*2",
                    "explanation_en": "content-box adds padding and border on both sides: 200 + 20 + 4 = 224.",
                    "explanation_ar": "يضيف content-box الحشو والحد من الجهتين: 200 + 20 + 4 = 224.",
                    "difficulty": 3,
                    "is_diagnostic": True,
                },
                {
                    "id": "fe:css-box:q3",
                    "kind": "mcq_single",
                    "prompt_en": "What does `box-sizing: border-box` change?",
                    "prompt_ar": "ماذا تغيّر `box-sizing: border-box`؟",
                    "options": [
                        {
                            "id": "a",
                            "en": "`width` now includes padding and border",
                            "ar": "يصبح `width` متضمناً الحشو والحد",
                        },
                        {"id": "b", "en": "Margins stop collapsing", "ar": "تتوقف الهوامش عن الانهيار"},
                        {"id": "c", "en": "The border becomes invisible", "ar": "يصبح الحد غير مرئي"},
                        {"id": "d", "en": "`width` is measured in rem", "ar": "يُقاس `width` بالريم"},
                    ],
                    "answer_key": {"option_id": "a"},
                    "explanation_en": "border-box makes the declared width the on-screen width, padding and border included.",
                    "explanation_ar": "تجعل border-box العرض المعلن هو العرض على الشاشة شاملاً الحشو والحد.",
                    "difficulty": 3,
                    "is_diagnostic": False,
                },
            ],
        },
        {
            "id": "fe:css-layout",
            "title_en": "Layout with flexbox",
            "title_ar": "التخطيط باستخدام Flexbox",
            "summary_en": "One-dimensional layout: direction, distribution along the axis, alignment across it.",
            "summary_ar": "تخطيط أحادي البعد: الاتجاه، والتوزيع على المحور، والمحاذاة عبره.",
            "kind": "skill",
            "bloom_level": "apply",
            "difficulty": 3,
            "prerequisites": ["fe:css-box"],
            "sequence": 50,
            "est_minutes": 35,
            "lesson": {
                "id": "fe:css-layout:lesson",
                "title_en": "A row (or column) that arranges itself",
                "title_ar": "صف (أو عمود) يرتّب نفسه",
                "est_minutes": 25,
                "body_md_en": (
                    "## The container decides\n"
                    "```css\n"
                    ".row { display: flex; gap: 1rem; justify-content: space-between; align-items: center; }\n"
                    "```\n"
                    "- `display: flex` makes the *children* flex items in a row.\n"
                    "- `flex-direction` picks the main axis (`row` or `column`).\n"
                    "- `justify-content` distributes items *along* the main axis.\n"
                    "- `align-items` aligns them *across* it.\n"
                    "- `gap` is the honest space between items — no margin hacks.\n"
                    "- `flex-wrap: wrap` lets items flow to a new line when space runs out."
                ),
                "body_md_ar": (
                    "## الحاوية تقرر\n"
                    "```css\n"
                    ".row { display: flex; gap: 1rem; justify-content: space-between; align-items: center; }\n"
                    "```\n"
                    "- تجعل `display: flex` *الأبناء* عناصر مرنة في صف.\n"
                    "- تختار `flex-direction` المحور الرئيسي (`row` أو `column`).\n"
                    "- توزّع `justify-content` العناصر *على طول* المحور الرئيسي.\n"
                    "- تحاذي `align-items` العناصر *عبر* ذلك المحور.\n"
                    "- و`gap` هي المسافة الصادقة بين العناصر — دون حيل هوامش.\n"
                    "- وتسمح `flex-wrap: wrap` بانتقال العناصر لسطر جديد عند نفاد المساحة."
                ),
            },
            "items": [
                {
                    "id": "fe:css-layout:q1",
                    "kind": "mcq_single",
                    "prompt_en": "In a default (row) flex container, what does `justify-content` control?",
                    "prompt_ar": "في حاوية مرنة افتراضية (صف)، بما تتحكم `justify-content`؟",
                    "options": [
                        {
                            "id": "a",
                            "en": "Distribution of items along the row (main axis)",
                            "ar": "توزيع العناصر على طول الصف (المحور الرئيسي)",
                        },
                        {"id": "b", "en": "Vertical alignment of items", "ar": "المحاذاة العمودية للعناصر"},
                        {
                            "id": "c",
                            "en": "The text alignment inside items",
                            "ar": "محاذاة النص داخل العناصر",
                        },
                        {"id": "d", "en": "The size of the container", "ar": "حجم الحاوية"},
                    ],
                    "answer_key": {"option_id": "a"},
                    "explanation_en": "justify-content works along the main axis; align-items works across it.",
                    "explanation_ar": "تعمل justify-content على المحور الرئيسي؛ وalign-items عبره.",
                    "difficulty": 3,
                    "is_diagnostic": True,
                },
                {
                    "id": "fe:css-layout:q2",
                    "kind": "mcq_multi",
                    "prompt_en": "Which of these belong on a flex *container*? (choose all that apply)",
                    "prompt_ar": "أيٌّ مما يلي ينتمي إلى *حاوية* مرنة؟ (اختر كل ما ينطبق)",
                    "options": [
                        {"id": "a", "en": "`flex-direction`", "ar": "`flex-direction`"},
                        {"id": "b", "en": "`gap`", "ar": "`gap`"},
                        {"id": "c", "en": "`justify-content`", "ar": "`justify-content`"},
                        {"id": "d", "en": "`float`", "ar": "`float`"},
                    ],
                    "answer_key": {"option_ids": ["a", "b", "c"]},
                    "explanation_en": "Direction, gap and justification are container properties; float is an older layout tool, ignored on flex items.",
                    "explanation_ar": "الاتجاه والفجوة والتوزيع خواص الحاوية؛ أما float فأداة تخطيط أقدم تُتجاهل على العناصر المرنة.",
                    "difficulty": 3,
                    "is_diagnostic": False,
                },
                {
                    "id": "fe:css-layout:q3",
                    "kind": "short_answer",
                    "prompt_en": "Which declaration turns an element into a flex container? (property: value)",
                    "prompt_ar": "أي تصريح يحوّل عنصراً إلى حاوية مرنة؟ (خاصية: قيمة)",
                    "options": None,
                    "answer_key": {"accepted": ["display: flex", "display:flex"]},
                    "explanation_en": "`display: flex` on the parent makes its children flex items.",
                    "explanation_ar": "تجعل `display: flex` على الأب أبناءه عناصر مرنة.",
                    "difficulty": 2,
                    "is_diagnostic": True,
                },
            ],
        },
        {
            "id": "fe:responsive",
            "title_en": "Responsive design and units",
            "title_ar": "التصميم المتجاوب والوحدات",
            "summary_en": "Relative units (%, rem, vw), the viewport meta, and media queries mobile-first.",
            "summary_ar": "الوحدات النسبية (٪ وrem وvw)، ووسم العرض، واستعلامات الوسائط بدءاً من الهاتف.",
            "kind": "skill",
            "bloom_level": "apply",
            "difficulty": 3,
            "prerequisites": ["fe:css-layout"],
            "sequence": 60,
            "est_minutes": 35,
            "lesson": {
                "id": "fe:responsive:lesson",
                "title_en": "Design for the small screen first",
                "title_ar": "صمّم للشاشة الصغيرة أولاً",
                "est_minutes": 25,
                "body_md_en": (
                    "## Non-negotiable first step\n"
                    "```html\n"
                    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                    "```\n"
                    "Without it, phones render a shrunken desktop page.\n\n"
                    "## Units that adapt\n"
                    "- `%` of the parent, `rem` relative to the root font size (1.5rem ≈ 24px at the "
                    "16px default), `vw`/`vh` relative to the viewport.\n"
                    "- Fixed `px` widths are what break on a 360px phone.\n\n"
                    "## Mobile-first media queries\n"
                    "Base styles serve small screens; `@media (min-width: 700px)` *adds* the wide-screen "
                    "layout. Enhancing up beats patching down."
                ),
                "body_md_ar": (
                    "## الخطوة الأولى غير القابلة للتفاوض\n"
                    "```html\n"
                    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                    "```\n"
                    "بدونها تعرض الهواتف صفحة سطح مكتب مصغّرة.\n\n"
                    "## وحدات تتكيف\n"
                    "- `٪` من الأب، و`rem` نسبة لحجم خط الجذر (1.5rem ≈ 24px عند الافتراضي 16px)، "
                    "و`vw`/`vh` نسبة لمنفذ العرض.\n"
                    "- والأعراض الثابتة بـ`px` هي ما ينكسر على هاتف بعرض 360px.\n\n"
                    "## استعلامات وسائط تبدأ من الهاتف\n"
                    "تخدم الأنماط الأساسية الشاشات الصغيرة؛ وتضيف `@media (min-width: 700px)` تخطيط "
                    "الشاشة الواسعة. التحسين صعوداً خير من الترقيع نزولاً."
                ),
            },
            "items": [
                {
                    "id": "fe:responsive:q1",
                    "kind": "numeric",
                    "prompt_en": "The root font size is the default 16px. How many px is `1.5rem`?",
                    "prompt_ar": "حجم خط الجذر هو الافتراضي 16px. كم بكسل تساوي `1.5rem`؟",
                    "options": None,
                    "answer_key": {"value": 24},
                    "verify_expr": "1.5 * 16",
                    "explanation_en": "1rem equals the root font size: 1.5 × 16px = 24px.",
                    "explanation_ar": "يساوي 1rem حجم خط الجذر: 1.5 × 16 = 24 بكسل.",
                    "difficulty": 2,
                    "is_diagnostic": True,
                },
                {
                    "id": "fe:responsive:q2",
                    "kind": "mcq_single",
                    "prompt_en": "What is a media query for?",
                    "prompt_ar": "ما فائدة استعلام الوسائط؟",
                    "options": [
                        {
                            "id": "a",
                            "en": "Applying styles only when conditions (like viewport width) match",
                            "ar": "تطبيق أنماط فقط عند تحقق شروط (مثل عرض المنفذ)",
                        },
                        {"id": "b", "en": "Loading image files faster", "ar": "تحميل الصور أسرع"},
                        {
                            "id": "c",
                            "en": "Querying a database from CSS",
                            "ar": "استعلام قاعدة بيانات من CSS",
                        },
                        {"id": "d", "en": "Playing audio and video", "ar": "تشغيل الصوت والفيديو"},
                    ],
                    "answer_key": {"option_id": "a"},
                    "explanation_en": "`@media (min-width: 700px) { ... }` applies its rules only at 700px and wider.",
                    "explanation_ar": "يطبّق `@media (min-width: 700px)` قواعده فقط عند 700px فأكثر.",
                    "difficulty": 2,
                    "is_diagnostic": True,
                },
                {
                    "id": "fe:responsive:q3",
                    "kind": "true_false",
                    "prompt_en": "True or false: mobile-first means the base CSS targets small screens and media queries add wide-screen rules.",
                    "prompt_ar": "صواب أم خطأ: البدء من الهاتف يعني أن CSS الأساسية للشاشات الصغيرة واستعلامات الوسائط تضيف قواعد الشاشة الواسعة.",
                    "options": None,
                    "answer_key": {"value": True},
                    "explanation_en": "Mobile-first = small-screen base + min-width enhancements.",
                    "explanation_ar": "البدء من الهاتف = قاعدة للشاشات الصغيرة + تحسينات min-width.",
                    "difficulty": 2,
                    "is_diagnostic": False,
                },
            ],
        },
        {
            "id": "fe:js-dom",
            "title_en": "JavaScript and the DOM",
            "title_ar": "JavaScript ونموذج كائن المستند",
            "summary_en": "Finding elements, listening to events, changing text and classes in response.",
            "summary_ar": "إيجاد العناصر والاستماع للأحداث وتغيير النص والأصناف استجابةً لها.",
            "kind": "skill",
            "bloom_level": "apply",
            "difficulty": 3,
            "prerequisites": ["fe:html-semantics"],
            "sequence": 70,
            "est_minutes": 40,
            "lesson": {
                "id": "fe:js-dom:lesson",
                "title_en": "Find it, listen, respond",
                "title_ar": "اِوجد، واستمع، واستجب",
                "est_minutes": 25,
                "body_md_en": (
                    "## The three-step pattern\n"
                    "```js\n"
                    "const btn = document.querySelector('#greet');\n"
                    "btn.addEventListener('click', () => {\n"
                    "  document.querySelector('#msg').textContent = 'Hello!';\n"
                    "  document.body.classList.toggle('celebrate');\n"
                    "});\n"
                    "```\n"
                    "- `querySelector` takes the same selectors as CSS and returns the first match.\n"
                    "- `addEventListener` registers a response to an event (`click`, `submit`, `input`…).\n"
                    "- `textContent` sets text *as text* (never parsed as HTML — that is what makes it safe).\n"
                    "- `classList` (`add`/`remove`/`toggle`) changes appearance by toggling styled classes, "
                    "so design stays in CSS."
                ),
                "body_md_ar": (
                    "## النمط ذو الخطوات الثلاث\n"
                    "```js\n"
                    "const btn = document.querySelector('#greet');\n"
                    "btn.addEventListener('click', () => {\n"
                    "  document.querySelector('#msg').textContent = 'مرحباً!';\n"
                    "  document.body.classList.toggle('celebrate');\n"
                    "});\n"
                    "```\n"
                    "- تأخذ `querySelector` المحدّدات نفسها في CSS وتعيد أول تطابق.\n"
                    "- وتسجّل `addEventListener` استجابة لحدث (`click` و`submit` و`input`…).\n"
                    "- وتضع `textContent` النص *كنص* (لا يُفسَّر HTML أبداً — وهذا ما يجعلها آمنة).\n"
                    "- وتغيّر `classList` (`add`/`remove`/`toggle`) المظهر عبر أصناف منسّقة، فيبقى التصميم في CSS."
                ),
            },
            "items": [
                {
                    "id": "fe:js-dom:q1",
                    "kind": "mcq_single",
                    "prompt_en": "Which call finds the first element matching a CSS selector?",
                    "prompt_ar": "أي استدعاء يجد أول عنصر مطابق لمحدّد CSS؟",
                    "options": [
                        {
                            "id": "a",
                            "en": "`document.querySelector('#msg')`",
                            "ar": "`document.querySelector('#msg')`",
                        },
                        {
                            "id": "b",
                            "en": "`document.findElement('#msg')`",
                            "ar": "`document.findElement('#msg')`",
                        },
                        {"id": "c", "en": "`css.select('#msg')`", "ar": "`css.select('#msg')`"},
                        {"id": "d", "en": "`page.get('#msg')`", "ar": "`page.get('#msg')`"},
                    ],
                    "answer_key": {"option_id": "a"},
                    "explanation_en": "querySelector returns the first match for a CSS selector; the others do not exist.",
                    "explanation_ar": "تعيد querySelector أول تطابق لمحدّد CSS؛ والباقي غير موجود.",
                    "difficulty": 2,
                    "is_diagnostic": True,
                },
                {
                    "id": "fe:js-dom:q2",
                    "kind": "short_answer",
                    "prompt_en": "Which property safely replaces an element's visible text?",
                    "prompt_ar": "أي خاصية تستبدل نص عنصر المرئي بأمان؟",
                    "options": None,
                    "answer_key": {"accepted": ["textContent"]},
                    "explanation_en": "textContent treats the value as plain text, never as HTML markup.",
                    "explanation_ar": "تعامل textContent القيمة كنص صرف، لا كترميز HTML أبداً.",
                    "difficulty": 2,
                    "is_diagnostic": True,
                },
                {
                    "id": "fe:js-dom:q3",
                    "kind": "mcq_multi",
                    "prompt_en": "Which are real `classList` methods? (choose all that apply)",
                    "prompt_ar": "أيٌّ مما يلي دوال حقيقية في `classList`؟ (اختر كل ما ينطبق)",
                    "options": [
                        {"id": "a", "en": "`add`", "ar": "`add`"},
                        {"id": "b", "en": "`remove`", "ar": "`remove`"},
                        {"id": "c", "en": "`toggle`", "ar": "`toggle`"},
                        {"id": "d", "en": "`push`", "ar": "`push`"},
                    ],
                    "answer_key": {"option_ids": ["a", "b", "c"]},
                    "explanation_en": "classList offers add/remove/toggle/contains; push belongs to arrays.",
                    "explanation_ar": "تقدم classList الدوال add/remove/toggle/contains؛ أما push فللمصفوفات.",
                    "difficulty": 3,
                    "is_diagnostic": False,
                },
            ],
        },
        {
            "id": "fe:project",
            "title_en": "Project: a responsive profile page",
            "title_ar": "مشروع: صفحة تعريف متجاوبة",
            "summary_en": "Combine semantics, flexible layout and one interaction into a page about you.",
            "summary_ar": "اجمع الدلالة والتخطيط المرن وتفاعلاً واحداً في صفحة عنك.",
            "kind": "project",
            "bloom_level": "create",
            "difficulty": 4,
            "prerequisites": ["fe:responsive", "fe:js-dom"],
            "sequence": 80,
            "est_minutes": 90,
            "lesson": {
                "id": "fe:project:lesson",
                "title_en": "The capstone brief",
                "title_ar": "تعريف المشروع الختامي",
                "est_minutes": 25,
                "body_md_en": (
                    "## Brief\n"
                    "Build a one-page profile about yourself (or a fictional person): header with your "
                    "name, a main section with two or three cards (skills, projects, interests), a "
                    "contact form, and a footer.\n\n"
                    "## Requirements\n"
                    "- Semantic landmarks and exactly one `<h1>`; every image has `alt`, every input a label.\n"
                    "- Cards in a wrapping flex row; the page must work at 360px without sideways scrolling.\n"
                    "- One JavaScript interaction (for example a button that toggles a dark class).\n"
                    "- Keep styling in a `<style>` block or one CSS file; no frameworks.\n\n"
                    "## How it is judged\n"
                    "The rubric in the project brief: structure, responsiveness, accessibility, interaction."
                ),
                "body_md_ar": (
                    "## التعريف\n"
                    "ابنِ صفحة تعريف واحدة عن نفسك (أو شخصية خيالية): ترويسة باسمك، وقسم رئيسي فيه بطاقتان "
                    "أو ثلاث (مهارات ومشاريع واهتمامات)، ونموذج تواصل، وتذييل.\n\n"
                    "## المتطلبات\n"
                    "- معالم دلالية و`<h1>` واحد فقط؛ ولكل صورة `alt` ولكل حقل وسم.\n"
                    "- بطاقات في صف مرن يلتف؛ ويجب أن تعمل الصفحة عند 360px بلا تمرير جانبي.\n"
                    "- تفاعل JavaScript واحد (مثلاً زر يبدّل صنف الوضع الداكن).\n"
                    "- أبقِ التنسيق في كتلة `<style>` أو ملف CSS واحد؛ بلا أطر عمل.\n\n"
                    "## معايير التقييم\n"
                    "سلّم التقييم في تعريف المشروع: البنية والتجاوب وقابلية الوصول والتفاعل."
                ),
            },
            "project": {
                "id": "fe:project:profile-page",
                "title_en": "Build: your profile page",
                "title_ar": "مشروع: صفحة تعريفك",
                "brief_md_en": (
                    "## Brief\n"
                    "One page about you: header with your name, `<main>` with 2–3 cards (skills, "
                    "projects, interests), a contact form, and a footer.\n\n"
                    "## Requirements\n"
                    "- Semantic landmarks, one `<h1>`, `alt` on images, labels on inputs.\n"
                    "- Flexbox card row that wraps; no sideways scrolling at 360px; viewport meta present.\n"
                    "- One working JavaScript interaction.\n\n"
                    "## Submitting\n"
                    "Paste the complete HTML document (with its `<style>` and `<script>`) as the artifact. "
                    "In the reflection, describe one layout bug you hit and how you diagnosed it. Check "
                    "each rubric row only after testing the page at phone width."
                ),
                "brief_md_ar": (
                    "## التعريف\n"
                    "صفحة واحدة عنك: ترويسة باسمك، و`<main>` فيه بطاقتان أو ثلاث (مهارات ومشاريع "
                    "واهتمامات)، ونموذج تواصل، وتذييل.\n\n"
                    "## المتطلبات\n"
                    "- معالم دلالية و`<h1>` واحد و`alt` للصور ووسوم للحقول.\n"
                    "- صف بطاقات مرن يلتف؛ وبلا تمرير جانبي عند 360px؛ مع وسم العرض.\n"
                    "- تفاعل JavaScript واحد يعمل فعلاً.\n\n"
                    "## التسليم\n"
                    "الصق مستند HTML كاملاً (مع `<style>` و`<script>`) عملاً مُسلَّماً. وفي التأمل صِف خطأ "
                    "تخطيط واجهته وكيف شخّصته. لا تعلّم أي صف إلا بعد اختبار الصفحة بعرض الهاتف."
                ),
                "rubric": [
                    {
                        "id": "semantic_structure",
                        "label_en": "Semantic landmarks, one h1, alt text and labels throughout",
                        "label_ar": "معالم دلالية وh1 واحد ونصوص بديلة ووسوم في كل مكان",
                        "required": True,
                    },
                    {
                        "id": "responsive",
                        "label_en": "Works at 360px with no sideways scrolling (viewport meta present)",
                        "label_ar": "يعمل عند 360px بلا تمرير جانبي (مع وسم العرض)",
                        "required": True,
                    },
                    {
                        "id": "layout",
                        "label_en": "Cards laid out with a wrapping flex row and gap (no floats/tables)",
                        "label_ar": "بطاقات بصف مرن يلتف مع gap (بلا float أو جداول)",
                        "required": True,
                    },
                    {
                        "id": "interaction",
                        "label_en": "One JavaScript interaction works and is keyboard-usable",
                        "label_ar": "تفاعل JavaScript واحد يعمل وقابل للاستخدام بلوحة المفاتيح",
                        "required": True,
                    },
                ],
                "min_artifact_chars": 400,
                "min_reflection_chars": 40,
                "est_minutes": 75,
            },
            "items": [
                {
                    "id": "fe:project:q1",
                    "kind": "mcq_single",
                    "prompt_en": "Your profile page looks zoomed-out and tiny on a phone. What is most likely missing?",
                    "prompt_ar": "تبدو صفحة تعريفك مصغّرة وضئيلة على الهاتف. ما المفقود على الأرجح؟",
                    "options": [
                        {"id": "a", "en": "The viewport meta tag", "ar": "وسم العرض (viewport)"},
                        {"id": "b", "en": "A CSS framework", "ar": "إطار عمل CSS"},
                        {"id": "c", "en": "JavaScript", "ar": "JavaScript"},
                        {"id": "d", "en": "More `<div>` elements", "ar": "عناصر `<div>` إضافية"},
                    ],
                    "answer_key": {"option_id": "a"},
                    "explanation_en": "Without the viewport meta, phones render a shrunken desktop layout.",
                    "explanation_ar": "بدون وسم العرض تعرض الهواتف تخطيط سطح مكتب مصغّراً.",
                    "difficulty": 3,
                    "is_diagnostic": True,
                },
                {
                    "id": "fe:project:q2",
                    "kind": "mcq_single",
                    "prompt_en": "Cards overflow the screen on a narrow phone. What is the cleanest fix?",
                    "prompt_ar": "تفيض البطاقات خارج الشاشة على هاتف ضيّق. ما أنظف إصلاح؟",
                    "options": [
                        {
                            "id": "a",
                            "en": "Let the flex row wrap (`flex-wrap: wrap`) and avoid fixed px widths",
                            "ar": "دع الصف المرن يلتف (`flex-wrap: wrap`) وتجنّب الأعراض الثابتة",
                        },
                        {
                            "id": "b",
                            "en": "Hide the page on small screens",
                            "ar": "إخفاء الصفحة على الشاشات الصغيرة",
                        },
                        {
                            "id": "c",
                            "en": "Set `overflow: visible` everywhere",
                            "ar": "ضبط `overflow: visible` في كل مكان",
                        },
                        {"id": "d", "en": "Make the font smaller until it fits", "ar": "تصغير الخط حتى يتسع"},
                    ],
                    "answer_key": {"option_id": "a"},
                    "explanation_en": "Wrapping + relative widths let cards stack instead of overflowing.",
                    "explanation_ar": "الالتفاف والأعراض النسبية يجعلان البطاقات تتراكم بدل أن تفيض.",
                    "difficulty": 3,
                    "is_diagnostic": False,
                },
                {
                    "id": "fe:project:q3",
                    "kind": "mcq_multi",
                    "prompt_en": "Before publishing, which checks matter most? (choose all that apply)",
                    "prompt_ar": "قبل النشر، أي الفحوصات أهم؟ (اختر كل ما ينطبق)",
                    "options": [
                        {
                            "id": "a",
                            "en": "Every image has alt text and every input a label",
                            "ar": "لكل صورة نص بديل ولكل حقل وسم",
                        },
                        {
                            "id": "b",
                            "en": "The page is fully usable with keyboard only",
                            "ar": "الصفحة قابلة للاستخدام الكامل بلوحة المفاتيح فقط",
                        },
                        {
                            "id": "c",
                            "en": "Text has enough contrast against its background",
                            "ar": "للنص تباين كافٍ مع خلفيته",
                        },
                        {
                            "id": "d",
                            "en": "The page uses as many fonts as possible",
                            "ar": "تستخدم الصفحة أكبر عدد ممكن من الخطوط",
                        },
                    ],
                    "answer_key": {"option_ids": ["a", "b", "c"]},
                    "explanation_en": "Alt/labels, keyboard usability and contrast are publish gates; more fonts only add weight.",
                    "explanation_ar": "النصوص البديلة والوسوم وقابلية لوحة المفاتيح والتباين بوابات نشر؛ أما كثرة الخطوط فوزن إضافي فقط.",
                    "difficulty": 3,
                    "is_diagnostic": False,
                },
            ],
        },
    ],
}
