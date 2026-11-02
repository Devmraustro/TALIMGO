أنت تواصل العمل على مشروع **TALIMGO** — منصة تعلم ذاتي بمحرك تعلم حتمي وذكاء اصطناعي محلي فقط.

المستودع: https://github.com/Devmraustro/TALIMGO

## 1. الحالة الفعلية عند آخر تحقق — 2026-11-02

- تم دمج [PR #11](https://github.com/Devmraustro/TALIMGO/pull/11) في `main` بالكاميت
  `e21366cd430837772edcae3a4349439c1761d3a5`. هذا هو **code baseline السابق لهذه المراجعة
  التوثيقية فقط**، وليس HEAD دائمًا؛ أعد قراءة `origin/main` قبل أي عمل جديد.
- أُغلق [PR #10](https://github.com/Devmraustro/TALIMGO/pull/10) بوصفه مكررًا ومستبدلًا بـ PR #11.
  لا تفتح PR آخر لإصلاح Vite نفسه.
- CI بعد الدمج على `main`: [run 41517171892](https://github.com/Devmraustro/TALIMGO/actions/runs/41517171892)
  على `e21366cd430837772edcae3a4349439c1761d3a5` — **7/7 وظائف ناجحة**.
- دخل مع PR #11 إصلاح تحذير أمان Vite (GHSA-8g5g-mxqh-grgj): التحديث من 6.4.4 إلى 6.4.5،
  وتغيير ربط خادم التطوير من `0.0.0.0` إلى `127.0.0.1`. نتيجة `npm audit` الموثقة: 0 ثغرات.

### أدلة CI وVercel — الحالي والتاريخي

| النطاق | الكاميت | الدليل الصحيح |
|---|---|---|
| `main` بعد دمج PR #11 | `e21366cd430837772edcae3a4349439c1761d3a5` | Run `41517171892` — 7/7؛ حالتا Vercel المرتبطتان بالكاميت `success`. |
| رأس PR #11 عند الدمج — تاريخي | `13c73881dbd356127047a0c2189e635935a4d30f` | Run `41509516797` كان push CI لهذا SHA، لا لـ `1e25ffe`. |
| فرع PR سابق — تاريخي | `1e25ffe76a065a10348c58ed1ea3e6ec75317a4b` | Run `41506736016` — 7/7؛ حالتا Vercel لهذا SHA بالذات `success`. ليس رأس `main`. |
| فرع PR سابق — تاريخي | `6f713462b9d9fd77a0fcd50f4e66d7fdc08c799d` | Run `41490792120` كان `pull_request` CI لهذا SHA، وليس CI بعد الدمج. |
| فرع PR #11 القديم بعد دمجه — ليس في `main` | `979f259c2272fe6516ad72ec72c7926795218853` | Run `41519616464` — 7/7 على فرع PR القديم. لا يثبت صحة التوثيق ولا يمثل `main`. |

### ملاحظة اختبارات Frontend المحلية

- سُجل timeout سابق واحد في ProjectsPanel ولم يُعَد إنتاجه؛ **السبب غير معروف** ولا يجوز اختلاق
  تفسير بنيوي أو تشغيلي له.
- بعد ذلك سُجل تشغيلان كاملان للـ frontend suite، وكانت نتيجة كل منهما `75 passed, 1 skipped`،
  ونجحت ثلاثة تشغيلات منعزلة لـ ProjectsPanel.
- هذه نتائج محلية تاريخية، وليست أرقام اختبارات CI الخاصة بكاميت `main` الحالي.

### حالة Vercel — لا تخلط بين البناء والإنتاج

- `talimgo-preview`: إلغاء نشر `main` مقصود؛ Ignored Build Step يوقف النشر التلقائي لـ main ويُبقي branch previews. **لا تزل هذا الإعداد باعتباره bug**.
- `talimgo-api`: آخر build من main حالته READY، لكن المشروع `live=false` ومحمٍ بـ SSO لجميع البيئات. فحص متغيرات البيئة دون فك تشفير أظهر صفر متغيرات Production؛ المتغيرات الموجودة خاصة بفرع Preview التجريبي فقط.
- منذ PR #8 يرفض التطبيق إعداد Production الناقص: يجب أن تكون `TALIMGO_ENV=production` صريحة، وأن تكون قاعدة البيانات PostgreSQL. لا تضف قيمًا وهمية ولا تستخدم SQLite في الإنتاج.
- لذلك: لا API عام موثّق حتى الآن، ولا قاعدة بيانات TALIMGO Production مؤكدة، ولا نشر إنتاج مكتمل. نجاح Vercel أو حالة READY يثبتان نتيجة النشر المرتبطة فقط، وليسا دليلًا على صحة API أو جاهزية الإنتاج.

### الاستضافة المفضلة

التوجه المعتمد في سير العمل الحالي هو **Alwaysdata**، لكن لا يُسمح بربط أو تعديل أي حساب/قاعدة بيانات قبل التأكد أنها مخصصة لـ TALIMGO وحده. لا تستخدم قواعد بيانات أو ملفات إعدادات أو حسابات قد تكون تابعة لـ AUSTRO. لا تتصل بأي مورد يحمل أو قد يحمل ملكية AUSTRO.

## 2. القواعد غير القابلة للتجاوز

1. الذكاء الاصطناعي المحلي المستضاف ذاتياً فقط؛ ممنوع OpenAI وGemini وAnthropic وأي AI Gateway أو fallback خارجي.
2. لا تستنتج قرارات المالك: العلامة التجارية، الدومين، العمر، الدول، الأسعار، الدفع، مزود البريد، اختيار النموذج.
3. لا تلمس `main` مباشرة. أنشئ feature branch ثم PR؛ لا تدمج PR دون أمر صريح من المالك.
4. لا تغيّر إعدادات Vercel/Alwaysdata، ولا DNS، ولا الأسرار، ولا قواعد البيانات، ولا تشغّل migrations على أي DB حقيقية دون تفويض محدد وبعد إثبات الملكية والعزل.
5. لا تعرض secrets أو database URLs أو بيانات المتعلمين. لا تطلب من المالك إرسالها في المحادثة؛ تُدار داخل لوحة الاستضافة أو ملفات آمنة.
6. لكل تغيير: فحص GitHub أولاً لإعادة الاستخدام، قراءة التراخيص، تغيير صغير، اختبارات regression، suite كاملة، تحديث الخطة، وفحص diff.
7. لا تكتب TESTED/CI-verified إلا بعد مشاهدة نتيجة تنفيذ فعلية. افصل بين unit/mock وreal runtime وproduction.
8. المحرك داخل `backend/app/learning/` يبقى حتمياً ونقياً دون I/O.
9. كل وصول إلى مورد/سجل يتحقق من الملكية من الخادم.
10. احترم سياسة التراخيص: MIT/BSD/Apache/ISC/OFL مع الإشعارات؛ GPL-3 يحتاج مراجعة قانونية مكتوبة؛ AGPL-3 ممنوع دون قرار المالك؛ المجهول = all rights reserved.

## 3. ترتيب العمل التالي

### أ. الاستضافة وقاعدة البيانات — الأولوية الأعلى

1. راجع `docs/ALWAYSDATA_DEPLOYMENT_RUNBOOK.md` و`docs/DEPLOYMENT.md`.
2. اطلب من المالك/تحقق عبر صلاحية موثوقة من أن Alwaysdata account مخصص لـ TALIMGO، وأنه يمكن إنشاء PostgreSQL database/user مستقلين داخل الحساب نفسه.
3. لا تفترض أن أي قاعدة بيانات Alwaysdata قديمة تخص TALIMGO؛ لا تستعمل أي قاعدة أو ملف env له علاقة محتملة بـ AUSTRO.
4. جهّز venv Python 3.11+، ثبّت `backend/pyproject.toml`، وأنشئ User Program من نوع ASGI باستخدام Uvicorn يستمع إلى عنوان IPv6 والمتغيرين `$IP` و`$PORT` اللذين توفرهما المنصة.
5. خزّن `TALIMGO_ENV=production` و`TALIMGO_SESSION_SECRET` القوي و`TALIMGO_DATABASE_URL` من PostgreSQL المخصص و`TALIMGO_ALLOWED_ORIGINS` الدقيقة و`TALIMGO_AI_ENABLED=false` في إعدادات سرية على الاستضافة.
6. لا تشغّل `alembic upgrade head` قبل تحقق المالك من أن DB الجديدة مستقلة وخالية ومخصصة لـ TALIMGO. بعدها فقط نفّذ production preflight ثم migrations و`alembic check`.
7. حافظ على واجهة/API من **نفس browser origin** عبر /api. عميل الواجهة يستخدم relative `/api/...` وsame-origin credentials؛ لا توجّه المتصفح مباشرة إلى API منفصل ولا تضعف `SameSite=Lax`. أثبت مسار reverse proxy/rewrite قبل نشر الواجهة.

### ب. التحقق من النشر

- جرّب `GET /api/health` وتحقق من JSON headers وTLS وredirects.
- تحقق أن `/api/docs` و`/api/openapi.json` يعيدان 404 في Production.
- استخدم `backend/scripts/verify_deployment.py` فقط ضد host يملكه المشروع ومصرح به، مع ضمان إنشاء الحساب التجريبي وحذفه والتحقق من إبطال الجلسة.
- لا تدّع صحة API من حالة Vercel READY وحدها.

### ج. النموذج المحلي

- لا تختر model نيابة عن المالك. افحص الرخصة والـ model card ومتطلبات RAM واللغات قبل طلب القرار.
- ثبّت runtime محلياً على جهاز/بنية TALIMGO يملكها المالك، مع عدم كشف port للعامة.
- نفّذ اختبارات عربية فصحى ولهجة جزائرية وفرنسية وإنجليزية، grounding، رفض citations المزيفة، injection، JSON schema، زمن الاستجابة والموارد. وثّق القياس لا الانطباع.
- لا تفعّل AI على بيئة Production قبل نجاح اختبارات النموذج الحقيقي والموافقة.

### د. المنتجات والحوكمة

- راجع `TALIMGO_MASTER_REFERENCE.md` §19 والـ requirements registry. أبقِ قرارات DEC غير المحسومة مفتوحة.
- المحتوى التعليمي للمسارين ما زال يحتاج subject-matter review.
- فحوص axe الآلية ناجحة في CI، لكن تدقيق WCAG بشري بقارئ شاشة ولوحة المفاتيح لم يُنفذ.
- البريد (التحقق واستعادة كلمة المرور)، الدفع، الأحداث التحليلية والميزات المؤسسية تبقى غير منفذة إلى أن تتخذ القرارات اللازمة.

## 4. أوامر تحقق مرجعية

```bash
# Backend (داخل backend/)
python -m pytest -p no:warnings
ruff check app tests scripts
ruff format --check app tests scripts
bandit -q -r app
python scripts/check_no_external_ai.py
alembic upgrade head && alembic check   # disposable test DB only

# Frontend (داخل frontend/)
npm ci --no-audit --no-fund
npm run typecheck
npm test -- --run
npm run build
node scripts/check-bundle.mjs --dist dist
node scripts/check-licences.mjs
npm audit
```

لا تنفذ migrations أو `verify_deployment.py` ضد بيئة إنتاج حقيقية إلا بعد تصريح صريح واثبات العزل والملكية.

## 5. طريقة التسليم

لكل دفعة أبلغ المالك بالعربية:
- ما تغير فعلياً + اسم الفرع/PR/commit.
- اختبارات CI وروابطها وعدد skipped وأسبابها.
- ما تم اختباره على بيئة محلية/Preview/Production كلٌ على حدة.
- ما تبقى، ومن يملك القرار أو الصلاحية المطلوبة.
لا تعلن اكتمال المنتج قبل استيفاء تعريف الانتهاء في `AGENTS.md` ومرجع المنتج.
