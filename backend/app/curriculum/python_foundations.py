"""Authored curriculum: Python programming foundations (path id ``python-foundations``).

This is content-as-data: objectives (stable learning targets with prerequisites), lessons, and
assessment items with answer keys. It is intentionally small and hand-authored so that every
answer key is verifiable.

Verification: items that can be checked mechanically carry ``verify_expr`` (a Python expression
whose evaluated value must equal the accepted answer). ``tests/test_curriculum.py`` executes those
expressions, so a wrong key fails the build instead of reaching a learner.

Modelling line (master reference section 7.1.3.3, UNESCO guidance): these are language models, not
oracles — no item asks for an unverifiable generative claim, and every key is authored, not produced
by AI.
"""

from __future__ import annotations

from typing import Any

PATH: dict[str, Any] = {
    "id": "python-foundations",
    "title_en": "Python programming foundations",
    "title_ar": "أساسيات البرمجة بلغة بايثون",
    "summary_en": (
        "Start from zero and finish able to read, write, debug and organise small Python programs, "
        "ending with a working command-line tool you built yourself."
    ),
    "summary_ar": (
        "ابدأ من الصفر وانتهِ بقدرتك على قراءة وكتابة وتصحيح وتنظيم برامج بايثون صغيرة، "
        "مع مشروع أخير: أداة سطر أوامر تعمل فعلاً من صنعك."
    ),
    "objectives": [
        {
            "id": "py:values",
            "title_en": "Variables, values and types",
            "title_ar": "المتغيرات والقيم والأنواع",
            "summary_en": "Store a value under a name; know the difference between text, whole numbers, decimals and booleans.",
            "summary_ar": "تخزين قيمة تحت اسم، والتمييز بين النص والأعداد الصحيحة والأعداد العشرية والقيم المنطقية.",
            "kind": "concept",
            "bloom_level": "understand",
            "difficulty": 1,
            "prerequisites": [],
            "sequence": 10,
            "est_minutes": 25,
            "lesson": {
                "id": "py:values:lesson",
                "title_en": "Names for things",
                "title_ar": "أسماء للأشياء",
                "est_minutes": 20,
                "body_md_en": (
                    "## What a variable is\n"
                    "A variable is a name you give to a value so you can use it again.\n\n"
                    "```python\n"
                    "age = 17          # whole number (int)\n"
                    "price = 12.5      # decimal (float)\n"
                    'name = "Amina"    # text (str)\n'
                    "is_ready = True   # boolean (bool)\n"
                    "```\n\n"
                    "## Types matter\n"
                    '`"12"` and `12` are different: the first is text, the second is a number.\n'
                    '`"12" + "3"` gives `"123"` (joining), while `12 + 3` gives `15` (adding).\n\n'
                    "## Checking and converting\n"
                    '`type(x)` tells you what something is. `int("12")` converts text to a number.\n\n'
                    "> Try it: in a Python shell, type `type(3 / 1)` — division always gives a float."
                ),
                "body_md_ar": (
                    "## ما هو المتغير؟\n"
                    "المتغير اسم تعطيه لقيمة لتستخدمها لاحقاً.\n\n"
                    "```python\n"
                    "age = 17          # عدد صحيح\n"
                    "price = 12.5      # عدد عشري\n"
                    'name = "أمينة"    # نص\n'
                    "is_ready = True   # قيمة منطقية\n"
                    "```\n\n"
                    "## الأنواع مهمة\n"
                    '`"12"` و`12` مختلفان: الأول نص والثاني عدد.\n'
                    'ناتج `"12" + "3"` هو `"123"` (دمج)، أما `12 + 3` فناتجه `15` (جمع).\n\n'
                    "## الفحص والتحويل\n"
                    '`type(x)` يخبرك بنوع القيمة، و`int("12")` يحوّل النص إلى عدد.\n\n'
                    "> جرّب: في مفسّر بايثون اكتب `type(3 / 1)` — القسمة تعطي دائماً عدداً عشرياً."
                ),
            },
            "items": [
                {
                    "id": "py:values:q1",
                    "kind": "mcq_single",
                    "prompt_en": "What is the value of `type(7 / 2)` in Python?",
                    "prompt_ar": "ما قيمة `type(7 / 2)` في بايثون؟",
                    "options": [
                        {"id": "a", "en": "int", "ar": "int"},
                        {"id": "b", "en": "float", "ar": "float"},
                        {"id": "c", "en": "str", "ar": "str"},
                        {"id": "d", "en": "bool", "ar": "bool"},
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "The `/` operator always returns a float in Python 3, so 7 / 2 is 3.5.",
                    "explanation_ar": "المعامل `/` يعيد دائماً عدداً عشرياً في بايثون 3، لذا 7 / 2 يساوي 3.5.",
                    "difficulty": 1,
                    "is_diagnostic": True,
                },
                {
                    "id": "py:values:q2",
                    "kind": "short_answer",
                    "prompt_en": "What does `12 + 3` evaluate to? (enter the number)",
                    "prompt_ar": "ما ناتج `12 + 3`؟ (أدخل الرقم)",
                    "options": None,
                    "answer_key": {"accepted": ["15"]},
                    "verify_expr": "12 + 3",
                    "explanation_en": "Both values are integers, so `+` adds them: 15.",
                    "explanation_ar": "القيمتان عددان صحيحان، لذلك يجمع المعامل `+` بينهما: 15.",
                    "difficulty": 1,
                    "is_diagnostic": True,
                },
                {
                    "id": "py:values:q3",
                    "kind": "mcq_single",
                    "prompt_en": 'What is `"12" + "3"`?',
                    "prompt_ar": 'ما ناتج `"12" + "3"`؟',
                    "options": [
                        {"id": "a", "en": "15", "ar": "15"},
                        {"id": "b", "en": "123", "ar": "123"},
                        {"id": "c", "en": "3", "ar": "3"},
                        {"id": "d", "en": "An error", "ar": "خطأ"},
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "Both sides are text, so `+` joins them: '123'.",
                    "explanation_ar": "الطرفان نصان، لذا يقوم `+` بدمجهما: '123'.",
                    "difficulty": 2,
                    "is_diagnostic": False,
                },
            ],
        },
        {
            "id": "py:strings",
            "title_en": "Working with text",
            "title_ar": "التعامل مع النصوص",
            "summary_en": "Join, slice, split, clean and measure text.",
            "summary_ar": "دمج النصوص وتقطيعها وتقسيمها وتنظيفها وقياس طولها.",
            "kind": "skill",
            "bloom_level": "apply",
            "difficulty": 2,
            "prerequisites": ["py:values"],
            "sequence": 20,
            "est_minutes": 25,
            "lesson": {
                "id": "py:strings:lesson",
                "title_en": "Text as a sequence of characters",
                "title_ar": "النص سلسلة من المحارف",
                "est_minutes": 20,
                "body_md_en": (
                    "## Joining\n"
                    '`first + " " + last` joins text. f-strings are clearer: `f"{first} {last}"`.\n\n'
                    "## Measuring and slicing\n"
                    '`len("talimgo")` is 7. `"talimgo"[0]` is `"t"`. `"talimgo"[0:3]` is `"tal"`.\n'
                    "Counting starts at 0 and the end of a slice is excluded.\n\n"
                    "## Splitting and cleaning\n"
                    '`"a,b,c".split(",")` gives `["a", "b", "c"]`.\n'
                    "`.strip()` removes spaces at both ends; `.lower()` changes case.\n\n"
                    "## Formatting numbers\n"
                    '`f"{ratio:.0%}"` prints a ratio as a percentage, e.g. 0.42 becomes "42%".'
                ),
                "body_md_ar": (
                    "## الدمج\n"
                    '`first + " " + last` تدمج النصوص، وf-strings أوضح: `f"{first} {last}"`.\n\n'
                    "## القياس والتقطيع\n"
                    '`len("talimgo")` تساوي 7، و`"talimgo"[0]` تساوي `"t"`، و`"talimgo"[0:3]` تساوي `"tal"`.\n'
                    "العدّ يبدأ من الصفر ونهاية المقطع غير مشمولة.\n\n"
                    "## التقسيم والتنظيف\n"
                    '`"a,b,c".split(",")` تعطي `["a", "b", "c"]`.\n'
                    "`.strip()` تحذف الفراغات من الطرفين، و`.lower()` تغيّر حالة الأحرف.\n\n"
                    "## تنسيق الأعداد\n"
                    '`f"{ratio:.0%}"` تطبع النسبة كنسبة مئوية، فتصبح 0.42 مثلاً "42%".'
                ),
            },
            "items": [
                {
                    "id": "py:strings:q1",
                    "kind": "short_answer",
                    "prompt_en": 'What is `len("talimgo")`?',
                    "prompt_ar": 'ما قيمة `len("talimgo")`؟',
                    "options": None,
                    "answer_key": {"accepted": ["7"]},
                    "verify_expr": 'len("talimgo")',
                    "explanation_en": "The word has 7 characters, so len returns 7.",
                    "explanation_ar": "الكلمة تحتوي 7 محارف، لذا تعيد len القيمة 7.",
                    "difficulty": 1,
                    "is_diagnostic": True,
                },
                {
                    "id": "py:strings:q2",
                    "kind": "mcq_single",
                    "prompt_en": 'What is `"talimgo"[0:3]`?',
                    "prompt_ar": 'ما ناتج `"talimgo"[0:3]`؟',
                    "options": [
                        {"id": "a", "en": "tal", "ar": "tal"},
                        {"id": "b", "en": "tali", "ar": "tali"},
                        {"id": "c", "en": "alim", "ar": "alim"},
                        {"id": "d", "en": "go", "ar": "go"},
                    ],
                    "answer_key": {"option_id": "a"},
                    "explanation_en": "Indexes 0, 1 and 2 are taken; the end index 3 is excluded, so 'tal'.",
                    "explanation_ar": "تُؤخذ الفهارس 0 و1 و2، والفهرس 3 غير مشمول، فالناتج 'tal'.",
                    "difficulty": 2,
                    "is_diagnostic": True,
                },
                {
                    "id": "py:strings:q3",
                    "kind": "mcq_single",
                    "prompt_en": 'What does `"a,b,c".split(",")` return?',
                    "prompt_ar": 'ماذا تعيد `"a,b,c".split(",")`؟',
                    "options": [
                        {"id": "a", "en": "abc", "ar": "abc"},
                        {"id": "b", "en": "['a', 'b', 'c']", "ar": "['a', 'b', 'c']"},
                        {"id": "c", "en": "'a b c'", "ar": "'a b c'"},
                        {"id": "d", "en": "3", "ar": "3"},
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "split returns a list of the parts between separators.",
                    "explanation_ar": "تعيد split قائمة بالأجزاء الواقعة بين الفواصل.",
                    "difficulty": 2,
                    "is_diagnostic": False,
                },
            ],
        },
        {
            "id": "py:conditionals",
            "title_en": "Making decisions",
            "title_ar": "اتخاذ القرارات",
            "summary_en": "Branch with if / elif / else and compare values safely.",
            "summary_ar": "استخدام if وelif وelse والمقارنة بين القيم بأمان.",
            "kind": "skill",
            "bloom_level": "apply",
            "difficulty": 2,
            "prerequisites": ["py:values"],
            "sequence": 30,
            "est_minutes": 30,
            "lesson": {
                "id": "py:conditionals:lesson",
                "title_en": "Branching",
                "title_ar": "التفريع",
                "est_minutes": 25,
                "body_md_en": (
                    "## Comparing\n"
                    "`==` asks a question, `=` assigns. `>=`, `<`, `!=` work as expected.\n\n"
                    "```python\n"
                    "score = 72\n"
                    "if score >= 80:\n"
                    '    print("strong")\n'
                    "elif score >= 60:\n"
                    '    print("pass")\n'
                    "else:\n"
                    '    print("keep practising")\n'
                    "```\n\n"
                    "## Truthiness\n"
                    "Empty text, `0`, `None` and empty lists count as false; almost everything else is true.\n\n"
                    "## Guarding types\n"
                    "Comparing a number to text raises `TypeError`: convert first with `int()` or `float()`."
                ),
                "body_md_ar": (
                    "## المقارنة\n"
                    "`==` تسأل سؤالاً أما `=` فتُسند قيمة. و`>=` و`<` و`!=` تعمل كما هو متوقع.\n\n"
                    "```python\n"
                    "score = 72\n"
                    "if score >= 80:\n"
                    '    print("ممتاز")\n'
                    "elif score >= 60:\n"
                    '    print("ناجح")\n'
                    "else:\n"
                    '    print("واصل التدريب")\n'
                    "```\n\n"
                    "## القيمة المنطقية الضمنية\n"
                    "النص الفارغ و`0` و`None` والقوائم الفارغة تُعدّ خطأ، وما عداها غالباً صحيح.\n\n"
                    "## حماية الأنواع\n"
                    "مقارنة عدد بنص تُطلق `TypeError`، لذا حوّل القيمة أولاً بـ `int()` أو `float()`."
                ),
            },
            "items": [
                {
                    "id": "py:conditionals:q1",
                    "kind": "mcq_single",
                    "prompt_en": "With `score = 72`, what does the branching example print?",
                    "prompt_ar": "إذا كانت `score = 72` فماذا يطبع مثال التفريع؟",
                    "options": [
                        {"id": "a", "en": "strong", "ar": "strong"},
                        {"id": "b", "en": "pass", "ar": "pass"},
                        {"id": "c", "en": "keep practising", "ar": "keep practising"},
                        {"id": "d", "en": "Nothing", "ar": "لا شيء"},
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "72 is below 80 but reaches the elif branch (>= 60), so 'pass'.",
                    "explanation_ar": "72 أقل من 80 لكنه يحقق فرع elif (أكبر من أو يساوي 60)، فالناتج 'pass'.",
                    "difficulty": 2,
                    "is_diagnostic": True,
                },
                {
                    "id": "py:conditionals:q2",
                    "kind": "short_answer",
                    "prompt_en": "Which operator asks whether two values are equal? (write the operator)",
                    "prompt_ar": "ما المعامل الذي يسأل: هل القيمتان متساويتان؟ (اكتب المعامل)",
                    "options": None,
                    "answer_key": {"accepted": ["==", "=="]},
                    "explanation_en": "`==` compares values; a single `=` assigns.",
                    "explanation_ar": "`==` يقارن القيم، أما `=` المفرد فيُسند.",
                    "difficulty": 1,
                    "is_diagnostic": False,
                },
                {
                    "id": "py:conditionals:q3",
                    "kind": "mcq_single",
                    "prompt_en": "Which value is treated as false in a condition?",
                    "prompt_ar": "أي قيمة تُعدّ خطأ في الشرط؟",
                    "options": [
                        {"id": "a", "en": '"0" (text)', "ar": '"0" (نص)'},
                        {"id": "b", "en": "0 (number)", "ar": "0 (عدد)"},
                        {"id": "c", "en": "[0]", "ar": "[0]"},
                        {"id": "d", "en": "1", "ar": "1"},
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "The number 0 is false; the text '0' and the list [0] are non-empty, so they are true.",
                    "explanation_ar": "العدد 0 خطأ، أما النص '0' والقائمة [0] فغير فارغين لذا تُعدّان صحيحاً.",
                    "difficulty": 3,
                    "is_diagnostic": False,
                },
            ],
        },
        {
            "id": "py:loops",
            "title_en": "Repeating work",
            "title_ar": "تكرار العمل",
            "summary_en": "Use for and while loops, with ranges and accumulators.",
            "summary_ar": "استخدام حلقتَي for وwhile مع النطاقات والمُجمِّعات.",
            "kind": "skill",
            "bloom_level": "apply",
            "difficulty": 3,
            "prerequisites": ["py:values", "py:conditionals"],
            "sequence": 40,
            "est_minutes": 35,
            "lesson": {
                "id": "py:loops:lesson",
                "title_en": "Doing something many times",
                "title_ar": "تكرار الشيء مرات عديدة",
                "est_minutes": 25,
                "body_md_en": (
                    "## for with range\n"
                    "```python\n"
                    "total = 0\n"
                    "for number in range(1, 4):   # 1, 2, 3\n"
                    "    total = total + number\n"
                    "print(total)                 # 6\n"
                    "```\n"
                    "`range(1, 4)` stops before 4.\n\n"
                    "## Accumulating\n"
                    "Start the accumulator before the loop (0 for sums, 1 for products).\n\n"
                    "## while\n"
                    "Use `while` when you do not know how many repeats you need; make sure something "
                    "inside the loop changes, or it never ends."
                ),
                "body_md_ar": (
                    "## حلقة for مع النطاق\n"
                    "```python\n"
                    "total = 0\n"
                    "for number in range(1, 4):   # 1, 2, 3\n"
                    "    total = total + number\n"
                    "print(total)                 # 6\n"
                    "```\n"
                    "`range(1, 4)` تتوقف قبل 4.\n\n"
                    "## التجميع\n"
                    "ابدأ المُجمِّع قبل الحلقة (0 للمجموع و1 للجداء).\n\n"
                    "## حلقة while\n"
                    "استخدم `while` عندما لا تعرف عدد التكرارات مسبقاً، وتأكد من تغيّر شيء داخل الحلقة "
                    "وإلا فلن تنتهي أبداً."
                ),
            },
            "items": [
                {
                    "id": "py:loops:q1",
                    "kind": "short_answer",
                    "prompt_en": "What does the loop example print? (enter the number)",
                    "prompt_ar": "ماذا تطبع الحلقة في المثال؟ (أدخل الرقم)",
                    "options": None,
                    "answer_key": {"accepted": ["6"]},
                    "verify_expr": "sum(range(1, 4))",
                    "explanation_en": "1 + 2 + 3 = 6; range stops before the end value.",
                    "explanation_ar": "1 + 2 + 3 = 6، وrange تتوقف قبل القيمة الأخيرة.",
                    "difficulty": 2,
                    "is_diagnostic": True,
                },
                {
                    "id": "py:loops:q2",
                    "kind": "mcq_single",
                    "prompt_en": "How many times does `for i in range(0, 5)` run?",
                    "prompt_ar": "كم مرة تُنفَّذ `for i in range(0, 5)`؟",
                    "options": [
                        {"id": "a", "en": "4", "ar": "4"},
                        {"id": "b", "en": "5", "ar": "5"},
                        {"id": "c", "en": "6", "ar": "6"},
                        {"id": "d", "en": "Infinite", "ar": "لا نهائي"},
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "range(0, 5) yields 0, 1, 2, 3, 4 — five values.",
                    "explanation_ar": "range(0, 5) تعطي 0 و1 و2 و3 و4، أي خمس قيم.",
                    "difficulty": 2,
                    "is_diagnostic": True,
                },
                {
                    "id": "py:loops:q3",
                    "kind": "mcq_single",
                    "prompt_en": "What most often causes a `while` loop never to end?",
                    "prompt_ar": "ما السبب الأكثر شيوعاً لعدم انتهاء حلقة `while`؟",
                    "options": [
                        {
                            "id": "a",
                            "en": "The condition never becomes false",
                            "ar": "الشرط لا يصبح خطأ أبداً",
                        },
                        {"id": "b", "en": "Using print inside it", "ar": "استخدام print داخلها"},
                        {"id": "c", "en": "Using a variable", "ar": "استخدام متغير"},
                        {"id": "d", "en": "Starting the accumulator at 0", "ar": "البدء بالمُجمِّع من 0"},
                    ],
                    "answer_key": {"option_id": "a"},
                    "explanation_en": "If nothing inside the loop changes the condition, it stays true forever.",
                    "explanation_ar": "إذا لم يغيّر شيء داخل الحلقة الشرط، فسيبقى صحيحاً إلى الأبد.",
                    "difficulty": 2,
                    "is_diagnostic": False,
                },
            ],
        },
        {
            "id": "py:lists",
            "title_en": "Storing sequences",
            "title_ar": "تخزين المتتاليات",
            "summary_en": "Create lists, read and change items, loop over them, and use the common helpers.",
            "summary_ar": "إنشاء القوائم وقراءة عناصرها وتعديلها والمرور عليها واستخدام الدوال الشائعة.",
            "kind": "skill",
            "bloom_level": "apply",
            "difficulty": 3,
            "prerequisites": ["py:values", "py:loops"],
            "sequence": 50,
            "est_minutes": 30,
            "lesson": {
                "id": "py:lists:lesson",
                "title_en": "Lists",
                "title_ar": "القوائم",
                "est_minutes": 25,
                "body_md_en": (
                    "## Creating and reading\n"
                    "`scores = [70, 85, 60]`; `scores[0]` is 70, `scores[-1]` is 60.\n\n"
                    "## Changing\n"
                    "`scores.append(90)` adds to the end; `scores[1] = 88` replaces an item.\n\n"
                    "## Looping\n"
                    "```python\n"
                    "for score in scores:\n"
                    "    print(score)\n"
                    "```\n\n"
                    "## Useful helpers\n"
                    "`len(scores)`, `sum(scores)`, `sorted(scores)`, `max(scores)`, `min(scores)`.\n"
                    "`sum(scores) / len(scores)` is the average — guard against an empty list first."
                ),
                "body_md_ar": (
                    "## الإنشاء والقراءة\n"
                    "`scores = [70, 85, 60]`، و`scores[0]` تساوي 70، و`scores[-1]` تساوي 60.\n\n"
                    "## التعديل\n"
                    "`scores.append(90)` تضيف في النهاية، و`scores[1] = 88` تستبدل عنصراً.\n\n"
                    "## المرور على العناصر\n"
                    "```python\n"
                    "for score in scores:\n"
                    "    print(score)\n"
                    "```\n\n"
                    "## دوال مفيدة\n"
                    "`len(scores)` و`sum(scores)` و`sorted(scores)` و`max(scores)` و`min(scores)`.\n"
                    "`sum(scores) / len(scores)` هي المتوسط، لكن احمِ نفسك من قائمة فارغة أولاً."
                ),
            },
            "items": [
                {
                    "id": "py:lists:q1",
                    "kind": "short_answer",
                    "prompt_en": "For `scores = [70, 85, 60]`, what is `sum(scores)`?",
                    "prompt_ar": "إذا كانت `scores = [70, 85, 60]` فما قيمة `sum(scores)`؟",
                    "options": None,
                    "answer_key": {"accepted": ["215"]},
                    "verify_expr": "sum([70, 85, 60])",
                    "explanation_en": "70 + 85 + 60 = 215.",
                    "explanation_ar": "70 + 85 + 60 = 215.",
                    "difficulty": 1,
                    "is_diagnostic": True,
                },
                {
                    "id": "py:lists:q2",
                    "kind": "mcq_single",
                    "prompt_en": 'What is `["a", "b", "c"][-1]`?',
                    "prompt_ar": 'ما قيمة `["a", "b", "c"][-1]`؟',
                    "options": [
                        {"id": "a", "en": '"a"', "ar": '"a"'},
                        {"id": "b", "en": '"c"', "ar": '"c"'},
                        {"id": "c", "en": "An error", "ar": "خطأ"},
                        {"id": "d", "en": "3", "ar": "3"},
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "A negative index counts from the end, so -1 is the last item.",
                    "explanation_ar": "الفهرس السالب يُعدّ من النهاية، لذا -1 هو العنصر الأخير.",
                    "difficulty": 2,
                    "is_diagnostic": False,
                },
                {
                    "id": "py:lists:q3",
                    "kind": "mcq_single",
                    "prompt_en": "Which line adds 90 to the end of `scores`?",
                    "prompt_ar": "أي سطر يضيف 90 إلى نهاية `scores`؟",
                    "options": [
                        {"id": "a", "en": "scores.add(90)", "ar": "scores.add(90)"},
                        {"id": "b", "en": "scores.append(90)", "ar": "scores.append(90)"},
                        {"id": "c", "en": "scores + 90", "ar": "scores + 90"},
                        {"id": "d", "en": "scores[90]", "ar": "scores[90]"},
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "append adds a single item to the end of a list.",
                    "explanation_ar": "append تضيف عنصراً واحداً إلى نهاية القائمة.",
                    "difficulty": 1,
                    "is_diagnostic": False,
                },
            ],
        },
        {
            "id": "py:dicts",
            "title_en": "Key–value data with dictionaries",
            "title_ar": "بيانات المفتاح والقيمة عبر القواميس",
            "summary_en": "Store records, look values up safely, and loop over keys and values.",
            "summary_ar": "تخزين السجلات والبحث الآمن عن القيم والمرور على المفاتيح والقيم.",
            "kind": "skill",
            "bloom_level": "apply",
            "difficulty": 3,
            "prerequisites": ["py:lists"],
            "sequence": 60,
            "est_minutes": 30,
            "lesson": {
                "id": "py:dicts:lesson",
                "title_en": "Dictionaries",
                "title_ar": "القواميس",
                "est_minutes": 25,
                "body_md_en": (
                    "## A record\n"
                    '```python\nstudent = {"name": "Amina", "score": 88}\n'
                    'print(student["name"])        # Amina\n```\n\n'
                    "## Missing keys\n"
                    '`student["age"]` raises `KeyError`. `student.get("age", 0)` returns 0 instead.\n\n'
                    "## Looping\n"
                    "```python\nfor key, value in student.items():\n    print(key, value)\n```\n\n"
                    "## Counting\n"
                    "A common pattern: `counts[word] = counts.get(word, 0) + 1`."
                ),
                "body_md_ar": (
                    "## سجل واحد\n"
                    '```python\nstudent = {"name": "أمينة", "score": 88}\n'
                    'print(student["name"])        # أمينة\n```\n\n'
                    "## مفاتيح غير موجودة\n"
                    '`student["age"]` تُطلق `KeyError`، أما `student.get("age", 0)` فتعيد 0.\n\n'
                    "## المرور على العناصر\n"
                    "```python\nfor key, value in student.items():\n    print(key, value)\n```\n\n"
                    "## العدّ\n"
                    "نمط شائع: `counts[word] = counts.get(word, 0) + 1`."
                ),
            },
            "items": [
                {
                    "id": "py:dicts:q1",
                    "kind": "short_answer",
                    "prompt_en": 'For `student = {"name": "Amina", "score": 88}`, what is `student["score"]`?',
                    "prompt_ar": 'إذا كان `student = {"name": "أمينة", "score": 88}` فما قيمة `student["score"]`؟',
                    "options": None,
                    "answer_key": {"accepted": ["88"]},
                    "explanation_en": "Indexing by key name returns the stored value, 88.",
                    "explanation_ar": "الفهرسة باسم المفتاح تعيد القيمة المخزنة، وهي 88.",
                    "difficulty": 1,
                    "is_diagnostic": True,
                },
                {
                    "id": "py:dicts:q2",
                    "kind": "mcq_single",
                    "prompt_en": 'Which expression avoids a `KeyError` when "age" may be missing?',
                    "prompt_ar": 'أي تعبير يتجنب `KeyError` عندما يكون المفتاح "age" غير موجود؟',
                    "options": [
                        {"id": "a", "en": 'student["age"]', "ar": 'student["age"]'},
                        {"id": "b", "en": 'student.get("age", 0)', "ar": 'student.get("age", 0)'},
                        {"id": "c", "en": "student.age", "ar": "student.age"},
                        {"id": "d", "en": 'student["age", 0]', "ar": 'student["age", 0]'},
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "get returns the default instead of raising when the key is missing.",
                    "explanation_ar": "تعيد get القيمة الافتراضية بدل إطلاق خطأ عند غياب المفتاح.",
                    "difficulty": 2,
                    "is_diagnostic": False,
                },
                {
                    "id": "py:dicts:q3",
                    "kind": "mcq_single",
                    "prompt_en": "What does `student.items()` give you in a `for` loop?",
                    "prompt_ar": "ماذا تعطيك `student.items()` في حلقة `for`؟",
                    "options": [
                        {"id": "a", "en": "Keys only", "ar": "المفاتيح فقط"},
                        {"id": "b", "en": "Values only", "ar": "القيم فقط"},
                        {"id": "c", "en": "Pairs of key and value", "ar": "أزواجاً من المفتاح والقيمة"},
                        {"id": "d", "en": "The number of keys", "ar": "عدد المفاتيح"},
                    ],
                    "answer_key": {"option_id": "c"},
                    "explanation_en": "items yields (key, value) tuples, which unpack into two variables.",
                    "explanation_ar": "تعيد items أزواجاً (مفتاح، قيمة) يمكن توزيعها على متغيرين.",
                    "difficulty": 2,
                    "is_diagnostic": False,
                },
            ],
        },
        {
            "id": "py:functions",
            "title_en": "Functions",
            "title_ar": "الدوال",
            "summary_en": "Package work into named, reusable units with parameters and return values.",
            "summary_ar": "تغليف العمل في وحدات مسمّاة قابلة لإعادة الاستخدام بمعاملات وقيم معادة.",
            "kind": "skill",
            "bloom_level": "apply",
            "difficulty": 4,
            "prerequisites": ["py:conditionals", "py:loops"],
            "sequence": 70,
            "est_minutes": 35,
            "lesson": {
                "id": "py:functions:lesson",
                "title_en": "Functions",
                "title_ar": "الدوال",
                "est_minutes": 25,
                "body_md_en": (
                    "## Defining\n"
                    "```python\n"
                    "def average(numbers):\n"
                    "    if not numbers:\n"
                    "        return 0\n"
                    "    return sum(numbers) / len(numbers)\n"
                    "```\n\n"
                    "## Return values\n"
                    "`return` sends a value back and ends the function. Without it, a function returns `None`.\n\n"
                    "## Parameters and defaults\n"
                    '`def greet(name, punctuation="!"):` lets callers omit the second argument.\n\n'
                    "## Small functions\n"
                    "A function that does one thing is easier to test than one that does five."
                ),
                "body_md_ar": (
                    "## التعريف\n"
                    "```python\n"
                    "def average(numbers):\n"
                    "    if not numbers:\n"
                    "        return 0\n"
                    "    return sum(numbers) / len(numbers)\n"
                    "```\n\n"
                    "## القيم المعادة\n"
                    "`return` تعيد قيمة وتنهي الدالة، وبدونها تعيد الدالة `None`.\n\n"
                    "## المعاملات والقيم الافتراضية\n"
                    '`def greet(name, punctuation="!")` تسمح للمستدعي بحذف الوسيط الثاني.\n\n'
                    "## دوال صغيرة\n"
                    "الدالة التي تفعل شيئاً واحداً أسهل اختباراً من دالة تفعل خمسة أشياء."
                ),
            },
            "items": [
                {
                    "id": "py:functions:q1",
                    "kind": "short_answer",
                    "prompt_en": "In the example, what is `average([2, 4, 6])`?",
                    "prompt_ar": "في المثال، ما قيمة `average([2, 4, 6])`؟",
                    "options": None,
                    "answer_key": {"accepted": ["4", "4.0"]},
                    "verify_expr": "sum([2, 4, 6]) / len([2, 4, 6])",
                    "explanation_en": "The sum is 12 and there are 3 items, so the average is 4.",
                    "explanation_ar": "المجموع 12 وعدد العناصر 3، فالمتوسط يساوي 4.",
                    "difficulty": 2,
                    "is_diagnostic": True,
                },
                {
                    "id": "py:functions:q2",
                    "kind": "mcq_single",
                    "prompt_en": "What does a function return if it has no `return` statement?",
                    "prompt_ar": "ماذا تعيد الدالة إذا لم تحتوِ على `return`؟",
                    "options": [
                        {"id": "a", "en": "0", "ar": "0"},
                        {"id": "b", "en": '""', "ar": '""'},
                        {"id": "c", "en": "None", "ar": "None"},
                        {"id": "d", "en": "An error", "ar": "خطأ"},
                    ],
                    "answer_key": {"option_id": "c"},
                    "explanation_en": "Python functions return None when there is no return statement.",
                    "explanation_ar": "تعيد دوال بايثون القيمة None عند غياب عبارة return.",
                    "difficulty": 2,
                    "is_diagnostic": False,
                },
                {
                    "id": "py:functions:q3",
                    "kind": "mcq_single",
                    "prompt_en": "Why does `average([])` return 0 in the example?",
                    "prompt_ar": "لماذا تعيد `average([])` القيمة 0 في المثال؟",
                    "options": [
                        {
                            "id": "a",
                            "en": "Because the guard returns early for an empty list",
                            "ar": "لأن الحماية تُرجع مبكراً عند قائمة فارغة",
                        },
                        {
                            "id": "b",
                            "en": "Because sum([]) is 0 and len([]) is 1",
                            "ar": "لأن sum([]) تساوي 0 وlen([]) تساوي 1",
                        },
                        {"id": "c", "en": "Because division rounds down", "ar": "لأن القسمة تُقرّب للأسفل"},
                        {
                            "id": "d",
                            "en": "It actually raises ZeroDivisionError",
                            "ar": "بل تُطلق ZeroDivisionError",
                        },
                    ],
                    "answer_key": {"option_id": "a"},
                    "explanation_en": "Dividing by len([]) would raise ZeroDivisionError; the guard prevents that.",
                    "explanation_ar": "القسمة على len([]) تُطلق ZeroDivisionError، والحماية تمنع ذلك.",
                    "difficulty": 4,
                    "is_diagnostic": True,
                },
            ],
        },
        {
            "id": "py:errors",
            "title_en": "Reading and handling errors",
            "title_ar": "قراءة الأخطاء ومعالجتها",
            "summary_en": "Read a traceback, catch the exceptions you expect, and avoid silent failures.",
            "summary_ar": "قراءة سجل الأخطاء والتقاط الاستثناءات المتوقعة وتجنب الفشل الصامت.",
            "kind": "skill",
            "bloom_level": "analyse",
            "difficulty": 4,
            "prerequisites": ["py:functions"],
            "sequence": 80,
            "est_minutes": 30,
            "lesson": {
                "id": "py:errors:lesson",
                "title_en": "Errors are information",
                "title_ar": "الأخطاء معلومة",
                "est_minutes": 25,
                "body_md_en": (
                    "## Reading a traceback\n"
                    "Read the **last line** first: it names the error. Then find the last line of *your* "
                    "code in the stack.\n\n"
                    "## Common ones\n"
                    "`NameError` (typo or undefined name), `TypeError` (wrong kind of value), "
                    '`ValueError` (`int("abc")`), `KeyError`, `IndexError`, `ZeroDivisionError`.\n\n'
                    "## Handling what you expect\n"
                    "```python\n"
                    "try:\n"
                    "    age = int(text)\n"
                    "except ValueError:\n"
                    "    age = None\n"
                    "```\n"
                    "Catch only the exceptions you can actually handle — a bare `except:` hides real bugs."
                ),
                "body_md_ar": (
                    "## قراءة سجل الخطأ\n"
                    "اقرأ **السطر الأخير** أولاً فهو يسمّي الخطأ، ثم ابحث عن آخر سطر من كودك في السجل.\n\n"
                    "## أخطاء شائعة\n"
                    "`NameError` (اسم خاطئ أو غير معرّف)، `TypeError` (نوع قيمة غير مناسب)، "
                    '`ValueError` عند `int("abc")`، و`KeyError` و`IndexError` و`ZeroDivisionError`.\n\n'
                    "## معالجة المتوقع\n"
                    "```python\n"
                    "try:\n"
                    "    age = int(text)\n"
                    "except ValueError:\n"
                    "    age = None\n"
                    "```\n"
                    "التقط فقط الاستثناءات التي تستطيع معالجتها فعلاً، فـ `except:` المجرّدة تخفي أخطاء حقيقية."
                ),
            },
            "items": [
                {
                    "id": "py:errors:q1",
                    "kind": "mcq_single",
                    "prompt_en": 'Which exception does `int("abc")` raise?',
                    "prompt_ar": 'أي استثناء تُطلقه `int("abc")`؟',
                    "options": [
                        {"id": "a", "en": "TypeError", "ar": "TypeError"},
                        {"id": "b", "en": "ValueError", "ar": "ValueError"},
                        {"id": "c", "en": "NameError", "ar": "NameError"},
                        {"id": "d", "en": "KeyError", "ar": "KeyError"},
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "The type is right (text) but the value cannot be converted, so ValueError.",
                    "explanation_ar": "النوع مناسب (نص) لكن القيمة غير قابلة للتحويل، لذا ValueError.",
                    "difficulty": 3,
                    "is_diagnostic": True,
                },
                {
                    "id": "py:errors:q2",
                    "kind": "mcq_single",
                    "prompt_en": "In a traceback, which line tells you what went wrong?",
                    "prompt_ar": "في سجل الخطأ، أي سطر يخبرك بما حدث؟",
                    "options": [
                        {"id": "a", "en": "The first line", "ar": "السطر الأول"},
                        {"id": "b", "en": "The last line", "ar": "السطر الأخير"},
                        {"id": "c", "en": "The longest line", "ar": "أطول سطر"},
                        {"id": "d", "en": "None of them", "ar": "لا شيء منها"},
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "The final line names the exception and gives its message.",
                    "explanation_ar": "السطر الأخير يسمّي الاستثناء ويعطي رسالته.",
                    "difficulty": 2,
                    "is_diagnostic": False,
                },
                {
                    "id": "py:errors:q3",
                    "kind": "mcq_single",
                    "prompt_en": "Why is a bare `except:` discouraged?",
                    "prompt_ar": "لماذا يُنصح بتجنب `except:` المجرّدة؟",
                    "options": [
                        {"id": "a", "en": "It is slower", "ar": "لأنها أبطأ"},
                        {
                            "id": "b",
                            "en": "It hides unexpected errors, including real bugs",
                            "ar": "لأنها تخفي أخطاء غير متوقعة، ومنها أخطاء حقيقية",
                        },
                        {"id": "c", "en": "It only works with files", "ar": "لأنها تعمل مع الملفات فقط"},
                        {"id": "d", "en": "It cannot be indented", "ar": "لأنها لا تقبل الإزاحة"},
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "Catching everything also catches mistakes you want to see and fix.",
                    "explanation_ar": "التقاط كل شيء يخفي أيضاً أخطاءً تريد رؤيتها وإصلاحها.",
                    "difficulty": 3,
                    "is_diagnostic": False,
                },
            ],
        },
        {
            "id": "py:files",
            "title_en": "Reading and writing files",
            "title_ar": "قراءة الملفات وكتابتها",
            "summary_en": "Open files safely with `with`, read lines, write text, and close properly.",
            "summary_ar": "فتح الملفات بأمان باستخدام `with` وقراءة الأسطر وكتابة النص والإغلاق السليم.",
            "kind": "skill",
            "bloom_level": "apply",
            "difficulty": 4,
            "prerequisites": ["py:functions", "py:errors"],
            "sequence": 90,
            "est_minutes": 25,
            "lesson": {
                "id": "py:files:lesson",
                "title_en": "Files and context managers",
                "title_ar": "الملفات ومديرو السياق",
                "est_minutes": 20,
                "body_md_en": (
                    "## Reading\n"
                    "```python\n"
                    'with open("notes.txt", encoding="utf-8") as handle:\n'
                    "    text = handle.read()\n"
                    "```\n"
                    "`with` closes the file even if an error happens inside the block.\n\n"
                    "## Writing\n"
                    '`open("out.txt", "w")` replaces the file; `"a"` appends.\n\n'
                    "## Line by line\n"
                    "`for line in handle:` keeps memory small for large files; remember each line keeps "
                    "its `\\n`."
                ),
                "body_md_ar": (
                    "## القراءة\n"
                    "```python\n"
                    'with open("notes.txt", encoding="utf-8") as handle:\n'
                    "    text = handle.read()\n"
                    "```\n"
                    "`with` تغلق الملف حتى لو حدث خطأ داخل الكتلة.\n\n"
                    "## الكتابة\n"
                    'النمط `open("out.txt", "w")` يستبدل الملف، والوضع `"a"` يضيف إليه.\n\n'
                    "## سطراً بسطر\n"
                    "`for line in handle:` يستهلك ذاكرة أقل مع الملفات الكبيرة، وتذكّر أن كل سطر يحتفظ "
                    "بمحرف السطر الجديد."
                ),
            },
            "items": [
                {
                    "id": "py:files:q1",
                    "kind": "mcq_single",
                    "prompt_en": "Why is `with open(...)` preferred over calling `open` directly?",
                    "prompt_ar": "لماذا يُفضَّل `with open(...)` على استدعاء `open` مباشرة؟",
                    "options": [
                        {
                            "id": "a",
                            "en": "It closes the file automatically, even on error",
                            "ar": "لأنها تغلق الملف تلقائياً حتى عند الخطأ",
                        },
                        {"id": "b", "en": "It reads faster", "ar": "لأنها أسرع في القراءة"},
                        {"id": "c", "en": "It compresses the file", "ar": "لأنها تضغط الملف"},
                        {"id": "d", "en": "It encrypts the contents", "ar": "لأنها تشفّر المحتوى"},
                    ],
                    "answer_key": {"option_id": "a"},
                    "explanation_en": "The context manager guarantees the file is closed when the block ends.",
                    "explanation_ar": "مدير السياق يضمن إغلاق الملف عند انتهاء الكتلة.",
                    "difficulty": 3,
                    "is_diagnostic": True,
                },
                {
                    "id": "py:files:q2",
                    "kind": "mcq_single",
                    "prompt_en": "Which mode appends to an existing file without erasing it?",
                    "prompt_ar": "أي وضع يضيف إلى ملف موجود دون محوه؟",
                    "options": [
                        {"id": "a", "en": '"r"', "ar": '"r"'},
                        {"id": "b", "en": '"w"', "ar": '"w"'},
                        {"id": "c", "en": '"a"', "ar": '"a"'},
                        {"id": "d", "en": '"x"', "ar": '"x"'},
                    ],
                    "answer_key": {"option_id": "c"},
                    "explanation_en": "'a' appends; 'w' would truncate the file first.",
                    "explanation_ar": "'a' تضيف، أما 'w' فتحذف المحتوى أولاً.",
                    "difficulty": 2,
                    "is_diagnostic": False,
                },
                {
                    "id": "py:files:q3",
                    "kind": "mcq_single",
                    "prompt_en": 'What happens with `open("missing.txt")` when the file does not exist?',
                    "prompt_ar": 'ماذا يحدث عند `open("missing.txt")` إذا لم يكن الملف موجوداً؟',
                    "options": [
                        {"id": "a", "en": "It creates an empty file", "ar": "ينشئ ملفاً فارغاً"},
                        {"id": "b", "en": "It raises FileNotFoundError", "ar": "يُطلق FileNotFoundError"},
                        {"id": "c", "en": "It returns None", "ar": "يعيد None"},
                        {"id": "d", "en": "It returns an empty string", "ar": "يعيد نصاً فارغاً"},
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "Reading mode requires the file to exist; a missing one raises FileNotFoundError.",
                    "explanation_ar": "وضع القراءة يتطلب وجود الملف، وغيابه يُطلق FileNotFoundError.",
                    "difficulty": 3,
                    "is_diagnostic": False,
                },
            ],
        },
        {
            "id": "py:modules",
            "title_en": "Modules and imports",
            "title_ar": "الوحدات والاستيراد",
            "summary_en": "Split code across files, import what you need, and use the standard library.",
            "summary_ar": "تقسيم الكود بين ملفات واستيراد ما تحتاجه واستخدام المكتبة القياسية.",
            "kind": "skill",
            "bloom_level": "analyse",
            "difficulty": 4,
            "prerequisites": ["py:functions"],
            "sequence": 100,
            "est_minutes": 25,
            "lesson": {
                "id": "py:modules:lesson",
                "title_en": "Modules",
                "title_ar": "الوحدات",
                "est_minutes": 20,
                "body_md_en": (
                    "## Importing\n"
                    "`import math` then `math.sqrt(9)`. Or `from math import sqrt` then `sqrt(9)`.\n\n"
                    "## Your own module\n"
                    "Any `.py` file is a module: `from helpers import average`.\n\n"
                    "## The main guard\n"
                    "```python\n"
                    'if __name__ == "__main__":\n'
                    "    main()\n"
                    "```\n"
                    "This runs code only when the file is executed directly, not when it is imported."
                ),
                "body_md_ar": (
                    "## الاستيراد\n"
                    "`import math` ثم `math.sqrt(9)`، أو `from math import sqrt` ثم `sqrt(9)`.\n\n"
                    "## وحدتك الخاصة\n"
                    "أي ملف `.py` هو وحدة: `from helpers import average`.\n\n"
                    "## حماية البرنامج الرئيسي\n"
                    "```python\n"
                    'if __name__ == "__main__":\n'
                    "    main()\n"
                    "```\n"
                    "هذا ينفّذ الكود فقط عند تشغيل الملف مباشرة، لا عند استيراده."
                ),
            },
            "items": [
                {
                    "id": "py:modules:q1",
                    "kind": "mcq_single",
                    "prompt_en": "After `import math`, how do you call the square root of 9?",
                    "prompt_ar": "بعد `import math` كيف تستدعي الجذر التربيعي للعدد 9؟",
                    "options": [
                        {"id": "a", "en": "sqrt(9)", "ar": "sqrt(9)"},
                        {"id": "b", "en": "math.sqrt(9)", "ar": "math.sqrt(9)"},
                        {"id": "c", "en": "math(sqrt, 9)", "ar": "math(sqrt, 9)"},
                        {"id": "d", "en": "import sqrt(9)", "ar": "import sqrt(9)"},
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "A plain import keeps the module name as the prefix.",
                    "explanation_ar": "الاستيراد العادي يحتفظ باسم الوحدة كبادئة.",
                    "difficulty": 2,
                    "is_diagnostic": True,
                },
                {
                    "id": "py:modules:q2",
                    "kind": "mcq_single",
                    "prompt_en": 'What is the purpose of `if __name__ == "__main__":`?',
                    "prompt_ar": 'ما الهدف من `if __name__ == "__main__":`؟',
                    "options": [
                        {
                            "id": "a",
                            "en": "Run code only when the file is executed directly",
                            "ar": "تشغيل الكود فقط عند تنفيذ الملف مباشرة",
                        },
                        {
                            "id": "b",
                            "en": "Import every module automatically",
                            "ar": "استيراد كل الوحدات تلقائياً",
                        },
                        {
                            "id": "c",
                            "en": "Make the file executable on Linux",
                            "ar": "جعل الملف قابلاً للتنفيذ على لينكس",
                        },
                        {"id": "d", "en": "Start a web server", "ar": "تشغيل خادم ويب"},
                    ],
                    "answer_key": {"option_id": "a"},
                    "explanation_en": "Imported modules get their own __name__, so the block is skipped on import.",
                    "explanation_ar": "الوحدات المستوردة تحصل على قيمة __name__ مختلفة، فتُتجاهل الكتلة عند الاستيراد.",
                    "difficulty": 3,
                    "is_diagnostic": False,
                },
                {
                    "id": "py:modules:q3",
                    "kind": "short_answer",
                    "prompt_en": "Which keyword makes the contents of another module available? (one word)",
                    "prompt_ar": "ما الكلمة المفتاحية التي تجعل محتوى وحدة أخرى متاحاً؟ (كلمة واحدة)",
                    "options": None,
                    "answer_key": {"accepted": ["import"]},
                    "explanation_en": "`import` loads a module and binds its name in the current file.",
                    "explanation_ar": "`import` تحمّل الوحدة وتربط اسمها في الملف الحالي.",
                    "difficulty": 1,
                    "is_diagnostic": False,
                },
            ],
        },
        {
            "id": "py:debug",
            "title_en": "Debugging a program",
            "title_ar": "تصحيح البرامج",
            "summary_en": "Find the real cause of a bug by reading state, reducing the problem and testing assumptions.",
            "summary_ar": "إيجاد السبب الحقيقي للخطأ بفحص الحالة وتقليص المشكلة واختبار الافتراضات.",
            "kind": "skill",
            "bloom_level": "analyse",
            "difficulty": 4,
            "prerequisites": ["py:errors", "py:loops"],
            "sequence": 110,
            "est_minutes": 30,
            "lesson": {
                "id": "py:debug:lesson",
                "title_en": "A method, not luck",
                "title_ar": "منهج لا حظ",
                "est_minutes": 25,
                "body_md_en": (
                    "## 1. Reproduce it\n"
                    "Find the smallest input that shows the bug.\n\n"
                    "## 2. Read the state\n"
                    "Print the values just before the failing line, or use `breakpoint()` to inspect them.\n\n"
                    "## 3. Halve the search\n"
                    "Comment out half the work; which half still fails?\n\n"
                    "## 4. Test your assumption\n"
                    "The bug is usually a belief you never checked — the type of a value, the length of a "
                    "list, whether a file exists.\n\n"
                    "> Debugging is not guessing faster; it is making the program tell you what it knows."
                ),
                "body_md_ar": (
                    "## 1. أعد إنتاج الخطأ\n"
                    "ابحث عن أصغر مدخل يُظهر المشكلة.\n\n"
                    "## 2. افحص الحالة\n"
                    "اطبع القيم قبل السطر الذي يفشل، أو استخدم `breakpoint()` لفحصها.\n\n"
                    "## 3. اقسم البحث\n"
                    "عطّل نصف العمل مؤقتاً: أي نصف ما زال يفشل؟\n\n"
                    "## 4. اختبر افتراضك\n"
                    "الخطأ غالباً اعتقاد لم تختبره: نوع قيمة، أو طول قائمة، أو وجود ملف.\n\n"
                    "> التصحيح ليس تخميناً أسرع، بل جعل البرنامج يخبرك بما يعرفه."
                ),
            },
            "items": [
                {
                    "id": "py:debug:q1",
                    "kind": "mcq_single",
                    "prompt_en": "A program fails only for some inputs. What is the best first step?",
                    "prompt_ar": "يفشل البرنامج مع بعض المدخلات فقط. ما أفضل خطوة أولى؟",
                    "options": [
                        {"id": "a", "en": "Rewrite the whole program", "ar": "إعادة كتابة البرنامج بالكامل"},
                        {
                            "id": "b",
                            "en": "Find the smallest input that still fails",
                            "ar": "إيجاد أصغر مدخل يفشل",
                        },
                        {
                            "id": "c",
                            "en": "Add random prints everywhere",
                            "ar": "إضافة طباعات عشوائية في كل مكان",
                        },
                        {
                            "id": "d",
                            "en": "Change the code until the error disappears",
                            "ar": "تغيير الكود حتى يختفي الخطأ",
                        },
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "A minimal reproduction turns a vague bug into a specific, testable case.",
                    "explanation_ar": "أصغر حالة تُنتج الخطأ تحوّل مشكلة غامضة إلى حالة محددة قابلة للاختبار.",
                    "difficulty": 3,
                    "is_diagnostic": True,
                },
                {
                    "id": "py:debug:q2",
                    "kind": "mcq_single",
                    "prompt_en": "Your loop computes the wrong total. What is the most useful thing to print?",
                    "prompt_ar": "حلقتك تحسب مجموعاً خاطئاً. ما أنفع قيمة لتطبعها؟",
                    "options": [
                        {"id": "a", "en": "The total after every iteration", "ar": "المجموع بعد كل تكرار"},
                        {"id": "b", "en": "The operating system version", "ar": "إصدار نظام التشغيل"},
                        {"id": "c", "en": "The number of files in the folder", "ar": "عدد ملفات المجلد"},
                        {"id": "d", "en": "Nothing; change the formula", "ar": "لا شيء؛ غيّر الصيغة"},
                    ],
                    "answer_key": {"option_id": "a"},
                    "explanation_en": "Watching the accumulator each iteration shows where it diverges from your expectation.",
                    "explanation_ar": "مراقبة المجموع في كل تكرار تُظهر موضع الاختلاف عن توقعك.",
                    "difficulty": 3,
                    "is_diagnostic": False,
                },
                {
                    "id": "py:debug:q3",
                    "kind": "short_answer",
                    "prompt_en": "Which built-in function pauses the program and lets you inspect variables? (name only)",
                    "prompt_ar": "ما الدالة المدمجة التي توقف البرنامج وتسمح لك بفحص المتغيرات؟ (الاسم فقط)",
                    "options": None,
                    "answer_key": {"accepted": ["breakpoint", "breakpoint()"]},
                    "explanation_en": "`breakpoint()` drops you into a debugger at that line.",
                    "explanation_ar": "`breakpoint()` تنقلك إلى مصحّح عند ذلك السطر.",
                    "difficulty": 2,
                    "is_diagnostic": False,
                },
            ],
        },
        {
            "id": "py:project",
            "title_en": "Project: a small command-line tool",
            "title_ar": "مشروع: أداة صغيرة لسطر الأوامر",
            "summary_en": "Build, test and explain a working tool that reads a file and reports a summary.",
            "summary_ar": "ابنِ واختبر واشرح أداة تعمل: تقرأ ملفاً وتعرض ملخصاً.",
            "kind": "project",
            "bloom_level": "create",
            "difficulty": 5,
            "prerequisites": ["py:dicts", "py:files", "py:modules", "py:debug"],
            "sequence": 120,
            "est_minutes": 120,
            "lesson": {
                "id": "py:project:lesson",
                "title_en": "The capstone brief",
                "title_ar": "تعريف المشروع الختامي",
                "est_minutes": 30,
                "body_md_en": (
                    "## Brief\n"
                    "Write `wordcount.py` that takes a file path and prints:\n\n"
                    "1. the number of lines,\n"
                    "2. the number of words,\n"
                    "3. the five most frequent words.\n\n"
                    "## Requirements\n"
                    "- Accept the path as `sys.argv[1]`.\n"
                    "- Handle a missing file with a friendly message and exit code 1.\n"
                    "- Count words case-insensitively and ignore punctuation.\n"
                    "- Use a dictionary for the counts and `sorted` for the top five.\n"
                    '- Include at least two functions and a `if __name__ == "__main__":` guard.\n\n'
                    "## How it is judged\n"
                    "Correctness on three files (see the rubric below), clarity of the code, and how you "
                    "explain one bug you found and fixed.\n\n"
                    "## Rubric (0–4 per row)\n"
                    "| Row | 4 means |\n"
                    "|---|---|\n"
                    "| Runs correctly | Works on all three files with no changes |\n"
                    "| Handles errors | Missing file and empty file both handled |\n"
                    "| Structure | Two or more clear functions, no duplication |\n"
                    "| Explanation | You can say why a bug happened, not just what you changed |\n"
                ),
                "body_md_ar": (
                    "## التعريف\n"
                    "اكتب `wordcount.py` يأخذ مسار ملف ويطبع:\n\n"
                    "1. عدد الأسطر،\n"
                    "2. عدد الكلمات،\n"
                    "3. الكلمات الخمس الأكثر تكراراً.\n\n"
                    "## المتطلبات\n"
                    "- استقبل المسار عبر `sys.argv[1]`.\n"
                    "- تعامل مع الملف المفقود برسالة واضحة ورمز خروج 1.\n"
                    "- احسب الكلمات دون حساسية لحالة الأحرف وتجاهل الترقيم.\n"
                    "- استخدم قاموساً للعدّ و`sorted` للخمس الأولى.\n"
                    '- ضمّن دالتين على الأقل وحماية `if __name__ == "__main__":`.\n\n'
                    "## معايير التقييم\n"
                    "الصحة على ثلاثة ملفات، ووضوح الكود، وقدرتك على شرح خطأ اكتشفته وأصلحته.\n\n"
                    "## سلّم التقييم (0–4 لكل صف)\n"
                    "| الصف | 4 تعني |\n"
                    "|---|---|\n"
                    "| التشغيل | يعمل مع الملفات الثلاثة دون تعديل |\n"
                    "| معالجة الأخطاء | يعالج الملف المفقود والفارغ |\n"
                    "| التنظيم | دالتان واضحتان على الأقل دون تكرار |\n"
                    "| الشرح | تشرح سبب الخطأ لا التعديل فقط |\n"
                ),
            },
            "items": [
                {
                    "id": "py:project:q1",
                    "kind": "mcq_single",
                    "prompt_en": "Your tool opens a missing file. What should it do?",
                    "prompt_ar": "أداتك تحاول فتح ملف غير موجود. ماذا يجب أن تفعل؟",
                    "options": [
                        {"id": "a", "en": "Crash with a traceback", "ar": "الانهيار مع سجل خطأ"},
                        {
                            "id": "b",
                            "en": "Print a clear message and exit with code 1",
                            "ar": "طباعة رسالة واضحة والخروج بالرمز 1",
                        },
                        {"id": "c", "en": "Create an empty file", "ar": "إنشاء ملف فارغ"},
                        {"id": "d", "en": "Print nothing and continue", "ar": "عدم طباعة شيء والاستمرار"},
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "A tool that will be used by a person should explain the problem and signal failure.",
                    "explanation_ar": "الأداة التي يستخدمها إنسان يجب أن تشرح المشكلة وتُشير إلى الفشل.",
                    "difficulty": 3,
                    "is_diagnostic": True,
                },
                {
                    "id": "py:project:q2",
                    "kind": "mcq_single",
                    "prompt_en": "Which structure is best for counting word frequencies?",
                    "prompt_ar": "أي بنية أنسب لعدّ تكرار الكلمات؟",
                    "options": [
                        {"id": "a", "en": "A list of words", "ar": "قائمة كلمات"},
                        {
                            "id": "b",
                            "en": "A dictionary from word to count",
                            "ar": "قاموس من الكلمة إلى عددها",
                        },
                        {"id": "c", "en": "One integer", "ar": "عدد صحيح واحد"},
                        {"id": "d", "en": "A text file", "ar": "ملف نصي"},
                    ],
                    "answer_key": {"option_id": "b"},
                    "explanation_en": "A dictionary maps each word to its running count in one pass.",
                    "explanation_ar": "القاموس يربط كل كلمة بعدّها في مرور واحد.",
                    "difficulty": 3,
                    "is_diagnostic": False,
                },
                {
                    "id": "py:project:q3",
                    "kind": "mcq_single",
                    "prompt_en": "You must show the five most frequent words. What do you do with the counts?",
                    "prompt_ar": "عليك عرض الكلمات الخمس الأكثر تكراراً. ماذا تفعل بعدّادات الكلمات؟",
                    "options": [
                        {
                            "id": "a",
                            "en": "Sort by count descending and take the first five",
                            "ar": "الترتيب تنازلياً حسب العدد وأخذ الخمس الأولى",
                        },
                        {
                            "id": "b",
                            "en": "Take the first five keys inserted",
                            "ar": "أخذ أول خمسة مفاتيح أُدخلت",
                        },
                        {
                            "id": "c",
                            "en": "Sum all counts and divide by five",
                            "ar": "جمع كل العدّادات والقسمة على خمسة",
                        },
                        {"id": "d", "en": "Print all words", "ar": "طباعة كل الكلمات"},
                    ],
                    "answer_key": {"option_id": "a"},
                    "explanation_en": "sorted(counts.items(), key=..., reverse=True)[:5] gives the top five.",
                    "explanation_ar": "sorted(counts.items(), key=..., reverse=True)[:5] تعطي الخمس الأولى.",
                    "difficulty": 4,
                    "is_diagnostic": True,
                },
            ],
        },
    ],
}
