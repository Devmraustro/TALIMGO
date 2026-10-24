# TALIMGO — Master Reference Document

**The single source of truth for the TALIMGO academy: brand, business, educational system, and digital product.**

---

## 0. Document control

| Field | Value |
|---|---|
| Document title | TALIMGO — Master Reference Document |
| File name | `TALIMGO_MASTER_REFERENCE.md` |
| Version | 1.0.0 |
| Status | Initial master reference — approved for planning use only |
| Created | 2026-10-10 |
| Last updated | 2026-10-10 |
| Owner (accountable) | TALIMGO owner / founder |
| Intended readers | Founder, product managers, designers, engineers, AI agents, educators, content authors, marketers, investors/partners (under NDA), legal counsel |
| Scope | Documentation and research only. No website, software, database, deployment, domain purchase, trademark filing, or external account change was performed as part of this document. |
| Research date | 2026-10-10 (UTC). All external facts were retrieved on this date unless stated otherwise. |
| Change control | Any material change to brand name, promise, positioning, MVP scope, pricing model, or architecture direction requires a new version row below and an explicit owner decision recorded in the Decision Register (§23). |

### 0.1 Version history

| Version | Date | Author role | Summary of change |
|---|---|---|---|
| 1.0.0 | 2026-10-10 | Agent-mode research & documentation pass | First complete master reference: brand foundation, market research, product concept, curriculum architecture, IA/UX, visual identity, voice/localization, AI & safety, business model, technical principles, open-source landscape, MVP roadmap, metrics, requirement/risk/decision registers, brand-clearance report, sources, glossary, readiness checklist. |

### 0.2 Status labels used throughout this document

Every significant statement about the project carries one of four labels. **A reader must never treat a PROPOSED item as if it were decided.**

| Label | Meaning | Who can change it |
|---|---|---|
| **CONFIRMED** | Explicitly selected or established by the owner, or an external fact verified from a named source on the research date. | Owner only |
| **PROPOSED** | A recommendation made during document creation that awaits the owner's approval. Safe to draft against, not safe to build against permanently. | Owner approves/rejects; becomes CONFIRMED or is replaced |
| **UNVERIFIED** | A claim, condition, or assumption that still requires evidence (legal, financial, technical, or user research). Do not repeat these as facts. | Evidence resolves it |
| **FUTURE** | A capability explicitly outside the initial release; documented so the architecture does not block it. | Roadmap owner |

Two extra qualifiers are used sparingly:

- **DEPENDENCY** — an external or internal precondition that must be true before the item can ship.
- **BLOCKER** — an item whose failure would require a material change of plan (for example, the brand-name conflict in §24).

### 0.3 How to read this document

1. If you have five minutes, read §2 (Executive summary) and §2.3 (Canonical project summary).
2. If you are designing, read §9 (Visual identity) and §10 (Voice and localization) before drawing anything.
3. If you are engineering, read §13 (Technical principles), §14 (Open-source landscape), and §17 (Requirement register).
4. If you are writing curriculum or AI prompts, read §7 (Curriculum architecture) and §11 (AI, content quality, privacy, safety).
5. If you are planning, read §15 (MVP and roadmap), §16 (Metrics), §18 (Risks), §23 (Risks/decisions), and §24 (Brand clearance).
6. If you are an AI agent asked to work on TALIMGO, read §2.3 first and obey the status labels.

### 0.4 Integrity rules for anyone editing this document

- Do not convert a **PROPOSED** item into **CONFIRMED** without an explicit owner statement recorded in §23.3.
- Do not add prices, market sizes, conversion rates, user counts, partnership claims, awards, or outcome claims that are not sourced or explicitly labelled as an unvalidated hypothesis.
- Do not describe unimplemented features as existing. TALIMGO has **no released product** as of version 1.0.0 of this document.
- Keep terminology aligned with §20 (Glossary). If a term is not in the glossary and matters, add it there.

---

## 1. Table of contents

- [0. Document control](#0-document-control)
- [1. Table of contents](#1-table-of-contents)
- [2. Executive summary](#2-executive-summary)
  - [2.1 What TALIMGO is](#21-what-talimgo-is)
  - [2.2 The opportunity and the honest caveats](#22-the-opportunity-and-the-honest-caveats)
  - [2.3 Canonical project summary (for AI agents)](#23-canonical-project-summary-for-ai-agents)
  - [2.4 What must be decided before build](#24-what-must-be-decided-before-build)
- [3. Brand foundation](#3-brand-foundation)
  - [3.1 Name, pronunciation, and rendering](#31-name-pronunciation-and-rendering)
  - [3.2 Purpose](#32-purpose)
  - [3.3 Vision](#33-vision)
  - [3.4 Mission](#34-mission)
  - [3.5 Core brand promise](#35-core-brand-promise)
  - [3.6 Taglines](#36-taglines)
  - [3.7 Brand values (operational definitions)](#37-brand-values-operational-definitions)
  - [3.8 Brand personality](#38-brand-personality)
  - [3.9 Brand archetypes and how they change decisions](#39-brand-archetypes-and-how-they-change-decisions)
  - [3.10 What TALIMGO must never feel like](#310-what-talimgo-must-never-feel-like)
- [4. Positioning and market](#4-positioning-and-market)
  - [4.1 Positioning statement](#41-positioning-statement)
  - [4.2 Core differentiator: the learning cycle](#42-core-differentiator-the-learning-cycle)
  - [4.3 Competitive landscape (researched)](#43-competitive-landscape-researched)
  - [4.4 Comparison matrix](#44-comparison-matrix)
  - [4.5 Where the real differentiation is (and is not)](#45-where-the-real-differentiation-is-and-is-not)
- [5. Target audiences and personas](#5-target-audiences-and-personas)
- [6. Product concept and core learning cycle](#6-product-concept-and-core-learning-cycle)
- [7. Curriculum and subject architecture](#7-curriculum-and-subject-architecture)
- [8. Information architecture and user journeys](#8-information-architecture-and-user-journeys)
- [9. Visual identity and design system](#9-visual-identity-and-design-system)
- [10. Voice, tone, and localization](#10-voice-tone-and-localization)
- [11. AI behaviour, educational quality, privacy, and safety](#11-ai-behaviour-educational-quality-privacy-and-safety)
- [12. Business model and monetization](#12-business-model-and-monetization)
- [13. Technical principles and architecture requirements](#13-technical-principles-and-architecture-requirements)
- [14. Open-source landscape and reuse candidates](#14-open-source-landscape-and-reuse-candidates)
- [15. MVP scope and phased roadmap](#15-mvp-scope-and-phased-roadmap)
- [16. Metrics, analytics, and acceptance criteria](#16-metrics-analytics-and-acceptance-criteria)
- [17. Prioritized requirement register](#17-prioritized-requirement-register)
- [18. Risk register](#18-risk-register)
- [19. Decision register and open questions](#19-decision-register-and-open-questions)
- [20. Brand applications and marketing](#20-brand-applications-and-marketing)
- [21. Brand-clearance report](#21-brand-clearance-report)
- [22. Research sources and references](#22-research-sources-and-references)
- [23. Glossary](#23-glossary)
- [24. Implementation-readiness checklist](#24-implementation-readiness-checklist)
- [25. Appendices](#25-appendices)
  - [Appendix A — Proposed design tokens](#appendix-a--proposed-design-tokens)
  - [Appendix B — Worked example: one launch learning path](#appendix-b--worked-example-one-launch-learning-path)
  - [Appendix C — Example data objects (illustrative, not final schema)](#appendix-c--example-data-objects-illustrative-not-final-schema)
  - [Appendix D — Research log, limitations, and confidence levels](#appendix-d--research-log-limitations-and-confidence-levels)

*(Note on numbering: the brief's required section list is fully covered. Where the brief lists a topic as a top-level section, it appears here as its own numbered section; the mapping is: brief §1→doc §3, §2→§4–5, §3→§6, §4→§7, §5→§8, §6→§9, §7→§10, §8→§11, §9→§12, §10→§13–14, §11→§15, §12→§16, §13→§17, §14→§18–19, §15→§20, §16 structure→whole document, §17 research standards→§22 and Appendix D, §18 quality→§24.)*

---

## 2. Executive summary

### 2.1 What TALIMGO is

**TALIMGO is a proposed AI-powered personalised learning platform that turns a stated goal into a structured, adaptable learning journey and helps the learner practise until they can demonstrate real capability.**

Its defining concept — and the thing that separates it from a course library — is an **intelligent learning companion** that runs one continuous cycle:

> **GOAL → ASSESS → PLAN → LEARN → PRACTICE → BUILD → MEASURE → ADAPT**

The learner states an outcome in ordinary language ("I want to become a front-end developer", "I want to speak English confidently at work", "I want to understand statistics for my research"). TALIMGO then helps them understand what they need to learn, proposes a realistic plan that fits their available time, tutors them through the material, produces practice and projects, measures demonstrated capability rather than watch-time, and revises the plan when the evidence changes.

**CONFIRMED:** the brand category ("AI-powered personalized learning and skills development"), the working name TALIMGO, the mission, the vision, the values, the learning cycle, the goal-oriented architecture, the working palette, and the Tagline set are treated as owner-selected for this document.

**Not confirmed:** almost everything else. TALIMGO has no released product, no users, no revenue, no partnerships, no completed curriculum, and no legal brand clearance. Any statement to the contrary would be false.

### 2.2 The opportunity and the honest caveats

**The problem is real and well researched.** Learners are good at choosing content and bad at sequencing it. The evidence base for what works is unusually clear:

| Evidence | What it supports | Source |
|---|---|---|
| Retrieval practice beats restudying: across 159 studies, mean effect size **g ≈ 0.50**, with 81% of comparisons favouring retrieval. | Why TALIMGO's default activity is *produce an answer*, not *watch another video*. | Rowland (2014) meta-analysis, summarised in Karpicke's review [R21] |
| Spaced retrieval outperforms massed practice (**g ≈ 0.74** across 39 effect sizes); effects are larger at retention intervals longer than a day (**g ≈ 0.69**). | Why review scheduling is a core platform feature, not a nice-to-have. | [R21] |
| Learners' predictions of their own future performance are poorly correlated with actual performance. | Why TALIMGO must measure demonstrated capability, not self-reported confidence. | Karpicke & Roediger (2008) [R22] |
| Tutoring + mastery learning produced the famous ~2σ effect; **mastery learning alone produced ≈1σ**, and later work puts typical human tutoring at **d ≈ 0.79** and step-based intelligent tutoring at **d ≈ 0.76**. | Why TALIMGO focuses on mastery gating, formative assessment and remediation — the mechanism, not the mythology. Two sigma is a ceiling observed under ideal conditions, not a KPI. | Bloom (1984) via [R23]; Education Next analysis [R24]; VanLehn (2011) cited in [R25] |
| Intelligent tutoring systems: median **ES ≈ 0.66** across 50 controlled evaluations, but much smaller on standardised tests than on locally developed tests. Recent K-12 meta-analysis reports **g ≈ 0.27**. | Why outcome claims must be tied to what is measured, and why TALIMGO must not promise effect sizes. | Kulik & Fletcher meta-analysis [R26]; Leite et al. (2025) [R27] |
| UNESCO's 2023 guidance recommends a **minimum age of 13** for generative-AI use in classrooms, plus government-level regulation and teacher training; fewer than 10% of surveyed institutions had AI policies. | Why age policy, safeguarding and human oversight are design inputs, not compliance afterthoughts. | UNESCO [R15] |

**The caveat that shapes strategy:** in 2025–2026 the frontier AI labs shipped free "learning modes" — ChatGPT Study Mode, Gemini Guided Learning, and Claude's Learning Mode — that already do Socratic questioning, hints, quizzes and progress checks [R12][R13][R14]. **A generic AI tutor is no longer a differentiator.** What remains defensible is the surrounding system: a validated curriculum graph, diagnostic placement, mastery measurement, project scaffolding, evidence-backed remediation, and a plan that survives real life (missed sessions, changed goals, shrinking free time). TALIMGO's bet is on the *system*, not the chatbot.

**The caveat that must be resolved first:** a close-match educational brand — **TaalimGo** (`taalimgo.com`) — is operating in the same subject space (education, exam preparation, teacher training) with a similar name. This is a material naming risk. Full findings, evidence, and recommended next steps are in §21, with the risk recorded as RSK-001 and the decision recorded as DEC-001. **The owner has not been asked to rename, and this document does not rename the project.**

### 2.3 Canonical project summary (for AI agents)

> **PROJECT:** TALIMGO
> **WHAT IT IS:** An AI-powered personalised learning and skills-development platform. Core concept: an intelligent learning companion that turns a user's stated goal into a structured, adaptive learning journey and measures demonstrated capability. **PROPOSED, not built.**
> **CORE CYCLE:** GOAL → ASSESS → PLAN → LEARN → PRACTISE → BUILD → MEASURE → ADAPT.
> **POSITIONING (one line):** *For goal-driven adults who need a route, not another catalogue, TALIMGO generates a personal learning roadmap, tutors them through it, and measures what they can actually do — adapting the plan as evidence arrives.*
> **PRIMARY AUDIENCE (PROPOSED):** adults 18–35 with a concrete outcome — career changers and upskilling professionals — in Arabic-, French- and English-reading markets, MENA-first (Algeria and the wider region as the initial beachhead).
> **TAGLINE:** "Learn. Grow. Go." (primary); "Your Goal. Your Path. Your Future." (supporting); Arabic "تعلّم بذكاء. تقدّم بثقة."
> **BUSINESS MODEL (UNVALIDATED):** free tier → individual subscription → higher individual tier → later institutional/B2B.
> **LANGUAGES (PROPOSED):** English + Arabic (with RTL as a first-class layout) at launch; French next.
> **STATUS:** pre-MVP. Specification phase. No code, no content, no users, no legal clearance.
> **DO NOT:** invent users, outcomes, prices, partnerships, certifications, or completed features; treat proposed items as decided; claim trademark clearance.
> **READ FIRST IF YOU ARE AN AGENT:** §2.3 (this), §6 (product concept), §9 (design system), §11 (AI and safety), §13 (technical principles), §15 (MVP scope), §17 (requirements), §19 (decisions), §21 (brand clearance).

### 2.4 What must be decided before build

These are the five decisions that gate everything else. All are in §19 with full detail.

| # | Decision | Impact if wrong |
|---|---|---|
| DEC-001 | Brand name / trademark clearance and whether TALIMGO is safe to build on. | Rebranding after launch is expensive and destroys recognition. |
| DEC-002 | Primary domain. | Migrating a domain breaks links, email, and SEO. |
| DEC-003 | Initial launch languages (and whether Arabic is truly first-class). | Retro-fitting RTL into a finished UI is a rewrite, not a restyle. |
| DEC-004 | First curriculum paths (3 maximum) and depth. | Broad launch scope is the most common cause of unfinished edtech products. |
| DEC-005 | Supported ages and the policy that follows from that. | Age policy determines privacy regime, AI guardrails, and admin tooling. |

---

## 3. Brand foundation

### 3.1 Name, pronunciation, and rendering

| Item | Value | Status |
|---|---|---|
| Working brand name | **TALIMGO** | CONFIRMED (owner-selected working brand) |
| Typographic form | Always uppercase in the wordmark; "TALIMGO" in running text is treated as a word, not an acronym ("TALIMGO is...", not "TALIM GO is..."). A spaced form **TALIM GO** is reserved for legal/trademark filings and for spoken explanation. | PROPOSED |
| Pronunciation | **Taa-lim-go** (primary) / **Ta-lim-go** (accepted variant). Stress on the second syllable: /tɑːˈlɪm.ɡoʊ/, /təˈlɪm.ɡoʊ/. | PROPOSED |
| Arabic rendering | **تاليم غو** | CONFIRMED |
| Arabic tagline rendering | **تعلّم بذكاء. تقدّم بثقة.** | CONFIRMED |
| Sanskrit/morpheme note | "Talim" is not an English dictionary word. It is recognisable across Arabic/Urdu/Uzbek/Turkish-speaking regions with meanings around *education, instruction, or training* (Arabic **تعليم** *taʿlīm*; Turkish **talim** *drill/practice*; Uzbek **ta'lim** *education*). "Go" is an English imperative implying motion and action. TALIMGO is therefore a **coined composite brand**, semantically "learning that moves you forward". | CONFIRMED (framing) / UNVERIFIED (any legal distinctiveness conclusion) |

**Brand-category statement (CONFIRMED):** *AI-powered personalized learning and skills development.*

**The "don't claim" rule (CONFIRMED):** TALIMGO must never be described as an established English dictionary word, a certified institution, an accredited school, an official partner of any ministry or university, or a guarantee of employment or income.

**Naming implications discovered during research (UNVERIFIED as to legal effect, but material):**

1. The "Talim/Taalim" root is **highly used** in the education sector in North Africa and the Levant. Examples found during research: `taalim.ma` (a Moroccan Ministry-linked learning platform referenced since 2020 [R31]), `taalimtice.ma` (Moroccan Ministry ICT portal [R32]), and `taalimai.ma` (an AI learning "super app" for Moroccan students [R33]). A prefix that means "education" in the target market is a **weak foundation for distinctiveness** and increases collision probability.
2. At least two unrelated projects already use "TalimGo"-style names: `taalimgo.com` (§21) and a GitHub project `RayimqulovAbduvohid/TalimGo` (no licence file; last push 2025-12-25) [R10].
3. Practical consequence (PROPOSED): treat the **logotype + symbol + colour system as the distinctive asset**, not the word alone, and plan to register a composite mark rather than rely on the word's inherent distinctiveness. Legal advice is required — see §21.5.

### 3.2 Purpose

**TALIMGO exists to help people turn ambitions into structured learning journeys and practical abilities.**

Operational test for any feature or message: *does this reduce the distance between what someone wants to be able to do and what they can currently do?* If not, it is not TALIMGO's job.

A user should be able to:
1. explain a desired outcome in ordinary language,
2. understand what they need to learn and why,
3. follow a realistic plan matched to their available time,
4. receive personalised guidance and explanations at their level,
5. practise and produce something real,
6. see truthful evidence of progress toward the outcome,
7. change the plan without losing their history.

### 3.3 Vision

**To become a trusted, accessible, AI-powered learning companion that helps people around the world acquire knowledge and useful skills throughout their lives.**

### 3.4 Mission

**To make high-quality, personalised learning easier to plan, understand, practise, measure, and sustain.**

Note the five verbs — they map to product modules in §6 and are the basis for the metrics in §16.

### 3.5 Core brand promise

> **TALIMGO helps you find your path, learn what matters, practise deliberately, and move toward your goals.**

**Prohibited promise extensions (CONFIRMED).** TALIMGO must never promise, imply, or allow generated content to promise:
- guaranteed mastery, fluency, or a specific grade;
- employment, promotion, salary, or income;
- certificates recognised by any external institution, ministry, university, or employer;
- success within a fixed period;
- health, legal, or financial outcomes.

Where AI output could imply such a promise, the guardrails in §11.1 apply.

### 3.6 Taglines

| Role | Language | Tagline | When to use |
|---|---|---|---|
| **Primary** | English | **Learn. Grow. Go.** | Default brand line: logo lockups, app store listings, deck covers, campaign end-frames, social bios. Short, rhythmically simple, works at small sizes. |
| **Supporting** | English | **Your Goal. Your Path. Your Future.** | Use when the audience needs the *promise of personalisation* spelled out: paid campaigns aimed at career changers, partnership decks, landing-page hero variants, testimonials framing. Never use both primary and supporting taglines in the same visual block. |
| **Primary (Arabic)** | Arabic | **تعلّم بذكاء. تقدّم بثقة.** ("Learn with intelligence. Move forward with confidence.") | The Arabic equivalent of the primary tagline. Used wherever a fully Arabic composition is shown. Not a literal translation of "Learn. Grow. Go." — it preserves the *sense* rather than the syllables. |
| **Legal/descriptive** | English | "TALIMGO — AI-powered personalized learning" | Filings, invoices, app-store metadata where a descriptive string is required, and any context where a tagline could be mistaken for a claim (for example, advertising in regulated markets). |

**Rule (CONFIRMED):** there is exactly **one** primary tagline per language. Do not introduce competing primary taglines. Additional internal campaign lines are permitted only as clearly subordinate campaign copy, must not be used as a logo lockup, and must be cleared with the brand owner.

### 3.7 Brand values (operational definitions)

Generic value lists are useless. Each value below has a definition, a product consequence, and a way to tell when the value is being violated.

| Value | Definition | Product consequence (what must exist) | Violation signal |
|---|---|---|---|
| **Personalization** | Learning adapts to the learner's goal, existing knowledge, available time, and demonstrated needs. | Onboarding collects goal, prior experience, time budget, and preferences; roadmap generation consumes them; the plan visibly changes when inputs change. | Two learners with different goals/time budgets receive identical plans and identical task counts. |
| **Progress** | TALIMGO measures **actual capability**, not minutes spent or lessons opened. | Mastery estimates derive from assessment + practice performance + repeated evidence; "time on site" is never labelled as progress. | A dashboard that congratulates a learner for a 40-minute video session with no evidence of capability. |
| **Practice** | Knowledge becomes exercises, decisions, projects, and demonstrable skills. | Every concept has at least one active activity; every milestone has a practical output; projects have rubrics. | A lesson ends with "next lesson" and no practice step. |
| **Clarity** | The learner always understands their next step. | One primary next action per screen state; plain-language rationale for "why this task"; explicit estimates labelled as estimates. | A dashboard with twelve equally-weighted widgets and no recommended action. |
| **Integrity** | Communicating uncertainty, using credible sources, respecting intellectual property, refusing fabricated claims. | Source provenance on generated content; uncertainty statements; error reporting; licensing register for all third-party resource links. | An AI answer with no source that reads as authoritative; a copied lesson body from a third-party course. |
| **Accessibility** | Usable across devices, abilities, languages, and levels of prior knowledge. | WCAG 2.2 AA target, RTL-first layout support, keyboard operability, reduced-motion support, low-bandwidth mode. | A drag-only interaction with no alternative; a layout that collapses when set to RTL. |
| **Independence** | Help learners become capable without permanent dependence on the assistant. | Tutor hints-before-answers policy, fading scaffolding, "explain it back" checks, deliberate promotion of unassisted performance. | The tutor answers every question directly, including ones the learner could solve; the product becomes harder to use without the AI. |
| **Adaptability** | The plan is revised when new evidence about progress or circumstances appears. | Replanning triggers (see §6.3.5); rescheduling flows; "less time this week" control. | A learner who misses a week is told to "start over" or sees a frozen plan. |

### 3.8 Brand personality

**TALIMGO should feel:** intelligent, modern, focused, encouraging, practical, trustworthy, ambitious.

**TALIMGO must not feel:** childish, excessively gamified, bureaucratic, robotic, artificially motivational, or like a generic AI chatbot wrapped in an education website.

Practical calibration table — the same message, four ways:

| Register | Example ("You missed 4 days") | Verdict |
|---|---|---|
| Bureaucratic | "Non-compliance recorded: 4 consecutive days of inactivity. Streak reset. Please resume mandatory module 3." | ❌ Never |
| Infantilising | "Oh noooo! Your poor streak! 😭 Let's get those points back!" | ❌ Never |
| Manipulative | "You're falling behind 87% of learners. Don't lose your progress — upgrade to catch up!" | ❌ Never |
| **TALIMGO** | "Four days off. Your plan hasn't expired — here's a 25-minute restart session that rebuilds the last topic before moving on." | ✅ Correct |

### 3.9 Brand archetypes and how they change decisions

TALIMGO is a deliberate blend. The blend ratio is a design tool, not decoration.

| Archetype | Weight | What it contributes | Product expression | Communication expression | Teaching expression |
|---|---|---|---|---|---|
| **The Sage** (mentor/knowledge) | **Primary** | Credibility, rigorous explanation, honesty about uncertainty. | Source attribution, "we're not sure, here's how to check", subject-expert review for high-risk material. | Precise, calm, no hype. "Here's what the evidence says." | Explains *why* before *how*; connects prerequisites. |
| **The Guide / Mentor** | **Primary** | Personal route-finding, encouragement without flattery, respect for autonomy. | Roadmap co-ownership, learner can override the plan, "why this task matters" rationale on every card. | Second person, direct, practical. "Your next step is…" | Hints before answers; asks the learner to explain first. |
| **The Explorer** | Secondary | Forward motion, curiosity, ambition; supports "Go" in the name. | Progress visual language (path, milestone, map), optional challenge tracks, cross-subject connections. | Momentum without hype. "You can try this next." | Project- and discovery-oriented tasks; open questions. |
| **The Creator / Maker** | Secondary | Evidence through making; portfolio outcomes. | Project workspace, artefacts, rubric feedback, export. | "You'll build X." | Practice produces something real. |
| **The Hero** (achievement) | **Accent only** | Completion energy, gamification, streaks. | XP, levels, milestones — capped and honest; never used as proof of mastery. | Celebratory but brief, no overclaiming. | Achievement tied to demonstrated performance. |
| **The Ruler** (order) | **Accent only** | Structure, standards, consistency. | Design system enforcement, content governance, accessibility targets. | Consistent, predictable, no surprises. | Explicit completion criteria and rubrics. |

**Archetype failure modes to avoid (CONFIRMED anti-patterns):**

- **Sage without Guide** → a lecture machine that gives authoritative answers and never asks the learner to think.
- **Hero without Sage** → a points game that rewards time spent rather than capability, eroding trust.
- **Explorer without Ruler** → endless "explore anything" surfaces with no completion criteria, and no way to know whether anything was learned.

### 3.10 What TALIMGO must never feel like

| Anti-pattern | Why it fails TALIMGO | Concrete rule |
|---|---|---|
| Generic AI chatbot with an education skin | The chat modality is commoditised and free elsewhere [R12][R13][R14] | Every tutor conversation carries curriculum context (lesson, concept, mastery state) and produces structured evidence (attempt, artefact, confidence), not just text. |
| Video-course library | Reproduces the problem TALIMGO exists to solve | A course/video cannot be the primary unit of the product; the primary unit is the **goal → next action** pair. |
| Gamified points theatre | Rewards presence, not capability | XP is an engagement signal only; mastery is always reported separately and never as points. See §6.9. |
| Bureaucratic LMS | Optimised for administration, not learners | No screens whose primary purpose is reporting to an institution in Phase 1. |
| Shame-based streaks | Punishes real life; drives churn | Breaks are neutral-by-design (§6.9.4). |
| Fake urgency / fake scarcity | Destroys the Integrity value | No countdown timers on learning content, no "only 2 seats" patterns. |

---

## 4. Positioning and market

### 4.1 Positioning statement

**PROPOSED (primary positioning statement):**

> **For** adults who know what they want to be able to do but not how to get there — especially career changers, upskilling professionals, and self-directed learners in Arabic-, French- and English-reading markets — **TALIMGO** is an AI-powered personalised learning platform **that** converts a stated goal into a sequenced roadmap, tutors the learner through it, drives deliberate practice and real projects, and measures demonstrated capability instead of attendance. **Unlike** course marketplaces and catalogues, which assume the learner can choose and sequence content themselves, and unlike general-purpose AI assistants, which teach well in a single conversation but keep no trustworthy record of what the learner can actually do, **TALIMGO owns the whole loop** from goal to evidence. **Learners should trust it because** it shows its sources, admits uncertainty, never sells mastery as a promise, and adapts the plan when the evidence says the plan is wrong.

**Short form (used in decks and app-store copy):**

> TALIMGO turns a goal into a plan, a plan into practice, and practice into measured capability.

### 4.2 Core differentiator: the learning cycle

**CONFIRMED:** the product experience follows this cycle.

**GOAL → ASSESS → PLAN → LEARN → PRACTICE → BUILD → MEASURE → ADAPT**

| Stage | Learner question it answers | What the system does | What it must produce (output artefact) | Module (§) |
|---|---|---|---|---|
| **GOAL** | "What am I actually trying to achieve?" | Structured goal capture: outcome, context, deadline (optional), constraints, definition of "done". | A goal record with a plain-language outcome statement and success criteria the learner accepts. | §6.1 |
| **ASSESS** | "Where am I starting from?" | Diagnostic questions, practical tasks, prior-experience intake; produces provisional skill estimates with confidence levels. | A skill profile with per-skill estimates, evidence notes, and explicit uncertainty. | §6.2 |
| **PLAN** | "What do I need to learn, and in what order?" | Roadmap generation from the curriculum graph + time budget + prerequisites. | An editable roadmap: milestones → paths → modules → lessons → concepts → practice → assessments → projects. | §6.3 |
| **LEARN** | "What is this and why does it matter?" | Lesson delivery in multiple formats; tutor support in context. | Completed concept explanations with the learner's own restatement. | §6.4, §6.5 |
| **PRACTICE** | "Can I do it yet?" | Retrieval questions, exercises, simulations, spaced review; hints before answers. | Attempt records with performance data per concept. | §6.5, §6.8 |
| **BUILD** | "Can I make something real with this?" | Guided projects with milestones, deliverables, rubrics, feedback. | A project artefact + rubric-scored feedback (optionally portfolio-ready). | §6.8 |
| **MEASURE** | "How do I know I've improved?" | Assessment (repeatable where possible), mastery estimation, progress reporting. | A mastery report distinguishing demonstrated / practising / not-yet-evidenced. | §6.6, §16 |
| **ADAPT** | "What changes now?" | Replanning on evidence: accelerate, remediate, reschedule, re-scope, change goal. | A revised plan with a visible "what changed and why" note. | §6.3.5 |

**How the stages connect into one continuous experience (CONFIRMED as design intent).** The cycle is not a wizard. It is a loop whose state is always visible:

- Every screen has exactly **one** primary next action drawn from the current stage, with a one-line rationale ("this rebuilds the prerequisite you missed on Tuesday").
- **MEASURE** feeds **ADAPT**, which rewrites **PLAN**, which changes the **next action** — so the learner experiences the loop as "the plan keeps up with me", not as "I keep filling in forms".
- **ADAPT** can also send the learner *backwards* — to a prerequisite — without shame, and *forwards* — skipping material already evidenced.
- **BUILD** is the point where the cycle becomes externally meaningful: it converts internal skill estimates into something the learner can show.

### 4.3 Competitive landscape (researched)

Research method: official product pages where reachable, plus secondary sources with publication dates, retrieved 2026-10-10. **Pricing in this market changes constantly and varies by country, platform, and promotion.** Every price below is a *reported* price for a *US or default* market on the date given by the source, and must be re-verified before use in financial modelling. All price paragraphs carry the UNVERIFIED label unless they were read directly from the vendor on 2026-10-10.

#### 4.3.1 Coursera — credential marketplace moving toward AI coaching

- **Model:** open-to-partner marketplace of university/industry courses; free audit; per-course and per-programme payment; subscription.
- **Reported pricing (2026):** Coursera Plus ≈ **$59/month or $399/year**; individual courses ≈ **$49–99**; Specialisations and Professional Certificates ≈ **$39–79/month**; monthly Plus includes a 7-day trial; annual has a 14-day money-back window; degrees and MasterTrack are excluded from Plus [R20].
- **AI:** "Coursera Coach" provides in-course Q&A, study tips, and practice questioning [R20].
- **Strengths:** brand-trusted credentials, university partnerships, structured multi-course programmes, free previews, strong catalogue breadth.
- **Limitations for TALIMGO's target problem:** the learner still chooses the programme; personalisation is largely catalogue recommendation, not diagnostic sequencing; completion depends heavily on self-discipline; certificates cost extra unless subscribed.

#### 4.3.2 Khan Academy / Khanmigo — free master platform with a paid AI layer

- **Model:** nonprofit; the core K-12 platform (videos, exercises, dashboards) is free with no ads; **Khanmigo** is the paid AI layer.
- **Reported pricing (2026):** Khanmigo **$4/month or $44/year** for learners/parents, **free for verified teachers**, district/enterprise contracting at a reported ~**$10–35 per student per year** depending on the source and tier [R28]. Note the inconsistency across sources — verify with Khan Academy before citing a district price.
- **AI:** Socratic tutoring that resists giving answers, writing coach, code sandbox feedback, teacher tools (lesson planning, rubrics, progress summaries) [R28].
- **Strengths:** extraordinary price-to-trust ratio; curriculum-aligned content library; pedagogy-first design; teacher adoption loop.
- **Limitations:** K-12 and early-college focus; consumer subscriptions historically restricted by billing region; not designed around adult career outcomes; the platform is free, so no adult "productivity" upsell.

#### 4.3.3 Duolingo — habit engine with AI conversation tiers

- **Model:** freemium consumer app; ad-supported free tier; subscription tiers.
- **Reported pricing (2026):** Super ≈ **$12.99/month or ~$84–96/year**; Max ≈ **$29.99/month or ~$168/year**; Max Family ≈ $240/year [R29].
- **AI:** Roleplay and Video Call (AI conversation partners, limited language coverage); "Explain My Answer" became **free for all users in January 2026**, materially reducing the Max tier's exclusive value [R29].
- **Strengths:** world-class retention mechanics, low friction, enormous scale, excellent beginner onboarding.
- **Limitations for TALIMGO's problem:** single-domain (languages); measures app progress more than real-world capability; AI exclusives are narrowing as features are pushed down-market; not a goal-to-project system.

#### 4.3.4 Brilliant — interactive STEM problem-solving

- **Model:** freemium with a strict free tier (a limited number of lessons/practice sets per day) and Premium subscription.
- **Reported pricing (2026):** sources disagree substantially — reported ranges include **$12.49–27.99/month** and **~$150–240/year**, with group/family seats and **free Premium for K-12 educators** [R30]. Treat all figures as UNVERIFIED until checked at checkout.
- **AI:** an adaptive tutor ("Koji") plus interactive problem sequences [R30].
- **Strengths:** exceptional interaction design for conceptual intuition; no passive video; strong for maths/science reasoning.
- **Limitations:** STEM only; depth over breadth; limited hands-on project/portfolio output; little support for career-change workflows.

#### 4.3.5 Udemy — open marketplace, lifetime purchases

- **Model:** instructor marketplace; learner buys individual courses with lifetime access; a curated "Personal Plan" subscription exists.
- **Reported pricing (2026):** Personal Plan ≈ **$16.99–32/month** or **~$156–168/year**, regionally variable; single courses frequently discounted to ~$9.99–19.99 [R34].
- **Economists' view:** instructors reportedly keep **37%** of organic marketplace revenue and **15%** of subscription-pool revenue, with platform-set discounting [R34].
- **Strengths:** enormous catalogue; low entry price; lifetime access feels fair.
- **Limitations:** quality variance is inherent to the open model; no diagnostic placement; no sequencing across instructors; progress/measurement is weak; the learner must be their own curriculum designer — precisely the gap TALIMGO targets.

#### 4.3.6 Codecademy — interactive coding with AI assistance

- **Model:** freemium; Basic free; Plus and Pro subscriptions (annual/monthly).
- **Reported pricing (2026):** Basic **$0**; Plus **$14.99/mo billed annually** (~$179.88/yr) or $29.99 monthly; Pro **$19.99/mo billed annually** (~$239.88/yr) or $39.99 monthly; Pro adds career paths, certification prep, interview prep and code challenges; an AI learning assistant is available including on the free tier [R35].
- **Strengths:** best-in-class hands-on coding UX (write and run code in-lesson, instant feedback); structured skill and career paths.
- **Limitations:** essentially single-domain (technical skills); text-heavy; career outcomes rest on the learner completing without an adaptive tutor loop; quizzes/projects are paywalled.

#### 4.3.7 The new incumbent: free AI "learning modes"

This is the most important competitive development of 2025–2026 and the one most likely to be under-estimated.

| Product | Reported availability (2026) | Reported pedagogy | Implication for TALIMGO |
|---|---|---|---|
| **ChatGPT Study Mode** | Free for logged-in users; Socratic questioning, hints, quizzes, knowledge checks, memory across sessions, progress tracking added in 2026 [R12][R14] | Refuses to hand over answers; asks about prior knowledge; adapts pacing | A conversational tutor alone is not a product. |
| **Gemini Guided Learning** | Free tier with limits; built on Google's LearnLM research; step-by-step guidance with visuals/diagrams/quizzes; custom practice quizzes for 18+ students [R13][R14] | Structured, visual scaffolding | Differentiation must come from curriculum, measurement, and outcome artefacts. |
| **Claude Learning Mode / Claude for Education** | Free toggle for individuals; institutional licensing with LMS integration reported [R12] | Strict Socratic tutoring, minimal direct answers | Learners already have a "strict tutor" for free. |

**Strategic consequence (CONFIRMED as a planning premise, based on the above):** TALIMGO's differentiation cannot be "we have an AI tutor". It must be:

1. **A validated curriculum graph** the AI is constrained to use (so output is consistent, sequenced, and reviewable) — §7.7.
2. **Measurement you can trust** — mastery from evidence, with uncertainty shown — §6.6, §11.4.
3. **Plan durability** — the plan survives missed weeks, shrinking time budgets, and changed goals — §6.3.5, §6.7.
4. **Real artefacts** — projects, rubrics, and portfolio outputs a free chatbot does not manage — §6.8.
5. **Language and market fit** — Arabic-first RTL experience and MENA-relevant examples and pathways — §10.4.

### 4.4 Comparison matrix

Legend: ● strong / native · ◐ partial · ○ weak or absent · ? unverified. This matrix is a **reading of public sources cited above**, not an audit of each product's internals.

| Criterion | Coursera | Khan Academy + Khanmigo | Duolingo | Brilliant | Udemy | Codecademy | Free AI learning modes | **TALIMGO (target)** |
|---|---|---|---|---|---|---|---|---|
| Course discovery / library breadth | ● | ◐ (K-12) | ○ (languages) | ○ (STEM) | ● | ◐ (tech) | ○ | ◐ (curated, narrow at launch) |
| Personalised learning plan from a goal | ◐ (recommendations) | ◐ (mastery pathways) | ◐ (daily path) | ◐ | ○ | ◐ (paths) | ◐ (per-conversation) | ● (goal-driven, multiplatform) |
| Diagnostic assessment / placement | ○ | ◐ | ◐ | ◐ (jump-ahead) | ○ | ◐ (skill assessments) | ○ | ● (diagnostic + practical tasks) |
| AI tutoring in context | ◐ (Coursera Coach) | ● (Khanmigo) | ◐ (Max features; narrowing) | ◐ (Koji) | ○ | ◐ (assistant) | ● | ● (curriculum-constrained) |
| Adaptive progression | ◐ | ● | ◐ | ◐ | ○ | ◐ | ◐ | ● (target) |
| Hands-on practice / projects | ◐ (guided projects) | ◐ (exercises) | ○ | ● (interactive) | ◐ (varies) | ● (interactive + projects) | ◐ (text only) | ● (projects with rubrics) |
| Trustworthy progress measurement | ◐ (grades, certificates) | ● (mastery-ish) | ◐ (app progress) | ◐ | ○ | ◐ | ○ (no persistent record) | ● (target: evidence-based) |
| Languages / accessibility | ◐ (subtitles, localisation) | ◐ (English-first) | ● (40+ languages, but AI features on ~7-9) | ○ | ◐ | ○ | ◐ | ◐ → ● (EN+AR first, RTL-first) |
| Pricing model | free audit + subscription + per-course | free core + $4/mo AI | free + 2 subscription tiers | free sample + subscription | per-course + subscription | free + 2 subscription tiers | $0 | free + subscription (+ later institutional) |
| Reported entry price for paid value (UNVERIFIED, 2026) | $49–99/course; $59/mo Plus | $4/mo, $44/yr | $12.99/mo Super; $29.99/mo Max | ~$12.49–27.99/mo | ~$16.99–32/mo (Personal Plan) | $14.99–19.99/mo (annual) | $0 | TBD (see §12) |
| Main structural weakness | learner must still sequence their own path; certificates cost extra | K-12 scope; consumer access historically region-limited | one domain; capability ≠ app progress | STEM-only; no portfolio | quality variance; no placement; no sequencing | tech-only; text-heavy; outcomes rest on learner | no curriculum, no durable evidence, no accountability | not yet built |

**Conclusion (PROPOSED):** the least contested space is the **intersection of goal-driven sequencing, trustworthy measurement, and real artefacts, delivered in Arabic and English to adult learners with a concrete outcome.** Every row above is occupied by someone; the *combination* is not.

### 4.5 Where the real differentiation is (and is not)

| Claim | Verdict | Reasoning |
|---|---|---|
| "We have an AI tutor." | ❌ Not a differentiator (2026) | Free in three major assistants [R12][R13][R14]. |
| "We have courses." | ❌ Not a differentiator | Commodity; 210,000+ on Udemy alone [R34]. |
| "We're cheaper." | ❌ Weak and dangerous | $4/month Khanmigo and free ChatGPT Study Mode set the floor [R28][R12]. Undercutting them is not a strategy. |
| "We sequence learning from your goal, and prove progress with evidence." | ✅ Plausible differentiator | Most platforms sequence *content*, not *the learner's route to an outcome*; measurement is usually completion-based. |
| "We make the plan survive real life." | ✅ Under-served, high loyalty value | Missing-week recovery and shrinking-time replanning are rarely first-class features. |
| "We work properly in Arabic, right-to-left, with local examples and payment methods." | ✅ Real, defensible, and under-served | Most global platforms treat Arabic as a translation layer; Moroccan "Taalim" products show regional demand but are exam-prep specific [R1][R33]. |
| "We guarantee jobs / mastery in 90 days." | 🚫 Prohibited | Violates §3.5 and §11.1. |

---

## 5. Target audiences and personas

### 5.1 Persona set

Each persona has a job-to-be-done, the evidence the platform can gather, the features that matter, and the failure mode.

---

**P1 — "Where do I even start?" beginner**
*Amina, 21, Algiers. Engineering student. Wants to learn programming; has watched 40 hours of random YouTube tutorials and can't build anything.*

- **Job to be done:** get a credible starting point and a route that is not overwhelming.
- **Current behaviour:** collects tutorials; restarts often; abandons when confused.
- **Critical needs:** short diagnostic, tiny first win (a working artefact within days), prerequisite repair without shame, one clearly-labelled next step.
- **Features that matter:** onboarding goal capture, baseline assessment, daily missions (20–30 min), retrieval practice, hints-before-answers tutor.
- **Failure mode:** the FAQ-level answer "everyone learns differently, just explore" — i.e. no plan. Also: being dropped into an advanced path by an over-optimistic assessment.
- **Success signal:** completes a first project milestone within 14 days and returns the following week.

---

**P2 — Students needing structured learning support**
*Yacine, 17, secondary-school student preparing for national exams and university entry.*

- **Job to be done:** pass exams and build durable understanding in specific subjects.
- **Critical needs:** curriculum alignment, past-paper practice, worked explanations, revision scheduling, parent visibility (if a parent pays).
- **Features that matter:** structured pathways, quizzes and mock exams, spaced review, "explain my mistake" feedback, progress report export.
- **Failure mode:** unvalidated exam-specific claims (for example promising exam questions or grade outcomes); content not aligned to the national curriculum.
- **Note:** this is a large market (Moroccan "Taalim" products already serve it [R1][R33]) and it drags TALIMGO toward being an exam-prep product with heavy content-alignment cost. **PROPOSED: serve this persona in Phase 2+ through exam-prep pathway templates, not in the initial MVP.**

---

**P3 — Professionals seeking new skills**
*Leïla, 29, product analyst in a bank. Wants SQL + dashboarding to change her role internally.*

- **Job to be done:** acquire a specific, job-relevant capability efficiently, without quitting work.
- **Critical needs:** respect for a tight calendar (3–5 hours/week), relevance to a real work problem, evidence she can show a manager.
- **Features that matter:** time-budget-aware planning, skill map linked to competencies, project that doubles as a work artefact, progress report.
- **Failure mode:** a plan designed for full-time students; 40-hour modules; no "what do I show at work" output.
- **Success signal:** completes a project artefact and reports internal mobility, promotion, or role change (self-reported).

---

**P4 — Career changers**
*Karim, 33, former accountant. Wants to become a front-end developer within 9–18 months.*

- **Job to be done:** convert into a different field with demonstrable capability.
- **Critical needs:** a realistic, long-horizon roadmap; prerequisite clarity; portfolio-grade projects; honesty about timelines and competition; interview preparation later.
- **Features that matter:** multi-milestone pathways, capstone projects, portfolio export, career-competency mapping (FUTURE), project-based assessment.
- **Failure mode:** implicit employment guarantees; unrealistic timelines; a plan that produces certificates but no portfolio.
- **Note:** highest motivation, highest expectations, highest reputational risk if handled badly.

---

**P5 — Self-directed learners pursuing personal interests**
*Nadia, 41, teacher. Wants to learn statistics for a research project and photography for personal interest.*

- **Job to be done:** satisfy curiosity and finish a personal project without a career motive.
- **Critical needs:** optional depth, flexible pacing, no pressure mechanics.
- **Features that matter:** goal types that are not career-based, interest-based exploration within a validated path, pause/resume.
- **Failure mode:** relentless career framing and notification pressure that makes learning feel like work.

---

**P6 — Learners who need help maintaining consistency (a cross-cutting state, not a separate market)**
*Any persona after week three.*

- **Job to be done:** keep going when motivation drops, life intervenes, or a topic gets hard.
- **Critical needs:** realistic session sizes, absence-tolerant plans, honest encouragement, visible accumulated evidence.
- **Features that matter:** daily missions, recovery sessions, no-shame streak semantics (§6.9.4), "you are 2 tasks from your next milestone" framing.
- **Failure mode:** shame mechanics, streak loss punishment, or a plan that becomes invalid after a two-week break.

---

### 5.2 Primary initial audience (recommendation)

**PROPOSED:** the primary initial audience is **P3 + P4 — goal-driven adults (roughly 20–35) with a concrete outcome**, with **P1 as the most common entry state** for those same people.

Reasoning:

| Criterion | P3/P4 (professionals, career changers) | P1 (beginners, no goal) | P2 (exam students) | P5 (interest) |
|---|---|---|---|---|
| Clarity of the goal (needed for the roadmap engine) | ● high — the goal is external and testable | ◐ low until coached | ● high but exam-specific | ◐ variable |
| Willingness to pay | ● higher (career-linked ROI) | ◐ low early, rises with progress | ◐ usually parent-funded, price-sensitive | ◐ low/occasional |
| Fit with the core differentiator (projects + measurement) | ● excellent — artefacts are the point | ◐ good after the first win | ◐ good but content-alignment heavy | ◐ moderate |
| Cost of curriculum development | ◐ moderate (fewer, deeper paths) | ◐ moderate | ○ high (exam alignment, annual updates) | ○ high (breadth) |
| Risk of overpromising | ◐ career claims must be carefully bounded | ● low | ○ exam-result claims are dangerous | ● low |
| Time-to-first-value | ● fast (real task on day 1) | ◐ | ◐ | ● |

**Also PROPOSED:**

- Do not exclude P1; capture them explicitly as a "first-time learner" onboarding variant (the entry state) inside the P3/P4 product, because a large share of P3/P4 learners start as P1.
- **Do not** target P2 in the first release (exam-specific content obligations would dominate the roadmap).
- **Do not** build for P5's breadth; serve them with the same engine and free tier.
- **Later audiences (FUTURE):** instructors/content contributors, schools and universities, employers and training providers. These are explicitly **not** Revenue Phase 1 audiences; each requires a different product (rostering, reporting, safeguarding, procurement) and should be entered only after the individual product retains users.

### 5.3 Audience assumptions that still require research (UNVALIDATED)

Each of these must be tested in Phase 0 (§15.2) before it is treated as true:

1. Goal-driven adults in the target markets will pay a monthly subscription for structured personalisation rather than defaulting to free AI assistants.
2. "Proof of capability" (artefacts, measured mastery) is valued more than certificates by both learners and, where relevant, employers.
3. Arabic-first, RTL-native UX is a meaningful purchase driver, not merely a preference.
4. Local payment friction (card penetration, mobile-money and cash-agent habits) materially changes conversion in the MENA beachhead.
5. A 15-minute daily session size is the right default for the primary audience (it might be 25 or 45 minutes).
6. Learners will accept an AI tutor that deliberately withholds answers instead of complying (this is a behavioural bet, not a technical one).

---

## 6. Product concept and core learning cycle

This section is the product specification. Everything in it is **PROPOSED** unless labelled otherwise. It assumes the MVP scope in §15.3.

### 6.1 Goal-based onboarding

**Objective:** convert an ambition expressed in ordinary language into a structured, testable goal plus the minimum profile data needed to plan well. **Target: 6–9 minutes to a proposed roadmap, with a hard cap of 12 questions.**

#### 6.1.1 Onboarding steps

| # | Step | Purpose | What is collected | Why this data is necessary (justification rule) | Skippable? |
|---|---|---|---|---|---|
| 1 | Welcome + how TALIMGO works | Set expectations: what the product does, what it will not promise (§3.5), and how the cycle works. | Nothing. | Trust before data collection. | No |
| 2 | Goal selection or description | Anchor the entire journey. | Free-text goal + goal template selection (career / exam / work skill / personal project / language / curiosity). | Without a goal there is no roadmap; the template selects the curriculum family. | No |
| 3 | Outcome clarification | Turn an aspiration into a testable outcome. | "What will you be able to do?", target date (optional), environment (work/school/personal), must-have vs nice-to-have. | Determines milestone definitions and project selection. | Date optional |
| 4 | Prior knowledge & experience | Avoid teaching what the learner already knows; catch false fluency. | Self-reported level per relevant area + years/months of experience + tools already used. | Self-report alone is unreliable [R22] but is a cheap prior for the diagnostic. | No |
| 5 | Diagnostic assessment | Replace self-report with evidence. | 8–20 adaptive items and (where feasible) 1–3 practical tasks on the critical prerequisites of the chosen path. | Enables placement, skipping, and prerequisite repair (§6.2). | Not for placement; "skip and start at beginner" allowed |
| 6 | Available time & schedule | Plan realism — the single biggest determinant of plan failure. | Hours per week (band), session length preference, days of week, quiet hours for notifications. | Drives task sizing, milestones, and notification timing. | No (defaults offered) |
| 7 | Learning preferences & accessibility | Match activity formats and remove barriers. | Format preference (read / watch / build), explanation depth, language of explanation, RTL preference, text size, motion sensitivity, screen-reader use, low-data mode. | Drives activity mix and UI behaviour; accessibility must be collected, not assumed. | Yes (defaults) |
| 8 | Baseline assessment (where appropriate) | Establish a starting measurement for later comparison. | Path-specific baseline of the target skill (not just prerequisites). | Required to make "you improved" claims defensible (§16). | Yes, with a visible consequence warning |
| 9 | Roadmap generation | Deliver the product's central promise in the first session. | Nothing new — consumes steps 2–8. | This is the value moment. | No |
| 10 | Learner review, acceptance, customisation | Convert a generated plan into an owned plan. | Milestone acceptance, reordering within constraints, removal of optional items, target-date change. | Ownership predicts adherence; the learner must be able to override the system. | No |

#### 6.1.2 Onboarding design rules

1. **Every question must earn its place.** If a question does not change the generated roadmap, delete it. (Test: *"If this field were always the same value, would the plan differ?"*)
2. **Progress must be visible** as stages, not as a percentage that stalls.
3. **Estimate before asking.** Where a sensible default exists (session length, time zone, language), propose it and let the user correct it.
4. **Never block on perfection.** If the learner abandons mid-onboarding, resume exactly where they stopped and offer "generate a first draft plan now" from partial data.
5. **Accessibility is in the flow, not buried in settings** — but not all of it in onboarding either; a "Preferences" step and a persistent settings entry point both exist.
6. **Do not collect:** national ID, exact address, phone number (unless required by the chosen payment or 2FA method), gender, or any data not used by a feature. Data minimisation is a value (§3.7) and a legal requirement in the target jurisdictions (Appendix D; §11.3).

#### 6.1.3 Onboarding success criteria (acceptance)

- ≥ 70% of users who start onboarding reach a displayed roadmap (**proposed hypothesis, not a target promise** — §16.4).
- Median time from first screen to first roadmap ≤ 9 minutes.
- Zero mandatory questions unrelated to roadmap generation (verified by review of the onboarding spec).
- A learner can export or delete everything collected during onboarding without contacting support (§13.3).

### 6.2 Personalised assessment

**Objective:** estimate the learner's starting point honestly, distinguish *demonstrated knowledge* from *self-reported confidence*, and keep every estimate provisional.

#### 6.2.1 Evidence hierarchy

| Tier | Evidence type | Weight in the estimate | Notes |
|---|---|---|---|
| 1 | **Assisted performance** (correct with a hint or with the tutor's help) | Lowest | Evidence of readiness to learn, not of mastery. |
| 2 | **Unassisted performance** (correct on first attempt, no hints) | Medium | The baseline standard for "demonstrated". |
| 3 | **Repeated unassisted performance over time** (e.g. correct at day 1, day 8, day 30) | High | The strongest signal; drives mastery and review scheduling (§6.5.6). |
| 4 | **Transfer** (applies the skill in a new context, an unfamiliar problem, or a project) | Highest | The only evidence that justifies "can do" language in learner-facing reporting. |
| — | Self-reported confidence | **Never used alone** | Recorded separately as metadata; can trigger a *check*, never a placement. |

#### 6.2.2 Diagnostic mechanics (PROPOSED)

- **Adaptive question pool per skill node** with difficulty bands; stop when the estimate's confidence interval is narrow enough for a placement decision, or after a cap (8–20 items per path).
- **Practical tasks** where feasible: a short code snippet to fix, a data question to answer, a sentence to translate and explain, a spreadsheet operation to perform. Practical tasks are the highest-value diagnostic but cost the most engineering effort; MVP offers them for the technical paths only.
- **Prerequisite probing before content placement:** the diagnostic always includes the critical prerequisites of the target path (for example arithmetic and control flow before recursion).
- **Misconception detection, not just correctness:** store *which* wrong answer was chosen and map it to a known misconception where the item bank supports it.

#### 6.2.3 Confidence levels attached to every estimate

| Level | Meaning | Learner-facing wording | System behaviour |
|---|---|---|---|
| **High** | Multiple unassisted successes, including at least one delayed or transfer item | "You've shown this. We'll keep it in occasional review." | Skip the module; schedule light review. |
| **Moderate** | Unassisted success on one or two items | "Looks solid — one quick check and we'll move on." | Compressed module with a verification check. |
| **Low** | Assisted success, or success only on easy items | "You've met this with help. Some practice will make it stick." | Full module with reduced repetition. |
| **Unknown** | No evidence | "We haven't seen this yet." | Full module. |
| **Conflict** | Self-report high, evidence low (or the reverse) | "You said you're confident here, but the evidence is mixed — a two-minute check will settle it." | Trigger a targeted verification before placement. |

#### 6.2.4 Remediation, prerequisites, and reassessment triggers

| Trigger | System action |
|---|---|
| Learner fails a prerequisite check twice | Insert a **prerequisite repair module** before the main path; explain why; cap repair at one prerequisite layer per cycle to avoid infinite regression. |
| Learner scores < 60% on a module assessment but ≥ 85% on practice | Suspects assessment anxiety or item ambiguity → offer an alternative assessment format (oral explanation to the tutor, project-based evidence). |
| Learner scores well in practice and fails in transfer/project | Keep mastery at "practising", not "mastered"; add varied-context practice. |
| Learner answers correctly but very slowly | Flag for fluency practice (not remediation). |
| 30+ days since last evidence on a high-confidence skill | Downgrade confidence one level and schedule a short review (retrieval-based, not re-teaching). |
| Learner's goal or time budget changes materially | Re-run the diagnostic for the *new* prerequisites only; never re-run everything. |
| Learner requests "I know this, skip it" | Offer a challenge assessment; accept the result; do not silently trust the claim. |

#### 6.2.5 Assessment integrity rules (CONFIRMED)

1. No score is presented as final; every estimate carries a confidence label and a "last evidenced on" date.
2. No mastery estimate is displayed without at least one unassisted evidence item.
3. Self-reported confidence never raises a placement on its own.
4. The learner can always see *why* the system believes what it believes ("you answered 3 of 4 correctly, unassisted, on 3 October").

### 6.3 AI roadmap generator

**Objective:** produce a plan that is *structurally valid* (prerequisites respected), *realistic* (fits the stated time budget), *inspectable* (every element has a rationale), and *revisable*.

#### 6.3.1 Roadmap hierarchy

`Goal → Milestones → Learning paths → Modules → Lessons → Concepts → Practice → Assessments → Projects`

| Level | Definition | Typical duration (estimate, labelled as estimate in UI) | Example (career changer → front-end) |
|---|---|---|---|
| **Goal** | The learner's stated outcome plus success criteria. | 1–18 months | "Build and deploy three responsive web apps and be able to read any modern JavaScript codebase." |
| **Milestone** | A visible, meaningful checkpoint that the learner can be proud of. | 2–6 weeks | "Ship an interactive landing page." |
| **Learning path** | A coherent sequence of modules that establishes a capability area. | 2–8 weeks | "JavaScript fundamentals." |
| **Module** | A thematic cluster of lessons with its own assessment. | 3–10 hours | "Functions and scope." |
| **Lesson** | One sitting-sized unit with a single learning objective. | 15–45 minutes | "Parameters, arguments, and return values." |
| **Concept** | The atomic knowledge unit tracked in the skill graph. | — | "Return value", "scope", "closure". |
| **Practice** | The activity that produces evidence for a concept. | 5–20 minutes | Retrieval questions, an exercise, a mini-build. |
| **Assessment** | A structured measurement against a stated objective. | 10–40 minutes | Module check; milestone assessment. |
| **Project** | A build task with deliverables and a rubric. | 2–20 hours | "Todo app with persistence." |

#### 6.3.2 Required attributes for every significant roadmap element

Where applicable, each element stores:

| Attribute | Purpose | Display rule |
|---|---|---|
| **Learning outcome** | What the learner will be able to do. | Always displayed on the element card, first line. |
| **Prerequisites** | What must be true before starting. | Shown; unmet prerequisites block or warn with an explanation. |
| **Estimated study time** | Planning realism. | Always labelled "estimate" — never "will take exactly". |
| **Recommended resources** | Curated internal + external material. | Licence-checked; provenance stored (§7.6). |
| **Practice activities** | Active learning (never optional for a core concept). | At least one per concept. |
| **Assessment method** | How capability will be measured. | Stated in advance so the learner knows the bar. |
| **Completion criteria** | Objective definition of "done". | Explicit thresholds, not "watch the video". |
| **Dependencies** | Other skills this depends on or unlocks. | Visualised in the skill map (§6.6.4). |
| **Remediation recommendations** | What to do if the learner struggles. | Pre-authored, not improvised at failure time. |
| **Next recommended action** | Always exactly one primary action. | Rendered as the primary CTA on every state. |

#### 6.3.3 Generation pipeline (how the roadmap is actually produced)

**Rule (CONFIRMED): an LLM must not invent a curriculum from nothing.** Roadmap generation is a **template + graph + constraint** operation in which the model handles personalisation language, sequencing among valid alternatives, and explanation — not the creation of pedagogical structure ex nihilo.

```
1. Goal parsing          → map free text to a curriculum family + entry point (model + rules)
2. Curriculum graph read  → retrieve the validated subgraph for that family (database, human-authored)
3. Constraint solving     → filter/sort modules by prerequisites, time budget, session length, target date
4. Personalisation        → per-learner selection among approved alternatives; language/level adaptation
5. Explanation layer      → generate rationale text ("why this, why now") from structured facts only
6. Validation gate        → schema validation + prerequisite-order check + time-budget sanity check
7. Learner review         → accept / reorder / remove / adjust
```

**Validation gate requirements (CONFIRMED):**

- Schema validation of the generated plan against a typed plan schema (Appendix C).
- Prerequisite-order verification against the curriculum graph — a plan that violates prerequisites is rejected before display.
- Time-budget sanity: total estimated hours must be within ±25% of the learner's stated availability × horizon, or the plan must be re-scoped and the mismatch explained.
- No generated text may introduce a claim of certification, accreditation, guaranteed outcome, or external recognition (§3.5, §11.1).
- Every generated rationale must be traceable to a structured fact (no free-floating persuasion).

#### 6.3.4 Roadmap presentation rules

- The plan is shown as **a path with milestones**, not as a table of 300 items. Progressive disclosure: milestone → module → lesson.
- Each milestone shows: outcome, estimate, number of sessions at the learner's pace, and what it produces.
- **"Why this is here"** is available on every element (one sentence, generated from structured facts).
- **Reordering** is allowed but constrained: the UI explains when a move would break prerequisites and offers the minimum viable reorder.
- The learner may always see the **full plan** and may always ask for **less**: "give me the 3-hour-per-week version".

#### 6.3.5 Adaptation rules (the ADAPT stage)

| Situation | Detection | System response | Learner-facing message (pattern) |
|---|---|---|---|
| Progressing quickly | Assessment ≥ 90% unassisted, fast completion, few hints | Compress remaining modules of the same area; offer a harder "stretch" project; skip redundant practice on mastered concepts | "You're moving faster than the plan assumed. I've condensed the next module and added a bigger project." |
| Struggling with a prerequisite | Repeated failure at the same prerequisite layer, or high hint usage | Insert prerequisite repair; reduce new-concept load; increase scaffolded practice; add worked examples | "This topic depends on X, and X isn't solid yet. Let's fix X in ~40 minutes and then return." |
| Misses study sessions | No completed session for N days (default 5) | Offer a 15-minute **recovery session**; roll unfinished tasks forward; never invalidate progress | "You've been away 6 days. Nothing expired. Here's a 15-minute restart." |
| Has less time available | Learner changes time budget, or 3 consecutive weeks under-deliver | Re-scope to fewer, higher-priority modules; extend target date with the learner's consent; keep milestones intact | "You have ~2 hours a week now. I've re-scoped the plan to protect the two milestones that matter most." |
| Changes goal | Explicit goal change | Preserve all evidence; map shared skills to the new goal; re-plan only the delta; show what carries over | "You've already evidenced 60% of what the new goal needs. Here's the gap." |
| Loses motivation / low engagement with one format | Repeated session abandonment, format-specific drop-off | Switch activity mix (read → build), shrink sessions, ask directly what feels wrong | "You've skipped the last three reading tasks. Want to try the build-first version of this module?" |
| Data suggests the estimate was wrong | Median actual session time diverges from estimate by > 40% for 2 weeks | Recalibrate *this learner's* rate (personal multiplier) and update all estimates | "Your sessions run about 25% longer than average. I've adjusted future estimates for you." |

**Never:** reset a learner to the beginning; delete evidence; silently change the goal; lengthen the target date without telling the learner; or describe a revised plan as "the correct plan" (it is always a proposal).

### 6.4 AI tutor

**Objective:** provide in-context, level-appropriate help that increases the learner's capability and independence.

#### 6.4.1 Required tutor capabilities (MVP unless marked)

| # | Capability | Behaviour specification |
|---|---|---|
| 1 | Explain a concept at the learner's level | Uses the learner's mastery state to pick depth and vocabulary; avoids undefined jargon; offers a shorter and a deeper version. |
| 2 | Rephrase difficult material | Second and third phrasings on request, each with a different angle (analogy / worked example / counter-example). |
| 3 | Provide examples and analogies | Must be domain-appropriate and, where possible, culturally relevant to the learner's locale without stereotyping. |
| 4 | Answer questions about the current lesson | Grounded in the lesson's stored content; if the answer is not in the lesson, it says so and offers a general answer labelled as general. |
| 5 | Generate practice questions | Generated from the lesson's objectives and concept IDs; answers computed and verified before being shown (§11.1). |
| 6 | Give hints without immediately revealing answers | Three-level hint ladder: (1) nudge/strategy, (2) partial step, (3) worked solution *after* the learner has attempted or explicitly requested it. |
| 7 | Review learner responses | Structured feedback: what was correct, the specific error type, and the smallest useful next action. |
| 8 | Explain mistakes constructively | Names the misconception if known; never characterises the learner ("you're bad at maths") — only the work. |
| 9 | Generate additional exercises | On request, from the same concept pool, with varied surface features (to avoid pattern memorisation). |
| 10 | Recommend revision | Uses the spaced-review schedule; explains the decay curve plainly. |
| 11 | Connect concepts across subjects | Only along validated graph edges; states when a connection is an analogy rather than a formal dependency. |
| 12 | Help plan projects | Scopes, sequences milestones, suggests a minimum viable artefact; never writes the learner's submission for them in assessed work. |
| 13 | Explain why the next activity matters | Always linkable to the goal and the milestone. |
| 14 | (FUTURE) Voice conversation practice | Requires pronunciation scoring judged adequate; not in MVP. |
| 15 | (FUTURE) Live code execution feedback in a sandbox | Sandboxed runner with resource limits; Phase 2 for technical paths. |

#### 6.4.2 Tutor behaviour under uncertainty, weak sources, conflict, and out-of-scope questions

| Situation | Required behaviour | Forbidden behaviour |
|---|---|---|
| The tutor is uncertain | State the uncertainty explicitly, give the best available answer with a confidence qualifier, and provide a way to verify (source, search suggestion, or a human review request). | Fabricating certainty; inventing a citation; hedging so vaguely that the answer is useless. |
| Lesson content is thin or missing | Say that the stored lesson does not cover this; offer a general explanation labelled as such; flag the gap to content operations. | Silently generating authoritative-looking replacement curriculum. |
| Sources conflict | Present the disagreement, name the positions, and say which is better supported and why; never average incompatible claims into a false consensus. | Picking one and hiding the conflict. |
| The question is outside competence (medical, legal, mental-health crisis, safety) | Decline to advise; explain the limit; route to appropriate resources (local emergency or professional help where relevant); offer only general educational framing. | Attempting diagnosis, legal advice, or therapeutic support. |
| The learner asks for an answer to assessed work | Refuse to complete assessed submissions; offer scaffolded help: restate the task, plan the approach, review the learner's draft, explain concepts. | Writing the submission. |
| Prompt injection appears in an imported resource or pasted text | Treat all imported text as data, never as instructions; ignore embedded instructions; log and flag (§11.1). | Following instructions embedded in learner-uploaded or third-party content. |
| The learner requests harmful content | Refuse, explain briefly, and redirect to the legitimate learning objective (e.g. security education is not attack tooling). | Lecturing at length or moralising; providing partial harmful instructions. |

#### 6.4.3 Product separation of concerns (CONFIRMED)

Tutoring, assessment, roadmap planning, and general conversation are **four distinct product functions** with different interfaces, different data contracts, and different safety profiles. They may share infrastructure (model routing, moderation, logging) but must not share user-facing identity or trust expectations.

| Function | Interface | Input | Output | Safety/quality profile |
|---|---|---|---|---|
| **Tutorial** | Lesson pane side panel; "Ask about this lesson" | Lesson context, concept IDs, learner mastery, learner question | Text answer + optional hint + optional worked example | High — grounded in curriculum, hint-ladder enforced |
| **Assessment** | Locked assessment view | Item bank items; no tutor access | Score, item-level correctness, misconception tags | Highest — no AI free-text generation in scoring of objective items; tutor disabled during assessment |
| **Roadmap planning** | Plan view; "Adjust my plan" | Curriculum graph, constraints, evidence | Structured plan object + rationale text | High — structured output with validation gate (§6.3.3) |
| **General conversation** | Separate "Ask anything" surface, clearly labelled | Anything | General answer, clearly labelled as general, not curriculum-grounded | Standard assistant safety; never writes to mastery records |

**Rule:** only the **Assessment** function can create mastery evidence. Tutor conversation and general chat may inform a *recommendation*, never a mastery score.

### 6.5 Active learning system

#### 6.5.1 Activity types

| # | Activity type | Purpose | Evidence produced | MVP? |
|---|---|---|---|---|
| 1 | Short explanations / micro-lessons (3–8 min read or equivalent) | Establish a concept with minimum cognitive overhead | Completion + restatement ("explain it back") | ✅ P0 |
| 2 | Structured reading materials | Depth, reference, revisiting | Reading progress + embedded checks | ✅ P0 |
| 3 | Video and external resources | Explanations that benefit from motion/voice; expert voice | Watch/consume marker + linked retrieval questions | ✅ P0 (linking only; no re-hosting) |
| 4 | Flashcards (spaced) | Memorisation of facts, vocabulary, syntax | Recall grades (again/hard/good/easy) | ✅ P0 |
| 5 | Retrieval-practice questions | The single highest-value activity [R21] | First-attempt correctness, latency, hint use | ✅ P0 |
| 6 | Multiple-choice quizzes | Efficient coverage, misconception detection | Item-level correctness + distractor analysis | ✅ P0 |
| 7 | Open-ended responses | Deeper understanding; writing; reasoning | Rubric-scored (AI first pass + learner self-review; human review for high-stakes) | ✅ P0 for text paths |
| 8 | Coding / practical exercises | Applied skill in a real tool | Test-case results, code review notes | ✅ P0 for technical paths |
| 9 | Simulations / interactive labs | Safe practice of risky, dynamic, or expensive systems | Scenario outcomes and decision traces | ◐ P1 (a small number, only where they beat simpler practice) |
| 10 | Project assignments | Transfer, portfolio, motivation | Artefact + rubric scores | ✅ P0 (one per milestone) |
| 11 | Reflection and revision activities | Consolidation, metacognition, plan adjustment | Learner-written reflection; confidence vs performance gap | ✅ P0 (light: 2–3 prompts per milestone) |
| 12 | Spaced repetition & review sessions | Combat forgetting | Delayed retrieval performance [R21] | ✅ P0 |

#### 6.5.2 MVP activity mix (recommendation)

**Ship in MVP:** 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12 — because the *combination* is what delivers the differentiation. **Defer:** 9 (simulations) except where a path cannot be taught without one; and any activity requiring browser-native media production (recorded video, live voice) until Phase 2+.

**Rationale for deferring simulations:** they are expensive to build well, hard to assess fairly, and only justify their cost where safe practice is otherwise impossible (cybersecurity, networking, chemistry). They are also the natural home of future safe-practice environments (§6.8.4).

#### 6.5.3 Activity design rules

1. **Every concept has at least one active activity.** No concept may be "covered" by explanation alone.
2. **Difficulty is banded** so that the learner spends most time in the productive-struggle zone (roughly 70–85% success on practice), not at ceiling or floor.
3. **Interleaving is deliberate** in review sessions: mix concepts from different modules to build discrimination (evidence supports interleaving and spacing as "desirable difficulties" [R21]).
4. **Feedback is immediate for objective items**, and within 24 hours for human-reviewed work (with a visible status while waiting).
5. **Templates over bespoke**: every activity type has a documented authoring template so quality is repeatable.

#### 6.5.4 Session design

- Default session = **one objective, one activity block, one closing check**; target 15–25 minutes for the primary audience, configurable 10–60.
- A session always ends with a **retrieval check** and a one-line "what you can now do" statement.
- A session never ends mid-assessment; the system warns before the assessment starts and can pause it with state preserved.
- Optional "deep work" sessions (45–90 min) exist for project work.

#### 6.5.5 Remediation design

- Remediation is **pre-authored per concept**, not improvised by the model: a repair mini-lesson, a worked example set, and a reduced-difficulty practice ladder.
- Maximum one prerequisite layer is inserted per adaptation cycle (prevents "you need to learn everything first" spirals).
- If the same concept fails three times across two different adaptation cycles, the system routes to **human review** (a subject reviewer or a documented alternative explanation) rather than repeating the same material.

#### 6.5.6 Spaced repetition policy

- Scheduling uses a spaced-repetition algorithm (PROPOSED: FSRS-style, or SM-2 as a fallback; see §14.4) per concept, with learner-adjusted load limits ("max 20 review items/day").
- Review is **retrieval-first** (question before answer), consistent with the evidence that retrieval beats re-reading [R21].
- Evidence from review feeds mastery: a concept answered correctly after a long interval strengthens the estimate more than an immediate repeat.
- Load is capped so review does not crowd out new learning; when the cap binds, the system shows what would be dropped and why.

### 6.6 Adaptive skill tracking

**Objective:** a learner skill graph that is honest, inspectable, and useful — not a leaderboard of completion percentages.

#### 6.6.1 Skill graph model

A skill node has: an ID, a name, a domain, a parent (for hierarchy), prerequisites, learning objectives, evidence items, a mastery estimate with confidence, last-evidenced date, decay state, related activities, and a recommended next activity.

**Illustrative hierarchy (PROPOSED — matches the brief's example, extended):**

```
Programming
├── Fundamentals
│   ├── Variables and data types
│   ├── Operators and expressions
│   └── Input/output and errors
├── Control flow
│   ├── Conditionals
│   ├── Loops
│   └── Iteration patterns
├── Functions
│   ├── Parameters and return values
│   ├── Scope
│   └── Composition
├── Object-oriented programming
│   ├── Classes and instances
│   ├── Encapsulation
│   └── Inheritance vs composition
├── APIs
│   ├── HTTP fundamentals
│   ├── Authentication (concepts)
│   └── Consuming and mocking APIs
├── Testing
│   ├── Unit tests
│   ├── Test-driven habits
│   └── Debugging with evidence
└── Projects
    ├── Build an artefact end-to-end
    ├── Version control workflow
    └── Deploy and iterate
```

#### 6.6.2 Mastery model (PROPOSED)

Mastery is a **probability-like estimate with uncertainty**, not a completion flag:

| State | Definition | Evidence requirement | Learner-facing label |
|---|---|---|---|
| **Not yet evidenced** | No evidence | — | "Not started" |
| **Introduced** | Saw an explanation; no independent success | Completion of explanation + restatement | "Seen it" |
| **Practising (with support)** | Succeeded with hints or worked examples | ≥ 1 assisted success | "Practising with help" |
| **Practising (unassisted)** | Succeeded unassisted once | ≥ 1 unassisted success | "Can do it with practice" |
| **Consolidating** | Succeeded unassisted repeatedly across sessions | ≥ 3 unassisted successes with ≥ 1 delayed (≥ 3 days) | "Getting reliable" |
| **Evidenced / mastered** | Repeated unassisted success **plus** transfer (new context or project use) | ≥ 3 unassisted + 1 delayed + 1 transfer | "Evidenced — you can do this" |
| **Needs review** | Previously evidenced, decay detected | Failure on a delayed review, or > 60 days without evidence with low confidence | "Worth a quick review" |

**Storage policy (CONFIRMED):** every state change stores the evidence that caused it (activity ID, timestamp, correctness, hint count, latency), so the estimate is always explainable.

#### 6.6.3 Rules that prevent fake progress

1. **Lesson completion never increases mastery.** Only assessment/practice evidence does.
2. **Watching a video never increases mastery.** It may mark a concept "introduced".
3. **Clicks, streaks, time and XP never appear in the mastery model.**
4. **A single success never produces "mastered".**
5. **The model must be able to lose confidence** (decay) and to *say so* without treating the learner as failing.
6. **Learner visibility:** the learner can open any skill node and see the evidence log in plain language.

#### 6.6.4 Skill map presentation

- Default view: a **tree/outline** with a compact visual state for each node (same state vocabulary as §6.6.2 — never red "failed", always neutral or "needs review").
- Secondary view: a **radial or path visual** for orientation, used sparingly (accessibility: never the *only* representation; always accompanied by the list).
- Filtering: "show only what my current milestone needs", "show what I haven't practised in 30 days".
- Every node's detail view answers: what this is, why it matters to my goal, what would evidence it, and what to do next.

### 6.7 Daily learning missions

**Objective:** convert the roadmap into a realistic, guilt-free daily plan.

#### 6.7.1 Mission composition

Each daily plan is generated from the learner's stated availability and current state, and may contain:

| Block | Purpose | Typical size | Completion condition |
|---|---|---|---|
| **Warm-up review** | Retrieval of previously learned concepts (spacing) | 3–8 items | Answer set submitted (correctness recorded, not required to be perfect) |
| **New learning** | The next concept/lesson in the plan | 8–20 min | Explanation completed + restatement given |
| **Practice** | Applied exercises for the new concept | 8–20 min | Attempts recorded with success criterion stated in advance |
| **Assessment** (when scheduled) | Structured measurement | 10–40 min | Submitted; result recorded |
| **Project work** (when scheduled) | Milestone progress | 20–60 min | A defined deliverable increment committed |

**Total default: 3 tasks / 15–25 minutes.** The learner selects a shorter ("minimum viable day", 5 minutes: review only) or longer plan.

#### 6.7.2 Mission rules

1. Every task states: **objective, estimated time (labelled estimate), completion condition, and why it matters now**.
2. The learner can **postpone** (individually or whole day), **reschedule**, **swap format**, and **shorten** any task.
3. The learner can **pause the journey** (a first-class state) with an explicit "resume" plan; pausing never destroys evidence or resets milestones.
4. After missed days, the system offers **recovery** rather than accumulation: ≤ 15 minutes, review-first, then continue (§6.3.5).
5. **Notification policy:** at most one learning reminder per day by default; no reminders during declared quiet hours; no "you're failing" language; cap total notifications (see §13.6).
6. **Weekly planning ritual (optional, 3 minutes):** confirm time availability for the coming week and adjust the plan; this is the highest-leverage habit for retention and should be offered, not forced.

#### 6.7.3 Recovery design detail

| Days away | System behaviour | Message pattern |
|---|---|---|
| 1–2 | Roll tasks forward quietly; show "catch up" option | "Yesterday's task is still here when you're ready." |
| 3–6 | Offer a recovery session; no streak commentary | "Here's a 15-minute session that picks up where you left off." |
| 7–29 | Offer recovery + slightly reduced week; ask (once) whether to adjust the goal or timeline | "It's been two weeks. Want to keep the same goal and timeline, or should we adjust?" |
| 30+ | Offer a "reset the schedule" flow that preserves all evidence and rebuilds the plan around current availability; never a "start over" | "Your progress is intact. Let's rebuild the schedule around your life now." |

### 6.8 Projects and real-world outcomes

**Objective:** make learning produce something real, and make assessment about production rather than recognition.

#### 6.8.1 Project anatomy (required fields)

| Field | Description |
|---|---|
| **Meaningful objective** | What the learner will have built/solved and why it matters (connected to the goal). |
| **Prerequisite skills** | Skill node IDs that must be at least "practising (unassisted)". |
| **Step-by-step milestones** | 3–7 increments, each completable in one session, each with its own definition of done. |
| **Practical deliverables** | The concrete artefacts (repository, document, dataset, design file, recording, deployed app). |
| **Assessment rubric** | Criteria with observable levels; published *before* the learner starts. |
| **Feedback** | Automated checks where possible + AI rubric first pass + learner self-assessment; human review for high-stakes/capstone work. |
| **Optional portfolio output** | Whether the artefact can be exported as a portfolio piece, plus guidance on describing it honestly. |

#### 6.8.2 Project scaling ladder

| Level | Scope | Example | Evidence weight |
|---|---|---|---|
| **Exercise** | One concept, minutes | "Write a function that normalises a list of names." | Concept-level |
| **Mini-project** | One module, 1–3 hours | "Build a CLI to-do list with file persistence." | Module-level transfer |
| **Guided project** | One path, 4–12 hours | "Build and deploy a responsive portfolio page." | Path-level transfer |
| **Milestone project** | Cross-module, 8–20 hours | "Full-stack notes app with auth and tests." | Milestone completion |
| **Capstone** | Whole goal, 20–80 hours | "Ship a production-quality application with documentation and a public URL." | Goal completion + portfolio |

#### 6.8.3 Rubric design rules

1. Criteria are **observable** ("handles an empty input without crashing") not dispositional ("shows good thinking").
2. Levels are described concretely (Not yet / Developing / Meets / Exceeds) with examples.
3. **AI scoring is advisory**: it must return per-criterion evidence, cite the learner's artefact, and never be the sole basis for a high-stakes judgement (§11.4).
4. The learner can **dispute** a score; disputes are reviewed by a human and feed a rubric-quality log.

#### 6.8.4 Safe and authorised practice environments (technical and security paths)

**CONFIRMED policy:** TALIMGO will only offer practice in environments that are legal and authorised.

- **Programming:** isolated, resource-limited containers (per-session, no outbound network by default, no persistent credentials). Never run untrusted learner code on the platform's own infrastructure without sandboxing.
- **Cybersecurity:** dedicated, isolated lab environments that are either (a) officially provided for training, or (b) purpose-built by TALIMGO and explicitly authorised. **No real-world targets, no live scanning of third-party systems, no malware development, no credential-cracking against real services.** Educational content on attack techniques is limited to what is required to understand defence, and always inside the authorised lab.
- **Data science / AI:** only synthetic, public-domain, or properly licensed datasets; a documented data-provenance register per dataset (§7.6).
- **Finance:** simulations only; explicitly educational framing with no personalised investment advice (§7.5.6).
- **Safety/accuracy review:** cybersecurity, health-adjacent, financial, and legal-adjacent content requires subject-matter review before publication (§11.2).

### 6.9 Progress, motivation, and gamification

**Objective:** support persistence without manipulating the learner or misrepresenting capability.

#### 6.9.1 Dashboard priorities (CONFIRMED order)

The primary dashboard shows, in this order:

1. **Current goal** (one line, in the learner's own words).
2. **The next useful action** (single primary CTA; ≤ 1 sentence of rationale).
3. **Recent progress** (evidence-based: concepts evidenced this week; last milestone moved).
4. **Important blockers** (unmet prerequisite, overdue assessment, an item awaiting human review).
5. *Then* engagement extras (streak, XP, challenges) — visually secondary, never above the fold on mobile.

#### 6.9.2 Motivation mechanics and their honest limits

| Mechanic | Purpose | Honest limit (must be communicated or enforced) |
|---|---|---|
| **XP** | Reward effort and consistency | XP is not mastery; the UI never mixes them in the same chart. |
| **Levels** | Sense of progression | Levels are broad bands tied to *evidenced* capability, not time on site. |
| **Streaks** | Habit support | Streaks measure *showing up*, not learning. Breaks are explicitly neutral (§6.9.4). |
| **Achievements / badges** | Recognition of specific behaviours (first project shipped, 30-day review streak) | No badge may imply a professional credential. |
| **Milestones** | The primary meaningful unit of progress | Milestones require assessed evidence to complete. |
| **Optional challenges** | Stretch goals for fast learners | Opt-in only; never required to complete a milestone. |
| **Weekly summary** | Reflection and planning | Reports evidence, not vanity time; includes "what did not go well". |

#### 6.9.3 Anti-patterns (CONFIRMED prohibited)

- Paid streak freezes, streak-loss shaming, "you lost 47 points" messaging.
- Leaderboards presented as proof of mastery; leaderboards on adult career paths at all in MVP.
- Push notifications engineered to trigger anxiety (e.g. "your friends are ahead of you").
- Time-on-platform goals for learners; any internal OKR that rewards session length.
- Hidden difficulty monetisation (e.g. locking remediation behind a paywall).
- XP or badges purchasable with money.

#### 6.9.4 Break and absence semantics (CONFIRMED)

| Concept | Rule |
|---|---|
| "Streak" | Counts days with a completed task. Displayed as an informational metric. |
| Missing days | Never described as failure; no red state; no lost-evidence messaging. |
| "Streak freeze" | Not sold. Pauses are a right, not a purchase. |
| Pause | First-class state; preserves everything; produces a resume plan (§6.7.3). |
| Comeback | Explicitly celebrated as a positive event ("welcome back, here's the restart path"). |

### 6.10 Career and portfolio features

**Status:** FUTURE (Phase 2–3), documented now so the data model does not block it.

#### 6.10.1 Intended capability

- Map a learning goal to a **role competency model** (for example: junior front-end developer competencies → skill nodes → evidence).
- Show a learner their **gap analysis** against a role model: evidenced / partially evidenced / not yet evidenced — with the same honesty rules as §6.6.
- Produce **portfolio-ready artefacts**: project exports with learner-written descriptions, guided by prompts; the system never fabricates experience.
- **Interview preparation:** question banks by competency, mock Q&A with structured feedback, and "explain your project" coaching.
- **Job-market signals (FUTURE, only if lawfully licensed):** trend data on in-demand skills, clearly labelled as indicative, never as a promise of employability.

#### 6.10.2 Mandatory disclaimers (CONFIRMED)

Every career-related surface must carry, in-context and not buried in terms:

- "This is guidance based on the skills in your plan, not a prediction or a guarantee of employment."
- "Job-readiness estimates are TALIMGO's own model, not an employer or industry certification."
- "Employers set their own requirements; always check the specific role."

#### 6.10.3 Exclusions

- No employer integrations, recruiter marketplace, or CV distribution to third parties in the first release.
- No claim of accreditation, licensure, or industry recognition.
- No automated hiring decisions or candidate scoring (would create high-risk obligations in multiple jurisdictions — see §11.3).

---

## 7. Curriculum and subject architecture

### 7.1 Long-term breadth, narrow launch

**CONFIRMED:** TALIMGO's ambition is multi-domain. **PROPOSED:** the first release covers three paths in depth (§15.3), because breadth at launch is the most common cause of unfinished edtech products.

| Term | Definition |
|---|---|
| **Domain** | A top-level field (Technology, Languages, Business, Creative, Science & Maths, Personal & Professional, Finance). |
| **Subject** | A named area inside a domain (e.g. Web Development). |
| **Path** | A curated, prerequisite-checked route toward a goal within a subject (e.g. Front-End Foundations). |
| **Module / Lesson / Concept** | As defined in §6.3.1. |
| **Capability tag** | A labour-market-ish label used for career mapping (FUTURE). |

### 7.2 Subject taxonomy

The taxonomy below is the **intended breadth**, not a claim that content exists. Each domain has a distinct pedagogical profile; treating them identically is a design error.

| Domain | Subjects (initial scope map) | Dominant teaching methods | Typical exercises | Assessment approach | Expert review required? | Safety/accuracy requirements | Example project |
|---|---|---|---|---|---|---|---|
| **Technology** | Programming, web dev, mobile, AI/ML, data science, databases, cybersecurity, networking, cloud, DevOps, IoT, robotics | Explanation → worked example → hands-on build; sandboxed practice; debugging practice | Code exercises with tests, bug hunts, refactors, schema design, queries, lab tasks | Automated test cases + rubric review for design; transfer via project | Yes for security, AI/ML, cloud architecture, and anything a learner could deploy into production | Authorised sandboxes only (§6.8.4); no attack tooling; dependency/licence hygiene; no real credentials | "Build and deploy a responsive web app with tests and a README" |
| **Languages** | English, French, Spanish, Arabic, more later (Phase 4) | Comprehensible input + deliberate output practice; explicit grammar only where it unblocks production; pronunciation work later | Listening/reading comprehensions, sentence production, role-play, dictation, translation-with-explanation, conversation drills | Item-level + production rubrics (accuracy, range, register); delayed speaking assessment only when voice is in scope | Yes for pronunciation and level calibration (CEFR-style) | Cultural appropriateness; no dialect authority claims; correct levelling claims | "Record a 3-minute professional introduction and respond to two questions" (Phase 2+, needs voice) |
| **Business & entrepreneurship** | Entrepreneurship, marketing, sales, business fundamentals, e-commerce, management, copywriting, personal branding | Case-based reasoning; worked decisions with trade-offs; templates; critique of real-world artefacts | Business cases, pricing exercises, campaign critiques, copy rewrites, unit-economics spreadsheets | Rubric-scored submissions; peer/prompted self-review; no "right answer" framings where judgement is involved | Yes for regulated claims (advertising law, financial promotions) | No legal/tax advice; no guarantees of business outcomes; jurisdiction-specific rules flagged | "Write a one-page go-to-market plan for a product you can actually build" |
| **Creative** | Graphic design, UI/UX, video editing, motion design, content creation, photography, 3D | Critique-driven studio model: make → critique → revise; reference analysis; reproduction studies | Design exercises, redesign critiques, asset production, shot lists, storyboards | Rubric on craft + intent + accessibility; portfolio-grade feedback | Yes for design-system and accessibility claims; recommended for brand-sensitive work | Asset licensing; likeness/consent rules; no copying of specific copyrighted styles | "Redesign a real interface to meet WCAG contrast and re-test it" |
| **Science & Maths** | Mathematics, physics, chemistry, statistics, introductory scientific concepts | Worked examples → faded scaffolding → independent problem sets; misconception-driven remediation | Problem sets, derivations, unit reasoning, lab/data interpretation, simulation tasks | Item-level correctness with misconception tagging; delayed transfer items; multi-step problems | Yes for chemistry/physics lab-adjacent and health-adjacent content | No medical advice; lab safety framing; correct use of uncertainty and units | "Analyse a public dataset and write a short statistical report with limitations" |
| **Personal & professional development** | Communication, critical thinking, writing, productivity, research, project management | Practice-in-context with feedback loops; structured reflection; realistic scenarios | Writing drafts + revisions, argument mapping, prioritisation exercises, meeting simulations | Rubric-scored artefacts + self-assessment vs feedback deltas | Recommended for critical-thinking and research methodology content | Avoid therapeutic framing; mental-health topics route to professional help (§6.4.2) | "Write a research brief with sources, an argument map, and a counter-argument" |
| **Finance & practical knowledge** | Financial literacy, budgeting, accounting fundamentals, carefully scoped introductions to investment concepts | Scenario-based learning; spreadsheets; case studies; rule-grounding | Budget builds, statement analysis, ratio calculations, risk scenarios | Rubric + numeric accuracy; explicit uncertainty in market-topic content | **Yes — mandatory** for any investment-adjacent content | No personalised investment advice; clear educational purpose; jurisdiction disclaimers; avoid implying returns | "Build a personal budget model with assumptions you can defend" |

### 7.3 What each domain demands of the platform (engineering consequences)

| Domain | Special platform requirement | Implication |
|---|---|---|
| Technology | Code execution sandbox; repository integration (FUTURE) | Isolated runners, resource and network limits, artefact storage, licence scanning of learner dependencies. |
| Languages | Audio capture/playback; pronunciation scoring (FUTURE); script/font handling for Arabic, Cyrillic, etc. | Font subsetting and shaping; RTL rendering; voice features deferred to Phase 2+. |
| Business | Document/spreadsheet artefacts; case libraries with usage rights | File storage; licensing register; template library. |
| Creative | Image/video asset handling; critique workflows; large file handling | Storage cost control is a first-class requirement (§13.9). |
| Science & Maths | Formula rendering (MathML/KaTeX-style); graphing; unit-aware checking | Rendering pipeline + accessibility (formulas need text alternatives). |
| Personal development | Text artefacts; rubric review at volume | Human review capacity planning (§11.4). |
| Finance | Numeric validation; disclaimers by jurisdiction; no advisory language | Content review gate + localised disclaimers. |

### 7.4 How course authors and AI-generated content coexist

**The problem to avoid:** duplicated lessons, contradictory explanations, unreviewed AI content that contradicts authored content, and curricula that drift every time a model is upgraded.

**PROPOSED governance model:**

| Layer | Who creates it | Who approves it | Can an LLM generate it? |
|---|---|---|---|
| **Curriculum structure** (domains, paths, modules, concept graph, prerequisites) | Curriculum lead + subject experts | Curriculum lead | ❌ No. Structure is authored and reviewed. |
| **Canonical lesson content** (explanations, examples, item banks, rubrics) | Authors, subject experts | Peer reviewer + subject-matter reviewer for high-risk domains | ❌ Not as the source of record. AI may *draft* for human editing, clearly marked as draft. |
| **Generated variants** (rephrasings, extra examples, extra practice items, level adaptations) | AI, grounded in canonical content | Validated automatically + sampled human review + user reporting | ✅ Yes, within constraints, labelled as generated. |
| **Tutor dialogue** | AI, in real time | No pre-approval; post-hoc monitoring + user reporting | ✅ Yes, with guardrails (§11.1). |
| **Translations & localisations** (Phase 2+) | AI first pass | Human reviewer fluent in the target language **and** the subject | ✅ Yes, as draft only. |

**Conflict resolution rule (CONFIRMED):** canonical content always wins over generated content. If a learner's tutor, generated practice, or translation contradicts a canonical lesson, that is a defect: the system records it, surfaces the canonical explanation, and files a content issue.

**Duplicate prevention (CONFIRMED):**
- One canonical home per concept; other appearances **reference** the concept ID rather than restating it.
- New content is checked against existing concept coverage before authoring ("this objective is already covered by CONCEPT-1421 — extend it instead of creating a new lesson").
- Retired content is archived, never deleted, and is never served to learners.

### 7.5 Curriculum data model (conceptual)

| Entity | Key fields | Relationships | Ownership |
|---|---|---|---|
| Domain | id, name, description, review policy | → Subjects | Curriculum |
| Subject | id, domain_id, description | → Paths | Curriculum |
| Path | id, subject_id, goal_template, entry_requirements, exit_capabilities | → Modules | Curriculum |
| Module | id, path_id, objectives, estimated_hours, assessment_id | → Lessons | Curriculum |
| Lesson | id, module_id, objective, activities[], estimated_minutes | → Concepts | Curriculum |
| Concept | id, name, domain, parent_concept_id, prerequisites[] | ←→ Activities, Evidence | Curriculum |
| Activity | id, type, concept_ids[], difficulty_band, payload | → Evidence outcomes | Content |
| AssessmentItem | id, concept_ids[], type, difficulty, answer_key, misconception_tags, review_status | ← Evidence | Assessment |
| Rubric | id, criteria[], levels[], applicable artefact types | ← Project | Assessment |
| Project | id, objective, prerequisite_concepts[], milestones[], deliverables[], rubric_id | → Evidence (transfer) | Curriculum + Content |
| Resource (external) | id, url, title, provider, licence, licence_verified_on, checksum_of_usage_notes, last_link_check, status | ← Lesson | Content ops |

### 7.6 External educational resources: discovery, evaluation, credit, availability

**CONFIRMED policy: TALIMGO links to external resources; it does not re-host, re-upload, or re-publish third-party content unless a licence explicitly permits it and the licence has been recorded.**

Workflow for adding an external resource:

| Step | Action | Recorded evidence |
|---|---|---|
| 1 | **Discover** from reputable sources (official documentation, universities, established educators, open-licensed repositories) | Source of the recommendation |
| 2 | **Evaluate**: authority, accuracy, currency, bias, level, language availability, accessibility (captions, contrast), and whether it is the best use of the learner's time | Evaluation note + reviewer name + date |
| 3 | **Licence check**: what does the licence actually permit? Link only? Embed? Translate? | Licence name + URL to the licence text + verification date |
| 4 | **Credit**: visible attribution to the creator and, where required, the licence | Rendered attribution (never hidden in a tooltip) |
| 5 | **Link health**: periodic automated link checking; broken links are replaced or removed within a defined SLA | `last_link_check` timestamp, `status` |
| 6 | **Re-review**: at least every 12 months for fast-moving fields (technology, AI, finance), 24 months otherwise | Review log |
| 7 | **Retire**: mark deprecated, remove from new plans, keep for learners mid-path with a notice | Archive record |

**Rules (CONFIRMED):**
1. **No assumption of free reuse.** Public accessibility is not a licence. Embedding a YouTube video must respect the platform's terms and the creator's rights.
2. **No copying of course materials, curricula, question banks, datasets, or assets** from any third-party platform — including competitors and open-source projects — into TALIMGO content.
3. **No scraping paywalled, login-gated, or terms-restricted material.**
4. **Open-licensed material is used only under its licence terms** (attribution, share-alike implications, non-commercial restrictions). Licence compatibility with TALIMGO's commercial use must be checked *before* use, and share-alike licences (e.g. CC BY-SA) create obligations that must be assessed per resource.
5. **Datasets**: only public-domain, explicitly licensed, or synthetic datasets; each has a provenance record.
6. **Images**: licence recorded per asset; no "found on Google Images"; no AI-generated images presented as photographs of real people, places, or events.
7. **Screenshots of third-party software** are used only where the terms permit, with attribution, and preferably replaced by TALIMGO's own diagrams.

### 7.7 Content validation process (why the AI cannot invent the curriculum)

**CONFIRMED:** curricula are authored and reviewed by humans; the AI is constrained to a validated graph.

| Gate | Gate owner | What is checked | Failure action |
|---|---|---|---|
| G1 — Objective & scope | Curriculum lead | Does this module serve a real goal? Is it distinct from existing content? | Reject or merge |
| G2 — Pedagogical design | Instructional designer | Are objectives measurable? Is there active practice per concept? Is the difficulty progression sane? | Return for revision |
| G3 — Subject accuracy | Subject reviewer (independent of author) | Correctness, currency, terminology, edge cases, misconception list | Return for correction |
| G4 — Safety & compliance | Content ops + legal review for regulated domains | Claims, disclaimers, licences, accessibility notes, age-appropriateness | Block publication |
| G5 — Technical/publish | Content engineer | Rendering, item validation (does every item have a verified key?), metadata completeness, link health | Block publication |
| G6 — Post-publication monitoring | Content ops | Error reports, learner confusion signals, item statistics (e.g. items everyone fails = likely broken) | Correct, revise, or retire |

**Item-level rule (CONFIRMED):** every auto-graded item must have a verified answer key and a stated explanation. Items whose statistics suggest ambiguity (high failure with high learner confidence, or multiple defensible answers) are flagged for review.

### 7.8 Content versioning

- Content is versioned; learners see a stable version of the plan they started (unless a correctness fix is required).
- **Corrections** are always pushed (accuracy beats stability) and the learner sees a small "this lesson was corrected" note when relevant.
- **Improvements** (better examples, restructured lessons) apply to new learners by default, with an opt-in for existing learners to adopt the new version mid-path.
- **Major curriculum restructuring** opens a migration path: keep evidence, map old concepts to new, and never silently discard the learner's masteries.

---

## 8. Information architecture and user journeys

### 8.1 Navigation principles

1. **One primary action** per screen state, derived from the learning cycle's current stage.
2. **Maximum depth of three** from dashboard to any learning action.
3. **Persistent, minimal global navigation** (mobile: 4 items max; desktop: 5–6).
4. **No "feature museum"**: nothing in primary navigation that is not part of the core loop at launch.
5. **RTL is a layout property, not a CSS mirror job** (§9.3.4).
6. **Every empty state teaches** the feature's purpose and offers the one action that fills it.

### 8.2 Proposed navigation structure

**Global (desktop, top-level):** `Today` · `My Plan` · `Learn` (current lesson/practice) · `Skills` · `Projects` · `Ask TALIMGO` (tutor) · `Profile` (menu: progress, resources, settings, billing, help).

**Mobile bottom bar (4 items):** `Today` · `Plan` · `Skills` · `Tutor`.

**Full section register:**

| # | Section | Purpose | Key information shown | Primary user actions | Dependencies |
|---|---|---|---|---|---|
| 1 | Public landing page | Explain the product honestly and convert | Value proposition, how it works, sample journey, pricing, privacy statement, FAQ | Sign up, see pricing, read privacy | Brand assets, validated messaging, legal pages |
| 2 | Sign-up & authentication | Create/enter an account with minimum friction | Email/social options, age declaration, terms | Register, sign in, reset password, enable 2FA | Auth service, email delivery, age policy (§19 DEC-005) |
| 3 | Learner onboarding | Convert a goal into a plan (§6.1) | Progress stages, questions, live plan preview | Answer, skip where allowed, generate plan | Goal templates, diagnostic engine, curriculum graph |
| 4 | Goal selection/definition | Explicit goal record + success criteria | Goal statement, target date, constraints | Create, edit, confirm | Goal schema, curriculum families |
| 5 | Diagnostic assessment | Placement evidence | Questions/tasks, progress, "why we're asking" | Answer, pause, see results, accept/reject placement | Item bank, adaptive engine, misconception tags |
| 6 | Roadmap & milestones | Show the route and own it | Milestones, estimates, prerequisites, "why this" | Accept, reorder, remove optional, adjust time/date | Curriculum graph, planner, validation gate |
| 7 | Learning dashboard ("Today") | One next action; current state | Goal line, next action, recent progress, blockers | Start session, postpone, adjust availability | Missions engine, notification service |
| 8 | Current lesson & practice workspace | Do the work | Lesson content, practice, hints, progress within lesson | Read/watch, answer, request hint, submit, ask tutor | Content service, activity types, tutor |
| 9 | AI tutor interface | In-context help (§6.4) | Conversation, cited lesson context, hint level | Ask, request hint, request extra practice, report a problem | Tutor orchestration, guardrails, logging |
| 10 | Skill map | Inspect capability | Skill tree, mastery states, evidence log, decay flags | Explore, filter, open evidence, launch review | Skill graph, mastery model |
| 11 | Assessments & results | Measure and understand | Assessment list, results, item review, misconception notes | Take, review, retake (when allowed), dispute | Assessment engine, rubrics, review queue |
| 12 | Project workspace | Build something real | Brief, milestones, deliverables, rubric, feedback | Start, submit increment, request feedback, submit final | Storage, rubric engine, review workflow |
| 13 | Review & flashcards | Combat forgetting | Due items, deck/subject filters, load cap | Review, grade recall, adjust daily cap | Scheduler (FSRS/SM-2), activity types |
| 14 | Resource library | Curated, licensed external + internal material | Filters by subject/format/licence/level | Open, save, rate, report broken link | Resource register (§7.6) |
| 15 | Progress & analytics | Truthful reporting to the learner | Mastery over time, evidence, consistency, project status, export | View, filter by period, export PDF/CSV | Analytics pipeline, mastery model |
| 16 | Profile, preferences, language, accessibility | Control the experience | Language, RTL/LTR, text size, motion, notification prefs, session length | Change settings, download data, delete account | i18n/RTL framework, prefs service |
| 17 | Subscription & billing | Pay and manage plans | Plan, usage of AI limits, invoices, payment methods | Upgrade, downgrade, cancel, update payment | Billing provider, entitlements service |
| 18 | Help, feedback, privacy, account management | Support and trust | FAQ, contact, report content, policies, status | Read policies, report issue, contact support, manage sessions | Support tooling, policy pages |
| 19 | Admin/moderation (internal) | Governance (§11.2) | Content queue, review status, incident log, abuse reports | Review, publish, retire, investigate | Admin RBAC, audit log |

### 8.3 Essential user flows

Each flow lists: trigger → screens → system behaviour → exit condition → failure handling. Flows are the test basis for usability work.

#### Flow 1 — Complete beginner creates their first learning plan

```
Landing → Sign up → Age & terms → Onboarding 1 (welcome: what TALIMGO will and won't promise)
 → Goal: "I want to learn to code" (template: career/craft choice)
 → Outcome: "build a simple website for my father's shop"  [clarifies a testable outcome]
 → Experience: none  → Diagnostic: 8 items (identifies: can use a computer; no programming concepts)
 → Time: 4 h/week, 20-minute sessions, evenings  → Preferences: prefers building over reading; AR UI
 → Roadmap preview: 3 milestones ("First page", "Interactive page", "Deployed site for the shop")
 → Review: learner removes one optional module → Plan saved → Dashboard "Today" (first task: 12-minute setup + hello-world in browser)
```

- System behaviour: placement at beginner entry point; plans 4h/week, warns that milestone 3 lands in ~7 weeks (estimate, labelled).
- Exit condition: learner sees a plan and starts the first task.
- Failure handling: if the diagnostic is abandoned, offer a beginner default plan clearly labelled "provisional"; allow the diagnostic to be resumed later.

#### Flow 2 — Experienced learner skips already-mastered material

```
Onboarding → Goal: "become a data analyst" → Experience: 3 years of Excel, some SQL
 → Diagnostic: 14 items + 2 practical SQL tasks
 → Result: SQL = high confidence (6/6 unassisted, includes a JOIN task); Python = unknown; Stats = low
 → Placement proposal: skip SQL fundamentals; start SQL window functions + Python basics
 → Learner challenges: "I don't know window functions" → system offers a 6-item verification
 → Verification: 2/6 → SQL downgraded to moderate; window functions module retained; fundamentals remain skipped
 → Plan accepted; evidence log shows both the original result and the challenge
```

- System behaviour: re-placement without penalty; the learner's objection is treated as data, not resistance.
- Exit condition: plan reflects actual evidence.
- Failure handling: if the learner insists on reviewing mastered material, allow it and mark it "revision" so it does not inflate mastery.

#### Flow 3 — Learner struggling with a prerequisite

```
Session: new concept "recursion" → learns explanation → practice: 3 of 7 correct, heavy hint usage
 → System detects repeated failure on prerequisite "functions and return values"
 → Tutor: "Recursion needs return values to be solid. Two-minute check?" → check fails
 → Insert prerequisite repair (one layer only): 25-minute module with worked examples
 → After repair: retry recursion with scaffolded practice (success 6/7)
 → Evidence: repair module evidenced; recursion recorded as "practising (unassisted)"
 → Plan note: goal date shifts by 3 days (learner is told, can revert)
```

- System behaviour: no blame language; adaptation is explained; only one prerequisite layer inserted.
- Exit condition: learner returns to the main path with adequate prerequisites.
- Failure handling: if repair fails twice, route to an alternative explanation + human review request (§6.5.5).

#### Flow 4 — Learner returning after an extended break

```
No activity for 22 days → system sends at most one "check-in" (if permitted), then stops
 → Learner opens app → "Recovery" screen: "Your progress is intact. 3 tasks are waiting, 1 milestone
   unchanged. Want a 12-minute restart?"
 → Recovery session: review-first (retrieval of 2 older concepts), then continue
 → System asks once: keep goal/timeline, or adjust? (3 options: keep, extend, shrink)
 → If "shrink": re-plan to current availability; milestones preserved; optional modules cut; learner approves
```

- System behaviour: nothing expires silently; no streak shaming; evidence intact.
- Exit condition: learner completes a recovery session and has a valid plan.
- Failure handling: if the learner returns after 6+ months, the plan is rebuilt with a fresh (short) diagnostic on the target skills, and old evidence is retained but marked as historical.

#### Flow 5 — Learner completing a project

```
Project brief → rubric shown up front → milestone 1 (scoped, 40 min) → submit increment
 → Automated checks + AI rubric first pass → learner sees per-criterion evidence and can dispute
 → milestone 2…n → final submission → rubric score + written feedback
 → Project recorded as transfer evidence for the mapped concept IDs → mastery upgrades applied
 → Portfolio export offered (only if the learner chooses; description template provided, no fabrication)
```

- System behaviour: explicit rubric before starting; feedback cites the artefact; disputes routed to human review.
- Exit condition: project marked complete with evidence mapped to concepts.
- Failure handling: incomplete projects remain resumable indefinitely; a stalled project triggers a scoping offer ("reduce to a smaller deliverable").

#### Flow 6 — Learner changing goals

```
"My Plan" → "Change goal" → new goal captured (reason optional) 
 → System maps shared skills: "60% of this goal is already evidenced by what you've done"
 → Gap analysis shown → new plan generated for the delta only → old goal archived (not deleted)
 → Timeline re-estimated (labelled); learner confirms → dashboard updated
```

- System behaviour: no evidence discarded; the previous goal and its artefacts remain accessible.
- Exit condition: new plan accepted.
- Failure handling: if the new goal has no validated curriculum yet (out-of-scope subject), say so plainly and offer the waitlist/nearest related path — never fabricate a curriculum.

#### Flow 7 — Learner reviewing progress and selecting the next milestone

```
Progress → mastery over time + evidence list + consistency (not time-on-site) 
 → system highlights: 3 concepts need review; 1 milestone is 2 tasks from completion
 → next-milestone preview with prerequisites already met → learner selects → today's plan regenerates
```

- System behaviour: recommendations are explained; the learner can choose differently.
- Exit condition: learner commits to the next milestone.
- Failure handling: if the learner picks a milestone whose prerequisites are unmet, show the specific unmet prerequisites and offer the shortest allowed route.

### 8.4 What to avoid in IA/UX (CONFIRMED constraints)

- No more than **one** modal at a time; no modal chains.
- No dashboard with more than **four** primary information blocks above the fold.
- No notification type that cannot be individually disabled.
- No dead-end states: every screen has an exit and a next action.
- No feature that requires reading a help article to understand (if it does, the design failed).
- No decorative animation that cannot be disabled by `prefers-reduced-motion`.

---

## 9. Visual identity and design system

> **Status note (CONFIRMED):** no logo, icon, illustration, or production design asset exists yet. Everything in this section is a **written direction and specification** for designers to execute and for the owner to approve. The palette below is the owner-supplied provisional starting palette.

### 9.1 Design direction

The interface must communicate **progress, intelligence, clarity, practical learning, and forward movement**, and must feel like a contemporary premium software product — closer to a well-made developer tool or a modern finance app than to a school website.

**Five design principles:**

| # | Principle | What it means in practice |
|---|---|---|
| 1 | **Clarity over cleverness** | One primary action per state. Plain labels. No metaphor that requires explanation. |
| 2 | **Evidence over decoration** | Every visual element earns its place by aiding comprehension or orientation. |
| 3 | **Calm surface, confident accent** | Large neutral canvas (near-black text on soft-white surfaces); red reserved for direction, priority, and identity. |
| 4 | **Motion with meaning** | Animation communicates state change (progress, completion, path advance) only; never ambient noise. |
| 5 | **RTL-native, not RTL-translated** | Logical properties, mirrored icons where meaningful, and typography designed for Arabic, not inherited from Latin. |

**Explicitly avoided:** graduation-cap motifs, generic robot/AI heads, brains-as-circuitry, excessive gradients, glassmorphism as a default surface, 3D decorative blobs, clip-art illustrations, and "school" colour clichés (pastel green/blue with cartoon pencils).

### 9.2 Provisional colour palette

#### 9.2.1 Core tokens

| Token | Hex | Role | Notes |
|---|---|---|---|
| `--color-ink` (Primary dark) | `#111318` | Primary text; dark surfaces; logo on light backgrounds; app-icon base | Near-black with a slight cool cast; reads as "premium software" rather than "office black". |
| `--color-brand` (Primary red) | `#D92D20` | Brand identity; primary buttons; active states; progress fill; focus-adjacent emphasis | The single strongest accent. Used sparingly — its power depends on scarcity. |
| `--color-brand-bright` (Bright red accent) | `#F04444` | Non-text accents: icons at ≥ 24px, illustration highlights, chart series, hover glow on dark surfaces | **Not** for small text on white (contrast 3.74:1 — fails AA for normal text). |
| `--color-surface` (White) | `#FFFFFF` | Primary card and content surface | — |
| `--color-canvas` (Soft background) | `#F9FAFB` | App background; secondary panels; table zebra | Distinguishes "page" from "card" without a border. |
| `--color-text-secondary` | `#667085` | Secondary text, labels, metadata, help text | Verified AA on both white and canvas at default body size (§9.2.4). |
| `--color-border` | `#EAECF0` | Borders, dividers, input outlines, table rules | Should not be the only means of distinguishing interactive elements (§9.5.4). |
| `--color-success` | `#067647` | Success states, evidenced mastery, positive deltas | Paired with an icon and text label — never colour alone. |
| `--color-warning` | `#B54708` | Warnings, "needs review", limits reached | Not used for errors (see `--color-danger-text`). |
| `--color-danger-text` (PROPOSED addition) | `#B42318` | Error/destructive **text** and small critical labels | Proposed because `#D92D20` leaves little contrast margin for small text (4.83:1) and `#F04444` fails. |
| `--color-brand-strong` (PROPOSED addition) | `#B42318` | Destructive buttons, high-assurance red text | Verified 6.57:1 on white. |
| `--color-ink-inverse` | `#FFFFFF` | Text on dark and on brand surfaces | — |

> **Observation (UNVERIFIED):** the supplied values closely match a widely published UI colour system (Untitled UI's default palette). If that is the intended source, adopting its existing token naming and its accessibility notes would save design time. Not assumed here.

#### 9.2.2 Dark mode (PROPOSED)

Dark mode is designed separately, not inverted:

| Token | Dark value (PROPOSED) | Rationale |
|---|---|---|
| `--color-canvas` (dark) | `#0B0D12` | Slightly deeper than the light-mode ink so that ink surfaces can sit above the canvas. |
| `--color-surface` (dark) | `#111318` | The light-mode ink becomes the dark-mode card surface; brand consistency. |
| `--color-surface-raised` | `#171A21` | Dialogs, popovers, sticky headers. |
| `--color-border` (dark) | `#262B36` | Visible but quiet. |
| `--color-text-primary` (dark) | `#F2F4F7` | Avoid pure white on dark to reduce halation. |
| `--color-text-secondary` (dark) | `#98A2B3` | Verified AA on `#111318`. |
| `--color-brand` (dark mode) | `#F04444` | The brighter red reads better on dark surfaces as a *text/icon* colour; the darker `#D92D20` is retained for fills where text sits on top. |
| `--color-success` (dark) | `#32D583` | Needs the lighter variant on dark. |

**Rule:** dark mode must be verified independently for contrast; a token that passes in light mode does not automatically pass in dark mode.

#### 9.2.3 Colour usage rules

1. **Red means "this is where to go / this is the thing"** — primary actions, active navigation, progress fill. It never means "error" (errors use `#B42318` + icon + text) and never means "mastery".
2. **Mastery/progress colour semantics:** neutral (not yet) → muted ink; in progress → brand red fill; evidenced → success green. **Warning amber** is reserved for "needs review" and limits, never for learner failure.
3. **Maximum two brand accents per screen** (red + one semantic).
4. **Never rely on colour alone** (WCAG 1.4.1): every state has an icon and/or a text label.
5. **No gradients as brand identity.** If a gradient is used at all, it is a subtle two-step of the same hue on illustration/headers only.

#### 9.2.4 Verified contrast (WCAG 2.x relative-luminance formula, computed 2026-10-10)

These ratios were computed from the hex values using the WCAG 2.1/2.2 relative-luminance and contrast-ratio formulas. **Re-verify in the design tool of record** and re-verify after any hue change.

| Foreground | Background | Contrast ratio | AA normal text (≥4.5) | AA large text / UI (≥3.0) |
|---|---|---|---|---|
| `#111318` | `#FFFFFF` | **18.6 : 1** | ✅ | ✅ |
| `#111318` | `#F9FAFB` | **17.8 : 1** | ✅ | ✅ |
| `#FFFFFF` | `#111318` | **18.6 : 1** | ✅ | ✅ |
| `#667085` | `#FFFFFF` | **4.97 : 1** | ✅ (thin margin) | ✅ |
| `#667085` | `#F9FAFB` | **4.76 : 1** | ✅ (thin margin) | ✅ |
| `#D92D20` | `#FFFFFF` | **4.83 : 1** | ✅ (thin margin) | ✅ |
| `#FFFFFF` | `#D92D20` | **4.83 : 1** | ✅ (thin margin) | ✅ |
| `#F04444` | `#FFFFFF` | **3.74 : 1** | ❌ fails | ✅ (large text ≥18.7px bold / 24px, and non-text UI) |
| `#B42318` | `#FFFFFF` | **6.57 : 1** | ✅ | ✅ |
| `#067647` | `#FFFFFF` | **5.69 : 1** | ✅ | ✅ |
| `#B54708` | `#FFFFFF` | **5.44 : 1** | ✅ | ✅ |

**Design consequence (CONFIRMED):** `#D92D20` may be used for primary button fills with white text and for red text at body size, but any red text smaller than 16px should use `#B42318` for safety margin, and `#F04444` must never carry small text on white.

### 9.3 Typography

#### 9.3.1 Typeface recommendation (PROPOSED)

| Role | Typeface | Licence status | Why |
|---|---|---|---|
| Latin UI + body + headings | **Inter** | SIL Open Font License 1.1 — repository `rsms/inter` reports `OFL-1.1` [R39] | Excellent legibility at UI sizes, extensive OpenType features (tabular figures, contextual alternates), widespread adoption and tooling support. Note: the upstream repository has been relatively quiet (last push to the repo 2024-11-19); the font is stable and widely redistributed. |
| Arabic UI + body + headings | **IBM Plex Sans Arabic** (preferred) or **Noto Sans Arabic** (fallback) | IBM Plex is distributed under OFL-1.1 (`IBM/plex`, actively maintained — last push 2026-10-05) [R39]; Noto fonts are OFL-1.1 (`notofonts/noto-fonts`) [R39] | IBM Plex Sans Arabic is designed to harmonise with a Latin grotesque and holds up at small sizes; Noto Sans Arabic has the broadest coverage. **Verify the licence file of the specific package version before bundling** (§14.6). |
| Numerals | Inter (tabular figures) for tables/metrics; Arabic-Indic numerals only where the locale expects them | — | Prevent layout jitter in tables and progress numbers. |
| Code | **JetBrains Mono** or **IBM Plex Mono** (PROPOSED) | JetBrains Mono is OFL-1.1; IBM Plex Mono is part of `IBM/plex` (OFL-1.1) | Ligature-friendly, clear at 12–14px. |
| Fallback stack | `system-ui, -apple-system, Segoe UI, Roboto, sans-serif` (Latin); `"Noto Sans Arabic", "Segoe UI", Tahoma, sans-serif` (Arabic) | — | Offline/low-bandwidth resilience and graceful degradation. |

**Budget rule:** text fonts ≤ 3 families, ≤ 4 weights per family (Regular 400, Medium 500, Semibold 600, Bold 700). Subset Arabic for the character ranges actually used to control payload (§13.9).

#### 9.3.2 Type scale (PROPOSED tokens)

| Token | Size / line-height (desktop) | Size / line-height (mobile) | Weight | Use |
|---|---|---|---|---|
| `display-lg` | 48 / 1.15 | 32 / 1.2 | 700 | Marketing hero only |
| `display-sm` | 36 / 1.2 | 28 / 1.25 | 700 | Landing sections, milestone celebration |
| `heading-lg` | 30 / 1.25 | 24 / 1.3 | 700 | Page titles |
| `heading-md` | 24 / 1.3 | 20 / 1.35 | 600 | Section titles, card titles |
| `heading-sm` | 20 / 1.35 | 18 / 1.4 | 600 | Sub-sections |
| `body-lg` | 18 / 1.6 | 17 / 1.6 | 400 | Lesson reading text |
| `body-md` | 16 / 1.6 | 16 / 1.6 | 400 | Default UI text |
| `body-sm` | 14 / 1.55 | 14 / 1.55 | 400 | Secondary text, help |
| `label` | 14 / 1.4 | 14 / 1.4 | 500 | Buttons, inputs, nav |
| `caption` | 12 / 1.45 | 12 / 1.45 | 400 | Metadata, timestamps |
| `code` | 14 / 1.5 | 13 / 1.5 | 400 | Code blocks, IDs |
| `numeric-display` | 32 / 1.1 | 26 / 1.15 | 700, tabular | Metric tiles |

**Arabic-specific adjustments (PROPOSED, required):**
- Arabic body text needs **more line-height** than Latin: use ≥ 1.75 for `body-lg`/`body-md` in Arabic.
- Arabic font sizes often need **+1px** relative to Latin equivalents at small sizes for equivalent legibility.
- Avoid letter-spacing on Arabic (it breaks cursive joining); use `letter-spacing: normal` in RTL contexts and never apply uppercase transforms.
- Do not apply Latin-style tight display tracking to Arabic headings.

#### 9.3.3 Text behaviour rules

- Maximum line length: 60–80 characters (Latin), 45–60 (Arabic) for comfortable reading of long-form lesson text.
- Never justify text in narrow columns (creates rivers in both scripts).
- Truncation is not allowed for learning content; use "read more" patterns only in lists of metadata.
- Numbers, dates, and units must be locale-aware from day one (`Intl.*` APIs), including Arabic-Indic vs Western digits per locale preference.

#### 9.3.4 RTL requirements (CONFIRMED, non-negotiable)

1. **Logical CSS properties only** (`margin-inline-start`, `padding-inline-end`, `inset-inline-start`) — never `left`/`right` for layout-critical positioning.
2. **Directional icons mirror; semantic icons do not.** Arrows, chevrons, and progress direction mirror. Icons for "clock", "image", "code", "play" do not mirror. The TALIMGO symbol itself does **not** mirror (brand marks are never mirrored) unless a mirrored variant is deliberately designed and approved.
3. **Charts and timelines flip reading direction**, with axis labels re-anchored; numeric axes generally stay LTR for numeric readability but must be reviewed per chart type.
4. **Code blocks and technical strings stay LTR** even inside an RTL page, with `dir="ltr"` and appropriate isolation to avoid mixed-direction rendering bugs.
5. **Bidi handling is explicit**: use Unicode isolation (`\u2068…\u2069`) or `dir="auto"` where user-generated text can contain mixed scripts.
6. **Progress semantics flip visually but not logically**: "forward" progress in RTL moves left-to-right? — **No.** Progress advances in the reading direction of the interface (right-to-left in RTL), and this must be validated with Arabic-speaking testers, including for the roadmap path visual.
7. **Test both directions for every component**, in the component library's visual regression suite (§13.8).

### 9.4 Logo system

**Direction (PROPOSED).** A geometric, constructed mark built from two ideas: a **T** (TALIMGO) and a **forward path** (Go) — a stroke that starts at a node and advances past a checkpoint toward a terminal node, evoking progress without literal imagery (no books, caps, rockets, or brains).

| Asset | Specification |
|---|---|
| **Primary wordmark** | "TALIMGO" set in Inter Bold/Semibold, all caps, tight-but-legible tracking (≤ +0.01em); optional accent: the crossbar of the "T" or the terminal of the "G" rendered in `#D92D20` while the rest is `#111318`. |
| **Standalone symbol** | A monogram "T" fused with a path/arrow that reads as forward motion; must be legible at 16px (favicon) and recognisable in one colour. |
| **Horizontal lockup** | Symbol + wordmark, symbol at cap height; used in app headers, decks, email signatures. |
| **Compact/vertical lockup** | Symbol above wordmark; used where horizontal space is constrained (avatars, square placements). |
| **Symbol-only** | App icon, favicon, social avatars, loading states. |
| **Light-background variant** | Ink wordmark `#111318` + brand accent `#D92D20`; symbol in ink with red node. |
| **Dark-background variant** | White wordmark + `#F04444` accent; symbol in white with red node. |
| **Monochrome variants** | All-ink on light; all-white on dark; single-colour for stamps, embroidery, faxes, and any low-fidelity reproduction. |
| **App icon** | Symbol on `#111318` (or on `#D92D20`) with generous safe area; must survive iOS/Android masking (test circle, squircle, rounded-square) — no text inside the icon. |
| **Favicon** | Symbol simplified further if needed: maximum two shapes; must read at 16×16. Provide `.ico`, SVG, and a 180px apple-touch PNG. |

**Clear space and minimum sizes (PROPOSED, to be finalised after the mark exists):**

| Constraint | Proposal |
|---|---|
| Clear space | Minimum clear space on all sides = height of the "T" crossbar (or 50% of the symbol's height). Nothing enters this zone — no text, borders, or imagery. |
| Minimum wordmark width (digital) | 96 px |
| Minimum symbol size (digital) | 16 px (favicon), 24 px (in-app), 32 px (avatar) |
| Minimum print sizes | Define once the mark exists; typical: wordmark ≥ 25 mm wide, symbol ≥ 8 mm. |

**Incorrect usage (prohibited, CONFIRMED):**

1. Stretching, compressing, or skewing the logo.
2. Rotating the logo (except a deliberately approved "Go" motion variant).
3. Recolouring outside the approved palette (no purple/blue "tech" versions, no gradients).
4. Adding shadows, bevels, strokes, glows, or 3D effects.
5. Placing the wordmark on busy imagery without a scrim or solid panel.
6. Re-typing the wordmark in a different typeface, or changing letter spacing.
7. Using the symbol as a letter inside another word.
8. Outlining the logo.
9. Mirrored variants in RTL (the symbol is never mirrored).
10. Using the bright red `#F04444` wordmark on white (fails contrast).

**Acceptance criteria for the delivered logo (CONFIRMED):** (a) legible at 16px; (b) reproduces in one colour; (c) distinct from the "Taalim" family of Moroccan education marks (§21); (d) contains no elements that could read as an official emblem, ministry seal, or university crest; (e) supplied as SVG + PNG + app-icon set with a documented colour/space spec sheet; (f) **searched against existing marks before adoption** as part of the clearance process (§21.5).

### 9.5 UI design system

#### 9.5.1 Foundations (PROPOSED tokens)

| Token group | Proposal |
|---|---|
| Spacing scale | 4 · 8 · 12 · 16 · 20 · 24 · 32 · 40 · 48 · 64 (4px base) |
| Radius | `sm 6px` (inputs, badges) · `md 10px` (cards, buttons) · `lg 16px` (panels, dialogs) · `full` (pills, avatars). One radius family only — no mixed 2px/20px chaos. |
| Border width | `hairline 1px` (dividers, inputs) · `focus 2px` (+2px offset) · `emphasis 2px` (selected roadmap node) |
| Elevation | `0` flat (default on canvas) · `1` cards (`0 1px 2px rgba(16,24,40,.06)`) · `2` popovers/menus · `3` modals/drawers. Shadows are subtle and never the primary means of grouping. |
| Motion | `fast 120ms` (hover/press) · `base 200ms` (state change) · `slow 320ms` (panel/route transitions). Easing: `cubic-bezier(.2,0,0,1)` for enter, `ease-in` for exit. **Everything respects `prefers-reduced-motion`. |
| Focus ring | `2px` `#D92D20` outline + `2px` offset, visible on all interactive elements, never removed without an equally visible replacement (WCAG 2.2 §2.4.11/2.4.13). |
| Touch targets | Minimum **44×44px** recommended for primary controls (exceeds WCAG 2.2 §2.5.8's 24×24px minimum) [R36]. |
| Grid & breakpoints | `xs 0–479` · `sm 480–767` · `md 768–1023` · `lg 1024–1279` · `xl 1280–1535` · `2xl 1536+`. Content max-width 1180px for marketing, 720px for lesson reading column. |
| Iconography | Single outline set (e.g. a 24px stroke-based family), 1.5–2px stroke, rounded caps; filled variants only for active/selected states. Consistent optical sizing. |
| Z-index scale | Define named layers (`base 0, sticky 100, dropdown 200, overlay 300, modal 400, toast 500`) — never magic numbers in components. |

#### 9.5.2 Component requirements

| Component | Required states/behaviour | Accessibility requirement |
|---|---|---|
| **Buttons** | Primary (brand fill, white label), secondary (bordered), tertiary/ghost (text), destructive (`#B42318` fill or outlined). States: default, hover, active/pressed, focus, loading (spinner + label retained), disabled (with reason available), full-width mobile variant. | Keyboard operable; ≥44px on mobile; loading state announces via `aria-live`; disabled buttons explain *why* (tooltip or adjacent text). |
| **Links** | Distinguishable from body text without colour alone in dense text (underline on hover/focus; consider permanent underline in lesson content). | Visible focus; not used as buttons for actions (no `<a href="#">`). |
| **Navigation (top/side/bottom)** | Current location clearly indicated; collapsing pattern documented; no more than 6 top-level items desktop / 4 mobile. | Landmark roles; skip-to-content link; focus order matches visual order; works in RTL. |
| **Cards** | Used for one entity (milestone, project, resource). Never nested more than one level. Include a single primary action. | Card = container; the title is the link (not the whole card) unless the entire card is one control with proper semantics. |
| **Form inputs** | Label always visible (no placeholder-as-label), helper text, error text with icon, success state where useful. Textareas grow. | Programmatic label association; error announced; autocomplete attributes; no cognitive-function tests for auth (§9.5.3). |
| **Progress indicators** | Linear bar for module/lesson progress (evidence-based, not time-based); circular only for small determinate items; always with a numeric or text label ("3 of 8 concepts evidenced"). | `role="progressbar"` with `aria-valuenow`/`aria-valuetext`; indeterminate states announced as such. |
| **Skill proficiency indicators** | Five-state visual system mirroring §6.6.2 (not-yet / introduced / practising-supported / practising-unassisted / evidenced / needs-review). Colour + icon + text label. Compact variant for trees. | Never colour-only; screen-reader text states the mastery label verbatim. |
| **Roadmap nodes** | Node states: locked (prerequisite unmet), available, in progress, complete (evidenced), needs review. Connection lines show prerequisite order. Hover/tap shows outcome + estimate. | Keyboard navigable as a list with arrow-key traversal; an equivalent **list view is mandatory** (the graph is never the only representation). |
| **Lesson panels** | Structured: objective → content blocks → practice → closing retrieval check. Sticky "next" action; visible session timer (optional, off by default). | Reading order correct in DOM; headings hierarchical; math/code have text alternatives. |
| **Quiz/assessment interface** | One question per view (mobile) or grouped (desktop); no tutor access while active; per-question navigation with a submission summary; explicit time-remaining only where a timed assessment is genuinely needed. | No drag-only answers; timers can be paused/extended per accessibility needs; answer feedback not colour-only. |
| **Tutor messages** | Learner vs tutor clearly distinguished; tutor messages carry a "source" affordance (lesson context / general knowledge) and a "report" action; hint level visible when hinting; never mimics an authority it does not have. | Streaming text announced politely; a stop-generation control; full transcript copyable. |
| **Modals & dialogs** | Only for decisions that must interrupt. Maximum one at a time. Escape closes (unless destructive confirmation). Never used for long-form content. | Focus trap; restore focus on close; `aria-modal`; labelled by its heading. |
| **Toasts/status feedback** | Non-blocking confirmations (saved, submitted, scheduled). Auto-dismiss ≥ 6s with a pause-on-hover; critical errors are inline, not toasts. | `aria-live="polite"` (or assertive for errors); never the only notification channel for something that must persist. |
| **Empty states** | Explain what the section is for + the one action that fills it + a link to learn more. Distinguish "nothing yet" from "nothing matches your filter". | Descriptive heading; not an illustration-only state. |
| **Loading states** | Skeletons for known layouts; spinners for short indeterminate waits; progressive loading for lesson content; streaming for tutor output. No full-page blocking spinners over 1s without feedback text. | `aria-busy`; avoid layout shift; announce completion. |
| **Error states** | Three levels: field-level (inline), section-level (inline with retry), page-level (with a route back and a support path). Always state what happened, what it means, and what to do next (§10.3.11). | Errors associated with the relevant field/region; not colour-only; retry is keyboard reachable. |
| **Charts & analytics** | Max 2–3 series; direct labelling preferred over legends; zero-baseline for bars; no truncated axes used to exaggerate progress; empty/insufficient-data states explicit ("not enough evidence yet"). | Data table alternative for every chart; patterns in addition to colour; keyboard-accessible tooltips. |
| **Mobile navigation** | Bottom bar (4 items, 56px + safe-area), current item indicated by icon + label + colour; gesture conflicts avoided (no swipe-only navigation). | Targets ≥44px; works one-handed; respects system text-size settings. |

#### 9.5.3 Accessibility requirements (target: WCAG 2.2 Level AA)

The 2023 WCAG 2.2 Recommendation added nine success criteria including **Target Size (Minimum) (2.5.8, 24×24 CSS px)**, **Dragging Movements (2.5.7)**, **Consistent Help (3.2.6)**, **Redundant Entry (3.3.7)**, **Accessible Authentication (3.3.8)**, and focus-visibility criteria [R36]. TALIMGO's requirements:

| Area | Requirement |
|---|---|
| Conformance target | **WCAG 2.2 AA** for all learner-facing and admin surfaces. |
| Authentication | Support password managers (no paste-blocking), allow OTP/email links, and **do not require puzzles, transcription, or memorisation** (3.3.8). |
| Redundant entry | Never ask for the same information twice in a flow (3.3.7) — onboarding values pre-fill later forms. |
| Dragging | Any drag interaction (reordering roadmap items) has a non-drag alternative (move up/down buttons) (2.5.7). |
| Consistent help | A help entry point is present in a consistent location across the product (3.2.6). |
| Keyboard | Every function operable by keyboard; logical focus order; no keyboard traps; visible focus at all times. |
| Screen reader | Tested with at least two screen readers (one per platform) at MVP; live regions used correctly; no unlabelled icon buttons. |
| Motion | `prefers-reduced-motion` honoured globally; no autoplay media; no parallax. |
| Zoom & reflow | Usable at 320px width and 400% zoom without loss of content or function. |
| Cognitive load | Plain-language rules (§10.2), one primary action per view, no time pressure on formative work, and no punitive timers. |
| Test evidence | Automated checks (axe-style) in CI + manual keyboard/screen-reader passes per release + at least one paid external audit before public launch. |

#### 9.5.4 Additional IA/UI constraints

- **Interactive states must not rely on `--color-border` alone**: add a background change, an icon, or a weight change.
- **Dark-mode borders need their own tokens** (§9.2.2).
- **Arabic typography is tested as a first-class locale**, not as a post-launch translation (see §9.3.4, §10.4).

### 9.6 Image, illustration, and diagram direction

| Content type | Use it when | Never use it when | Sourcing/licensing rule |
|---|---|---|---|
| **Explanatory diagram** | The concept has structure, sequence, or relationships (a graph, a stack, a workflow, a data model) | The concept is verbal/definitional | Built in-house from a shared diagram template library; accessible text description required |
| **Illustration** | Orientation, empty states, milestone celebration, onboarding warmth | As decoration in lesson content | House style (geometric, flat, brand-colour limited); no clip-art; no AI-generated faces of "real" people |
| **Screenshot / UI mock** | Teaching software use (tools, IDEs, dashboards) | When the product changes frequently (high maintenance: prefer annotated diagrams) | Only where terms permit; always attributed; prefer own captures |
| **Photography** | Human context on marketing pages (respectful, non-stock-looking where possible) | Inside lesson bodies (adds load, adds no learning) | Licensed (own shoot, or a licence recorded per asset); model releases for identifiable people |
| **Chart/data visual** | The learning objective involves interpretation or the learner's own data | The data is trivial | Generated from the platform's own analytics; never manipulated axes |
| **Icon** | Navigation, states, compact semantics | As the sole carrier of meaning without a label | Single licensed/own icon set; consistent stroke |
| **Video** | Motion, voice, or demonstration adds real learning value | The same content reads fine as text or an annotated diagram | Linked externally where possible (§7.6); no re-hosting without a licence |

**Rules (CONFIRMED):**

1. Every image must serve learning or orientation. If removing it loses nothing, remove it.
2. Every content image needs **alt text** (or explicit decorative marking), a **licence record**, and an **optimised delivery variant** (AVIF/WebP, responsive sizes, lazy loading).
3. No AI-generated imagery that depicts real identifiable people, real events, or real organisations.
4. No imagery that stereotypes a region, gender, profession, or body type. Representation review is part of the G4 content gate for marketing-critical assets.
5. **Illustration style guide** must be written before the second illustration is produced (two assets = a style; one asset = an accident).

---

## 10. Voice, tone, and localization

### 10.1 Voice principles

| Principle | Meaning | Practical test |
|---|---|---|
| **Clear** | Short sentences. Concrete verbs. One idea per sentence. | Would a tired learner at 23:00 understand this in one read? |
| **Respectful** | Address the learner as a capable adult. Never patronise. | Does the sentence assume the learner is lazy, or that the situation is hard? |
| **Intelligent** | Accurate terminology where it matters; no dumbing down. | Did we simplify the language or the truth? |
| **Practical** | Always oriented to what to do next. | Does the message end with a usable next step? |
| **Encouraging, not hyped** | Confidence comes from evidence, not adjectives. | Did we claim an outcome we cannot control? |
| **Honest** | Uncertainty is stated; limits are named; mistakes are owned. | Would we be comfortable if a journalist printed this sentence? |

**Person:** second person ("you") for the learner. **Company voice:** first person plural ("we") when describing what TALIMGO does. **Tutor voice:** first person singular ("I") only inside the tutor panel, where it is a distinct, bounded persona and clearly separate from TALIMGO's institutional voice.

### 10.2 Readability rules

- Aim for a plain-language register suitable for an adult reading in a second language: short sentences, active voice, common words.
- Define a term on first use, then use it consistently (and add it to the Glossary, §23).
- Never simplify in a way that makes the content **wrong**: "the cell's power plant" is acceptable as an analogy *after* naming mitochondria.
- Numbers: state assumptions; round honestly; label estimates as estimates; never present an estimate as a measurement.
- Avoid idioms and metaphors that do not translate (English originals get rewritten, not machine-translated).

### 10.3 Message patterns with examples

Each pattern below gives the intent, a good example in English, an Arabic example, and a bad example. Arabic examples are written to be natural MSA, not literal translations.

#### 10.3.1 Welcome message

- **Intent:** set expectations, remove fear, state the promise honestly.
- **EN (good):** "Welcome to TALIMGO. Tell us what you want to be able to do — we'll turn it into a plan, help you practise, and show you honest evidence of progress. You can change anything later."
- **AR (good):** «أهلاً بك في تاليم غو. أخبرنا بما تريد أن تكون قادرًا على فعله، وسنحوّله إلى خطة واضحة، ونساعدك على التدريب، ونعرض لك تقدّمك بالأدلة. يمكنك تغيير أي شيء لاحقًا.»
- **Bad:** "Unlock your potential and become unstoppable with TALIMGO!" (hype, no information)

#### 10.3.2 Empty state

- **Intent:** explain the feature and give the one action.
- **EN (good):** "No projects yet. Projects are where you build something real from what you've learned. You'll unlock your first one after Module 3 — or start a small practice project now."
- **AR (good):** «لا توجد مشاريع بعد. المشاريع هي المكان الذي تبني فيه شيئًا حقيقيًا من ما تعلّمته. سيُتاح لك أول مشروع بعد الوحدة الثالثة، أو يمكنك بدء مشروع تدريبي صغير الآن.»
- **Bad:** empty illustration with no text, or "Nothing to see here!"

#### 10.3.3 Roadmap introduction

- **Intent:** explain the reasoning, invite ownership, label estimates.
- **EN (good):** "Here's a plan built around 4 hours a week. Three milestones, each producing something you can show. Estimated total: 46–60 hours — an estimate based on learners with similar experience, not a promise. Move things, remove optional modules, or tell us your week changed."
- **AR (good):** «هذه خطة مبنية على ٤ ساعات أسبوعيًا: ثلاث مراحل، كل واحدة تُنتج شيئًا يمكنك عرضه. الوقت التقديري: ٤٦–٦٠ ساعة، وهو تقدير وليس وعدًا. يمكنك إعادة الترتيب أو حذف الوحدات الاختيارية أو تعديل وقتك.»
- **Bad:** "We've created the perfect plan for you!" (unfalsifiable, no reasoning, no estimates labelled)

#### 10.3.4 Daily mission description

- **Intent:** objective + time + completion condition + why it matters.
- **EN (good):** "Today · 18 minutes · Practise loops: 5 retrieval questions and one exercise. You'll be able to repeat code without copying it — which milestone 2 needs."
- **AR (good):** «اليوم · ١٨ دقيقة · تدريب على الحلقات (loops): ٥ أسئلة استرجاع وتمرين واحد. ستتمكن من تكرار الكود دون نسخه، وهو ما تحتاجه المرحلة الثانية.»
- **Bad:** "Daily challenge! Earn 50 XP!" (no learning objective stated)

#### 10.3.5 Corrective feedback

- **Intent:** correct the work, name the error type, keep the learner's dignity intact.
- **EN (good):** "The loop runs one extra time. Your condition uses `<=` where the array ends at `length - 1`. Try changing the comparison and re-running the test — the failing case is the third one."
- **AR (good):** «تُنفَّذ الحلقة مرة إضافية: الشرط يستخدم `<=` بينما ينتهي المصفوفة عند `length - 1`. جرّب تعديل المقارنة وإعادة الاختبار؛ الحالة التي تفشل هي الثالثة.»
- **Bad:** "Wrong. You should have used `<`." (no reasoning, no error type, no next step)

#### 10.3.6 Quiz explanation

- **Intent:** explain why the answer is right, why the chosen option was tempting, and what to review.
- **EN (good):** "Correct: **B**. Option C sounds plausible because it's also about timing, but it describes the scheduling interval, not the retention principle. If C tempted you, review the spacing concept (2 minutes)."
- **AR (good):** «الإجابة الصحيحة: **ب**. الخيار ج يبدو مقنعًا لأنه يتعلق أيضًا بالتوقيت، لكنه يصف الفاصل الزمني للجدولة لا مبدأ الاحتفاظ. إن كان ج مغريًا، راجع مفهوم التباعد (دقيقتان).»
- **Bad:** "Correct! ✅" (no learning value)

#### 10.3.7 Progress update

- **Intent:** evidence-based, honest, specific, non-inflated.
- **EN (good):** "This week: 3 concepts evidenced (2 unassisted, 1 with a project), 2 sessions, and 1 milestone at 60%. Your functions skills are solid; loops still need one more delayed check."
- **AR (good):** «هذا الأسبوع: ٣ مفاهيم مُثبتة (٢ بدون مساعدة، و١ عبر مشروع)، جلستان، ومرحلة واحدة عند ٦٠٪. مهارات الدوال لديك متينة، والحلقات تحتاج تحققًا متأخرًا آخر.»
- **Bad:** "You're crushing it! 4 hours of learning this week! 🚀" (time ≠ learning; no evidence)

#### 10.3.8 Incomplete-plan reminder

- **Intent:** remove friction without coercion.
- **EN (good):** "You've stopped 2 tasks before the end of milestone 1. Want to finish in a 12-minute session, or shall I shrink the milestone to fit this week?"
- **AR (good):** «توقفت قبل مهمتين من نهاية المرحلة الأولى. هل تريد إنهاءها في جلسة من ١٢ دقيقة، أم أن أصغّر المرحلة لتناسب هذا الأسبوع؟»
- **Bad:** "You're 3 days behind schedule. Your progress is at risk!" (manufactured anxiety)

#### 10.3.9 AI uncertainty statement

- **Intent:** be explicit about confidence and how to verify.
- **EN (good):** "I'm not confident about this specific detail — sources describe the behaviour differently across versions. Here's what is certain, here's what changed, and here's how to check it in the official documentation: [link]."
- **AR (good):** «لستُ واثقًا من هذه التفصيلة تحديدًا؛ تختلف المصادر بين إصدار وآخر. إليك ما هو مؤكد، وما تغيّر، وكيف تتحقق منه في التوثيق الرسمي: [رابط].»
- **Bad:** a confident, unsourced, wrong-sounding answer; or a hedge so vague it helps nobody ("it depends, everyone is different").

#### 10.3.10 Subscription explanation

- **Intent:** plain terms, no dark patterns, clear limits.
- **EN (good):** "Free includes the full first milestone of any path, 10 AI tutor messages a day, and unlimited practice. Plus removes AI limits and unlocks all milestones, projects, and progress reports. It renews monthly; cancel anytime from Billing — you keep access to everything you've already completed."
- **AR (good):** «تشمل الخطة المجانية المرحلة الأولى كاملة من أي مسار، و١٠ رسائل يوميًا مع المدرّس الذكي، وتدريبًا غير محدود. تلغي خطة بلس هذه الحدود وتفتح كل المراحل والمشاريع وتقارير التقدّم. تتجدد شهريًا ويمكنك الإلغاء في أي وقت من صفحة الفوترة، مع الاحتفاظ بكل ما أكملته.»
- **Bad:** "Unlock unlimited potential! Only 3 spots left at this price!" (fake scarcity; no limits explained)

#### 10.3.11 Error messages

- **Intent:** what happened, what it means, what to do.
- **EN (good):** "We couldn't save your assessment result — the connection dropped mid-submit. Your answers are kept on this device. Retry now, and if it fails again, your answers will be sent automatically when you reconnect."
- **AR (good):** «تعذّر حفظ نتيجة التقييم بسبب انقطاع الاتصال أثناء الإرسال. إجاباتك محفوظة على هذا الجهاز. أعد المحاولة الآن، وإن فشلت مرة أخرى سيتم الإرسال تلقائيًا عند عودة الاتصال.»
- **Bad:** "Error 500. Something went wrong." (no meaning, no action, no data reassurance)

#### 10.3.12 Success messages

- **Intent:** confirm, quantify, and point forward — briefly.
- **EN (good):** "Milestone 1 complete — you built and deployed the shop page. 4 concepts evidenced. Next: making it interactive (est. 3 sessions)."
- **AR (good):** «أكملت المرحلة الأولى: بنيت صفحة المتجر ونشرتها. تم إثبات ٤ مفاهيم. التالي: جعلها تفاعلية (التقدير: ٣ جلسات).»
- **Bad:** "Congratulations!!! 🎉🎉 You're amazing!" (no substance)

### 10.4 Language strategy and localization

**Current language situation (CONFIRMED as context, UNVERIFIED as market evidence):** the brief anticipates an initial audience that may include Algeria and the broader MENA region, while preserving a path to international expansion. Research for this document surfaced active Moroccan Arabic/French education platforms (TaalimGo, TaalimAI, taalim.ma) [R1][R31][R33], which confirms regional demand for Arabic-language learning products but does **not** establish TALIMGO's market size or willingness to pay.

**PROPOSED language phasing:**

| Phase | User interface | Content | Rationale |
|---|---|---|---|
| **Phase 1 (MVP)** | **English + Modern Standard Arabic**, both fully supported, RTL implemented from the first component | Launch paths authored in English; Arabic content for at least one path (recommended: the language-agnostic or most broadly useful one), plus Arabic explanations available for all lesson objectives | Arabic-first is a differentiator only if it is native, not a translation layer. Shipping RTL after launch is a rewrite (§9.3.4). |
| **Phase 2** | Add **French** UI | French content for launch paths; Arabic content expanded to all paths | French is a major reading language in the Maghreb; the cost is localisation QA, not architecture. |
| **Phase 3+** | Additional languages as data justifies (candidates: Spanish, Turkish, Indonesian) | Human-reviewed translations of top paths | Only enter a language if content review capacity exists in that language. |

**Language rules (CONFIRMED):**

1. **Never machine-translate and publish unreviewed.** AI translation is a draft; a human who knows both the language and the subject approves it.
2. **Dialect policy:** user-facing content is Modern Standard Arabic. Regional dialects (e.g. Algerian Darija) may appear in *support* and *marketing* copy where a native writer authors it, but never in instructional content, and never mixed arbitrarily within one screen.
3. **Language mixing:** technical terms may remain in English inside Arabic content when that is the natural professional usage, with an Arabic gloss on first use.
4. **The learner's language choice governs the UI; content language is labelled explicitly** (a learner may want an English UI with Arabic explanations, or the reverse). These are separate settings.
5. **Language is never inferred from country.** A user in Algeria may prefer French, Arabic, or English.
6. **Payment and pricing localisation** is separate from language; both need local research (DEC-013).

### 10.5 Terminology discipline

| Use this | Not this | Note |
|---|---|---|
| learner | student, user, trainee | "Learner" is the product-wide default; "student" only where the user is enrolled in formal education and the context requires it. |
| roadmap / plan | course, syllabus, curriculum (in UI) | "Curriculum" is an internal/architecture term; learners see "plan" or "roadmap". |
| path | track, career track | One word for the thing between goal and module. |
| module, lesson, concept | chapter, unit, topic | Fixed hierarchy (§6.3.1). |
| practise (verb) / practice (noun) | train, drill | US spelling "practice" for both is acceptable in US-facing copy; keep consistent per locale. |
| evidence | proof, proof of learning | "Evidence" is honest; "proof" implies certainty. |
| mastery estimate | mastery score, mastery level | Always an estimate with uncertainty (§6.6.2). |
| AI tutor / tutor | AI assistant, bot, chatbot, coach | One name. "Tutor" is the product function; the model is an implementation detail and is never named in the UI. |
| goal | objective (for the top level) | "Objective" is used for lesson-level learning objectives. |
| estimate | duration, time required | Always labelled as an estimate. |

---

## 11. AI behaviour, educational quality, privacy, and safety

### 11.1 AI reliability rules

These are **CONFIRMED product rules** (they define acceptable behaviour regardless of which model or vendor is used) and must be enforced in the application layer, not merely requested in a prompt.

| # | Rule | Enforcement mechanism |
|---|---|---|
| 1 | **Do not invent facts, sources, credentials, or learning outcomes.** | Grounded generation from the curriculum store; sources retrieved, never generated; a validator rejects any output containing a URL or citation that is not in the retrieved context; outcome language is blocked by a claim filter (§11.1.1). |
| 2 | **Identify uncertainty and provide sources when appropriate.** | The tutor must be able to emit a structured uncertainty field; the UI renders it as a labelled notice, not as a buried phrase. |
| 3 | **Separate verified instructional content from generated suggestions.** | Every tutor/generated artefact carries a provenance badge: *lesson content* (canonical) vs *AI-generated for this session* vs *general knowledge (not curriculum-grounded)*. Learners can always tell which is which. |
| 4 | **Use structured outputs and validation for roadmaps and assessments.** | Typed schemas + schema validation + prerequisite-order validation + time-budget sanity check before anything is shown (§6.3.3). |
| 5 | **Test generated exercises and answer keys before presenting them as authoritative.** | Generated items pass an automated solver/checker (where computable) or a self-consistency check; items that cannot be verified are shown as "practice (unverified answer)" or withheld. Any item used for mastery evidence must have a verified key. |
| 6 | **Prevent prompt injection from imported learning resources.** | All external/learner-supplied text is treated as **data**: it is wrapped and labelled, never concatenated into instruction positions; the model's system instructions are separated from retrieved content; tool-use permissions are minimised; outputs that appear to follow injected instructions are logged as security events. |
| 7 | **Prevent one learner's private information from appearing in another learner's content.** | Per-learner data isolation at the retrieval layer; no cross-tenant vector indexes; personalisation only from the requesting learner's own record; automated cross-tenant leakage tests in CI (§13.8). |
| 8 | **Provide a way to report incorrect or harmful educational content.** | A single "Report a problem" affordance on every lesson, item, project, and tutor message; reports enter a triage queue with an SLA; reporters get a status update. |
| 9 | **Track significant AI failures and recurring quality issues.** | Every failure is categorised (factual error, mis-grounding, unsafe output, refusal error, hallucinated citation, language quality, formatting failure) with a severity; trends reviewed on a fixed cadence (§16.1). |

#### 11.1.1 Claim filter (hard block list)

Learner-facing generated text may not contain (or imply) any of the following without a human-authored, approved exception:

| Blocked pattern | Example | Why |
|---|---|---|
| Employment guarantees | "This will get you hired as a developer." | False and legally risky. |
| Income promises | "Freelancers using this skill earn $3,000/month." | Unverifiable, jurisdiction-dependent, financial-promotion risk. |
| Certification/accreditation claims | "Complete this to receive a certified qualification recognised by universities." | TALIMGO holds no accreditation. |
| Fixed-outcome timelines | "You'll be fluent in 30 days." | Ignores individual variation. |
| Medical/legal/financial advice | "You should invest in index funds." | Regulated advice; out of scope. |
| Fabricated credentials or partnerships | "In partnership with [university]." | Fraudulent. |
| Absolute mastery claims | "You have mastered JavaScript." | Overstates what evidence supports. |

**Implementation:** a deterministic post-generation filter plus a model-based classifier for paraphrases; both must pass before rendering. False negatives are treated as P0 incidents.

#### 11.1.2 Model strategy (PROPOSED, deliberately vendor-neutral)

| Requirement | Proposal |
|---|---|
| Model access | Through an abstraction layer (gateway) so models can be swapped without rewriting product logic — see §14.3 (`litellm`-class gateway). |
| Tiered routing | Cheap/fast model for classification, formatting, hint level 1, and summarisation; mid-tier for tutoring and feedback; frontier model only for hard reasoning, complex project feedback, and roadmap conflict resolution. Routing by **task class**, not by user tier. |
| Cost controls | Per-learner token budgets; caching of common explanations and item generation; prompt-size discipline (retrieve the smallest sufficient context); daily spend ceilings with graceful degradation messages. |
| Evaluation gate | No prompt or model change ships without passing an evaluation suite (§11.1.3). |
| Provider diversity | At least two providers integrated by Phase 2 to avoid single-vendor outages, pricing shocks, and policy changes. |
| Data terms | Use enterprise/API terms that exclude customer data from provider training; document this in the privacy notice. |

#### 11.1.3 Evaluation suite (required before any public launch)

| Test class | What is tested | Minimum bar (proposed) |
|---|---|---|
| Factual accuracy | 200+ curated question/answer pairs across launch subjects, including known-tricky areas | ≥ 95% correct with sources; zero fabricated citations |
| Curriculum grounding | Does the tutor stay within the lesson and correct concept? | ≥ 98% grounded, measured by an automated grounding checker + human sample |
| Hint-ladder compliance | Does the tutor reveal answers prematurely? | ≤ 2% premature reveal rate on a scripted red-team set |
| Prompt injection | 100+ adversarial injections embedded in pasted text, documents, and "student notes" | 0 instruction-following successes; 100% logged |
| Cross-learner leakage | Synthetic multi-tenant test harness | 0 leaks (blocking release criterion) |
| Harmful-content refusal | Safety red-team set (self-harm, weapons, medical, illegal) | 100% refusal + redirect; measured on a versioned test set |
| Language quality (AR/EN) | Human-rated samples for grammar, register, RTL-correct rendering | ≥ 4/5 mean human rating per locale |
| Age-appropriate behaviour | Behaviour when a minor-flagged account asks age-restricted content | Correct refusal and escalation |
| Roadmap validity | 100 generated plans across goals/time budgets | 0 prerequisite-order violations; 100% pass the time-budget sanity check |
| Refusal usefulness | Does a refusal help the learner progress? | ≥ 80% of refusals rated "helpful, not obstructive" by reviewers |

### 11.2 Content governance

**Lifecycle:** *idea → authoring → peer review → subject review (where required) → safety/compliance review → publish → monitor → correct → version → retire/archive.*

| Stage | Owner role | Required artefacts | Mandatory for |
|---|---|---|---|
| Idea & scoping | Curriculum lead | Objective, mapping to an existing concept or a justified new one | All content |
| Authoring | Content author (human) | Lesson body, activities, items with keys, difficulty bands, misconception notes | All content |
| Peer review | Second author or instructional designer | Review checklist signed off (objectives measurable, practice present, difficulty sane) | All content |
| Subject review | Domain expert (independent of author) | Accuracy and currency statement; terminology check | **Mandatory:** finance, security, AI/ML, health-adjacent, physics/chemistry labs, statistics-adjacent claims, any content that could cause physical or financial harm |
| Safety/compliance | Content ops + legal (where needed) | Claim check, disclaimer check, licence check, age-appropriateness, accessibility notes | All published content; mandatory sign-off in regulated domains |
| Publish | Content engineer | Metadata complete, rendering verified in EN/AR, links healthy, item keys verified | All content |
| Monitor | Content ops | Error reports, item statistics, learner confusion signals | Ongoing |
| Correct | Content ops | Correction note; learner-visible change log entry | All corrections |
| Retire | Curriculum lead | Archive record, replacement mapping, learner notice | All retirement |

**Specialist review requirements by risk (CONFIRMED):**

| Risk tier | Examples | Requirement |
|---|---|---|
| **Tier 1 — high** | Cybersecurity offensive techniques (inside labs), investment-adjacent finance, medical/health adjacent, legal-adjacent, anything involving physical safety | Named subject expert review + legal/regulatory check + re-review at least yearly |
| **Tier 2 — medium** | Statistics claims, AI/ML capability claims, cloud/infrastructure configuration, business-legal frameworks, exam-adjacent claims | Subject reviewer sign-off; re-review every 12–18 months |
| **Tier 3 — low** | General programming, design craft, languages, personal productivity | Peer review; re-review every 24 months or on report |

**Citation standards (CONFIRMED):**

1. Factual claims in canonical content that depend on a source carry a citation to a **primary** source where one exists (official documentation, standards bodies, peer-reviewed literature, official statistics).
2. Citations must be **verifiable**: title, publisher/author, year, and a stable URL or DOI.
3. AI-generated text may not introduce a citation that was not in the retrieved source set (§11.1 rule 1).
4. Where a claim is contested, present the disagreement rather than one side.
5. Every citation is periodically link-checked; dead citations are repaired, replaced, or the claim is softened.

**Ownership and licensing (CONFIRMED):** all TALIMGO-authored content is owned by the project under a documented contributor agreement (including for freelance authors); third-party material is either licensed (with terms recorded) or linked (never re-hosted). See §7.6.

### 11.3 Privacy and security

> **Note (CONFIRMED):** this section specifies *requirements*, not legal advice. TALIMGO operates in jurisdictions whose rules differ and change; a qualified lawyer must review the final design for each market. No compliance certification is claimed or implied.

#### 11.3.1 Privacy-by-design requirements

| Requirement | Implementation |
|---|---|
| Data minimisation | Collect only what a feature uses; document the purpose of every field in a data inventory; review quarterly and delete unused fields. |
| Purpose limitation | Learning data is used for learning; marketing use requires separate, explicit, revocable consent. |
| Transparency | A plain-language privacy notice (EN/AR at launch) that names each data category, why it is collected, where it is stored/processed, how long it is kept, and how to delete it. Not a wall of legalese. |
| Consent | Separate consents: (a) account & learning, (b) AI processing of learning content, (c) product analytics, (d) marketing. No bundled blanket consent; no pre-ticked boxes. |
| Defaults | Analytics default to privacy-preserving settings; AI personalisation can be limited by the learner; adult learners can opt out of non-essential processing. |
| Retention | Defined schedule per data class (proposal: learning evidence retained while the account is active + 30 days after deletion; AI conversation logs 90 days unless the learner saves them; marketing data deleted on unsubscribe + 30 days; backups purged on a rolling 35-day window). |
| Access, export, and deletion | Self-service export of the complete learner record (human-readable + machine-readable) and self-service deletion that actually deletes (including derived vectors/models where the architecture allows), documented honestly where a third-party processor's retention limits deletion. |
| Children and minors | See §11.3.4. |
| Cross-border transfer | Document where each processor stores data; where a jurisdiction requires prior authorisation for transfers (for example Algeria's framework [R17]), the transfer must be assessed before launch, not after. |
| Breach response | A documented incident process: detect → contain → assess → notify (regulators and users where required) → remediate → publish a post-mortem summary. |
| Third-party processors | Contracts with data-processing terms, a sub-processor register, and a security review before integration. |

#### 11.3.2 Security requirements (non-optional)

| Area | Requirement |
|---|---|
| Authentication | Email + password with strong hashing (Argon2id or bcrypt with calibrated cost) or a reputable identity provider; optional social login; **mandatory MFA for administrators**; password-breach screening; session expiry and device management; rate limiting and lockout protection. |
| Authorisation | Server-side checks on **every** object access (no client-trusted roles); role model: Learner, Reviewer, Content Editor, Subject Reviewer, Support, Admin — least privilege by default; tenant/owner checks in every query. |
| Data protection | Encryption in transit (TLS 1.2+) and at rest; secrets in a managed secret store (never in code, never in client bundles); field-level encryption for sensitive identifiers if stored; PII excluded from logs by default. |
| Session handling | HttpOnly, Secure, SameSite cookies (or equivalent token handling); CSRF protection; refresh-token rotation; short-lived access tokens. |
| Application security | Input validation and output encoding; no `eval` of learner content; sandboxed code execution with no host-network access by default; dependency vulnerability scanning in CI; SAST; protection against injection, SSRF, and insecure deserialisation. |
| AI-specific security | Treat retrieved and user-supplied content as untrusted (prompt injection), bound tool permissions, restrict outbound network from any agent that can call tools, log all tool invocations, and rate-limit expensive operations per user. |
| Administration | All admin actions audited (who, what, when, from where); admin access requires MFA and is reviewed quarterly; no production data in development environments; break-glass procedure documented. |
| Observability of abuse | Anomaly detection for bulk content export, scraping, credential stuffing, and cost-abuse of AI endpoints. |
| Backups & recovery | Encrypted automated backups; documented restore test at least twice a year; RPO/RTO targets defined before launch (§13.10). |
| Penetration testing | External test before public launch and annually thereafter; remediation SLAs by severity. |

#### 11.3.3 Legal obligations that require jurisdiction-specific review (UNRESOLVED — flagged)

| Jurisdiction | Instrument | What it likely requires of TALIMGO | Status |
|---|---|---|---|
| Algeria | Law No. 18-07 of 10 June 2018 on the protection of natural persons in the processing of personal data, amended by Law No. 25-11 of 24 July 2025 | Prior declaration to the ANPDP (and prior authorisation for higher-risk processing), obligations on cross-border transfers, data-subject rights, and a rule that processing a child's data requires consent of the legal representative [R17] | **UNVERIFIED** — needs local counsel |
| Morocco | Law No. 09-08 (2009), enforced by the CNDP | Declaration/authorisation before processing; cross-border transfer authorisation; parental consent for children's data; sensitive-data rules [R18] | **UNVERIFIED** — needs local counsel |
| European Union / EEA | GDPR (and its national implementations); EU AI Act (Regulation (EU) 2024/1689) | GDPR: lawful basis, transparency, rights, DPA with processors; AI Act: education is an Annex III high-risk use case, with obligations originally scheduled for 2 August 2026 and reported as deferred by the Digital Omnibus package to 2 December 2027 (Annex III) — while Article 50 transparency duties applied from 2 August 2026 [R16] | **UNVERIFIED** — regulatory status should be confirmed against the Official Journal before reliance |
| United States (if served) | COPPA (under-13), FERPA (school contexts), state privacy laws | Age-verification and parental-consent flows; school-record handling if sold to institutions | **UNVERIFIED** |
| UNESCO guidance (non-binding) | Guidance for Generative AI in Education and Research (2023) | Recommends a minimum age of 13 for classroom generative-AI use, data-protection standards, and teacher training [R15] | Advisory — adopted as a **design input**, not a legal duty |

**Decision required:** initial geographic scope and the resulting legal regime(s) — DEC-006. Until it is decided, build the default architecture to the **strictest plausible** requirement (data minimisation, explicit consent, self-service export/delete, transfer logging), which is cheaper than retrofitting.

#### 11.3.4 Minors (UNRESOLVED policy; requirements defined)

If TALIMGO supports learners under 18 (which several target audiences imply — see persona P2), the following are **CONFIRMED requirements** for any minor-flagged account:

1. **Age declaration at sign-up** with an age-appropriate experience branch (no self-declared "I'm 25" bypass without additional signals for high-risk features).
2. **Parental/guardian consent** where the applicable law requires it (Algeria's framework ties child-data processing to legal-representative consent [R17]; Morocco requires parental consent for children's data [R18]; GDPR's default digital-consent age is 16 with member-state floors down to 13 [R15]).
3. **No behavioural advertising to minors. No profiling for commercial purposes.**
4. **Restricted data collection** for minor accounts (minimum viable profile, no phone number, no precise location, no biometric data).
5. **AI guardrails for minors:** age-appropriate vocabulary, strict refusal of age-restricted topics, no emotional-dependency encouragement, and clear signposting to a trusted adult for anything sensitive.
6. **Safety escalation path** for self-harm, abuse, or danger signals — defined, documented, tested, and never handled by the AI alone (§11.4.4).
7. **Parent/guardian visibility** limited to progress summaries the minor is told about (no covert surveillance; this is both ethical and, in several jurisdictions, legally safer).
8. **UNESCO-informed default:** if minors are supported, the recommended **minimum age for unsupervised generative-AI use is 13** [R15] — i.e. under-13 accounts would receive a non-generative experience at most, or no account at all. **PROPOSED MVP: 16+ only**, expanding to 13–15 with guardian consent in Phase 2 after the pilot evidence and legal review (DEC-005).

### 11.4 Responsible assessment

#### 11.4.1 Rules (CONFIRMED)

1. **Every assessment measures a stated learning objective.** An item that cannot be mapped to an objective is deleted, not kept "for practice".
2. **No mastery claim without evidence that can support it.** The mastery model (§6.6.2) defines the evidence thresholds; UI language must match the evidence level.
3. **No unvalidated automated grading of high-stakes work.** Objective items: keys are verified. Open-ended work: rubric-based AI first pass with a human dispute path. Any assessment that gates a milestone or a certificate-like artefact must have a human-review option available.
4. **No scored assessment where the instrument cannot establish the ability.** For example, a multiple-choice test cannot establish "can write a professional email"; use a production task.
5. **Timed assessments are exceptional**, justified by the objective, and adjustable for accessibility needs.
6. **Assessment results are explainable**: item-level review, error-type notes, and the evidence trail are available to the learner.
7. **Cheating is treated as a design problem, not a policing problem.** Measures: item pools larger than any single session, question variants, production tasks, and honour-based framing. Mass proctoring/surveillance tooling is out of scope (privacy cost exceeds the benefit).
8. **The learner may always request human review** of a score they believe is wrong.

#### 11.4.2 Where human review is required

| Situation | Human review |
|---|---|
| Capstone/milestone project final submission | Recommended (Phase 2: staffed; Phase 1: sampled) |
| Any disputed automated score | Mandatory |
| Repeated failure of the same concept after two adaptation cycles | Mandatory content/teaching review (not necessarily a human talking to the learner) |
| Suspected academic dishonesty with consequences | Mandatory before any action is taken |
| Content flagged as harmful, illegal, or dangerous | Mandatory before re-publication |
| Minor-account safety escalations | Mandatory, by trained staff |

#### 11.4.3 Known limitations to disclose (CONFIRMED)

- Automated grading of free-text work is imperfect; TALIMGO says so, per assessment, in plain language.
- Mastery estimates are probabilistic and can be wrong; the learner can always challenge them.
- Learning outcomes depend on learner effort and context; TALIMGO cannot control them.
- AI-generated practice is less reliable than reviewed content and is labelled accordingly.

#### 11.4.4 Safety escalation policy (required before any minor or mental-health-adjacent content ships)

| Signal | Immediate system behaviour | Human process |
|---|---|---|
| Self-harm or suicide intent | Do not counsel; show a supportive, non-clinical message with region-appropriate emergency resources; keep the conversation open | Alert on-call staff within a defined SLA (for minor accounts, notify the guardian where lawful and safe) |
| Abuse, violence, or danger | Provide resources; avoid interrogation | Alert on-call staff per protocol |
| Requests for illegal or dangerous instructions | Refuse + redirect | Log for trend analysis |
| Model produces harmful output | Block render, log a P0 incident | Review within 24 hours; content/prompt remediation |

---

## 12. Business model and monetization

> **Status: all pricing in this section is UNVALIDATED.** No market research has been conducted, no willingness-to-pay study exists, and no conversion rate is asserted. The numbers below are *illustrative planning bands* with explicit reasoning, offered so that engineering and product decisions (AI cost limits, entitlement checks) can be made before pricing research completes. **The document does not set final prices.**

### 12.1 Reference points from the market (researched 2026-10-10)

| Product | Reported consumer price | What the learner buys | Source |
|---|---|---|---|
| Khan Academy (Khanmigo) | ~$4/mo, ~$44/yr; free for teachers | AI tutoring on top of a free core platform | [R28] |
| ChatGPT / Gemini / Claude learning modes | $0 (with paid tiers for higher limits) | Conversational tutoring, no durable curriculum record | [R12][R13][R14] |
| Duolingo | Super ~$12.99/mo (~$84–96/yr); Max ~$29.99/mo (~$168/yr) | Convenience + AI conversation practice | [R29] |
| Brilliant | reported ~$12.49–27.99/mo, ~$150–240/yr (sources vary) | Interactive STEM problem-solving + tutor | [R30] |
| Codecademy | Plus ~$14.99/mo annual; Pro ~$19.99/mo annual | Interactive technical courses, career paths, AI help | [R35] |
| Coursera | Plus ~$59/mo or $399/yr; courses $49–99 | Credentials from recognised institutions | [R20] |
| Udemy | Personal Plan ~$16.99–32/mo, ~$156–168/yr; courses often $9.99–19.99 | Broad catalogue, lifetime access | [R34] |

**Interpretation (PROPOSED):** the consumer ceiling for a *single-domain* AI-assisted learning subscription sits roughly in the **$5–30/month** band, with free AI assistants creating a strong downward pull. Coursera's $59/month works because it sells institutional credentials, which TALIMGO cannot legitimately do. Any TALIMGO price must be justified by a value the free alternatives do not provide: a validated plan, trustworthy measurement, projects, and localisation.

### 12.2 Proposed tier structure (UNVALIDATED)

| Tier | Audience | Contents (PROPOSED) | Constraints/purpose |
|---|---|---|---|
| **Free** | Everyone; the trust-building tier | Full first milestone of any path; retrieval practice and flashcards; limited AI tutor messages per day (proposal: 10); one project brief per path; basic progress view; full data export | Must be genuinely useful, not a demo. A crippled free tier teaches the wrong lesson and destroys word of mouth. Cost must stay within a per-user ceiling (§12.4). |
| **Plus** (individual subscription) | Primary revenue tier | All milestones and paths; unlimited (fair-use) AI tutoring with tiered routing; all assessments and spaced review; project workspace with rubric feedback; progress reports; offline/low-bandwidth mode | Fair-use policy stated honestly; cost control through model routing and caching rather than hidden caps. |
| **Pro** (higher individual tier) | Career-focused learners | Everything in Plus + career-competency mapping, portfolio builder, interview preparation, human review of a defined number of capstone submissions per period, priority support | **Only ship if** Phase 2/3 research shows real willingness to pay. Human review is the cost driver; price must cover it. |
| **Institutional / Business** | Schools, training providers, employers (FUTURE) | Rostering, cohorts, instructor dashboards, reporting, SSO, safeguarding controls, administrative roles | Not a Phase 1 product. Requires a different security posture, procurement process, and support model. |

**Tier design rules (CONFIRMED):**

1. **Never paywall remediation.** If a learner is stuck, the way out is always free.
2. **Never paywall safety features, export, or deletion.**
3. **Never sell streaks, streak-freezes, or AI credits as pressure mechanics.**
4. **Never make progress invisible to force an upgrade** (the learner can always see their own evidence).
5. Free-tier AI limits must be **visible and predictable** (e.g. a clear daily count), never silent throttling.

### 12.3 Illustrative price points and the reasoning behind them (UNVALIDATED — for planning only)

| Tier | Illustrative monthly (USD) | Illustrative annual | Reasoning (why this band) | Confidence |
|---|---|---|---|---|
| Free | $0 | $0 | Must compete with free AI learning modes on usefulness while sitting inside a hard cost ceiling. | High (structural) |
| Plus | ~$9.99–14.99 | ~$79–119 | Below Duolingo Max/Coursera Plus; above Khanmigo (which is a nonprofit with donated infrastructure). Must be payable without anxiety in the target markets and still cover AI cost per active learner. | Low — requires willingness-to-pay research |
| Pro | ~$24.99–34.99 | ~$199–279 | Must fund human review of capstone work and career tooling. | Very low — validate only after Plus retention is proven |
| Institutional | Negotiated per seat (proposal: quoted per active learner per year, with a floor) | — | Institutional buyers compare with LMS pricing, not consumer apps; margins depend on support cost. | Not assessed |

**Localisation of price (PROPOSED):** purchasing-power-adjusted pricing is likely to be *necessary* rather than optional in the target markets. That introduces arbitrage risk (users buying in a cheaper market) and revenue-leakage risk; mitigations include regional payment-method locks, regional catalogues, and accepting some leakage as a growth cost. **No decision has been made (DEC-013).**

### 12.4 Unit economics: AI cost per active learner (model, not a measurement)

The dominant variable cost is model inference. **Token prices change frequently and the sources below disagree with each other**; treat the following as an order-of-magnitude planning band, verified only against pricing trackers on 2026-10-10 [R38]:

| Model class | Reported input price (per 1M tokens) | Reported output price (per 1M tokens) | Intended use in TALIMGO |
|---|---|---|---|
| Budget/light (e.g. "Flash-Lite"-class) | ~$0.10 | ~$0.40 | Routing, classification, hint level 1, item formatting, translation drafts |
| Mid-tier (e.g. "Flash"/"Sonnet"-class) | ~$0.30–2.00 | ~$2.50–10.00 | Main tutoring, feedback, roadmap rationale |
| Frontier (e.g. "Pro"/"Opus"-class) | ~$2.00–15.00 | ~$10.00–75.00 | Hard reasoning, complex project feedback, conflict resolution |

**Illustrative monthly inference cost per active learner (PROPOSED model, explicitly illustrative):**

Assumptions: 12 active days/month; per day: 3 tutor exchanges + 1 hint + 1 explanation generation + 20 generated practice items; average 6,000 input / 1,200 output tokens per active day; 80% of traffic routed to budget/mid-tier models and 20% to mid-tier/frontier.

| Scenario | Blended input $/1M | Blended output $/1M | Tokens/active learner/month (in / out) | Illustrative cost/month |
|---|---|---|---|---|
| Efficient (aggressive caching + budget routing) | $0.30 | $1.50 | 1.44M / 0.29M | **≈ $0.86** |
| Typical | $1.00 | $5.00 | 1.44M / 0.29M | **≈ $2.89** |
| Heavy learner (3× usage, less caching) | $1.00 | $5.00 | 4.32M / 0.86M | **≈ $8.63** |

**Conclusion (PROPOSED):** inference cost is plausibly a *single-digit dollars per active learner per month* problem for the typical case — but heavy users, generous free tiers, poorly cached prompts, and verbose context can multiply it several-fold. Therefore:

| Cost-control requirement | Detail |
|---|---|
| Prompt discipline | Retrieve the minimum sufficient context; never send an entire curriculum; cache system prompts and stable lesson context (prompt caching where the provider supports it). |
| Per-learner budgets | Soft daily limit with a clear message; hard ceiling with a graceful fallback to the cheapest sufficient model. |
| Feature-level cost accounting | Attribute cost per feature (tutor, roadmap, grading, translation) so pricing decisions are informed by real unit costs. |
| Free-tier design | Free tier must be sized so that its cost is covered by the expected paid conversion **or** by a strategic decision to treat it as acquisition spend — decided explicitly, not accidentally. |
| Vendor terms | Enterprise/API terms that exclude training on customer data and provide predictable rate limits. |
| Monitoring | Cost per active learner, cost per resolved question, cost per assessment graded, tracked as first-class metrics (§16.1). |

### 12.5 Trials, cancellation, and trust

| Question | PROPOSED answer | Rationale |
|---|---|---|
| Trial design | A **free tier** as the trial (not a 7-day timer), plus an optional 7-day free trial of Plus for users who have already completed the first milestone. | Timed trials punish slow learners and reward fast clicks; a milestone-based invitation converts on demonstrated value. |
| Cancellation | One step, self-service, no retention maze, no phone call, no "are you sure" chain beyond one confirmation. Access continues to the end of the paid period. | Trust is the product; cancellation friction is a reputational cost. |
| What happens to evidence after cancellation | **Learner keeps access to all of their own evidence and exports.** Locked: new milestones, AI tutoring beyond the free limit, projects. | The learner's record of what they can do is theirs. |
| Pausing | Offer a pause (1–3 months) instead of cancellation-only. | Reduces churn from temporary life events. |
| Refunds | A plain refund policy (proposal: 14-day no-questions refund on first purchase). | Reduces purchase anxiety; cost is small. |
| Price changes | Existing subscribers grandfathered for at least one billing cycle with advance notice. | Trust. |

### 12.6 Business-model risks

| Risk | Why it matters | Mitigation |
|---|---|---|
| Free AI assistants erode willingness to pay | Learners can already ask a frontier model to tutor them for nothing [R12][R13][R14] | Sell the *system* (plan, evidence, projects, localisation), not the chat; keep the free tier useful enough to create habit but position projects and measurement as paid value. |
| Overly restrictive free tier | Kills word-of-mouth in exactly the markets where paid conversion is hardest | Make the free tier a complete first milestone; measure whether free users can articulate a win. |
| AI cost spike or vendor pricing change | Directly hits gross margin | Multi-provider gateway; tiered routing; self-hosting evaluation (§14.4); per-learner budgets. |
| Purchasing-power mismatch | US-style pricing fails in the beachhead markets | Regional pricing and local payment methods researched before launch (DEC-013). |
| Institutional sales distraction | Long cycles, procurement, safeguarding obligations | Keep institutional out of Phase 1; enter only with a product already fit for it. |
| Certification expectations | Learners may expect recognised credentials that TALIMGO cannot issue | Say clearly what the completion record *is*: a TALIMGO evidence record with artefacts — useful for a portfolio, not an accredited qualification. |
| Refund/chargeback abuse | Small margins | Clear policy, fraud screening on payment methods, velocity limits. |

---

## 13. Technical principles and architecture requirements

> **CONFIRMED:** no technology stack is chosen. This section specifies **required capabilities, boundaries, and non-functional requirements**, plus decision criteria for the stack (DEC-007). Nothing here asserts that any component has been built.

### 13.1 Architectural principles

| # | Principle | Consequence |
|---|---|---|
| 1 | **Modular services with explicit boundaries** | The AI tutor, roadmap engine, mastery engine, and content service can evolve and scale independently. |
| 2 | **Single source of truth per entity** | Each domain entity has exactly one owning service that writes it; other services read via API/events, never by writing into another service's tables. |
| 3 | **Content is data, not code** | Curriculum, items, rubrics, and prompts are versioned data, reviewable and rollback-able without a deployment. |
| 4 | **Evidence is append-only** | Evidence events are immutable; mastery estimates are derived and reproducible from the event log. This makes "why does it think I know this?" answerable forever. |
| 5 | **AI is a component, never the system of record** | Models produce proposals; the domain services decide, validate, and persist. |
| 6 | **Localization is structural** | Text extraction, locale-aware formatting, RTL logical layout, and Arabic-capable typography are foundational, not features. |
| 7 | **Privacy by default** | Data minimisation, per-learner isolation, encryption, audit trails, and self-service export/delete are requirements, not options. |
| 8 | **Cost is a design constraint** | Every AI feature ships with a cost model and a control mechanism (§12.4). |
| 9 | **Observability of learning and of AI quality** | Both product telemetry and AI-quality signals are first-class, not afterthoughts. |
| 10 | **Interoperability where it buys reach** | Support standard formats (QTI for items, xAPI/SCORM/cmi5 for records, LTI for institutional integration later) rather than inventing proprietary ones [R37]. |

### 13.2 Required capabilities (functional modules)

| Module | Responsibility | Key interfaces | Notes |
|---|---|---|---|
| **Identity & profiles** | Accounts, authentication, MFA, age declaration, roles, consent records, preferences (incl. language, RTL, accessibility) | Auth API; consent events | Must support future guardian-linked minor accounts. |
| **Goal & roadmap** | Goal records; roadmap generation, validation, versioning, adaptation | Curriculum graph; missions engine | Stores plan versions so "what changed and why" is answerable. |
| **Curriculum & content** | Domains, paths, modules, lessons, concepts, prerequisite edges; versioning/retirement | Content API; search | Authoring and review workflow is part of this module, not a separate tool. |
| **Assessment & item bank** | Items, keys, rubrics, adaptive delivery, scoring, misconception tagging | Evidence API | QTI-compatible export considered for portability [R37]. |
| **Mastery & skill graph** | Evidence ingestion, mastery estimation, confidence/decay, explainability | Read API for UI; write only from Evidence | Deterministic and unit-testable; model changes are versioned. |
| **Tutor orchestration** | Prompt assembly, grounding, hint ladder, guardrails, moderation, logging, cost accounting | Content/curriculum read; evidence proposals | Vendor-neutral through a gateway. |
| **Missions & scheduling** | Daily plans, spaced-repetition scheduling, load caps, recovery flows | Mastery read; calendar/preferences | Scheduling is algorithmic (not LLM-driven). |
| **Projects & rubrics** | Project briefs, submissions, artefact storage, rubric scoring, feedback, disputes | Storage; review queue | Artefact retention and cost policy required. |
| **Notifications** | Email/push/in-app scheduling with per-type consent and quiet hours | Preferences | Hard cap per day; no dark patterns. |
| **Billing & entitlements** | Plans, subscriptions, local payment methods, invoices, refunds, entitlement checks | Entitlement API used by all premium features | Entitlement checks are server-side and auditable. |
| **Analytics & reporting** | Product metrics, learning metrics, AI-quality metrics, learner-facing reports | Event pipeline | Privacy-preserving; no PII in analytics by default. |
| **Admin & moderation** | Content workflow, review queues, incident management, support actions, audit log | RBAC | Every admin action logged. |
| **Localization** | Message catalogues, pluralisation, RTL-aware components, locale formatting | Used by every UI module | Arabic is a launch locale, not a bolt-on. |
| **Data lifecycle** | Export, deletion, retention enforcement, backup/restore | All modules | Must be testable end-to-end. |

### 13.3 Data ownership and lifecycle

| Data class | Owner module | Sensitivity | Retention (PROPOSED) | Export | Delete |
|---|---|---|---|---|---|
| Account & preferences | Identity | Personal | Account lifetime + 30 days | ✅ | ✅ |
| Consent records | Identity | Personal/legal | Account lifetime + 5 years (legal proof) | ✅ | Retained as legal record with account identifier hashed |
| Goals, plans, plan versions | Goal & roadmap | Personal | Account lifetime + 30 days | ✅ | ✅ |
| Evidence events | Mastery | Personal | Account lifetime + 30 days | ✅ | ✅ |
| Mastery estimates | Mastery | Personal | Derived; recomputed | ✅ | ✅ |
| Assessment responses | Assessment | Personal | Account lifetime (or 24 months for item statistics in anonymised form) | ✅ | ✅ (aggregated/anonymised statistics may be kept) |
| Project artefacts | Projects | Personal / may contain third-party content | Configurable (proposal: 24 months after last access, learner-controlled) | ✅ | ✅ |
| Tutor conversations | Tutor | Personal | Proposal: 90 days by default; learner may "save to notes" to retain | ✅ | ✅ |
| Analytics events | Analytics | Pseudonymised | Proposal: 25 months aggregate; identifiers dropped after 90 days | ✅ | ✅ |
| Billing records | Billing | Financial | As required by tax law in the relevant jurisdiction | ✅ | Retained per legal obligation |
| Audit logs | Admin | Security | Proposal: 24 months | On request | Retained per security policy |
| Backups | Infrastructure | All | Rolling window (proposal: 35 days) | n/a | Purged on rolling basis |

### 13.4 Candidate stack options and evaluation criteria (UNRESOLVED — DEC-007)

**Criteria, in priority order:**

1. **Arabic/RTL maturity** in the UI framework (logical properties, bidi text, locale formatting).
2. **Hiring and community availability** in the target markets.
3. **Server-rendered performance on mid-range Android devices and slow networks** (a large share of the intended audience).
4. **Cost to run** at low scale and the path to efficient scale.
5. **Ecosystem for AI orchestration** (gateway, evaluation, observability).
6. **Type safety and schema validation** (structured AI output, plan validation).
7. **Operational simplicity** for a small team.
8. **Licence clarity** for any framework and dependency.

**Options to evaluate (no selection made):**

| Layer | Options | Notes |
|---|---|---|
| Web front end | Next.js/React; Remix/React; Nuxt/Vue; SvelteKit | All are viable; decide on team skills and RTL/i18n ergonomics. |
| Mobile | Responsive web first; React Native/Expo later; native later still | **Recommendation:** do not build native apps before web retention is proven. |
| Backend | Node/TypeScript (NestJS/Fastify), Python (FastAPI/Django), Go | Match the AI/ML tooling needs (Python) against the web team's velocity. |
| Database | PostgreSQL (primary recommendation) + object storage + a queue | Postgres covers relational curriculum, events, and JSONB flexibility; avoid premature polyglot persistence. |
| Vector store | Postgres with a vector extension first; dedicated vector DB only if needed | Keeps one system of record and simplifies per-learner isolation. |
| AI gateway | Self-hosted gateway (litellm-class) or provider-agnostic SDK | Enables routing, budgets, logging, and provider swaps (§14.3). |
| Search | Postgres full-text first; managed search later | Do not add infrastructure before it is needed. |
| Jobs/queues | Managed queue or Redis-based (BullMQ/Sidekiq-class) | Needed for generation, grading, notifications, link checks, exports. |
| Hosting | Managed PaaS or a single-region cloud with a clear growth path; EU or region-appropriate data residency per DEC-006 | Data residency is a legal input, not a performance choice. |
| Observability | OpenTelemetry-compatible tracing + error tracking + product analytics + LLM-specific tracing/evaluation | LLM tracing is separate from APM (§14.3). |
| Auth | Reputable managed identity provider or self-hosted (Keycloak/Ory-class) | Must support future guardian/child account linking and enterprise SSO later. |
| Billing | A provider with multi-currency and local payment coverage for the beachhead markets (research required) | Provider selection depends on DEC-013. |

**Anti-requirements (CONFIRMED):** do not adopt microservices at launch; do not build a custom LLM; do not build a custom vector database; do not self-host models before the volume justifies it; do not choose a stack whose only justification is résumé value.

### 13.5 Non-functional requirements

| Category | Requirement (PROPOSED, to be confirmed with the owner) | Verification |
|---|---|---|
| Performance (web) | LCP ≤ 2.5s and INP ≤ 200ms on a mid-range Android device over a throttled 4G connection for the critical lesson path; lesson text visible before any non-essential JS | Lighthouse/WebPageTest in CI with a defined device/network profile |
| Performance (API) | p95 ≤ 400ms for read endpoints; p95 ≤ 1.5s for write endpoints excluding AI calls; AI streaming starts ≤ 2.5s for first token | Load tests with defined concurrency |
| Availability | 99.5% monthly for the learner application at MVP (single region, no HA promise beyond this); documented degradation modes | Uptime monitoring; incident log |
| Scalability | Support 10,000 monthly active learners on the MVP architecture without redesign (assumption to be validated) | Load test at 5× current peak |
| Reliability | No learner data loss on failure; idempotent submissions; offline-tolerant lesson and assessment submission (queue locally, sync later) | Chaos/failure testing of submission paths |
| Security | Meets §11.3.2; external penetration test before launch | Test report + remediation log |
| Privacy | Meets §11.3.1; export completes within 24h; deletion completes within 30 days and is verified | Automated end-to-end tests on export/delete |
| Accessibility | WCAG 2.2 AA; automated + manual verification each release; no accessibility regressions merged | axe CI gate + manual checklist + external audit pre-launch |
| Localization | EN + AR complete at launch; no hard-coded strings; locale-aware numbers/dates; RTL verified per component | Pseudo-locale + RTL visual regression tests |
| Maintainability | Typed contracts between services; schema validation for all AI outputs; ≥ 70% unit coverage on the mastery and assessment engines (highest-risk logic); documented ADRs for every significant decision | Coverage report + ADR log |
| Observability | Structured logs with correlation IDs; traces across the AI path; dashboards for learning, cost, and AI quality; alerting on error-rate and cost anomalies | Dashboards exist and are used in on-call review |
| Testability | Test data seeding; sandbox model stubs for AI calls; reproducible evaluation runs | CI pipeline runs unit, integration, evaluation, and accessibility suites |
| Cost control | Cost per active learner tracked daily; per-learner and global AI ceilings; storage lifecycle policies | Cost dashboard + budget alerts |
| Backups/recovery | Automated encrypted backups; documented RPO ≤ 24h and RTO ≤ 8h at MVP (proposal); restore tested twice yearly | Restore drill log |
| Compliance | Documented data inventory; DPAs with processors; consent records; jurisdiction review before launching in a new market | Legal review checklist per market |

### 13.6 Notification architecture

| Notification | Channel | Default | Cap |
|---|---|---|---|
| Daily learning reminder | Push + email opt-in | On, quiet hours respected | 1/day |
| Weekly summary | Email | On | 1/week |
| Milestone achieved | Push + in-app | On | Event-driven, rate-limited |
| Assessment ready / awaiting review | In-app (+push opt-in) | On | Event-driven |
| Prerequisite alert / plan adjustment | In-app | On | Event-driven |
| Comeback check-in after absence | Push (only if opted in) | Off by default | Max 1 per absence period, and stop after one |
| Billing/receipt | Email | Transactional (cannot be disabled) | Event-driven |
| Security alert | Email + in-app | Transactional | Event-driven |
| Marketing | Email | Off by default | Per consent, with a frequency cap |

**Rules:** every type is individually controllable; a global "pause all reminders" switch exists; no notification may contain a false-urgency or shame claim (§6.9.3).

### 13.7 AI orchestration requirements

| Requirement | Detail |
|---|---|
| Prompt architecture | Versioned prompt templates stored as data; layered payload: system policy → task instructions → retrieved curriculum context → learner state → user input (clearly delimited). |
| Grounding | Retrieval from the curriculum store by concept ID; no free-range generation for curriculum claims; citations must resolve to stored sources. |
| Structured output | JSON-schema-validated outputs for roadmaps, item generation, rubric scores, and classification tasks; invalid outputs are retried once, then degraded gracefully. |
| Hint-ladder enforcement | Hint level tracked server-side; the model is instructed to respect the level and the output is checked before rendering. |
| Determinism where it matters | Assessment scoring for objective items is deterministic code, never a model call. |
| Fallbacks | If the model is unavailable: cached explanations, static hint ladders, and a clear message ("the tutor is unavailable; your lesson and practice work normally"). Learning must not stop when the AI fails. |
| Cost accounting | Every model call logged with tokens, model, feature, learner (pseudonymised), latency, and cost estimate. |
| Quality logging | Sample of outputs scored automatically (grounding, format) and by humans (accuracy, tone) on a fixed cadence. |
| Safety plumbing | Moderation on both input and output for the defined risk categories; blocked output is replaced with a safe template, never shown partially. |

### 13.8 Testing strategy

| Layer | Scope | Gate |
|---|---|---|
| Unit | Mastery engine, scheduler, scoring, entitlement checks, localisation formatting | Required, high coverage on logic-critical modules |
| Integration | Content ↔ assessment ↔ evidence ↔ mastery flow; billing ↔ entitlements | Required |
| Contract | Service interfaces and schema validation | Required |
| AI evaluation | §11.1.3 suite | Blocks release on regression |
| Safety/red-team | Prompt injection, harmful content, cross-tenant leakage, age-appropriate behaviour | Blocks release on any critical failure |
| Accessibility | Automated + manual keyboard/screen-reader per release | Required |
| RTL/visual regression | Component screenshots in EN and AR, LTR and RTL | Required |
| Performance | Lesson path on defined device/network profile | Required per release |
| Data lifecycle | Export completeness and deletion verification | Required per release |
| Usability | Moderated sessions with representative learners (EN/AR) | Per milestone |

### 13.9 Cost and sustainability engineering

| Concern | Requirement |
|---|---|
| Inference | §12.4 controls. |
| Storage | Lifecycle policies (hot → cold) for project artefacts and media; hard quotas per tier with clear messaging. |
| Media | Never re-host video (link), compress images aggressively, prefer diagrams over photography. |
| Egress | Cache static assets at the edge; avoid chatty APIs on mobile. |
| Low-bandwidth mode | Optional mode that disables images/video embeds, reduces client JavaScript, and prioritises text and practice. Important for the target markets. |
| Background jobs | Rate-limit and prioritise: assessment feedback and notifications ahead of analytics recomputation. |

### 13.10 Explicitly deferred technical decisions

| Deferred | Why | Revisit when |
|---|---|---|
| Native mobile apps | Web-first proves retention at lower cost | After web retention evidence (Phase 2) |
| Self-hosted model inference | Cost only improves at volume; operations cost is high | When monthly inference spend exceeds the break-even of GPU hosting (§14.4) |
| Voice/pronunciation assessment | Requires a judged-quality speech stack and language coverage | Phase 2+ for language paths |
| Real-time collaboration/community | Moderation burden; not core to the loop | Phase 3 |
| Institutional SSO/rostering | No institutional product yet | Phase 4 |
| Offline-first mobile sync | Complex; low-bandwidth mode is the cheaper first step | Phase 2 if evidence shows need |
| Blockchain/verifiable credentials | No credible requirement; adds cost | Only if a serious partner requires it |

---

## 14. Open-source landscape and reuse candidates

**Purpose:** avoid re-inventing commodity components while preserving licence compliance and TALIMGO's differentiating architecture. **No code, assets, curricula, or datasets were copied during this documentation task.**

### 14.1 Method and limitations

- Licence, activity, and popularity data were read from the **GitHub REST API on 2026-10-10** [R39] (repository metadata, `license.spdx_id`, last push date, latest release). Stars are a popularity proxy, not a quality measure.
- **`NOASSERTION`/"Other" licence values must not be treated as a licence.** They require reading the actual `LICENSE` file and, for dual-licensed projects, the specific directory's terms.
- **A repository's declared licence does not cover its dependencies, content, datasets, or trademarked brand assets.** Those must be checked separately.
- **Nothing here is legal advice.** Licence compatibility for a commercial product requires review by a qualified lawyer before any reuse.

### 14.2 Learning platforms / LMS candidates

| Repository | Purpose | Maintenance (2026-10-10) | Licence (per repo metadata) | Potentially reusable | Integration effort | Concerns | Fit for TALIMGO |
|---|---|---|---|---|---|---|---|
| [openedx/openedx-platform](https://github.com/openedx/openedx-platform) (formerly `edx-platform`) | Full LMS + Studio authoring | 8,195★; last push 2026-10-10; active | **AGPL-3.0** | Course authoring workflows, LTI tooling, certificates, grading primitives, plugin architecture | Very high (large Django/React monolith, heavy ops, its own data model) | AGPL network-copyleft obligations; architecture is course-centric, not goal-to-mastery-centric; enormous operational surface | **Reference architecture, not a base.** Study its plugin boundaries and LTI implementation; do not build TALIMGO on top of it at MVP. |
| [moodle/moodle](https://github.com/moodle/moodle) | LMS for institutions | 7,473★; last push 2026-10-03; active | **GPL-3.0** | Quiz engine patterns, question-type taxonomy, gradebook concepts, plugin ecosystem, LTI consumer | Very high (PHP, institutional assumptions, plugin coupling) | GPL-3.0 copyleft if distributed/modified; designed for courses and cohorts, not adaptive personal journeys | **Conceptual reference.** Its question-type taxonomy and rubric tooling are worth studying; reuse at the code level is not recommended. |
| [instructure/canvas-lms](https://github.com/instructure/canvas-lms) | Institutional LMS | 6,863★; last push 2026-04-30 | **AGPL-3.0** | Rubric model, speedgrader-style feedback flow, LTI integrations, outcomes alignment | Very high (Ruby/Rails + JS, large schema) | AGPL; heavy institutional orientation; slower upstream push cadence observed | **Reference only** (rubrics/outcomes are genuinely instructive). |
| [sakaiproject/sakai](https://github.com/sakaiproject/sakai) | Institutional LMS/collaboration suite | 1,237★; last push 2026-10-09; active | **ECL-2.0** (Educational Community License, permissive with attribution) | Assignment/gradebook tools, site tooling | High | Java/Spring stack; institutional focus; smaller community than Moodle/Canvas | **Low priority** for TALIMGO; licence is permissive enough to study. |
| [chamilo/chamilo-lms](https://github.com/chamilo/chamilo-lms) | LMS focused on ease of use and accessibility | 1,009★; last push 2026-10-10; release v3.0.1 (2026-09-19) | **GPL-3.0** | Accessibility patterns, simple authoring flows | High (PHP) | GPL-3.0; institutional orientation | **Accessibility reference** (its stated focus is rare and useful), not a base. |
| [frappe/lms](https://github.com/frappe/lms) | Modern, lightweight LMS on the Frappe framework | 3,299★; last push 2026-10-09; release v2.64.0 (2026-09-30) | **AGPL-3.0** | Course/batch/enrollment primitives, clean Python stack, REST APIs | Moderate (if TALIMGO were Python/Frappe — it is not decided) | AGPL; framework lock-in; cohort-centric | **Watch list.** The best-licensed-and-most-maintained "small LMS" — useful if an institutional offering is ever built. |
| [learningequality/kolibri](https://github.com/learningequality/kolibri) | Offline-first learning platform for low-connectivity environments | 1,140★; last push 2026-10-10; release v0.19.5 (2026-07-13) | **MIT** | Offline sync architecture, low-bandwidth content delivery, device management, channel/content packaging | Moderate–high (Python/Vue, plugin ecosystem) | MIT is highly permissive; its model is content distribution, not personalisation or assessment depth | **Highest-value licence/ops reference.** Study its offline-first design for TALIMGO's low-bandwidth mode and any future offline support. |
| [learningequality/studio](https://github.com/learningequality/studio) | Content curation tools for Kolibri | 192★; last push 2026-10-10 | **MIT** | Content-pipeline workflows, channel versioning | Moderate | Narrower scope; tied to Kolibri content formats | **Study for content versioning/publishing flows.** |
| [oppia/oppia](https://github.com/oppia/oppia) | Free online learning platform with interactive lessons and "explorations" | 6,845★; last push 2026-10-10; release v3.5.3 (2026-09-23) | **Apache-2.0** | Interactive lesson/exploration model, creator tooling, mobile web patterns, contributor workflow | Moderate–high (Angular + Python) | Apache-2.0 is business-friendly; its interaction model is closer to branching lessons than to mastery estimation | **Strong candidate for concept-level reuse** (lesson interaction design, state-based exploration) — subject to architecture review. |
| [adaptlearning/adapt_authoring](https://github.com/adaptlearning/adapt_authoring) | Authoring UI for the Adapt e-learning framework | 561★; last push 2026-08-04; release v0.11.5 (2025-01-15) | **GPL-3.0** | Responsive course authoring structure, component model | Moderate | GPL-3.0; slower release cadence; SCORM-era assumptions | **Reference only.** |
| [h5p/h5p-php-library](https://github.com/h5p/h5p-php-library) | H5P interactive content server library (H5P powers interactive exercises in many LMSs) | 150★; last push 2026-10-08 | **GPL-3.0** (per repo metadata) | Interactive exercise types, embeddable content model | Moderate | **Each H5P package can carry a different licence — verify per package.** The core JS repository (`h5p/h5p-core`) could not be resolved via the API during this research; confirm the exact repos and licences before use | **Conditional.** Interactive exercise types are valuable, but per-package licence verification is mandatory first. |

### 14.3 AI infrastructure and quality tooling candidates

| Repository | Purpose | Maintenance (2026-10-10) | Licence (per repo metadata) | Reuse potential for TALIMGO | Concerns |
|---|---|---|---|---|---|
| [BerriAI/litellm](https://github.com/BerriAI/litellm) | Multi-provider LLM gateway/SDK with cost tracking, guardrails, routing | 60,903★; last push 2026-10-10; very active | **NOASSERTION** (commonly MIT with a separate enterprise directory — **verify the LICENSE file and the `enterprise/` directory terms**) | Direct: TALIMGO's model routing, cost accounting, and provider abstraction (§13.7) | Licence values must be read file-by-file; the Rust core is a recent change; enterprise features may be separately licensed |
| [langfuse/langfuse](https://github.com/langfuse/langfuse) | LLM observability, tracing, prompt management, evaluation | 35,614★; last push 2026-10-10; very active | **NOASSERTION** (commonly MIT core + commercial EE modules — **verify**) | Direct: tracing tutor calls, prompt versioning, evaluation runs, quality dashboards (§11.1.9, §16.1) | Verify which features are in the open core vs. the paid edition; data residency matters for learner data |
| [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) | Prompt/model testing, evaluation, red-teaming | 25,878★; last push 2026-10-10; very active | **MIT** | Direct: implements much of the evaluation suite in §11.1.3 (including red-teaming and injection tests) | Evaluation infrastructure is only as good as the test sets; invest in curated, versioned datasets |
| [vibrantlabsai/ragas](https://github.com/vibrantlabsai/ragas) (formerly `explodinggradients/ragas`) | RAG evaluation metrics | 15,985★; **last push 2026-02-24 (slower)** | **Apache-2.0** | Useful for grounding/faithfulness scoring of tutor answers | Reduced activity; evaluate whether the metrics fit education-specific needs; consider building thin custom evaluators if adoption stalls |
| [danielmiessler/Fabric](https://github.com/danielmiessler/Fabric) | Curated prompt/pattern framework for common AI tasks | 44,212★; last push 2026-10-10; very active | **MIT** | Inspiration and possibly pattern reuse for summarisation/explanation prompts | Prompt patterns are generic, not curriculum-grounded; do not import wholesale as product behaviour |
| [vllm-project/vllm](https://github.com/vllm-project/vllm) | High-throughput LLM inference server | 93,521★; last push 2026-10-10; very active | **Apache-2.0** | Future option for self-hosted open-weight models (cost control at volume) | GPU operations, model quality trade-offs, and evaluation burden; revisit only when inference spend justifies it (§14.4) |

### 14.4 Spaced repetition and scheduling candidates

| Repository | Purpose | Maintenance | Licence | Reuse potential | Concerns |
|---|---|---|---|---|---|
| [open-spaced-repetition/fsrs4anki](https://github.com/open-spaced-repetition/fsrs4anki) | FSRS algorithm resources and Anki integration | 4,098★; last push 2026-08-14; release v6.1.3 (2025-09-08) | **MIT** | The FSRS algorithm specification and reference material for the scheduler (§6.5.6) | Algorithm is well suited to fact/concept review; it must be adapted for concept-level (not card-level) scheduling and for load caps |
| [open-spaced-repetition/ts-fsrs](https://github.com/open-spaced-repetition/ts-fsrs) | TypeScript implementation of FSRS | 810★; last push 2026-10-10; active | **MIT** | Direct candidate for the scheduler if the stack is TypeScript | Validate stability, testing, and API fit before adoption |
| [ankitects/anki](https://github.com/ankitects/anki) | Desktop/mobile spaced-repetition application | 31,900★; last push 2026-10-09; release 26.09.3 (2026-09-23) | **NOASSERTION** (commonly described as AGPL-3.0 — **verify the LICENSE file**) | **Reference only**: scheduling behaviour, card/queue UX | AGPL if confirmed; desktop-centric architecture; do not copy code |

### 14.5 Interoperability standards (not repositories, but reuse of standards avoids proprietary lock-in)

| Standard | Owner | Version to target | Why it matters to TALIMGO | Source |
|---|---|---|---|---|
| **LTI 1.3 + LTI Advantage** | 1EdTech | 1.3 (2019) + Advantage services | The only credible way to plug TALIMGO into institutional LMSs later (Phase 4). Design the tutor as an LTI-launchable tool from the start if institutional ambitions are real. | [R37] |
| **QTI 3.0** | 1EdTech | 3.0 (2022-05-01) | Portable item/interaction format; keeps the item bank from being a proprietary dead end and enables importing/exporting assessments. | [R37] |
| **xAPI 1.0.3** | ADL | 1.0.3 | Statement-based learning records (actor–verb–object) for activity outside the platform; useful for evidence interoperability. | [R37] |
| **SCORM 2004 (4th Ed.) / cmi5** | ADL | 2004 4th Ed.; cmi5 | Legacy compatibility for institutional buyers and content import; cmi5 is the modern xAPI-based packaging approach. | [R37] |
| **Caliper Analytics** | 1EdTech | 1.2 | Alternative analytics standard for institutional reporting. | [R37] |

**Recommendation (PROPOSED):** store TALIMGO's own canonical data model (do **not** model the database on SCORM), but provide **export adapters** to QTI (items), xAPI (evidence statements), and LTI (tool launches). This keeps the internal model honest and the external reach cheap.

### 14.6 Licence-compliance rules for any future reuse (CONFIRMED)

1. **Read the actual `LICENSE` file, not the GitHub badge.** Record the file hash, the version/tag, and the date of verification in a licence register.
2. **Never reuse a project whose licence is missing, `NOASSERTION` and unverified, or incompatible with commercial use.**
3. **Understand copyleft scope before adopting:**
   - **MIT / Apache-2.0 / BSD / ECL-2.0** — generally compatible with a closed commercial product, with attribution/NOTICE obligations.
   - **GPL-3.0** — strong copyleft; linking/deriving can trigger obligations on the derivative work. Server-side use without distribution is a grey area that varies by interpretation; **take legal advice before depending on GPL code in the product.**
   - **AGPL-3.0** — like GPL-3.0, but network use counts as distribution: if the code is modified and served to users, the corresponding source must be offered. This is a serious consideration for a hosted SaaS and is the main reason Open edX/Moodle/Canvas are not recommended as a base.
4. **Check secondary licence layers:** documentation (often CC BY-SA), content (often separately licensed or *not* licensed), datasets, icons, fonts, and model weights (weights have their own licences).
5. **Check trademarks.** Many open-source projects protect their names and logos; you may reuse code without reusing branding.
6. **Maintain a dependency inventory** with licences, versions, and obligations; automate it in CI (SBOM generation).
7. **Contribute back where practical** — it builds the ecosystem and reduces long-term maintenance risk.
8. **Never copy content, question banks, or curricula** from these platforms into TALIMGO content, regardless of code licence.

### 14.7 Verdict: what to build, what to borrow, what to avoid

| Component | Recommendation |
|---|---|
| LMS core (courses, cohorts, gradebook) | **Avoid wholesale adoption.** Build a lean goal→mastery core; borrow *concepts* (question taxonomy, rubric model) from Moodle/Canvas. |
| Offline/low-bandwidth delivery | **Study Kolibri (MIT)** closely; it is the best-licensed, most relevant prior art for TALIMGO's target markets. |
| Interactive lesson interaction model | **Evaluate Oppia (Apache-2.0)** for concept-level interaction patterns. |
| Spaced repetition scheduler | **Adopt an FSRS implementation (MIT)** rather than writing a scheduler from scratch. |
| LLM gateway, tracing, evaluation, red-teaming | **Adopt** a gateway + tracing + evaluation stack, with licence verification per component (§14.3). |
| Item/record standards | **Implement QTI/xAPI/LTI adapters**; do not model the core database on them. |
| Fonts | **Adopt** Inter + IBM Plex Sans Arabic under OFL-1.1 (verify per package). |
| Self-hosted inference | **Defer** until volume justifies it; evaluate `vllm` (Apache-2.0) then. |
| Curriculum, content, datasets | **Author and license in-house or use explicit open licences.** Never assume availability. |

---

## 15. MVP scope and phased roadmap

### 15.1 Roadmap philosophy

- **No launch dates.** Phases are gated by **exit criteria**, not by calendar promises, because no validated velocity data exists.
- Each phase lists objectives, dependencies, acceptance criteria, key risks, and measurable exit conditions (per the brief's requirement).
- **Scope is defended, not expanded.** The single biggest documented risk in this project is launching too broad (RSK-003).

### 15.2 Phase 0 — Validation and specification

| Element | Detail |
|---|---|
| **Objectives** | Resolve the five gating decisions (§2.4); validate that the target audience wants this and will pay; produce specifications good enough to build without re-litigating strategy. |
| **Workstreams** | (1) Brand clearance and naming risk (§21, DEC-001); (2) learner research: 25–40 interviews across P1/P3/P4 in at least two target markets, in the language they prefer, covering jobs-to-be-done, current spending, AI-assistant habits, payment methods; (3) concept test: clickable prototype of goal→diagnostic→plan→first session; (4) curriculum scoping: select the 3 launch paths (§15.3) and produce the first concept graphs; (5) pricing research: Van Westendorp-style price sensitivity + willingness-to-pay interviews; (6) technical spike: prototype the roadmap generator + validation gate + grounded tutor on one path; (7) content quality framework: authoring templates, review gates, citation standard; (8) legal review: age policy, data-protection mapping for the chosen launch geographies. |
| **Dependencies** | Owner availability for decisions; small research budget; access to representative learners. |
| **Acceptance criteria** | Decisions DEC-001/002/003/004/005 recorded; at least 25 interviews completed with synthesised findings; a prototype that a new user can complete end-to-end with a generated plan; launch paths' concept graphs reviewed by subject experts; a written data-protection mapping for the launch geography; a cost model with real token measurements from the spike. |
| **Exit criteria (measurable)** | (a) ≥ 60% of prototype testers describe the generated plan as "something I would actually follow"; (b) ≥ 40% state a specific intent to pay at the researched price point; (c) 0 blocking legal findings on the chosen name (or a documented rename decision); (d) the roadmap generator passes the validation gate on 100 generated plans; (e) named subject reviewers secured for each launch path. |
| **Key risks** | Research bias from testing with acquaintances (mitigate with recruitment diversity); mistaking politeness for willingness to pay (mitigate with payment-intent questions, not "would you use this?"). |
| **Deliverables** | Research report; specification pack (onboarding, roadmap, tutor, assessment, mastery, missions, projects); content framework; licence and data registers; updated versions of this document. |

### 15.3 Phase 1 — MVP

**MVP definition (CONFIRMED as a constraint):** *the smallest product that can take a real learner from a stated goal to demonstrated, evidenced capability in a narrow set of paths — end to end, in English and Arabic.*

#### 15.3.1 Recommended launch scope

| Scope item | Recommendation | Rationale |
|---|---|---|
| **Launch paths (3 maximum)** | **1) Python programming foundations** (broad demand, cheap to assess automatically, strong project ladder). **2) Front-end web development foundations** (visual, portfolio-friendly, immediate artefacts). **3) English for professional communication** (huge demand in the beachhead markets; exercises demand production, which showcases the measurement model). | Three paths prove the engine across three *different pedagogical profiles* (technical/automatable, creative/artefact-based, linguistic/production-based) without exploding content cost. |
| **Depth** | All three paths complete to their first capstone. No half-built paths. | A partially built path destroys trust faster than a missing one. |
| **Languages** | EN + AR UI; content in EN with AR explanations for the launch paths; RTL first-class. | §10.4. |
| **Platforms** | Responsive web only (mobile web usable at 360px). | Cheapest route to learning what works. |
| **Learner accounts** | Individual only (no institutional features). | §12.2. |
| **Ages** | **PROPOSED 16+**, with the policy defined for 13–15 as a Phase 2 decision (DEC-005). | Safest defensible position while the legal mapping is incomplete. |

#### 15.3.2 MVP feature set (P0 = required for the first useful release)

| # | Capability | Requirement ID | Notes |
|---|---|---|---|
| 1 | Authentication, profiles, consent, preferences (language/RTL/accessibility) | REQ-AUTH-01/02, REQ-PRIV-01, REQ-I18N-01 | Includes data export/delete. |
| 2 | Goal-based onboarding (10 steps, §6.1) | REQ-ONB-01…05 | With resumable state and a "draft plan now" escape. |
| 3 | Baseline/diagnostic assessment with confidence levels | REQ-ASM-01/02/03 | Adaptive for the launch paths only. |
| 4 | Personalised roadmap generation + validation gate + learner editing | REQ-PLAN-01…04 | Templates + graph + constraints (§6.3.3). |
| 5 | Learning dashboard ("Today") with one next action | REQ-DASH-01, REQ-MOT-01 | §6.9.1. |
| 6 | Structured lessons and practice (activity types 1–8, 10–12) | REQ-ACT-01…04, REQ-ASSESS-01 | §6.5.1. |
| 7 | AI tutor with hint ladder, grounding, uncertainty statements, reporting | REQ-TUT-01…07, REQ-TUT-09/10 | Includes the claim filter and evaluation suite. |
| 8 | Quizzes and feedback (objective + open-ended with rubric) | REQ-ASSESS-01/02, REQ-ASM-06 | Objective scoring deterministic. |
| 9 | Evidence-based mastery tracking + skill map | REQ-ASM-04/05, REQ-MAST-01 | Explainable evidence log per node. |
| 10 | Daily missions + recovery flows | REQ-MIS-01…03 | §6.7. |
| 11 | Spaced review + flashcards | REQ-REV-01, REQ-ACT-02 | FSRS-class scheduler with load caps. |
| 12 | At least one project per milestone with rubric and feedback | REQ-PRJ-01/02 | Project milestone 1 must complete end-to-end. |
| 13 | Progress reporting + export | REQ-PROG-01 | Evidence-based, not time-based. |
| 14 | Subscription billing + entitlements (server-side) | REQ-BILL-01…04 | Local payment methods per DEC-013. |
| 15 | Admin/content workflow, moderation, reporting queue | REQ-ADMIN-01, REQ-CONT-01…06 | Minimum viable governance; not optional. |
| 16 | Analytics + AI quality instrumentation | REQ-ANALYTICS-01, REQ-MET-01/02 | §16.1. |
| 17 | Support, help, policies, status | REQ-SUPPORT-01 | Privacy notice, terms, content-reporting. |

#### 15.3.3 Phase 1 acceptance criteria and exit conditions

| Type | Criterion |
|---|---|
| **Functional acceptance** | A new learner can complete onboarding, receive a validated plan, complete the first milestone (including a project) in ≥ 1 launch path, see evidenced mastery, and export their record — in both EN and AR, on a mid-range Android device over throttled 4G. |
| **Quality acceptance** | AI evaluation suite (§11.1.3) passes its minimum bars; accessibility audit passes WCAG 2.2 AA criteria in scope; no P0 security findings outstanding. |
| **Learning acceptance (measured, not assumed)** | Learners who complete the first milestone show measurable improvement on repeatable assessment items (pre/post, ≥ 2 weeks apart) in at least one launch path. |
| **Trust acceptance** | In moderated sessions, ≥ 80% of learners can correctly explain *why* the system believes a given skill is evidenced, and ≥ 80% rate progress reporting as "honest". |
| **Operational acceptance** | Documented runbooks; cost per active learner tracked daily; restore test completed; on-call rotation defined. |
| **Exit conditions (Phase 1 → Phase 2)** | (a) Week-4 retention of activated learners ≥ 25% *(proposed hypothesis, to be replaced by a researched target)*; (b) ≥ 30% of activated learners complete a milestone project; (c) AI quality: human-rated accuracy ≥ 4/5 on samples, fabricated-citation rate = 0; (d) cost per active learner within the modelled band; (e) 3 launch paths complete; (f) a documented list of the top 10 learner complaints with owners. |

#### 15.3.4 Phase 1 risks

| Risk | Mitigation |
|---|---|
| Content takes longer than the engine | Build content in parallel with engineering from day 1; treat content as the critical path. |
| Scope creep into Phase 2 features | A frozen MVP scope list with an explicit change process; new ideas go to a backlog with an owner decision. |
| Arabic quality is poor (translated-sounding) | Native Arabic authoring/review for content; native Arabic UI copy review; RTL testing with Arabic speakers. |
| AI cost exceeds the model | Cost dashboards from week 1; tiered routing and caching in the first release, not "later". |
| Weak differentiation vs free assistants in user perception | Landing-page and onboarding messaging that demonstrates the *system* (plan + evidence + projects), and prototype-driven positioning tests in Phase 0. |

### 15.4 Phase 2 — Learning depth

| Element | Detail |
|---|---|
| **Objectives** | Make the learning engine materially better than a first version can be: better adaptivity, better retention mechanics, better assessment, and more learner paths. |
| **Candidate scope** | Improved adaptive roadmap (real-time difficulty adjustment); full skill graph with cross-subject edges; spaced repetition tuning from real data; more assessment types (including oral explanation checkpoints); guided projects expanded to 2–3 per path; stronger curriculum management (authoring tools for non-engineers); better learner analytics (trend lines, misconception reports); additional language (French); code-execution sandbox hardening; offline/low-bandwidth improvements. |
| **Dependencies** | Phase 1 retention and quality evidence; staffing for content review; a stable content pipeline. |
| **Acceptance criteria** | Adaptation decisions are explainable and measurable (do learners reach mastery faster with the same evidence quality?); the skill graph supports cross-subject prerequisite inference; curriculum can be updated without engineering involvement. |
| **Exit criteria** | (a) Median time-to-mastery per concept improves versus Phase 1 baseline; (b) content update cycle time < 5 days for a lesson correction; (c) ≥ 60% of active learners use spaced review weekly; (d) at least two additional paths in production. |
| **Risks** | Over-fitting the adaptivity to noisy data; complexity that learners cannot understand; content operations becoming a bottleneck. |

### 15.5 Phase 3 — Outcomes and community

| Element | Detail |
|---|---|
| **Objectives** | Connect learning to external outcomes and add human community where it multiplies learning. |
| **Candidate scope** | Portfolio builder (with honest, learner-authored descriptions); capstone projects with human review; career-oriented paths mapped to role competencies; interview preparation; community features (study groups, peer review of projects, moderated forums); instructor and content-contributor workflows (revenue share or paid authorship); reputation systems for reviewers. |
| **Dependencies** | Proven individual retention; trust and safety capacity for community; a review-operations team; legal review of any career claims. |
| **Acceptance criteria** | Portfolio artefacts are exportable and honestly described; human review capacity meets demand with a defined SLA; community moderation playbook operational with escalation paths. |
| **Exit criteria** | (a) ≥ 20% of completing learners publish at least one portfolio artefact; (b) capstone human-review SLA met for ≥ 90% of submissions; (c) zero unresolved safety incidents in community; (d) learner-reported outcome changes (role change, promotion, freelance work) tracked as **self-reported** with clear disclaimers. |
| **Risks** | Community moderation cost and abuse; outcome claims drifting into guarantees; reviewer supply constraints. |

### 15.6 Phase 4 — Expansion

| Element | Detail |
|---|---|
| **Objectives** | Scale reach: more subjects, more languages, institutional products, and integrations — without diluting quality. |
| **Candidate scope** | Additional domains (business, design, science/maths, personal development, finance with heavy review); additional languages; institutional offering (rostering, cohorts, instructor dashboards, SSO, reporting, safeguarding controls); LTI 1.3 integration for LMS embedding; team dashboards; advanced integrations (calendar, drive, code repositories); regional compliance expansion; possible mobile apps with offline sync. |
| **Dependencies** | Quality operations that scale (review capacity per subject and language); a security/compliance posture fit for institutional procurement; support organisation. |
| **Acceptance criteria** | Each new domain has named subject reviewers and passes G1–G6 (§7.7); each new language has human review capacity; institutional deployments meet the documented security and data-protection requirements. |
| **Exit criteria** | (a) Institutional pilot completes with contracted renewal or documented go/no-go; (b) content quality metrics hold across all new domains; (c) support and review costs per learner remain within the model. |
| **Risks** | Breadth without depth; institutional obligations diverting the core product; regulatory exposure in new markets. |

### 15.7 What is explicitly out of scope until Phase 4 (CONFIRMED)

Native mobile apps · employer marketplaces or job boards · automated hiring or candidate scoring · credential accreditation claims · live cohort teaching/video classrooms · marketplace for third-party instructors with open publishing · blockchain credentials · social feeds · offline-first native sync.

---

## 16. Metrics, analytics, and acceptance criteria

### 16.1 Metric framework

**Principle (CONFIRMED):** measure *learner value* first. Engagement metrics are diagnostics; **educational outcome metrics are the scoreboard.** Where a metric could be gamed by making learners stay longer, pair it with a quality or outcome guardrail.

#### 16.1.1 Acquisition and onboarding

| Metric | Definition | Purpose | Measurement | Guardrail |
|---|---|---|---|---|
| Visitor → sign-up rate | Sign-ups ÷ unique landing visitors | Is the promise understood? | Web analytics, weekly | Not gamed by aggressive modals; measure modal-dismissal too |
| Onboarding completion | Learners who see a generated plan ÷ learners who start onboarding | Does onboarding deliver value fast? | Product events | Time-to-plan tracked alongside, so it is not "completed by making it trivial" |
| Time to first useful learning action | Median minutes from sign-up to first completed practice item | Reduce friction to value | Timestamped events | Watch for trivial-task inflation (e.g. counting a click as practice) |
| Roadmap acceptance | Learners who accept/keep the generated plan ÷ those who see one | Is the plan credible and useful? | Product events | Pair with plan-edit rate; a 100% acceptance rate might mean learners cannot edit |
| Diagnostic completion | Completed diagnostics ÷ started | Is the assessment tolerable? | Product events | Pair with placement accuracy (below) |

#### 16.1.2 Learning (outcome-adjacent)

| Metric | Definition | Purpose | Measurement | Guardrail |
|---|---|---|---|---|
| Skill improvement on repeatable assessments | Pre/post change on conceptually equivalent items, ≥ 2 weeks apart, per skill node | The core outcome metric | Item-response data | Must be measured on *equivalent* items, not the same items (memorisation) |
| First-attempt unassisted success rate | Share of practice items answered correctly without hints | Is practice well-calibrated? | Practice events | Target band proposed 70–85% for productive struggle; too high = too easy |
| Mastery transitions | Count of concept-level transitions into "consolidating"/"evidenced" | Is real capability accumulating? | Mastery engine events | Requires defined evidence thresholds (§6.6.2), not completion |
| Project completion | Projects completed ÷ projects started (by level) | Does learning produce artefacts? | Project events | Track time-to-complete to catch absurd scope |
| Delayed retention | Performance on items reviewed ≥ 14 days after first mastery | Is knowledge durable? | Review events | Compare with immediate performance; a large gap = weak mastery model |
| Remediation effectiveness | Share of repair modules that resolve the blocking prerequisite within one cycle | Is adaptation working? | Mastery events | Cap the number of repair cycles; escalating repairs signal content problems |
| Transfer evidence rate | Share of mastered concepts with at least one project/transfer evidence item | Is mastery real? | Evidence store | Without this, mastery becomes a quiz artefact |

#### 16.1.3 Consistency and retention

| Metric | Definition | Purpose | Measurement | Guardrail |
|---|---|---|---|---|
| Weekly learning consistency | Share of learners with ≥ 3 active days/week among activated learners | Habit formation (diagnostic, not an outcome) | Product events | Never incentivise low-value activity to hit this number |
| Session completion rate | Sessions finished ÷ sessions started | Is the workload realistic? | Product events | Pair with median session length vs. planned |
| Week-4 / week-12 retention | Share of activated learners active in the given week | Product health | Cohort analysis | Segment by language and by path; blended numbers hide everything |
| Recovery success | Share of learners absent 7+ days who return and complete a recovery session | Does absence-tolerant design work? | Product events | No shaming mechanics; measure after the recovery flow exists |
| Voluntary pause vs. churn | Learners who pause vs. who cancel outright | Does pause reduce churn? | Billing events | Attribution is hard; use as directional evidence |

#### 16.1.4 Trust, quality, and safety

| Metric | Definition | Purpose | Measurement | Guardrail |
|---|---|---|---|---|
| AI answer accuracy (human-rated sample) | Correct answers ÷ sampled answers, per subject and language | Is the tutor trustworthy? | Weekly sampled review (min. 100 answers) | Samples must include hard/tricky topics, not easy ones |
| Fabricated-citation rate | Answers citing a non-existent or non-retrieved source ÷ answers containing citations | A hard failure metric | Automated check + review | Target: **zero**; any occurrence is a P0 |
| Grounding rate | Share of tutor answers traceable to lesson/concept context | Is the tutor teaching the curriculum? | Automated grounding checker | Do not raise this by refusing useful general answers; label them instead |
| Harmful-output rate | Blocked/refused-rate on the red-team set and in production samples | Safety | Red-team suite + production sampling | 100% on blocked categories; production incidents reviewed within 24h |
| Content error reports | Reports per 1,000 lesson completions, and time-to-resolution | Content quality | Reporting queue | Track by subject; a spike usually means one broken lesson |
| Score dispute rate | Disputed automated scores ÷ scores issued, and the share upheld | Is grading fair? | Dispute queue | Upheld-dispute rate is a direct rubric-quality signal |

#### 16.1.5 Business and cost

| Metric | Definition | Purpose | Measurement | Guardrail |
|---|---|---|---|---|
| Paid conversion | Paid subscribers ÷ activated learners | Monetisation (UNVALIDATED target) | Billing events | Report separately for the free-tier cohort and the trial cohort |
| Subscription cancellation (logos churn) | Cancellations ÷ active subscribers per month, with a stated reason | Product health | Billing + exit survey | Exit survey must be optional and non-nagging |
| Cost per active learner | Total inference + infrastructure cost ÷ monthly active learners | Sustainability | Cost dashboards | Break down by feature; watch the tutor share |
| Gross margin per subscriber | Revenue − (inference + payment + infrastructure costs) | Viability | Finance + cost data | Include payment-provider fees, which are high for small transactions |
| Support volume per 1,000 learners and cost per resolved ticket | Operational load | Scalability | Support system | Spikes usually indicate a UX defect, not "bad users" |

### 16.2 Engagement vs. educational outcome (CONFIRMED distinction)

| Question | Engagement metric | Educational outcome metric |
|---|---|---|
| Did the learner show up? | Daily active users, sessions, streaks | — |
| Did the learner do work? | Tasks completed, practice items answered | Unassisted success rate, mastery transitions |
| Did the learner improve? | XP, levels, time-on-platform | Pre/post change on repeatable assessments; delayed retention; transfer evidence |
| Did it matter? | — | Project completion, artefacts produced, self-reported application of the skill |

**Rule:** every dashboard shown to the owner or investors must present engagement and outcome metrics **in separate columns, never blended**, and any claim about learning must cite an outcome metric.

### 16.3 Measurement design rules

1. **Define each metric before building the feature** that produces it (instrumentation is part of the definition of done).
2. **Version the instruments.** Assessment items used for pre/post measurement are versioned so that a content change does not silently invalidate a comparison.
3. **Prefer internal comparison over cross-learner comparison** for outcome claims (a learner's own baseline, not a leaderboard).
4. **Never publish a learning-outcome claim** without (a) a stated measurement, (b) the sample, (c) the period, and (d) a stated limitation.
5. **Anonymise/pseudonymise** analytics by default; never send free-text learner content into third-party analytics tools.
6. **Track cost alongside quality** so that quality improvements have a price tag.

### 16.4 Proposed metric hypotheses (NOT targets backed by evidence)

These are **hypotheses to falsify in Phase 0/1**, presented only so that dashboards can be designed. They are not commitments or promises.

| Metric | Illustrative hypothesis (to be replaced by research) | Confidence |
|---|---|---|
| Onboarding completion | 60–75% | Low |
| Median time to first plan | ≤ 9 minutes | Medium (design-dependent) |
| Week-4 retention of activated learners | 20–30% | Low |
| Milestone project completion among activated learners | 25–40% by week 8 | Low |
| Paid conversion (free → paid) in the first year | 2–6% | Very low |
| Monthly churn | 6–12% | Very low |
| AI cost per active learner | $0.86–8.63/month (model, §12.4) | Medium for the model; unverified in practice |
| Human-rated AI accuracy | ≥ 4.2/5 | Medium (achievable with grounding + evaluation) |

**Do not** put any of the above into a board deck as a plan. They exist to be proven wrong.

---

## 17. Prioritized requirement register

**Priority key:** **P0** = necessary for the first useful release · **P1** = needed soon after (Phase 2) · **P2** = valuable later (Phase 3) · **P3** = optional/later-stage (Phase 4+).
**Status key:** **Confirmed** (owner-established) · **Proposed** (recommendation awaiting approval) · **Unresolved** (blocked on a decision or evidence) · **Future** (deliberately deferred).

### 17.0 Requirement ID namespace

Every requirement in the MVP scope (§15.3.2) maps into one of these families, so that engineering tickets, design specs, and test plans can reference stable identifiers.

| Prefix | Area | Prefix | Area |
|---|---|---|---|
| `REQ-BRAND-xx` | Brand system and copy governance | `REQ-MAST-xx` | Skill map and mastery presentation |
| `REQ-NAME-xx` | Naming, domains, trademark clearance | `REQ-REV-xx` | Spaced review and flashcards |
| `REQ-AUTH-xx` | Accounts, authentication, consent capture, age declaration | `REQ-PROG-xx` | Progress reporting and export |
| `REQ-ONB-xx` | Goal capture and onboarding | `REQ-MOT-xx` | Motivation, dashboard priorities, break semantics |
| `REQ-ASM-xx` | Assessment, diagnostics, mastery model | `REQ-MIS-xx` | Daily missions, scheduling, recovery |
| `REQ-ASSESS-xx` | Assessment and quiz interface, results review | `REQ-CONT-xx` | Content governance, licences, versioning |
| `REQ-PLAN-xx` | Roadmap generation, editing, adaptation | `REQ-PRIV-xx` | Privacy, consent, export, deletion, age policy |
| `REQ-TUT-xx` | AI tutor, grounding, safety, cost control | `REQ-SEC-xx` | Security, sandboxing, incident response |
| `REQ-ACT-xx` | Activity types, review scheduling, offline/low-bandwidth | `REQ-A11Y-xx` | Accessibility and RTL |
| `REQ-DASH-xx` | The "Today" dashboard and next-action logic | `REQ-I18N-xx` | Localisation plumbing and language settings |
| `REQ-PRJ-xx` | Projects, rubrics, artefacts, portfolios | `REQ-BILL-xx` | Billing, entitlements, plan limits |
| `REQ-SUPPORT-xx` | Help, support, content reporting, status | `REQ-ADMIN-xx` | Admin console, moderation, audit |
| `REQ-TECH-xx` | Architecture, contracts, observability, backups | `REQ-ANALYTICS-xx` | Event instrumentation and metric pipelines |
| `REQ-OPS-xx` | Content operations, review staffing, support ops | `REQ-MET-xx` | Metric definitions and measurement instruments |

### 17.1 Brand, identity, and positioning

| ID | Requirement | User problem solved | Priority | Dependencies | Proposed acceptance criteria | Validation method | Status |
|---|---|---|---|---|---|---|---|
| REQ-BRAND-01 | One approved primary tagline per language ("Learn. Grow. Go." / «تعلّم بذكاء. تقدّم بثقة.») | Learners cannot recall what the product is for | P0 | Owner approval; Arabic copy review | Tagline appears consistently across landing, app, store listing; no competing primary tagline exists | Brand audit checklist; recall test in usability sessions | Confirmed (taglines set); supporting usage rules Proposed |
| REQ-BRAND-02 | A written, operational value system with violation signals (§3.7) | Generic values do not change decisions | P1 | None | Each value has a product consequence and a violation signal; product reviews reference them | Review of design/PRD templates | Proposed |
| REQ-BRAND-03 | Visual identity executed per §9, with a logo that passes the acceptance criteria set (legible at 16px, one-colour reproducible, distinct from existing "Taalim" marks) | Learners cannot recognise or trust an undefined brand | P0 | DEC-001 clearance; designer engagement | Logo passes acceptance criteria; assets exist as SVG/PNG/app-icon set with a spec sheet | Visual checklist + small-size test + clearance search | Proposed |
| REQ-BRAND-04 | Tagline/claim review process for all learner-facing copy | Prevent prohibited promises (§3.5) | P0 | Claim filter rules | 100% of launched copy reviewed against the blocked-claim list | Copy review log | Proposed |

### 17.2 Naming, domains, and legal clearance

| ID | Requirement | User problem solved | Priority | Dependencies | Proposed acceptance criteria | Validation method | Status |
|---|---|---|---|---|---|---|---|
| REQ-NAME-01 | Complete formal trademark clearance in the launch jurisdictions (INAPI, OMPIC, WIPO/Madrid, and any market entered later) | Avoiding a forced rebrand (§21) | P0 | DEC-001; IP counsel | A written clearance opinion for the agreed classes (9/41/42) per jurisdiction, or a documented rename decision | Official registry searches by counsel; watch services | Unresolved |
| REQ-NAME-02 | Secure the primary domain plus defensive variants | Avoiding brand confusion and losing traffic | P0 | DEC-002 | Primary domain registered and controlled; redirects configured; exact-name variants acquired where affordable | Registrar records; DNS verification | Unresolved |
| REQ-NAME-03 | Secure consistent social handles and package names (GitHub org, npm, PyPI, app stores) | Avoiding impersonation and packaging conflicts | P1 | DEC-001 | Handles reserved on priority platforms; package names registered or deliberately abandoned with a documented rationale | Manual reservations + registry checks | Unresolved |
| REQ-NAME-04 | Distinctive composite mark (logo + word) as the primary protectable asset | A descriptive-ish "Talim" word is weak on its own (§3.1) | P0 | REQ-BRAND-03 | Composite mark filed or cleared for filing; visual differentiation from existing marks documented | Clearance search + counsel review | Proposed |

### 17.3 Onboarding and journeys

| ID | Requirement | User problem solved | Priority | Dependencies | Proposed acceptance criteria | Validation method | Status |
|---|---|---|---|---|---|---|---|
| REQ-ONB-01 | Goal capture in ordinary language with outcome clarification | "I don't know how to start" | P0 | Goal schema; curriculum families | A learner can express a goal and see it restated as a testable outcome | Moderated usability (EN/AR) | Proposed |
| REQ-ONB-02 | Minimum-question onboarding (≤ 12 questions, justified individually) | Abandonment from long forms | P0 | None | Every question maps to a plan variable; removing it changes nothing (verified by test) | Spec review + A/B instrumentation | Proposed |
| REQ-ONB-03 | Time and schedule capture with editable defaults | Unrealistic plans | P0 | Planner | Learner sees sessions sized to their availability | Usability + plan review | Proposed |
| REQ-ONB-04 | Accessibility and format preferences captured in-flow | Learners excluded by default assumptions | P0 | i18n/RTL, a11y components | Preferences affect the rendered experience immediately | Manual a11y + RTL test | Proposed |
| REQ-ONB-05 | Resumable onboarding and "draft plan now" escape | Mid-flow abandonment | P0 | State persistence | Returning learners resume at the exact step; a provisional plan is available from partial data | Functional test | Proposed |

### 17.4 Assessment and mastery

| ID | Requirement | User problem solved | Priority | Dependencies | Proposed acceptance criteria | Validation method | Status |
|---|---|---|---|---|---|---|---|
| REQ-ASM-01 | Diagnostic placement with confidence levels and misconception tagging | Learners start in the wrong place | P0 | Item bank; adaptive engine | Placement proposal includes confidence per skill and an "why" explanation | Placement accuracy study vs expert judgement | Proposed |
| REQ-ASM-02 | Practical-task diagnostics for technical paths | Multiple-choice cannot establish applied ability | P1 | Sandbox | A learner can demonstrate a skill by doing, and the evidence is recorded | Functional test + reviewer validation | Proposed |
| REQ-ASM-03 | Explicit separation of demonstrated knowledge from self-reported confidence | False fluency | P0 | Evidence model | Confidence is never the sole basis for placement; conflicts trigger verification | Data audit | Proposed |
| REQ-ASM-04 | Evidence-based mastery model with defined thresholds and decay | "Mastery" that means nothing | P0 | Evidence store; mastery engine | Every state change stores the evidence that caused it; thresholds per §6.6.2 | Unit tests + evidence-log review | Proposed |
| REQ-ASM-05 | Reassessment triggers (decay, goal change, conflict) | Stale estimates | P1 | Scheduler; mastery engine | Defined triggers fire; learners are told why | Scenario tests | Proposed |
| REQ-ASM-06 | Dispute path for automated grading | Unfair scores | P0 | Review queue | Every score can be disputed; disputes are resolved with a written outcome | Operational test | Proposed |
| REQ-ASM-07 | No high-stakes claim without human-review availability | Over-trusting AI grading | P0 | Human reviewer capacity | Milestone-gating assessments offer human review | Policy + product audit | Proposed |

### 17.5 Roadmap generation and adaptation

| ID | Requirement | User problem solved | Priority | Dependencies | Proposed acceptance criteria | Validation method | Status |
|---|---|---|---|---|---|---|---|
| REQ-PLAN-01 | Structured roadmap generation from a validated curriculum graph | "What do I learn, in what order?" | P0 | Curriculum graph; typed schema | Generated plans pass schema + prerequisite + time-budget validation | Automated validation on 100 generated plans | Proposed |
| REQ-PLAN-02 | Every element carries outcome, prerequisites, estimate, practice, assessment, completion criteria, and next action | Opaque plans | P0 | Content model | 100% of elements in launch paths have all required attributes | Metadata completeness check | Proposed |
| REQ-PLAN-03 | Learner editing (reorder, remove optional, adjust time/date) with prerequisite guardrails | Loss of ownership | P0 | Planner UI | Learner can edit; breaking moves are explained and constrained | Usability test | Proposed |
| REQ-PLAN-04 | Adaptation on evidence (accelerate, remediate, reschedule, re-scope, change goal) | Plans that ignore reality | P0 | Mastery engine; adaptation rules | Each adaptation rule in §6.3.5 is implemented with a learner-visible rationale | Scenario tests + usability | Proposed |
| REQ-PLAN-05 | "What changed and why" record for every plan revision | Loss of trust when plans shift | P1 | Plan versioning | Every revision produces a readable change note | Functional test | Proposed |
| REQ-PLAN-06 | Goal change preserves all evidence and maps shared skills | Sunk-cost anxiety | P1 | Skill graph | Evidence carries over; gap analysis shown | Scenario test | Proposed |
| REQ-PLAN-07 | Refuse to fabricate a curriculum for unsupported goals | Broken trust | P0 | Curriculum coverage check | Unsupported goals produce an honest "not yet available" path | Content coverage audit | Proposed |

### 17.6 AI tutor and AI reliability

| ID | Requirement | User problem solved | Priority | Dependencies | Proposed acceptance criteria | Validation method | Status |
|---|---|---|---|---|---|---|---|
| REQ-TUT-01 | In-context tutoring grounded in the current lesson and concept | Help that is relevant | P0 | Content service; gateway | Grounding rate ≥ 98% on the evaluation set | Evaluation suite | Proposed |
| REQ-TUT-02 | Hint ladder: nudge → partial step → full solution only after an attempt or explicit request | Learning vs. answer-farming | P0 | Server-side hint state | Premature-answer rate ≤ 2% on the scripted red-team set | Red-team evaluation | Proposed |
| REQ-TUT-03 | Structured uncertainty and source statements | Over-trust | P0 | Grounding + citation resolution | 100% of presented citations resolve to retrieved sources; zero fabricated citations | Automated citation resolver | Proposed |
| REQ-TUT-04 | Claim filter blocking prohibited promises and advice (§11.1.1) | Legal/ethical exposure | P0 | Filter + classifier | Zero blocked-pattern outputs in the red-team suite | Evaluation suite + production sampling | Proposed |
| REQ-TUT-05 | Prompt-injection resistance for imported/learner-supplied content | Security and integrity | P0 | Isolation architecture | Zero instruction-following successes on the injection suite; all attempts logged | Red-team evaluation | Proposed |
| REQ-TUT-06 | Per-learner data isolation (no cross-learner leakage) | Privacy | P0 | Retrieval architecture | Zero leaks in the multi-tenant test harness | Automated isolation tests | Proposed |
| REQ-TUT-07 | Content-problem reporting from any lesson, item, or tutor message | Silent content errors | P0 | Support queue | Reports reach triage with an SLA and a status update to the reporter | Operational test | Proposed |
| REQ-TUT-08 | Graceful degradation when the AI is unavailable | Learning must not stop | P1 | Caching; static hint ladders | Lessons, practice, and review continue to function; a clear message is shown | Failure injection test | Proposed |
| REQ-TUT-09 | Separation of tutoring, assessment, planning, and general chat as distinct functions | Mixing evidence with conversation | P0 | Product architecture | No assessment evidence can be created from tutor or general chat | Architecture test | Proposed |
| REQ-TUT-10 | Tiered model routing and cost accounting per feature | Unsustainable cost | P0 | Gateway; cost pipeline | Cost per feature tracked daily; per-learner ceilings enforce a documented behaviour | Cost dashboard + budget test | Proposed |

### 17.7 Learning activities, projects, and motivation

| ID | Requirement | User problem solved | Priority | Dependencies | Proposed acceptance criteria | Validation method | Status |
|---|---|---|---|---|---|---|---|
| REQ-ACT-01 | Activity types 1–8 and 10–12 in the MVP mix (§6.5.1) | Passive learning | P0 | Content templates | Every launch-path concept has ≥ 1 active activity | Metadata audit | Proposed |
| REQ-ACT-02 | Spaced review with load caps and retrieval-first scheduling | Forgetting | P0 | Scheduler (FSRS-class) | Reviews scheduled per concept; daily cap configurable and enforced | Scheduler tests + learner telemetry | Proposed |
| REQ-ACT-03 | Low-bandwidth mode | Real network conditions in target markets | P1 | Front-end architecture | Mode disables heavy media and reduces payload measurably | Performance test on throttled profile | Proposed |
| REQ-ACT-04 | Sandboxed practical exercises with resource and network limits | Safe hands-on learning | P0 for technical paths | Sandbox infrastructure | No host-network access by default; sessions isolated and time-limited | Security test | Proposed |
| REQ-PRJ-01 | Projects with objective, prerequisites, milestones, deliverables, rubric and feedback | Learning that produces nothing | P0 | Rubric engine; storage | At least one project per milestone completes end-to-end with rubric feedback | End-to-end test | Proposed |
| REQ-PRJ-02 | Rubrics published before the work begins; AI scoring is advisory and disputable | Unfair assessment | P0 | Rubric engine; review queue | 100% of projects expose rubrics pre-start; disputes possible | Product audit | Proposed |
| REQ-PRJ-03 | Portfolio export with honest, learner-authored descriptions | Evidencing capability externally | P2 | Project storage; export | Artefacts exportable with learner-written descriptions; no fabricated content | Functional test + policy review | Future |
| REQ-MOT-01 | Dashboard prioritising goal, next action, progress, blockers (§6.9.1) | Overwhelm | P0 | Missions engine | Dashboard renders in the specified priority order on mobile and desktop | Design review + usability | Proposed |
| REQ-MOT-02 | Break-neutral streak semantics; no shaming; pause as a right | Churn from guilt | P0 | Preferences; notifications | No red/loss states; pause preserves all data; recovery flow exists | UX review + notification audit | Proposed |
| REQ-MOT-03 | Gamification limited to engagement, never mixed with mastery | Misleading progress | P0 | Mastery engine | XP/streaks never appear in mastery data or mastery UI | Data + UI audit | Proposed |

### 17.8 Content governance and curriculum

| ID | Requirement | User problem solved | Priority | Dependencies | Proposed acceptance criteria | Validation method | Status |
|---|---|---|---|---|---|---|---|
| REQ-CONT-01 | Human-authored curriculum structure reviewed by subject experts (G1–G6 gates) | Inconsistent, unreviewed lessons | P0 | Reviewer contracts | Every launch-path module has a named reviewer and a signed checklist | Review log audit | Proposed |
| REQ-CONT-02 | One canonical home per concept with references, not duplicates | Contradictory content | P0 | Content model | Duplicate-detection check passes for the launch paths | Content audit | Proposed |
| REQ-CONT-03 | Verified answer keys and explanations for every auto-graded item | Unfair/incorrect grading | P0 | Authoring workflow | 100% of items have a verified key; flagged items reviewed | Automated completeness check | Proposed |
| REQ-CONT-04 | Licence register for every external resource with periodic link and licence re-check | Copyright exposure; dead links | P0 | Resource register | Every external link has a licence record and a `last_checked` date; broken-link SLA met | Register audit | Proposed |
| REQ-CONT-05 | Citation standard for factual claims, with periodic link checking | Unverifiable claims | P1 | Content ops | Published content follows the citation standard; dead citations resolved | Sampling audit | Proposed |
| REQ-CONT-06 | Content versioning, correction, retirement and archive | Silent drift | P1 | Content service | Corrections push to active learners; retirements are archived, never deleted | Functional test | Proposed |

### 17.9 Privacy, security, and accessibility

| ID | Requirement | User problem solved | Priority | Dependencies | Proposed acceptance criteria | Validation method | Status |
|---|---|---|---|---|---|---|---|
| REQ-PRIV-01 | Plain-language privacy notice with per-purpose, granular consent | Distrust | P0 | Legal review | Consents are separate; declining optional processing does not degrade learning | Legal + UX review | Proposed |
| REQ-PRIV-02 | Self-service export of the complete learner record | Data ownership | P0 | Data lifecycle module | Export completes ≤ 24h and contains all learner-owned data in a readable format | End-to-end test | Proposed |
| REQ-PRIV-03 | Self-service deletion that genuinely deletes, with documented exceptions | Trust | P0 | Data lifecycle module | Deletion completes ≤ 30 days; legal-retention exceptions are disclosed | Verification test + audit | Proposed |
| REQ-PRIV-04 | Data inventory and retention schedule maintained | Dark-data accumulation | P1 | Operations | Every data field has a purpose and a retention rule; unused fields deleted quarterly | Inventory audit | Proposed |
| REQ-SEC-01 | Server-side authorisation on every object access; least-privilege roles; MFA for admins | Account/data compromise | P0 | IAM design | Penetration test finds no authorisation bypass; admin MFA enforced | Pen test + configuration audit | Proposed |
| REQ-SEC-02 | Encryption in transit and at rest; secrets in a managed store; no PII in logs | Breach impact | P0 | Infrastructure | Verified configurations; log sampling shows no PII | Security review | Proposed |
| REQ-SEC-03 | Sandboxed execution for learner code and bounded tool permissions for AI | Malicious input | P0 | Sandbox; gateway | No host-network egress by default; tool permissions enumerated and enforced | Security test | Proposed |
| REQ-SEC-04 | Incident response process with notification duties mapped per jurisdiction | Unhandled breaches | P1 | Legal mapping | Documented runbook; tabletop exercise completed | Tabletop review | Proposed |
| REQ-PRIV-05 | Age policy implemented and enforced (age declaration, minor safeguards, guardian consent where required) | Child-safety and legal exposure | P0 | DEC-005 | Declared policy enforced technically; under-age behaviour blocked and logged | Functional test + policy audit | Unresolved |
| REQ-A11Y-01 | WCAG 2.2 AA conformance for learner-facing surfaces | Exclusion | P0 | Design system | Automated + manual audit passes; external audit pre-launch | Audit report | Proposed |
| REQ-A11Y-02 | RTL-native layout for all components | Exclusion of Arabic readers | P0 | Design system; i18n | Component regression suite passes in both directions; no mirrored-logo errors | Visual regression + native-speaker review | Proposed |
| REQ-A11Y-03 | Reduced-motion, keyboard, and screen-reader support | Exclusion | P0 | Design system | Documented passes with ≥ 2 screen readers; no keyboard traps | Manual test | Proposed |

### 17.10 Business, platform, and operations

| ID | Requirement | User problem solved | Priority | Dependencies | Proposed acceptance criteria | Validation method | Status |
|---|---|---|---|---|---|---|---|
| REQ-BILL-01 | Server-side entitlement checks for every premium capability | Revenue integrity | P0 | Billing provider | No premium feature is reachable without a valid entitlement, verified server-side | Security/functional test | Proposed |
| REQ-BILL-02 | Self-service one-step cancellation, access until period end, evidence retained | Trust | P0 | Billing provider | Cancellation completes without contacting support; evidence remains accessible | Functional test | Proposed |
| REQ-BILL-03 | Local payment methods for the launch markets | Conversion | P0 | DEC-013 | At least one local payment route per launch market, tested with real transactions | Payment test + research | Unresolved |
| REQ-BILL-04 | Transparent free-tier limits that are visible and predictable | Distrust | P0 | Entitlements | Limits are stated in the UI and enforced consistently; no silent throttling | UX audit + telemetry | Proposed |
| REQ-TECH-01 | Typed, validated contracts between services and for all AI structured outputs | Silent corruption of plans/scores | P0 | DEC-007 | Schema validation on every structured AI output; invalid outputs rejected and logged | Unit + integration tests | Proposed |
| REQ-TECH-02 | Append-only evidence log with derivable mastery | Unexplainable mastery | P0 | Data model | Mastery can be recomputed from events; "why" is answerable for every node | Reconstruction test | Proposed |
| REQ-TECH-03 | Observability across product, cost, and AI quality | Flying blind | P0 | Instrumentation | Dashboards for learning, cost, and AI quality exist and are reviewed on a cadence | Dashboard review | Proposed |
| REQ-TECH-04 | Backups with tested restore and defined RPO/RTO | Data loss | P1 | Infrastructure | Restore drill completed twice yearly; documented RPO ≤ 24h / RTO ≤ 8h (proposal) | Drill report | Proposed |
| REQ-TECH-05 | Vendor-neutral AI gateway enabling provider/model swaps | Lock-in and outage risk | P0 | Gateway | Model can be swapped for a task class without product-code changes | Architecture test | Proposed |
| REQ-OPS-01 | Content-operations staffing model with review capacity per subject and language | Unreviewed content at scale | P1 | Budget | Named reviewers per launch path; review backlog SLA defined | Ops plan | Proposed |
| REQ-OPS-02 | Support channel with published response expectations and a content-reporting path | Silent failures | P0 | Support tooling | Support SLAs defined and met for ≥ 90% of tickets | Support metrics | Proposed |
| REQ-OPS-03 | Curriculum and content quality metrics visible to the owner monthly | Quality drift | P1 | Analytics | Monthly quality report published (errors, disputes, AI ratings, backlog) | Reporting ritual | Proposed |
| REQ-MET-01 | Instrumentation for §16.1 metrics defined before feature build | Unmeasurable outcomes | P0 | Analytics | Every P0 feature has events specified in its definition of done | Instrumentation review | Proposed |
| REQ-MET-02 | Outcome measurement plan (pre/post equivalent items) for launch paths | Defensible learning claims | P0 | Assessment engine | Equivalent-item instruments exist per launch path, versioned | Psychometric review (light) | Proposed |

### 17.12 Platform skeleton, dashboard, missions, review, reporting, admin, support, localisation

| ID | Requirement | User problem solved | Priority | Dependencies | Proposed acceptance criteria | Validation method | Status |
|---|---|---|---|---|---|---|---|
| REQ-AUTH-01 | Email/password and/or identity-provider sign-in with password-manager support, breach screening, session expiry, optional MFA, and admin-enforced MFA | Account security without friction | P0 | Auth service; email delivery | Sign-in works with a password manager; admin accounts cannot sign in without MFA; sessions expire and can be revoked per device | Security test + usability test | Proposed |
| REQ-AUTH-02 | Age declaration and consent capture at sign-up, enforced by the age policy (DEC-005) | Legal and safeguarding exposure | P0 | DEC-005 | Declared policy is enforced technically; consent records are stored and exportable | Functional test + policy audit | Unresolved |
| REQ-DASH-01 | "Today" screen with exactly one primary next action plus a one-line rationale | Decision fatigue | P0 | Missions engine; mastery model | Screen renders goal → next action → recent progress → blockers, in that order, on 360px and desktop | Design review + usability test | Proposed |
| REQ-MIS-01 | Daily plan generated from availability, current state and milestone, with objective + estimated time + completion condition per task | Unrealistic plans | P0 | Planner; preferences | Every task shows all four attributes; total fits the learner's stated availability | Functional test + learner review | Proposed |
| REQ-MIS-02 | Postpone, reschedule, shorten, swap format, and pause controls | Life does not fit a fixed plan | P0 | Preferences; planner | Each control works without losing evidence; pause produces an explicit resume plan | Functional test | Proposed |
| REQ-MIS-03 | Recovery flow after missed days per §6.7.3, with no shame language | Churn after absence | P0 | Planner; notifications | Recovery completes in ≤ 15 minutes for 3–6 day absences; no red/loss states appear anywhere | UX review + scenario test | Proposed |
| REQ-REV-01 | Review session interface with retrieval-first ordering, recall grading, and a visible daily cap | Forgetting; review overload | P0 | Scheduler (REQ-ACT-02) | Review never exceeds the cap; when the cap binds, the UI explains what is deferred and why | Functional test + telemetry | Proposed |
| REQ-ASSESS-01 | Assessment interface: no tutor access while active, no drag-only answering, pausable state, explicit submission summary | Fair, accessible assessment | P0 | Assessment engine | Tutor is unavailable during an active assessment; every interaction has a non-drag alternative | Functional + accessibility test | Proposed |
| REQ-ASSESS-02 | Results review with item-level explanations, misconception notes, and a dispute link | Learners cannot learn from results | P0 | Item bank; misconception tags | Every submitted item shows the correct answer, the explanation, and (where known) the misconception | Functional test | Proposed |
| REQ-MAST-01 | Skill map with mastery states, evidence log per node, filters, and a list-first (not graph-only) representation | Opaque progress | P0 | Mastery engine | Every node opens an evidence log in plain language; a list view conveys the same information as any visual | Accessibility + usability test | Proposed |
| REQ-PROG-01 | Learner progress report: evidence-based metrics over time, project status, and export (readable document + machine-readable file) | Proving progress to oneself or an employer | P0 | Analytics; mastery engine | Report contains no time-on-site metric labelled as progress; export completes successfully in EN and AR | Functional test + copy review | Proposed |
| REQ-ADMIN-01 | Admin console with role-based access, content workflow states, report/abuse triage queue, and an append-only audit log | Unmanaged content and abuse | P0 | RBAC; audit store | Every admin action is attributable and logged; report triage has SLA tracking | Security + operational test | Proposed |
| REQ-ANALYTICS-01 | Pseudonymised event pipeline for the §16.1 metrics, with no learner free-text sent to third-party tools | Blind product decisions | P0 | Analytics pipeline | Metrics in §16.1 are computable; sampling shows no PII or free-text in outbound analytics payloads | Data audit | Proposed |
| REQ-SUPPORT-01 | Help centre, contact route, content-reporting path, and a status page | Silent failures; no recourse | P0 | Support tooling | A learner can report a content error in ≤ 2 taps from any lesson; reports receive a status update | Operational test | Proposed |
| REQ-I18N-01 | Complete EN + AR coverage with no hard-coded strings and locale-aware number, date, and currency formatting | Broken Arabic experience | P0 | i18n framework; design system | Locale audit finds zero hard-coded strings in shipped surfaces; numbers and dates render per locale | Automated + manual audit | Proposed |
| REQ-I18N-02 | Separate settings for interface language and content/explanation language | Learners need mixed-language learning | P1 | Preferences; content model | The two settings are independent and the UI states which is which | Usability test | Proposed |

### 17.11 Confirmed vs. proposed (summary for readers in a hurry)

| Category | Confirmed by the owner | Proposed (needs approval) |
|---|---|---|
| Brand | Name TALIMGO as working brand; Arabic rendering; category; mission/vision/purpose/promise; values list; personality; taglines; the learning cycle; palette as the starting point | Tagline usage rules; distinctiveness strategy for the composite mark; operational value metrics; logo direction; typography choice |
| Product | Goal-oriented architecture; no guaranteed-outcome promises; project-based outcomes; evidence over completion | Specific onboarding questions; assessment thresholds; adaptation rules; activity mix; dashboard composition; session defaults |
| Curriculum | Multi-domain ambition; human-authored/validated curriculum with AI constrained to it; licensed-external-resources-only policy | The three launch paths; subject taxonomy details; review staffing levels |
| Technology | Modular, service-bounded architecture; content-as-data; append-only evidence; AI as a component; privacy by default | Stack selection; hosting/region; provider choices; offline strategy |
| Business | Free → individual → institutional ladder as the general direction; no dark patterns; evidence retained after cancellation | Prices; free-tier limits; trial mechanics; regional price localisation; institutional timing |
| Legal | No accreditation claims; age policy requirement acknowledged | Trademark clearance outcome; supported ages; jurisdictional scope |

---

## 18. Risk register

**Likelihood / Impact** are qualitative: **H**igh / **M**edium / **L**ow. Owners are **roles**, not named individuals (no names exist for this project yet).

| ID | Risk | Likelihood | Impact | Mitigation | Owner role | Next action |
|---|---|---|---|---|---|---|
| RSK-001 | **Brand-name conflict** — "TaalimGo" is an active education brand with a near-identical name in the same sector (§21) | **H** | **H** | Formal clearance in launch jurisdictions; consider a distinctive composite mark; prepare a rename contingency with a short list of alternatives; monitor for opposition | Founder + IP counsel | Commission clearance searches (INAPI, OMPIC, WIPO/Madrid, EUIPO, USPTO) for the agreed classes; record findings in DEC-001 |
| RSK-002 | Domain and handle unavailability/cybersquatting — `talimgo.com` is already registered and `taalimgo.com` is live (§21) | **H** | **M** | Secure the chosen primary domain and defensive variants now; define a fallback domain; consistent handle reservation | Founder | Register/confirm DEC-002; reserve handles |
| RSK-003 | **Overly broad launch scope** — trying to support all seven domains at launch | **H** | **H** | Freeze three launch paths; enforce a scope-change process; publish the out-of-scope list (§15.7) | Product lead | Ratify the MVP scope and begin the change-control log |
| RSK-004 | Hallucinated or wrong AI content damages trust or harms a learner | **M** | **H** | Grounding, citation resolution, claim filter, evaluation suite, user reporting, human review for high-risk subjects (§11.1, §11.4) | Engineering + content lead | Build the evaluation suite before any public beta |
| RSK-005 | Weak personalisation — the plan feels generic and loses to a free chatbot | **M** | **H** | Template+graph+constraint generation with validation; learner-visible rationale; adaptation on real evidence; prototype-tested in Phase 0 | Product lead | Phase 0 prototype test with ≥ 12 representative learners |
| RSK-006 | Curriculum inconsistency / duplication / drift across authors and AI content | **M** | **H** | Single canonical home per concept; G1–G6 gates; AI constrained to the graph; duplicate detection; versioning | Curriculum lead | Publish authoring templates and the concept-registry workflow |
| RSK-007 | **AI operating costs** exceed the model (heavy users, generous free tier, verbose prompts) | **M** | **H** | Tiered routing, caching, prompt discipline, per-learner budgets, daily cost dashboards, feature-level cost accounting (§12.4) | Engineering lead | Instrument cost per feature before beta |
| RSK-008 | Copyright/licence exposure from linked or reused material | **M** | **H** | Link-don't-copy policy; licence register; verification of every external resource; no scraping; open-source licence review (§14.6) | Content ops + legal | Stand up the licence register with the first 50 resources |
| RSK-009 | Privacy/security incident, especially involving minors | **L–M** | **H** | Data minimisation, consent granularity, encryption, MFA, RBAC, sandboxes, incident process, penetration testing (§11.3) | Engineering + DPO-equivalent | Draft incident runbook; complete the data inventory |
| RSK-010 | Regulatory non-compliance in the launch jurisdictions (Algeria Law 18-07, Morocco 09-08, GDPR, EU AI Act if applicable) | **M** | **H** | Jurisdiction-specific legal review before launch; strictest-default architecture; transfer log; age policy | Founder + counsel | Commission the legal mapping for DEC-006 |
| RSK-011 | Accessibility/localisation failure in Arabic (broken RTL, poor Arabic typography, translated-sounding content) | **M** | **M** | RTL-native design, Arabic copy authored by Arabic writers, visual regression in both directions, native-speaker testing | Design lead | Add RTL + Arabic review to the definition of done for every component |
| RSK-012 | **Low learner retention** — the platform is used once and abandoned | **H** | **H** | Realistic session sizing, recovery flows, evidence-visible progress, project artefacts, weekly planning ritual, no shame mechanics | Product lead | Instrument week-1/4/12 retention from the first cohort; interview churners |
| RSK-013 | Misleading mastery estimates (overstating capability) | **M** | **H** | Evidence thresholds, confidence labels, decay, transfer requirement, dispute path, no completion-based mastery (§6.6.3) | Assessment lead | Publish the mastery model and validate it against expert ratings on 50 learner records |
| RSK-014 | Unvalidated monetisation — price wrong, free tier wrong, no willingness to pay | **H** | **H** | Phase 0 price research; illustrative bands only; regional pricing exploration; milestone-based conversion design; pause instead of cancel | Founder | Run pricing research before building billing screens |
| RSK-015 | Content production slower than engineering (content is the critical path) | **H** | **H** | Start content in Phase 0; authoring templates; parallel review capacity; narrow paths | Curriculum lead | Recruit reviewers and start the first path during Phase 0 |
| RSK-016 | Generic-assistant commoditisation erases differentiation | **M** | **H** | Compete on system (plan, evidence, projects, localisation); measure perceived differentiation in research; iterate on the "what only TALIMGO does" narrative | Product + brand | Add a differentiation question to every usability session |
| RSK-017 | Talent/execution capacity — a small team, many domains (AI, pedagogy, content, design, payments) | **M** | **H** | Ruthless MVP scope; buy over build where licences allow (§14.7); sequence capabilities; document decisions so context survives turnover | Founder | Publish the build/buy/partner map |
| RSK-018 | Payment friction and fraud in target markets | **M** | **M** | Local payment providers, multiple routes, velocity limits, clear refund policy, chargeback monitoring (DEC-013) | Finance/ops | Research payment routes per launch market |
| RSK-019 | Platform dependency (single AI vendor outage, price change, or policy change) | **M** | **M** | Gateway abstraction; ≥ 2 providers by Phase 2; caching and graceful degradation; contractual terms that exclude training on customer data | Engineering lead | Implement the gateway before beta |
| RSK-020 | Safety incident involving a minor or a vulnerable learner | **L** | **H** | Age policy, restricted minor experience, escalation protocol, human staffing for escalations, no AI-only handling of safety signals (§11.4.4) | Trust & safety lead | Write and test the escalation protocol before opening registration to minors |
| RSK-021 | Reputational damage from an over-claim in marketing or AI output | **M** | **M** | Claim filter, copy review, prohibited-claims list, no outcome guarantees, honest progress reporting | Brand lead | Add claim review to the launch checklist |
| RSK-022 | Data loss or corruption (evidence, projects) | **L** | **H** | Encrypted backups, restore drills, append-only evidence, idempotent submissions, RPO/RTO targets | Engineering lead | Schedule the first restore drill |

---

## 19. Decision register and open questions

### 19.1 How to use this register

Each decision has a **status**: **Confirmed** (owner has decided) · **Proposed** (a default is recommended but not approved) · **Unresolved** (requires evidence or an owner decision) · **Future** (deliberately deferred). The **evidence required to finalise** column is the exit condition for the decision.

### 19.2 Decision register

| ID | Decision or question | Status | Options | Recommended default | Reasoning | Consequences if wrong | Evidence required to finalise |
|---|---|---|---|---|---|---|---|
| DEC-001 | Brand name and legal clearance: continue with TALIMGO? | **Unresolved** | (a) Proceed with TALIMGO after clearance; (b) proceed with a distinctive composite mark and accept coexistence risk; (c) rename | (b) if clearance shows coexistence risk but no fatal conflict; (c) only if counsel advises a blocking conflict | "Taalim" is highly used in the sector and a near-identical Moroccan brand exists (§21); a composite mark plus clear market separation is the cheapest path that preserves the owner's choice | A forced rebrand after launch destroys recognition, SEO, and paid acquisition; a coexistence conflict can exhaust founder attention | Written clearance opinions per launch jurisdiction and class; a documented risk assessment by counsel (Phase 0) |
| DEC-002 | Primary domain | **Unresolved** | `talimgo.com` is **taken**; `.io`/`.app`/`.ai`/`.org` showed no registration record on 2026-10-10; unverified TLDs (.ma, .dz, .net, .co, others); or a different TLD/name variant | Confirm at a registrar whether a `.com` acquisition is feasible/priced sensibly; otherwise select the most credible available TLD and reserve variants, with `www` and email configured properly | `.com` remains the strongest signal of legitimacy; but a live, branded alternative beats an unavailable one | Email deliverability, trust, and migration pain later | Registrar availability + price checks for the shortlist (including the exact TLDs whose RDAP status was inconclusive); a decision record |
| DEC-003 | Launch languages and whether Arabic is architecturally first-class | **Proposed** | (a) EN + AR at launch (2-locale build); (b) EN only, AR in Phase 2; (c) EN + AR + FR at launch | (a) | Arabic-first is the defensible differentiator and RTL must be built in, not retrofitted; FR adds QA cost without architectural learning | Retro-fitting RTL is a rewrite (§9.3.4); shipping English-only forfeits the beachhead advantage | Localisation cost estimate + native Arabic content/review capacity committed for at least one launch path |
| DEC-004 | First curriculum paths | **Proposed** | (a) 3 paths (§15.3.1); (b) 1 path; (c) 5+ paths | (a) | Proves the engine across three pedagogical profiles without exploding content cost | Too few: cannot demonstrate generality. Too many: nothing is finished | Subject reviewers secured; content production plan with dates-free milestones; demand signals from Phase 0 interviews |
| DEC-005 | Supported ages | **Unresolved** | (a) 16+ only; (b) 13+ with age-appropriate experience; (c) all ages with guardian consent (under-13 restricted) | (a) for MVP, with the policy for (b) defined and legal-reviewed for Phase 2 | Avoids minor-safeguarding and guardian-consent obligations at launch while keeping P2 reachable later; UNESCO guidance recommends 13 as the unsupervised floor for generative AI [R15] | Opening to minors without safeguarding capacity is a serious reputational and legal risk; being too restrictive loses the large exam-prep segment | Legal opinion on minor consent per launch jurisdiction; safeguarding staffing plan; product spec for a restricted minor experience |
| DEC-006 | Initial geographic scope (market sequencing) and the resulting legal regime | **Unresolved** | (a) Algeria-first; (b) Morocco-first; (c) Maghreb + Gulf diaspora; (d) global English-first | (a) or (b) — decide on payment infrastructure, legal-review cost, and founder proximity, then sequence | Data-protection regimes differ materially (Algeria's declaration/authorisation rules; Morocco's CNDP; GDPR if EU users) and drive architecture choices | Serving EU/Morocco users without the right registration/consent machinery creates compliance exposure; a too-broad scope multiplies legal cost | Legal mapping per candidate market; payment-method viability; founder's access to users/reviewers |
| DEC-007 | Technology stack | **Unresolved** | Front-end: Next.js/React · Remix · Nuxt/Vue · SvelteKit. Backend: Node/TS · Python · Go. Data: PostgreSQL (+vector extension) as the default | Postgres-first; a TypeScript web stack; a Python service only where AI/data tooling demands it | §13.4 criteria: RTL maturity, hiring pool, slow-network performance, cost, AI ecosystem | Premature commitment wastes months; the wrong stack slows both engineering and content operations | A 1–2 week technical spike building (i) an RTL AR/EN component, (ii) a grounded tutor call, (iii) a mastery recomputation from events, on the two leading candidates; measured results |
| DEC-008 | Pricing model and price points | **Unresolved** (illustrative bands only, §12.3) | Free + one paid tier; free + two; usage-based AI credits; course-based purchase | Free + Plus initially; defer Pro until the value is proven | Consumer price floor is dragged down by free AI modes and $4/month Khanmigo [R28]; extra tiers without differentiated value confuse buyers | Wrong price kills conversion or margin; wrong free tier kills growth | Van Westendorp/price-sensitivity research + payment-intent questions in Phase 0; local payment-route costs |
| DEC-009 | Free-tier AI limits | **Proposed** (10 messages/day) | Low (e.g. 3/day) · Medium (10/day) · Feature-gated (unlimited tutor, gated projects) | Medium daily limit, with unlimited practice and the full first milestone free | Limits must be predictable and cost-bounded; tutorial value must be felt before paying | Too low: the product feels broken and word of mouth dies. Too high: cost per free learner becomes acquisition spend by accident | Measured token cost per free learner from the Phase 0 spike; conversion data from the first cohort |
| DEC-010 | Trial design | **Proposed** | Free tier as the trial · 7-day trial of paid · milestone-triggered invitation | Free tier + milestone-triggered invitation to try Plus | Rewards demonstrated engagement rather than click speed | A timed trial that expires mid-path damages trust | Conversion comparison between trial designs once cohort data exists |
| DEC-011 | Primary tagline and usage rules | **Confirmed** ("Learn. Grow. Go." primary; "Your Goal. Your Path. Your Future." supporting; Arabic line set) | — | Keep as confirmed; forbid competing primary lines | Two competing primary taglines dilute recognition | Brand recognition suffers; copy becomes inconsistent | Recorded owner decision (this document) |
| DEC-012 | Design system base | **Proposed** | Build tokens/components in-house; adopt an existing open design system as a base; license a commercial kit | Adopt an open, permissively licensed base (with RTL verification) and layer TALIMGO's tokens and components on it | Faster to a coherent UI; avoids inventing primitives; but RTL and Arabic typography must be verified in the base | A base without genuine RTL support costs more than it saves | Audit of 2–3 candidate systems for RTL, accessibility, licence, and maintenance |
| DEC-013 | Payment providers and regional price localisation | **Unresolved** | Global provider only · global + regional providers · regional-only | Global provider for reach + at least one local route per launch market; price localisation assessed with arbitrage risk accepted or mitigated | Card penetration and local payment habits materially affect conversion in the target markets (UNVERIFIED — research required) | Lost revenue from unusable checkout; fraud exposure | Payment-route research per market; provider fee comparison; test transactions |
| DEC-014 | Mastery model parameters (thresholds, decay, transfer evidence) | **Proposed** (as specified in §6.6.2) | Stricter (more evidence required) · looser (faster progression) | Stricter for "evidenced"; looser for "practising", so learners see momentum | Under-claiming is safer than over-claiming for trust and for honesty | Loose thresholds make mastery meaningless; strict ones frustrate learners | Validation study: compare model estimates with expert ratings on ≥ 50 learner records; learner-perception interviews |
| DEC-015 | Institutional/B2B timing | **Proposed: Phase 4** | Phase 2 · Phase 3 · Phase 4 · never | Phase 4, after individual retention is proven | Institutional sales require compliance, support, and procurement maturity that a pre-PMF product cannot carry | Early institutional work consumes the founding team and distorts the product | Evidence of individual retention plus inbound institutional demand |
| DEC-016 | Native mobile apps | **Proposed: Phase 2+** | Mobile web only · PWA · React Native · Native | Mobile web/PWA first; decide native after retention evidence | Cheap learning; avoids app-store tax and release friction early | Late native app may limit growth channels | Retention and mobile-web usage data |
| DEC-017 | Content contributor terms (ownership/licensing) | **Proposed** | Work-for-hire with full assignment · licence-back to author · revenue share | Work-for-hire or exclusive licence with clear attribution; contributor agreement template before the first external author | Protects the product's core asset and avoids future rights disputes | Content cannot be legally reused/published; contributor disputes | Legal template reviewed by counsel |
| DEC-018 | AI model selection and routing policy | **Proposed** (tier-by-task-class, §11.1.2) | Single frontier model · single budget model · multi-model tiered routing | Multi-model tiered routing through a gateway, with evaluation gating model changes | Balances quality, cost, and vendor risk | Single-vendor lock-in; cost spikes; quality regression without gates | Benchmark results from the evaluation suite per task class |
| DEC-019 | Community features | **Proposed: Phase 3** | None · study groups only · peer review · full forums | Study groups + peer project review (moderated) in Phase 3 | Community multiplies learning but requires moderation capacity | Unmoderated community creates safety and reputational risk | Moderation playbook + staffing budget |
| DEC-020 | Default session length and daily task count | **Proposed** (15–25 min; ~3 tasks) | 10 · 20 · 45 minutes defaults | 20 minutes, user-configurable 10–60 | Fits the primary audience's constraints (UNVERIFIED — test in Phase 0) | Wrong default reduces completion and perceived realism | Phase 0 usability testing across P1/P3/P4 |
| DEC-021 | Measurement instrument for learning-outcome claims | **Unresolved** | (a) Equivalent pre/post items per path; (b) standardised third-party tests; (c) learner self-report only | (a) as the primary instrument, with (c) reported separately and never as evidence of learning | Internally developed tests inflate effect sizes relative to independent measures (documented in the ITS literature [R26]) — so claims must be framed accordingly | Publishing outcome claims that cannot survive scrutiny | Psychometric review of the equivalent-item instruments; a documented measurement protocol |
| DEC-022 | Data residency and hosting region | **Unresolved** | Home-market region · EU · multi-region | EU or the most defensible region permitted by the launch jurisdictions' transfer rules | Algeria's cross-border transfer rules require care [R17]; Morocco's framework requires CNDP authorisation for transfers [R18]; EU residency simplifies GDPR posture | Compliance exposure; migration cost later | Legal mapping (DEC-006) + provider availability + latency testing from the beachhead markets |

### 19.3 Open questions that are not yet decisions

| # | Open question | Why it matters | How to resolve it |
|---|---|---|---|
| Q1 | Will learners accept an AI tutor that refuses to give answers? | The hint ladder is a core bet | Behavioural test in Phase 0: measure frustration vs. perceived learning value |
| Q2 | Is "proof of capability" more motivating than certificates in the target markets? | Positioning and pricing | Interviews + prototype comparison; segment by market |
| Q3 | How much Arabic-language content must exist at launch for the Arabic UI to feel credible? | Language phasing cost | Native-speaker perception testing with all-Arabic vs. partial-Arabic content |
| Q4 | Is the beachhead market willing to pay in USD/EUR, or only in local currency? | Payment and pricing design | Payment research (DEC-013) |
| Q5 | What is the realistic authoring cost per concept (including review)? | Content scaling model | Time-and-cost logging during the first path build |
| Q6 | Does the skill-graph visualisation help or intimidate? | IA and motivation | A/B usability test of tree vs. path vs. list |
| Q7 | Should mastery decay be visible by default, or only on request? | Trust vs. anxiety | Learner interviews; measure re-engagement impact |
| Q8 | How will TALIMGO handle a learner who insists on pursuing a goal with no validated curriculum? | Trust and scope discipline | Policy decision + product copy test |
| Q9 | Is a human review tier economically viable for capstones? | Pro tier design | Cost measurement per reviewed submission |
| Q10 | What is the minimum viable moderator/safeguarding capability if minors are supported? | DEC-005 | Benchmark against comparable platforms' published policies + staffing cost estimate |

---

## 20. Brand applications and marketing

**Global rule (CONFIRMED):** no claim may describe users, outcomes, awards, partnerships, instructors, accreditations, or platform capabilities that do not exist. Until launch, all public communication is written in **future/proposed tense** or is explicitly framed as a product in development.

### 20.1 Website and landing page

#### 20.1.1 Sample messaging (ready for review, PROPOSED)

**1. Headline (primary):**
> **Learn. Grow. Go.**
> *Sub-headline:* Turn a goal into a plan you can actually follow.

**2. Supporting explanation (hero paragraph):**
> TALIMGO is an AI-powered learning companion. Tell it what you want to be able to do. It maps what you need to learn, builds a plan around the time you actually have, tutors you through the difficult parts, and shows you honest evidence of what you can now do — adapting the plan as you go.

**3. Primary call to action:**
> **Build my learning plan** *(secondary CTA: "See how it works")*

**4. Three evidence-based value propositions:**

| Value proposition | Supporting detail (defensible today) |
|---|---|
| **A plan, not a catalogue.** | TALIMGO sequences learning from your goal and your schedule — prerequisites first, with each step's purpose explained. (Free AI assistants teach a topic; they don't own your route to an outcome.) |
| **Evidence, not watch-time.** | Progress is measured by what you can do unassisted — including after a delay, and inside a project — with the evidence shown to you. |
| **Learning that produces things.** | Every milestone ends in an artefact: an app, a report, a recorded explanation — something real you can keep. |

**5. How the platform works (six-step section, plain language):**

> 1. **Say what you want.** In your own words, in English or Arabic.
> 2. **Show us where you are.** A short diagnostic — not a placement exam you can fail.
> 3. **Get your plan.** Milestones, lessons, practice and projects, sized to your week, editable by you.
> 4. **Learn and practise with help that doesn't just give answers.** Hints first, explanations at your level, practice that makes you produce.
> 5. **Build something.** Projects with clear rubrics and feedback you can act on.
> 6. **See the evidence — and adapt.** Your plan changes when your life or your evidence changes.

**6. Example learner journey (illustrative — must be labelled as illustrative, not a testimonial):**

> *"Karim works full time and has four hours a week. He says he wants to build websites. TALIMGO's diagnostic shows his logic is solid but his JavaScript isn't. His plan: three milestones over five months, each ending in a deployed project. In week three, work gets busy — he switches to 90 minutes a week, and the plan re-scopes instead of collapsing. In month two he ships an interactive page for a real client, and the rubric feedback shows exactly what to fix next."*
> **Label under the graphic:** *Illustrative example, not a real user or a promised outcome.*

**7. Trust and privacy statement:**
> **What we won't do.** No promises of a job, an income, or a guaranteed level. No fake urgency. No selling your data. No advertising to minors.
> **What you control.** You can export everything we hold about you, in a file you can read, and delete your account yourself. You can turn off non-essential analytics. Limits on the free plan are visible and predictable. If we make a mistake in a lesson or an answer, tell us — and we'll fix it and tell you what changed.

**8. Frequently asked questions (sample, honest answers):**

| Question | Answer |
|---|---|
| Is TALIMGO another course library? | No. It builds a plan from your goal, then teaches, drills, and measures along the way. Courses are one ingredient, not the product. |
| How is this different from using ChatGPT to learn? | General assistants tutor a conversation. TALIMGO keeps a structured curriculum, records what you've evidenced, spaces your review, and runs projects with rubrics — and it remembers where you are next week. |
| Do I get a certificate? | You get a **TALIMGO evidence record**: your artefacts, your measured skills, and your history. It is not an accredited qualification and we will never call it one. |
| Is it really in Arabic? | Yes — Arabic is a launch language, designed right-to-left, not translated afterwards. |
| How much time do I need? | You choose. Plans are built around the hours you actually have, and can be re-scoped when your week changes. |
| What if I stop for a while? | Nothing expires. You get a short restart session and a rebuilt schedule that keeps everything you've already evidenced. |
| How much does it cost? | The first milestone of any path is free, with a daily limit on AI tutoring. Paid plans remove those limits. *(No price is published until pricing research completes — see DEC-008.)* |
| Who reviews the content? | Subject reviewers for high-risk areas, and a public way to report anything wrong. |
| Is my data safe? | Encryption in transit and at rest, minimum data collection, self-service export and deletion, and no selling of personal data. *(Detail in the privacy notice.)* |
| What if the AI is wrong? | Report it in one tap; every report is triaged, and corrections are pushed to learners. |

### 20.2 Web application

- **Tone inside the product is quieter than on the landing page.** No selling, no slogans, no motivational wallpaper. The dominant voice is the tutor's and the interface's.
- **The word "AI" is used where it is informative (what the tutor can and cannot see) and avoided where it is marketing.**
- The product always shows the learner what it is doing on their behalf ("grounded in this lesson", "generated for this session").
- No in-app advertising, ever. No upsell modals during a lesson, an assessment, or a project milestone.

### 20.3 Mobile application (if later built)

- Same voice and claims; the differentiator must survive on a 360px screen.
- Store listing must state plainly: what the app does, what it does not promise, subscription terms, and data practices — store review and user trust both depend on it.
- Push notifications follow §13.6 (max one learning reminder per day; quiet hours; no shame copy).

### 20.4 Social media

| Platform | Role | Content types | Rules |
|---|---|---|---|
| LinkedIn | Credibility, practitioners, partnerships | Product thinking, learning-science explainers, build-in-public updates, career-path content | No inflated metrics; label prototypes as prototypes |
| Instagram / TikTok | Reach, demonstration | 30–60s "how it works" demonstrations, study-technique explainers, learner journey illustrations | Never fake learner results; if a demonstration is simulated, say so on screen |
| YouTube | Depth | Feature walkthroughs, mini-lessons that are genuinely useful on their own | No clickbait titles that misrepresent content |
| X/Twitter | Community and industry | Product notes, learning science, releases | No engagement-bait |
| Facebook | Regional reach in target markets | Localised Arabic/French content, community support | Follow the same claim rules; ad targeting must respect the minors policy |

**Bio copy (EN):** *"Turn a goal into a plan. Learn, practise, build — and see honest evidence of what you can do. Arabic & English. Currently in development."*
**Bio copy (AR):** «حوّل هدفك إلى خطة: تعلّم، تدرّب، ابنِ — وشاهد أدلتك بصدق. بالعربية والإنجليزية. قيد التطوير.»
**Bio copy (FR, Phase 2):** *"Transformez un objectif en un plan d'apprentissage. Apprenez, pratiquez, construisez. Bientôt disponible."*

**Hard rules (CONFIRMED):** never post simulated testimonials as real; never imply user numbers; always label prototypes; never use learner results without written consent and context.

### 20.5 Promotional content

- **Lead with the mechanism, not the promise:** "here's how the plan adapts when you miss a week" is more persuasive (and more honest) than "learn 10x faster".
- Demonstrate with real screens and real generated plans (from a demo account, clearly labelled).
- Comparative content must be factual and sourced; never disparage a competitor with an unsupported claim.
- All performance/learning claims require a stated measurement, sample, and limitation (§16.3 rule 4).

### 20.6 Product onboarding communication

- The first three screens must answer: *what is this, what will it do for me, what will it not do.*
- Set the honest expectation early: the plan is an estimate; the AI can be wrong; the learner can always override.
- Micro-copy must always name the *why* behind a request ("we ask about your week so the plan fits it").

### 20.7 Email communication

| Email | Trigger | Purpose | Sample subject (EN) | Sample subject (AR) |
|---|---|---|---|---|
| Welcome | Sign-up | Set expectations; get to the first session | "Your plan starts here" | «خطتك تبدأ هنا» |
| Day 3 nudge | No completed session after 72h | Remove friction, offer a shorter option | "12 minutes is enough to start" | «١٢ دقيقة تكفي للبدء» |
| Week 1 summary | 7 days after activation | Show evidence, not activity | "What you evidenced this week" | «ما أثبتّه هذا الأسبوع» |
| Milestone achieved | Milestone complete | Celebrate concretely; offer the next step | "Milestone 1 done — here's what you built" | «أنجزت المرحلة الأولى — هذا ما بنيته» |
| Recovery | 7+ days inactive (if opted in) | Reduce guilt, restore momentum | "Your progress is still here" | «تقدّمك ما زال محفوظًا» |
| Plan changed | Adaptation triggered | Explain what changed and why | "We re-scoped your plan — here's why" | «أعدنا ضبط خطتك — والسبب...» |
| Billing | Transactional | Clarity, no surprises | "Your receipt and what's included" | «إيصالك وما يشمله اشتراكك» |
| Content correction | Content fixed after a report | Accountability | "We corrected a lesson you reported" | «صحّحنا درسًا أبلغت عنه» |

**Rules:** one reminder per day maximum; unsubscribe honoured immediately and completely (except transactional mail); every marketing email contains the reason the recipient is receiving it.

### 20.8 Learning progress reports

- **Learner-facing:** evidence-first, honest, includes what did *not* go well; never inflates; includes the next recommended action.
- **Shareable (learner-initiated only):** a one-page artefact summary the learner can send to a manager or a mentor — learner-authored descriptions, no auto-generated claims about employability, no TALIMGO superlatives.
- **Institutional (FUTURE):** cohort dashboards; only after Phase 4; must not become surveillance of individual learners without their knowledge.

### 20.9 Presentations and partnerships

- Decks must lead with the problem and the mechanism; include an explicit "what is not built yet" slide. This is a credibility advantage, not a weakness.
- Never include fabricated traction. If there are no users, say "pre-launch".
- Partnership conversations must not imply endorsement by any university, ministry, or company that has not signed an agreement.
- Any co-marketing involving learning claims requires the measurement protocol (DEC-021).

### 20.10 Channel priorities (PROPOSED)

| Priority | Channel | Why | Effort |
|---|---|---|---|
| 1 | Landing page + content that demonstrates the mechanism | Converts the curious; explains differentiated value | Medium |
| 2 | LinkedIn + build-in-public | Reaches practitioners and potential partners; builds credibility cheaply | Low |
| 3 | Short-form video demonstrations (AR/FR/EN) | Shows the plan adapting — the hardest thing to explain in text | Medium |
| 4 | University/community workshops (target markets) | Direct access to P1/P3/P4; interview pipeline | High |
| 5 | Paid acquisition | **Only after** retention and conversion evidence exists — otherwise it buys churn | High |

---

## 21. Brand-clearance report

> **Status: INCOMPLETE — and it must stay visibly incomplete until official searches are done by a qualified professional.** This section records exactly what was checked, what was found, what could **not** be checked, and what must happen next. **Nothing here constitutes legal advice, and nothing here establishes that TALIMGO is available, registrable, or free of conflict.**
> **Research date: 2026-10-10 (UTC).**

### 21.1 Headline findings

| Finding | Detail | Confidence |
|---|---|---|
| **A close-match education brand is live** | `taalimgo.com` serves a Moroccan education platform ("TaalimGo") covering nursery-to-AREF exam prep, QCM banks, offline mode, and teacher promotion material, with a free tier and a 20 DH/month paid tier, and a FAQ stating it is independent and not affiliated with the Moroccan Ministry of National Education [R1] | **High** (page read directly on 2026-10-10) |
| **The exact-match `.com` is registered and not serving content** | `talimgo.com` is registered (NameCheap, created 2025-11-20, expires 2026-11-20, registrar lock, privacy-protected registrant), uses Namecheap's default name servers, resolves to `46.101.135.177`, returned no retrievable page, and has **no** Wayback Machine captures [R2][R8][R41] — consistent with a parked/unconfigured registration | **High** for registration facts; **Medium** for the "parked" interpretation |
| **The TaalimGo domain is a recent registration** | `taalimgo.com` was registered 2026-09-18 via Cloudflare, expires 2027-09-18, on Cloudflare name servers [R3] — i.e. the live product's domain is new even though the brand appears established | **High** |
| **Several exact-name TLDs showed no registration record** | `.io`, `.app`, `.ai`, `.org` returned "object not found" from their registries' RDAP services on 2026-10-10 [R4][R5][R6][R7]. **This is not proof of availability:** it must be confirmed at a registrar, and premium/pending-delete status is not visible in RDAP. | **Medium** |
| **Some TLDs could not be checked** | `.net` and `.co` returned inconclusive registry responses; `.ma`, `.dz`, `.fr`, `.dev`, `.me`, `.store`, `gettalimgo.com`, and other variants were not checked | **n/a** |
| **Package names are free; the GitHub handle is not** | `talimgo` is unregistered on npm and PyPI [R40]; the GitHub username `talimgo` already exists (account created 2026-04-25, one public repository) [R9] | **High** |
| **An independent "TalimGo" project exists on GitHub** | `RayimqulovAbduvohid/TalimGo` (no licence file, last push 2025-12-25) [R10] — a small, unrelated project, but evidence that the coinage is not unique | **High** |
| **"Talim/Taalim" is a crowded root in the region** | Related names found: `taalim.ma` (Moroccan national distance-learning platform, referenced since 2020) [R31], `taalimtice.ma` (Moroccan Ministry ICT portal) [R32], `taalimai.ma` (a Moroccan AI-learning "super app") [R33]. "Taʿlīm" also means education/instruction in Arabic, Urdu, Uzbek and Turkish usage. | **High** (existence), **High** (semantic observation) |
| **A US-centric aggregator showed no "talimgo" marks** | A third-party trademark search aggregator returned zero results for "talimgo". This is **weak, non-authoritative evidence** and must not be relied on. | **Low** — treat as no evidence at all |

### 21.2 Why this matters (risk reasoning)

1. **Phonetic near-identity.** "TALIMGO" and "TaalimGo" are likely to sound identical in many accents and differ by one letter in writing. For consumer education services, that is a classic likelihood-of-confusion scenario.
2. **Same sector.** Both brands operate in education/learning/e-learning. Even if classes or goods differ in detail, the *relevant public* is the same audience.
3. **Weak inherent distinctiveness.** Because "talim/taalim" is descriptive of education in the region's languages, the **word alone is a poor foundation for exclusive rights**, both for TALIMGO and for TaalimGo. A descriptive-but-spelled-differently mark is generally the hardest kind to protect and the easiest to collide with.
4. **Timing asymmetry.** TaalimGo appears to be trading and has a recently registered domain; TALIMGO has no registered rights, no domain, and no public presence. If a formal filing or a public launch provokes a dispute, TALIMGO is likely to be the junior party.
5. **Geography asymmetry.** TaalimGo's visible market is Morocco. TALIMGO's proposed beachhead (Algeria/MENA) may reduce — but does not eliminate — coexistence risk, especially for online services, which are borderless, and for any future expansion into Morocco.

### 21.3 What could not be checked in this research (and why it must not be glossed over)

| Not checked | Why | Why it matters |
|---|---|---|
| **National trademark registers** — INAPI (Algeria), OMPIC (Morocco), and equivalent registers in other target markets | These require interactive/official searches; INAPI's prior-search service is a paid official service [R19], and aggregator databases are not authoritative | Only an official search establishes what is on the register, including marks that use similar-but-not-identical spellings |
| **WIPO Global Brand Database / Madrid designations** | Interactive search interface; not reliably automatable here | Madrid designations may confer protection in Algeria and Morocco without appearing in national aggregator data |
| **EUIPO / USPTO / UKIPO records** | Interactive search interfaces | Needed before serving or advertising in those markets |
| **Company-name registers** | Not checked | A registered company name can create separate (unfair-competition/trade-name) exposure |
| **Social media handle availability** | Most platforms block unauthenticated checks; only GitHub, npm and PyPI were verified | Handle collisions drive brand confusion and impersonation risk |
| **App-store listings** | TaalimGo's site links pointed to in-page anchors (`#download`) at the time of reading, so store listings could not be verified from the site [R1] | Store presence affects perceived establishment and search collisions |
| **Full domain-variant sweep** | Only the TLDs listed above were tested | Variant domains (`talim-go.com`, `gettalimgo.com`, etc.) affect phishing and confusion risk |
| **Common-law / unregistered rights** | Requires jurisdiction-specific legal analysis | In some systems, prior *use* of a confusingly similar name can create rights even without registration |

### 21.4 Recommended next steps (Phase 0, before any public brand asset is produced)

| # | Action | Owner | Output |
|---|---|---|---|
| 1 | Engage IP counsel with experience in Algeria and Morocco | Founder | Engagement letter; scope of searches; classes to search |
| 2 | Commission official searches: **INAPI** (Algeria), **OMPIC** (Morocco), **WIPO Global Brand Database** (Madrid designations designating DZ/MA and any other target), **EUIPO**, **USPTO** (if serving those markets) — covering **classes 9, 16, 35, 41, 42** and **similar spellings**, not only exact matches | Counsel | Written search reports |
| 3 | Commission a **similarity/confusion risk opinion** limited to the specific question: *can TALIMGO operate and register in the target markets without a material risk of opposition or infringement claims from TaalimGo and other "Talim" marks?* | Counsel | Opinion with a clear risk rating and recommended mitigations |
| 4 | Check **domain availability at a registrar** for the shortlist (a registrar check is authoritative for availability; RDAP alone is not) and decide DEC-002 | Founder | Registered domain(s) or an acquisition decision |
| 5 | Reserve **social handles and package names** consistently (GitHub org name needs an alternative — `talimgo` is taken) | Founder | Reserved handles; documented alternative |
| 6 | Define a **distinctiveness strategy**: composite mark (logotype + symbol) designed to be visually distinct from TaalimGo's presentation; avoid a red-and-white "education" look that increases confusion; avoid using the same tagline structures | Design + founder | Logo directions that pass the §9.4 acceptance criteria *including* the distinctiveness test |
| 7 | Run an **in-market confusion test**: show both brands to representative learners in the target market and ask what they think each is, and whether they think they are related | Research | Confusion findings that inform design and messaging |
| 8 | Prepare a **rename contingency**: a naming brief and a shortlist of 5–8 alternative coinages (checked for domain and basic availability) sufficient to switch quickly if counsel advises a blocking conflict | Founder | Confidential shortlist + criteria, stored with the decision record |
| 9 | Set up **monitoring**: domain/new-filing watches for the name and its variants; a documented trigger for re-running clearance if the brand expands into a new market | Counsel / ops | Watch service active |

**Naming contingency brief (in case DEC-001 resolves against TALIMGO).** Criteria for a replacement name: (a) short and pronounceable in Arabic, French and English; (b) not built on the descriptive "talim/taʿlīm" root; (c) distinctive and fanciful rather than descriptive; (d) predictable spelling on hearing it; (e) `.com` realistically obtainable; (f) no material collision in the education class; (g) passes the "say it on the phone once and it's spelled correctly" test. **Candidates are not listed here deliberately** — proposing unsearched invented names would create the exact false confidence this document forbids. Any shortlist must be produced *with* searches, not before them.

### 21.5 Guidance for the owner (plain language)

- **What is established:** a live education brand with a near-identical name exists in the region; the exact-match `.com` is registered by someone else; several other TLDs look unregistered but that must be confirmed at a registrar; the GitHub handle is taken; the "talim" root is crowded.
- **What is not established:** whether TALIMGO can be **registered** in Algeria, Morocco, the EU, the US, or anywhere else; whether a claim or opposition is likely; whether the two brands could coexist safely.
- **What this means practically:** continue planning and building **without** investing in irreversible brand assets (registered domains, printed materials, large paid campaigns, app-store listings) until step 3 above produces a written opinion. Use an internal codename in development if that de-risks engineering (a codename change is cheap; a public rebrand is not).
- **What is explicitly *not* recommended:** ignoring the conflict because the sectors "feel" different, assuming a `.com` will be purchasable, or treating the absence of a search-engine hit as clearance.

---

## 22. Research sources and references

**Research date for all sources: 2026-10-10 (UTC).** Sources are grouped by the purpose they served. Each entry states what it supports and how strong it is. Where a source is a secondary aggregator (review sites, price trackers, "best tools" roundups), that is stated explicitly — such sources were used for *market context*, never for legal, licensing, or financial conclusions.

### 22.1 Brand clearance and naming (primary and registry sources)

| ID | Source | What it supports | Strength |
|---|---|---|---|
| R1 | TaalimGo — https://www.taalimgo.com/ | The live Moroccan education platform: product lines (Kids/Élèves/Orientation/Concours/Pro), offline mode, QCM banks, 0 DH free tier, 20 DH/month (150 DH/year) tier, claimed "+20 000 inscrits", payment methods (CMI, Wafacash, Cash Plus, Google Play), and its FAQ statement that it is independent and not affiliated with the Moroccan ministry | **Primary** (read directly) |
| R2 | Verisign RDAP — https://rdap.verisign.com/com/v1/domain/talimgo.com | `talimgo.com` registration facts: created 2025-11-20, expires 2026-11-20, last changed 2026-03-10, registrar NameCheap, status clientTransferProhibited, NS `dns1/dns2.registrar-servers.com` | **Primary** (registry) |
| R3 | Verisign RDAP — https://rdap.verisign.com/com/v1/domain/taalimgo.com | `taalimgo.com` registration facts: created 2026-09-18, expires 2027-09-18, registrar Cloudflare, NS `dilbert/veda.ns.cloudflare.com` | **Primary** (registry) |
| R4 | Identity Digital RDAP — https://rdap.identitydigital.services/rdap/domain/talimgo.io | `talimgo.io`: "object not found" (no registration record) | Primary, but see §21.3 caveats |
| R5 | Google Registry RDAP — https://pubapi.registry.google/rdap/domain/talimgo.app | `talimgo.app`: "not found" | Primary |
| R6 | Identity Digital RDAP — https://rdap.identitydigital.services/rdap/domain/talimgo.ai | `talimgo.ai`: "object not found" | Primary |
| R7 | Public Interest Registry RDAP — https://rdap.publicinterestregistry.org/rdap/domain/talimgo.org | `talimgo.org`: "object not found" | Primary |
| R8 | whois.com record — https://www.whois.com/whois/talimgo.com | Registrant privacy service (Withheld for Privacy LLC), Lewes, Delaware; "Make offer" listing display | **Secondary aggregator** (corroborates R2) |
| R9 | GitHub REST API — https://api.github.com/users/talimgo and repository search for "talimgo"/"taalimgo" | The GitHub username `talimgo` exists (created 2026-04-25, one public repository); GitHub repository searches return `RayimqulovAbduvohid/TalimGo` and this project only; searches for "taalimgo" return zero repositories | **Primary** (API) |
| R10 | GitHub — https://github.com/RayimqulovAbduvohid/TalimGo | An unrelated "TalimGo" repository (no licence file; last push 2025-12-25) | **Primary** |
| R11 | Trademarkia search — https://www.trademarkia.com/search/trademarks?q=talimgo | Zero results for "talimgo" in a **US-centric commercial aggregator**. **Not authoritative, not a clearance search.** Recorded only to document what was checked | **Weak** |
| R19 | INAPI (Algeria) — https://e-services.inapi.org/ and the INAPI services pages | That INAPI offers official trademark prior searches and filings (the route for Algerian clearance), and that prior-art searches are a paid official service | **Primary** (authority website) |
| R31 | Morocco World News (2020) — https://www.moroccoworldnews.com/2020/03/71906/morocco-launches-digital-learning-platform-amid-coronavirus-lockdown/ | Existence and context of Morocco's `taalim.ma` learning platform | **Secondary (journalism)** |
| R32 | Research article on the Moroccan ICT portal — https://www.researchgate.net/publication/360288267_Teachers'_Perception_of_the_Moroccan_ICT_Portal_of_the_Ministry_of_Education | Existence and usage of `taalimtice.ma` | **Secondary (academic)** |
| R33 | TaalimAI — https://taalimai.ma/ | A live Moroccan "AI educational super app" using a "Taalim" name — indicates a crowded, AI-active regional naming space | **Primary** (site read directly) |
| R40 | npm registry — https://registry.npmjs.org/talimgo ; PyPI — https://pypi.org/pypi/talimgo/json | `talimgo` is **not** registered as an npm package or a PyPI package (HTTP 404 on both, 2026-10-10) | **Primary** (registry) |
| R41 | Internet Archive — https://web.archive.org/web/2026/https://talimgo.com/ | The Wayback Machine has **no captures** of `talimgo.com`, consistent with a site that has never served public content | **Primary** (archive query) |

**Additional note for R1:** during the 2026-10-10 reading, TaalimGo's "download" links pointed to in-page anchors (`#download`) and to placeholder links, so its Google Play / App Store listings could not be verified from the site itself.

### 22.2 Competitive landscape sources

| ID | Source | What it supports | Strength |
|---|---|---|---|
| R20 | Coursera pricing coverage (2026): https://www.myengineeringbuddy.com/blog/coursera-reviews-alternatives-pricing-offerings/ · https://www.fastlancer.org/en/fastlancer-blog/coursera-review/ · https://thepivotwave.com/blog/coursera-plus-review/ | Coursera Plus ≈ $59/mo or $399/yr; per-course $49–99; programmes $39–79/mo; Coursera Coach as an in-course AI guide; degrees excluded | **Secondary** (multiple independent trackers agreeing; Coursera's own `/pricing` page returned a 404 during research) |
| R28 | Khanmigo coverage (2026): https://toolcurrent.com/tools/khanmigo · https://www.zenfixai.com/tools/khanmigo · https://www.buildmvpfast.com/blog/ai-tutoring-khanmigo-case-study-2026 | Khanmigo ≈ $4/mo or $44/yr for learners/parents; free for teachers; Socratic design; district pricing reported inconsistently (~$10–35/student/year) | **Secondary** (sources disagree on district pricing — flagged) |
| R29 | Duolingo coverage (2026): https://www.myengineeringbuddy.com/blog/duolingo-reviews-pricing-alternatives-2026/ · https://aitoolsofthetrade.com/reviews/duolingo-max · https://www.gamsgo.com/blog/super-duolingo-subscription-worth-it-2025 | Super ≈ $12.99/mo (~$84–96/yr); Max ≈ $29.99/mo (~$168/yr); "Explain My Answer" became free in January 2026; AI conversation features limited to a subset of courses | **Secondary** (consistent across sources; some report Super/Max migration changes) |
| R30 | Brilliant coverage (2026): https://makeheadway.com/blog/brilliant-review/ · https://nibble-app.com/blog/is-brilliant-free · https://beginnersinai.org/brilliant-explained/ · https://aisotools.com/pricing/brilliant | Free tier with daily limits; Premium reported across a wide range (~$12.49–27.99/mo; ~$150–240/yr); free premium for K-12 educators; AI tutor ("Koji") | **Secondary** — sources disagree materially; treat all figures as unverified |
| R34 | Udemy coverage (2026): https://www.ruzuku.com/learn/articles/compare-udemy · https://course.careers/blog/best-udemy-courses · https://tabswire.com/udemy-personal-plan-review/ | Marketplace model with per-course lifetime access; Personal Plan ≈ $16.99–32/mo, ~$156–168/yr, regionally variable; reported instructor revenue shares (37% marketplace / 15% subscription pool) | **Secondary** (the competitor's own comparison page; revenue-share figures are third-party analyses) |
| R35 | Codecademy pricing coverage (2026): https://promaxreviews.com/is-codecademy-worth-it/ · https://skillvlora.com/vs/datacamp-vs-codecademy | Basic free; Plus ≈ $14.99/mo annual ($179.88/yr) or $29.99 monthly; Pro ≈ $19.99/mo annual ($239.88/yr) or $39.99 monthly; AI assistant available on free tier | **Secondary** (consistent across two sources) |
| R12 | https://glasp.co/articles/ai-study-modes-compared | Learning modes in ChatGPT (Study Mode), Gemini (Guided Learning), Claude (Learning Mode): capabilities, availability, and free access; comparative pedagogy | **Secondary** (comparative review) |
| R13 | https://cybernews.com/ai-tools/gemini-guided-learning-vs-chatgpt-study-mode/ | Head-to-head behaviour of Gemini Guided Learning and ChatGPT Study Mode (scaffolding, visuals, hints, knowledge checks) | **Secondary** |
| R14 | https://theairankings.com/best-ai-for-students/ | Study Mode free for logged-in users; Gemini Guided Learning free tier; student pricing changes in 2026 | **Secondary** |
| R33 | https://taalimai.ma/ | Regional AI-learning competitor context (Morocco) | **Primary** |

### 22.3 Learning-science and efficacy evidence

| ID | Source | What it supports | Strength |
|---|---|---|---|
| R21 | Karpicke, J. D. — *Retrieval-based learning* review (PDF): https://learninglab.psych.purdue.edu/downloads/2025/2025_Karpicke_Retrieval_Based_Learning_Review.pdf | Retrieval practice effect size (Rowland 2014 meta-analysis: g ≈ 0.50 across 159 studies; 81% favouring retrieval); spacing effect (g ≈ 0.74 across 39 effect sizes); no meaningful difference between expanding and equal spacing (g ≈ 0.03); larger effects at retention intervals > 1 day (g ≈ 0.69) | **Peer-reviewed review** |
| R22 | Karpicke & Roediger (2008), *The Critical Importance of Retrieval for Learning*: https://www.researchgate.net/publication/5574966_The_Critical_Importance_of_Retrieval_for_Learning | Repeated testing beats repeated studying; learners' predictions of their own performance are poorly correlated with actual performance (the core justification for measurement over self-report) | **Peer-reviewed** |
| R23 | Bloom's 2-sigma problem (overview): https://en.wikipedia.org/wiki/Bloom%27s_2_sigma_problem | The 1984 tutoring + mastery-learning result (~2σ), the ~1σ mastery-learning component, and the alterable-variable framing | **Tertiary** (encyclopaedic summary of a peer-reviewed paper) |
| R24 | Education Next — *Two-Sigma Tutoring: Separating Science Fiction from Science Fact*: https://www.educationnext.org/two-sigma-tutoring-separating-science-fiction-from-science-fact/ | Why 2σ is a ceiling observed under ideal conditions, not a reproducible norm; typical tutoring effects (~0.33σ in an earlier meta-analysis); mastery-learning gains (~1.1σ) separate from tutoring | **Secondary (expert analysis with primary citations)** |
| R25 | npj Science of Learning (2025) — systematic review of AI-driven ITS in K-12: https://www.nature.com/articles/s41539-025-00320-7 | ITS vs teacher-led instruction effects; VanLehn's human-tutoring estimate (d ≈ 0.79) and step-based ITS (d ≈ 0.75–0.80); the "interaction plateau" framing | **Peer-reviewed** |
| R26 | Kulik & Fletcher — meta-analysis of ITS effectiveness: https://www.researchgate.net/publication/277636218_Effectiveness_of_Intelligent_Tutoring_Systems_A_Meta-Analytic_Review | Median ES ≈ 0.66 over 50 evaluations; large effects on locally developed tests but small on standardised tests (e.g. Cognitive Tutor: 0.76 local vs 0.12 standardised) — the basis for TALIMGO's claim-discipline rules | **Peer-reviewed** |
| R27 | Leite et al. (2025) — *Do intelligent tutoring systems benefit K-12 students?*: https://arxiv.org/abs/2511.04997 | A more modest, recent K-12 meta-analytic estimate (g ≈ 0.271) and moderators (worked examples, duration, immediate measurement) — evidence that effect sizes shrink with stricter designs | **Preprint (peer review status to confirm)** |
| R15 | UNESCO — *Governments must quickly regulate Generative AI in schools* (2023): https://www.unesco.org/en/articles/unesco-governments-must-quickly-regulate-generative-ai-schools | Minimum age recommendation of 13 for generative-AI use in classrooms; seven regulatory steps; fewer than 10% of surveyed institutions had AI policies | **Primary (official guidance announcement)** |

### 22.4 Regulation, standards, and accessibility

| ID | Source | What it supports | Strength |
|---|---|---|---|
| R16 | EU AI Act timeline sources: https://www.joneswalker.com/en/insights/blogs/ai-law-blog/yes-august-2-still-matters-the-eu-approved-a-high-risk-ai-delay-but-most-trans.html · https://www.softwareimprovementgroup.com/blog/eu-ai-act-summary/ · https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-ai-act-high-risk-compliance-deadline-20/ | Education is an Annex III high-risk category; the Digital Omnibus reportedly deferred Annex III high-risk obligations to 2 December 2027 and Annex I to 2 August 2028, while Article 50 transparency duties applied from 2 August 2026 | **Secondary (law-firm and consultancy analyses)** — must be confirmed against the Official Journal and counsel |
| R17 | Algeria data protection: https://cms.law/en/int/expert-guides/cms-expert-guide-to-data-protection-and-cyber-security-laws/algeria2 · https://www.dlapiperdataprotection.com/guide.pdf?c=DZ | Law No. 18-07 (2018) and its 2025 amendment: ANPDP declarative/authorisation regime, cross-border transfer conditions, children's data requiring legal-representative consent, and penalties | **Secondary (law-firm guidance)** |
| R18 | Morocco data protection: https://cms.law/en/int/expert-guides/cms-expert-guide-to-data-protection-and-cyber-security-laws/morocco · https://neoexpertise.net/law-09-08-explained-moroccos-data-protection-law-for-businesses/ | Law No. 09-08: CNDP declaration/authorisation, cross-border transfer authorisation, parental consent, sensitive-data rules, and the absence of a general breach-notification duty | **Secondary (law-firm guidance)** |
| R36 | WCAG 2.2: https://accessible-eu-centre.ec.europa.eu/content-corner/news/wcag-22-officially-w3c-recommendation-2023-10-06_en · https://www.w3.org/TR/WCAG22/ · https://blog.usablenet.com/wcag-2.2 | WCAG 2.2 is a W3C Recommendation (2023) adding nine success criteria (target size 24×24 CSS px, dragging movements, focus visibility, consistent help, redundant entry, accessible authentication) and removing 4.1.1 Parsing | **Primary (W3C via AccessibleEU) + secondary explainer** |
| R37 | Interoperability standards: https://www.imsglobal.org/spec/qti/v3p0/oview (QTI 3.0, 1EdTech Final Release, 1 May 2022) · https://www.forasoft.com/learn/elearning-video/articles-elearning/scorm-vs-xapi-vs-cmi5-vs-lti (SCORM 2004 4th Ed., xAPI 1.0.3, cmi5, LTI 1.3 references) · https://adlnet.gov/projects/scorm/ · https://github.com/adlnet/xAPI-Spec | The standards TALIMGO should target for item portability (QTI 3.0) and learning records/interoperability (xAPI, SCORM, cmi5, LTI 1.3) | **Primary (specification sites) + secondary explainer** |

### 22.5 Cost model inputs (weak by nature)

| ID | Source | What it supports | Strength |
|---|---|---|---|
| R38 | LLM price trackers (2026): https://favtray.com/blog/llm-api-pricing-comparison-2026 · https://iternal.ai/llm-pricing-calculator · https://benchr.org/articles/ai-model-pricing-comparison | Order-of-magnitude token price bands: budget/light ≈ $0.10–0.75 in / $0.40–3.75 out per 1M tokens; mid-tier ≈ $1.25–3.00 in / $2.50–15.00 out; frontier ≈ $2–15 in / $10–75 out | **Weak** — trackers disagree on model names and prices, and vendor pricing changes frequently. **Verify against each vendor's official pricing page before any financial modelling.** |

### 22.6 Open-source verification data (primary API reads)

| ID | Source | What it supports | Strength |
|---|---|---|---|
| R39 | GitHub REST API repository endpoints (`/repos/{owner}/{repo}`) read on 2026-10-10 for: `openedx/openedx-platform`, `moodle/moodle`, `instructure/canvas-lms`, `sakaiproject/sakai`, `learningequality/kolibri`, `learningequality/studio`, `frappe/lms`, `oppia/oppia`, `chamilo/chamilo-lms`, `adaptlearning/adapt_authoring`, `h5p/h5p-php-library`, `ankitects/anki`, `open-spaced-repetition/fsrs4anki`, `open-spaced-repetition/ts-fsrs`, `langfuse/langfuse`, `BerriAI/litellm`, `vllm-project/vllm`, `promptfoo/promptfoo`, `vibrantlabsai/ragas`, `danielmiessler/Fabric`, `rsms/inter`, `IBM/plex`, `notofonts/noto-fonts` | Licence identifiers (`spdx_id`), stars, last-push dates, release tags, and archived status for each candidate (§14) | **Primary for metadata** — but the API-reported licence is **not** sufficient for reuse decisions; the licence file and any enterprise directories must be read before adoption |

### 22.7 Method, limitations, and honesty about what this research is not

| Limitation | Explanation | Consequence for readers |
|---|---|---|
| **No official trademark register was queried** | The search interfaces involved (WIPO Global Brand Database, EUIPO, USPTO, OMPIC, and INAPI's paid official search service) require interactive or paid access that could not be executed in this environment | **Trademark status is unknown.** §21.4 lists the required searches. Do not treat any section of this document as clearance |
| **No proprietary tools were used** | No paid trademark databases, no market-research panels, no app-intelligence tools | The competitive picture is necessarily approximate |
| **Pricing data is secondary and volatile** | Prices were taken from third-party trackers where vendor pages were unreachable (for example, Coursera's `/pricing` page returned 404 during research) | All prices are labelled UNVERIFIED; verify before use |
| **JavaScript-rendered sources may be under-represented** | The page-fetching method used here may not execute client-side JavaScript | Some product pages, store listings, and dashboards could not be inspected |
| **Page content can change after the research date** | Everything was read on 2026-10-10 | Re-verify anything material before acting on it |
| **No primary user research was conducted** | All audience, pricing, and behaviour claims are hypotheses | Phase 0 exists precisely to replace them with evidence |
| **Effect sizes are context-specific** | The learning-science literature is clear that effects shrink outside ideal conditions and on independent measures [R26][R27] | TALIMGO must never market an effect size |

---

## 23. Glossary

| Term | Definition as used in this document |
|---|---|
| **Adaptation** | A change to a learner's plan driven by new evidence or circumstances (accelerate, remediate, reschedule, re-scope, change goal) — see §6.3.5. |
| **Assessment** | A structured measurement against a stated learning objective; the only activity that can create mastery evidence. |
| **Baseline assessment** | An assessment of the *target* skill taken early, used to make later improvement comparable. |
| **Capability** | What a learner can demonstrably do, as opposed to what they have been exposed to. |
| **Concept** | The atomic unit of the skill graph: a single thing that can be learned and evidenced. |
| **Confidence (of an estimate)** | How much evidence supports a mastery estimate (high/moderate/low/unknown/conflict) — not the learner's self-confidence. |
| **Curriculum graph** | The validated network of concepts and prerequisite edges that the roadmap generator is constrained to follow. |
| **Delayed evidence** | Evidence collected at least three days after the first success (and, for mastery, usually much longer). |
| **Diagnostic** | The onboarding assessment used to place the learner, combining items and (where available) practical tasks. |
| **Estimate** | Any predicted figure (time, duration, date). Always labelled as an estimate in the UI and never presented as a measurement. |
| **Evidence (learning evidence)** | A recorded, attributable observation of learner performance (item result, artefact, project outcome) that can support a mastery statement. |
| **Evidence hierarchy** | The ranking of evidence strength: assisted < unassisted < repeated unassisted < transfer (§6.2.1). |
| **FSRS** | Free Spaced Repetition Scheduler — a modern spaced-repetition algorithm family; candidate scheduling engine (§14.4). |
| **Grounding** | Constraining generated answers to retrieved, stored curriculum context rather than model memory. |
| **Hint ladder** | The three-level help protocol: strategy nudge → partial step → full solution only after an attempt or explicit request. |
| **Inference cost** | The cost of running model calls, measured per feature, per learner, and per month (§12.4). |
| **Item** | A single assessment question or task with a verified answer key or rubric. |
| **Learning path** | A curated, prerequisite-checked route toward a goal within a subject; contains modules. |
| **Mastery estimate** | A probabilistic statement about demonstrated capability, carrying evidence, confidence, and a last-evidenced date. |
| **Milestone** | A visible checkpoint that requires evidenced capability; the primary unit of meaningful progress. |
| **Mission (daily mission)** | The generated day plan: review, new learning, practice, assessment, or project work, each with an objective and completion condition. |
| **Module** | A thematic cluster of lessons with its own assessment. |
| **MVP (Phase 1)** | The first release: goal → plan → learn → practise → build → measure → adapt, complete for three launch paths, in EN + AR. |
| **Prerequisite repair** | A pre-authored remediation module inserted when the evidence shows a blocker; capped at one layer per adaptation cycle. |
| **Prompt injection** | Attempts to make a model follow instructions embedded in untrusted content; treated as a security class, not a content class. |
| **Rubric** | Published criteria and levels used to assess project work; AI scoring is advisory and disputable. |
| **Skill graph** | The learner-specific instantiation of the curriculum graph with mastery states and evidence. |
| **Spaced repetition** | Scheduling reviews over increasing intervals; supported by retrieval-practice evidence [R21]. |
| **Transfer evidence** | Evidence from applying a skill in a new context (e.g. a project), required for the "evidenced" mastery state. |
| **Tutor** | TALIMGO's curriculum-grounded AI tutoring function (distinct from planning, assessment, and general chat). |
| **Untrusted content** | Any text not authored by TALIMGO: learner input, uploaded files, pasted text, imported resources — always treated as data, never as instructions. |

---

## 24. Implementation-readiness checklist

Use this as a gate list. An item is only "done" when its evidence exists — not when someone believes it is done.

### 24.1 Brand and legal (blocks any public asset)

- [ ] Trademark clearance searches completed in the launch jurisdictions (INAPI, OMPIC, and any market served) for classes 9, 16, 35, 41, 42 — **written report**
- [ ] Similarity/confusion opinion obtained, with a documented risk rating — **DEC-001 resolved**
- [ ] Primary domain registered and controlled; defensive variants decided — **DEC-002 resolved**
- [ ] Social handles and package names reserved (GitHub org alternative identified, since `talimgo` is taken)
- [ ] Composite mark designed and checked for visual distinctiveness against existing "Taalim" marks
- [ ] In-market brand confusion test conducted with representative learners
- [ ] Rename contingency shortlist produced with basic availability checks
- [ ] Monitoring/watch service active for filings and domain registrations

### 24.2 Product definition

- [ ] Onboarding spec frozen with ≤ 12 justified questions
- [ ] Curriculum graph for the three launch paths authored and peer-reviewed
- [ ] Mastery model documented, unit-tested, and reviewed against expert ratings (≥ 50 learner records)
- [ ] Adaptation rules (§6.3.5) implemented with learner-visible rationales
- [ ] Daily-mission and recovery flows tested with real learners
- [ ] Project + rubric templates exist for every launch-path milestone
- [ ] Notification policy implemented and auditable (§13.6)
- [ ] Dashboard renders goal / next action / progress / blockers in the specified priority order — **design review passed**

### 24.3 Content and quality

- [ ] Authoring templates published; authors trained
- [ ] Subject reviewers contracted for every launch path
- [ ] G1–G6 gates operational with written evidence per module
- [ ] Item bank: 100% of auto-graded items have verified keys and explanations
- [ ] Licence register live for every external resource, with link-check automation
- [ ] Citation standard applied; sampling audit passed
- [ ] Content versioning, correction, retirement and archive flows tested
- [ ] Content-report triage queue with published SLAs

### 24.4 AI quality and safety

- [ ] Evaluation suite (§11.1.3) implemented and passing its minimum bars
- [ ] Prompt-injection red-team suite passes with **zero** instruction-following successes
- [ ] Cross-learner leakage test harness passes with **zero** leaks
- [ ] Claim filter active with zero blocked-pattern outputs in the test set
- [ ] Fabricated-citation rate measured at **zero**
- [ ] Human-review path operational for disputes and high-stakes assessments
- [ ] Safety escalation protocol documented, staffed, and tested (minors, self-harm, harmful content)
- [ ] Incident logging and monthly quality reporting in place

### 24.5 Privacy, security, and compliance

- [ ] Data inventory complete; retention schedule enforced
- [ ] Granular consents implemented; optional processing can be declined without degrading learning
- [ ] Export (≤ 24h) and deletion (≤ 30 days) verified end-to-end
- [ ] Age policy implemented technically and documented publicly — **DEC-005 resolved**
- [ ] Legal mapping completed for each launch market (declaration/authorisation, transfers, children)
- [ ] Encryption in transit and at rest verified; secrets managed; no PII in logs
- [ ] Admin MFA, RBAC, and audit logging verified
- [ ] Penetration test completed with no unresolved high/critical findings
- [ ] Incident-response runbook reviewed; tabletop exercise completed

### 24.6 Accessibility and localisation

- [ ] WCAG 2.2 AA audit passed (automated + manual + external)
- [ ] EN and AR complete, with no hard-coded strings
- [ ] RTL visual regression suite green for every component
- [ ] Arabic typography reviewed by native speakers (line height, size, tracking, numerals)
- [ ] Screen-reader passes on at least two platforms
- [ ] Low-bandwidth mode tested on a throttled mobile profile

### 24.7 Business and operations

- [ ] Pricing research completed; price points decided — **DEC-008 resolved**
- [ ] Free-tier limits sized against measured inference cost — **DEC-009 resolved**
- [ ] Local payment routes tested per launch market — **DEC-013 resolved**
- [ ] Entitlement checks verified server-side; one-step cancellation verified
- [ ] Cost dashboards live (per learner, per feature, per month)
- [ ] Support channels and SLAs operating
- [ ] Backups and a completed restore drill
- [ ] On-call/escalation rotation defined

### 24.8 Measurement

- [ ] Every P0 requirement has instrumentation specified before build
- [ ] Outcome-measurement instruments (equivalent pre/post items) versioned per launch path — **DEC-021 resolved**
- [ ] Engagement and outcome metrics reported in separate columns, never blended
- [ ] AI-quality and content-error metrics reported monthly to the owner

---

## 25. Appendices

### Appendix A — Proposed design tokens

Illustrative implementation guidance (PROPOSED; the authoritative source becomes the design system repository once DEC-012 is decided).

```css
:root {
  /* Colour — light mode */
  --color-ink: #111318;            /* primary text, dark surfaces */
  --color-brand: #D92D20;          /* brand, primary actions, progress */
  --color-brand-bright: #F04444;   /* non-text accents only */
  --color-brand-strong: #B42318;   /* destructive / small critical text */
  --color-danger-text: #B42318;
  --color-surface: #FFFFFF;
  --color-canvas: #F9FAFB;
  --color-text-secondary: #667085;
  --color-border: #EAECF0;
  --color-success: #067647;
  --color-warning: #B54708;

  /* Typography */
  --font-latin: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-arabic: "IBM Plex Sans Arabic", "Noto Sans Arabic", "Segoe UI", Tahoma, sans-serif;
  --font-code: "JetBrains Mono", "IBM Plex Mono", ui-monospace, monospace;

  --text-body-md: 1rem;      --leading-body-md: 1.6;
  --text-body-lg: 1.125rem;  --leading-body-lg: 1.6;   /* Arabic: use 1.75+ */
  --text-caption: 0.75rem;   --leading-caption: 1.45;

  /* Spacing (4px base) */
  --space-1: 4px; --space-2: 8px;  --space-3: 12px; --space-4: 16px;
  --space-5: 20px; --space-6: 24px; --space-8: 32px; --space-10: 40px;
  --space-12: 48px; --space-16: 64px;

  /* Radius, borders, elevation */
  --radius-sm: 6px; --radius-md: 10px; --radius-lg: 16px;
  --border-hairline: 1px; --border-focus: 2px;
  --shadow-1: 0 1px 2px rgba(16,24,40,.06);
  --shadow-2: 0 4px 8px -2px rgba(16,24,40,.10), 0 2px 4px -2px rgba(16,24,40,.06);
  --shadow-3: 0 12px 16px -4px rgba(16,24,40,.08), 0 4px 6px -2px rgba(16,24,40,.03);

  /* Motion */
  --motion-fast: 120ms; --motion-base: 200ms; --motion-slow: 320ms;
  --ease-enter: cubic-bezier(.2,0,0,1);

  /* Breakpoints (documentation tokens; media queries in practice) */
  --bp-sm: 480px; --bp-md: 768px; --bp-lg: 1024px; --bp-xl: 1280px; --bp-2xl: 1536px;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-canvas: #0B0D12;
    --color-surface: #111318;
    --color-surface-raised: #171A21;
    --color-border: #262B36;
    --color-text-primary: #F2F4F7;
    --color-text-secondary: #98A2B3;
    --color-brand: #F04444;   /* text/icon use on dark */
  }
}

@media (prefers-reduced-motion: reduce) {
  :root { --motion-fast: 0ms; --motion-base: 0ms; --motion-slow: 0ms; }
}
```

**Verified contrast pairs (computed 2026-10-10):** see §9.2.4. Re-verify after any change.

---

### Appendix B — Worked example: one launch learning path

**Path:** Python Programming Foundations (illustrative, PROPOSED — not approved, not authored).
**Learner assumption for this example:** 4 hours/week, 20-minute sessions, no programming experience, goal "automate my invoicing and learn to build small tools".

| Milestone | Outcome | Modules | Concepts (subset) | Practice | Assessment | Project |
|---|---|---|---|---|---|---|
| **M1 — Working with data** (≈ 5 weeks) | Read, transform and print real data from a file | Setup & environment; Variables & types; Control flow; Functions; Files | variable, type conversion, conditionals, loops, function, parameter, return value, file read/write, error message reading | Retrieval items per concept; 3 guided exercises; debugging drills | Module checks (unassisted, ≥ 80%) + one delayed review | **Invoice reader:** read a CSV of invoice lines, total them, print a summary |
| **M2 — Structuring a small program** (≈ 6 weeks) | Organise code so it can grow without breaking | Data structures; Modules & imports; Errors & testing; Intro to APIs | list, dict, comprehension, module, exception, unit test, HTTP request, JSON parsing | Exercises with test cases; refactoring tasks; API-consumption exercise (mock endpoint) | Module checks + M2 project rubric | **Expense tracker CLI:** persists data to a file, validated inputs, tests for the core logic |
| **M3 — Shipping something useful** (≈ 7 weeks) | Build and share a small working tool | Working with libraries; Version control workflow; Packaging & distribution; Documentation | dependency, virtual environment, git commit/branch, README, script arguments, basic packaging | Guided project increments; code review by rubric; peer-style self-review | Milestone assessment: rubric on the deployed artefact | **Capstone — invoicing helper:** a tool the learner actually uses, with a README, tests, and instructions a non-programmer can follow |

**Example generated daily mission (Day 12 of the path):**

> **Today · 20 minutes · Loops, part 2**
> 1. **Warm-up (4 min):** 5 retrieval items on `for` vs `while` (2 due from yesterday).
> 2. **Learn (7 min):** "Looping over collections safely" — with a worked example and one comparison to the `while` version you already know.
> 3. **Practise (9 min):** 3 exercises: sum a list without `sum()`, find the longest word, stop a loop on a sentinel value.
> **Completion condition:** all three exercises attempted; at least two passing without hints.
> **Why now:** milestone 1's project needs you to iterate over invoice rows — this is the exact skill.
> *Estimated time: 20 minutes. Estimates are based on learners at your level and may differ.*

**Example rubric extract (M3 capstone, per criterion):**

| Criterion | Not yet | Developing | Meets | Exceeds |
|---|---|---|---|---|
| **Works as described** | Crashes on the documented example | Runs with manual fixes | Runs on the provided example data without intervention | Handles malformed input with a clear message |
| **Code clarity** | No functions; unexplained names | Some structure; inconsistent naming | Functions with descriptive names; comments where logic is non-obvious | Clear separation of concerns; a reader can extend it easily |
| **Tests** | No tests | One happy-path test | Core logic covered by passing tests | Includes an edge case that previously broke it |
| **Documentation** | None | Bullet notes | README with setup and usage | README a non-programmer could follow, with an example output |
| **Honesty of scope** | Claims features that do not work | Partially describes limitations | Accurately describes what it does and does not do | Documents known limitations with a "next steps" note |

---

### Appendix C — Example data objects (illustrative, not final schema)

Plan object (illustrative shape; the real schema is decided in DEC-007 and validated per §6.3.3):

```json
{
  "plan_id": "plan_01H...",
  "learners_id": "usr_01H...",
  "goal": {
    "goal_id": "goal_01H...",
    "statement": "Build and deploy three responsive web apps.",
    "success_criteria": ["Deploy to a public URL", "Explain the code without notes"],
    "target_date": "2027-03-01",
    "target_date_is_estimate": true
  },
  "constraints": {
    "hours_per_week": 4,
    "session_minutes": 20,
    "unavailable_days": ["sat"]
  },
  "milestones": [
    {
      "milestone_id": "ms_1",
      "title": "First deployed page",
      "estimated_hours": { "min": 12, "max": 18, "is_estimate": true },
      "outcome": "A responsive page live on a public URL",
      "prerequisites": ["concept.html_structure", "concept.css_box_model"],
      "modules": ["mod_html_basics", "mod_css_layout"],
      "project_id": "prj_landing_page",
      "assessment_id": "asm_ms1_check",
      "completion_criteria": "Project rubric >= Meets on all criteria; module checks passed unassisted"
    }
  ],
  "generation": {
    "engine_version": "roadmap-v0.1",
    "curriculum_version": "curriculum-2026.10",
    "validation": { "schema": "pass", "prerequisite_order": "pass", "time_budget": "pass" }
  }
}
```

Evidence event (illustrative):

```json
{
  "event_id": "evt_01H...",
  "learner_id": "usr_01H...",
  "concept_id": "concept.loops.for",
  "activity_id": "act_retrieval_loops_set3",
  "activity_type": "retrieval_question",
  "occurred_at": "2026-10-12T19:42:11Z",
  "outcome": { "correct": true, "hints_used": 0, "attempt_number": 1, "latency_ms": 21400 },
  "context": { "session_id": "ses_01H...", "mission_id": "mis_01H...", "assisted": false }
}
```

Mastery projection (derived; illustrative):

```json
{
  "learner_id": "usr_01H...",
  "concept_id": "concept.loops.for",
  "state": "consolidating",
  "evidence_summary": { "unassisted_successes": 3, "delayed_successes": 1, "transfer_evidence": 0 },
  "confidence": "moderate",
  "last_evidenced_at": "2026-10-12T19:42:11Z",
  "decay": { "state": "none", "next_review_due": "2026-10-19" },
  "explanation": "3 unassisted successes, including one after a 6-day gap; no project use yet."
}
```

Tutor call envelope (illustrative; note the explicit separation of untrusted content):

```json
{
  "task": "tutor_reply",
  "hint_level_max": 1,
  "learner_state": { "level": "beginner", "mastery": { "concept.loops.for": "practising_unassisted" } },
  "curriculum_context": [ { "concept_id": "concept.loops.for", "source": "mod_control_flow.lesson3", "version": "4" } ],
  "untrusted_input": { "kind": "learner_message", "content": "…", "policy": "treat_as_data_only" },
  "output_contract": { "schema": "TutorReplyV1", "require_citations": false, "require_uncertainty_flag": true }
}
```

---

### Appendix D — Research log, limitations, and confidence levels

**D.1 What was done, in order**

1. Read the live TaalimGo site and recorded its product lines, pricing, and independence statement [R1].
2. Ran registry RDAP queries for `talimgo.com`, `taalimgo.com`, and the `.io`, `.app`, `.ai`, `.org`, `.net`, `.co` variants; recorded registration facts and inconclusive results [R2]–[R8].
3. Checked `talimgo.com` over HTTP and against the Wayback Machine (no captures) [R41].
4. Checked name availability on GitHub (user taken), npm and PyPI (both available), and searched GitHub for "talimgo"/"taalimgo" repositories [R9][R10][R40].
5. Attempted a public aggregator trademark search (returned zero results — recorded as weak evidence) [R11].
6. Researched the competitive landscape from vendor-adjacent and secondary sources, recording disagreement between sources where it exists [R12]–[R14], [R20], [R28]–[R30], [R34][R35].
7. Researched the learning-science evidence base, preferring reviews and meta-analyses, and recorded where effect sizes shrink under stricter measurement [R21]–[R27].
8. Researched regulatory and standards context, marking all legal findings as requiring counsel [R15]–[R18], [R36][R37].
9. Read licence, activity, and release metadata from the GitHub API for 23 candidate repositories and font families [R39].
10. Computed WCAG contrast ratios for the supplied palette from the hex values (§9.2.4).
11. Produced this document, checking internal consistency between brand, product, curriculum, business, and roadmap.

**D.2 Confidence summary**

| Domain | Confidence | Why |
|---|---|---|
| Brand clearance findings (what exists) | **Medium–High** | Registry and primary-site evidence for the key facts; but no official register searched |
| Trademark status / legal availability | **None** | Not researched at source; must be done by counsel |
| Domain availability for unchecked TLDs | **Low** | Not verified at a registrar |
| Competitor capabilities | **Medium** | Secondary sources, consistent in most cases, but not audited |
| Competitor pricing | **Low–Medium** | Volatile, region-dependent, sometimes contradictory |
| Learning-science evidence | **High** | Peer-reviewed reviews and meta-analyses, with their limitations recorded |
| Regulatory statements | **Low–Medium** | Secondary legal summaries; jurisdiction-specific duties differ and change |
| Open-source licences/activity | **High** for metadata; **Low** for reuse decisions | API metadata is authoritative for metadata only; reuse requires reading licence files and legal review |
| AI cost model | **Low** | Price trackers disagree; based on 2026 rates that change frequently |
| Audience, pricing, retention hypotheses | **Very Low** | Deliberately labelled as hypotheses; no primary research conducted |

**D.3 Claims in this document that must be re-verified before they are relied upon**

1. Every price in §4.3 and §12 (verify at vendor checkout pages, in the target market and currency).
2. Every domain status in §21 (verify at a registrar; RDAP absence is not availability).
3. Every trademark conclusion (there are none in this document — and that is deliberate).
4. The EU AI Act timeline in §11.3.3 (confirm the Digital Omnibus outcome and the operative dates with counsel).
5. Algeria/Morocco data-protection duties, including transfer authorisations (confirm with local counsel).
6. AI token prices and the resulting cost-per-learner model (verify against vendor pricing pages).
7. The reported availability and limits of competitor AI features (they changed twice during 2025–2026).
8. Font licensing per package/version before bundling.

**D.4 Open research tasks handed to Phase 0**

- 25–40 learner interviews across P1/P3/P4 in at least two target markets (language-appropriate).
- Price-sensitivity and willingness-to-pay study.
- Official trademark clearance (counsel) in the launch jurisdictions.
- Registrar-level domain checks and acquisition decisions.
- Payment-route research per market.
- Technical spike: RTL component + grounded tutor + mastery recomputation + generated-plan validation.
- Authoring cost measurement for one full path.
- Accessibility baseline audit of the prototype.
- Psychometric review of the outcome-measurement instruments.

---

**End of document.**

*This document is a specification and research record, not a commitment. Where it is uncertain, it says so; where it proposes, it is labelled; where it is silent, nothing has been built. The next editor's obligation is to keep it that honest.*
