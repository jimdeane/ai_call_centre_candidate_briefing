# Weekend Replit Challenges

**Context**
You’ll pick **one** of the three challenges below and deliver a working Flask web app **built and deployed on Replit**. Assume you’re building tooling for a small BPO/call‑centre serving financial‑services customers. Keep it minimal but usable. Solve the right problem with clear, simple code and a tidy UI.

As far as possible let Replit make the choices for 
* the look and feel of the web app 
* the workings of the program
* just tell Replit waht you want nort how to do it 

**Ground Rules**

* Stack: **Python 3 + Flask**, HTML/Jinja, vanilla JS if needed.
* Data: Start with in‑memory structures; SQLite is optional (nice, not required).
* Host: Use **Replit Deploy** and provide the public URL.
* Collaboration: You may use any references. All work must be your own.
* Timebox: This is designed for a **single weekend**. Aim small; make it solid.
* Documentation: A short **README** that tells us how to run, what works, and what you’d do next.

---

## Challenge A — Mini Complaint Intake & Tracker

**Problem**
Agents need a bare‑bones internal tool to log customer complaints and track their status from **Open → In Progress → Resolved**. Nothing fancy; it must be quick to use during a call.

**User Stories**

* As an **agent**, I can log a new complaint with Customer Name, Account Number, Description, and Priority (Low/Medium/High).
* As an **agent**, I can see a list of all complaints sorted by **most recent** first.
* As an **agent**, I can change a complaint’s **status** without leaving the list.
* As a **team lead**, I can **filter** by status and **search** by customer name or account number.

**Functional Requirements**

* **/new**: Form to create a complaint (simple validation: required fields).
* **/** (or **/list**): Table of complaints showing: Date/Time, Customer Name, Account No, Priority, Status, and a short Description (truncated).
* **Inline Status Update**: Each row includes a control to change Status (no page reload required is nice, but not mandatory).
* **Sorting & Filtering**: Sort by created date and priority; filter by status.

**Non‑Functional**

* Layout should be readable at 1280×800. One CSS file or CDN (Bootstrap allowed).
* Clean, consistent naming; keep modules small.

**Data Model (suggested)**

```yaml
Complaint:
  id: int
  created_at: datetime
  customer_name: str
  account_number: str
  description: str
  priority: Low|Medium|High
  status: Open|In Progress|Resolved
```

**Deliverables**

* Replit project URL + **deployed URL**.
* README with: feature list, known gaps, and “next steps”.

**Evaluation Rubric (what we look for)**

* **Correctness & UX** (is it fast to log and update?)
* **Code quality** (structure, naming, no mystery globals)
* **Traceability** (clear commit messages; small commits)
* **Scope control** (MVP first; stretch if time allows)

**Hints (optional)**

* Use `request.form` and `redirect(url_for(...))` after POST.
* Store complaints in a list or dict; add SQLite only if you finish early.
* Truncate long descriptions with a helper filter.

**Stretch Goals**

* CSV export of filtered complaints.
* Simple role toggle (Agent/Lead) via a query param or cookie.
* Add a “tags” field and filter by tag.

**Suggested Weekend Milestones**

* **Sat AM**: Scaffold Flask app, base template, “new complaint” form.
* **Sat PM**: List view + sort/filter; inline status change.
* **Sun AM**: Polish UX, README, deploy to Replit.
* **Sun PM**: One or two stretch items.

---

## Challenge B — Call‑Centre Shift Scheduler (Micro‑Roster)

**Problem**
A small team needs a simple scheduler to assign **agents to Morning/Afternoon/Evening shifts** per day and let staff view the week at a glance.

**User Stories**

* As an **admin**, I can assign one or more agents to a **date + shift**.
* As an **agent**, I can see the **current week’s** schedule in a grid.
* As an **admin**, I can quickly see unfilled shifts.

**Functional Requirements**

* **/admin**: Form with Date picker, Shift (Morning/Afternoon/Evening), and Agent Name (free text is fine) and an “Add” button.
* **/schedule**: Weekly view (Mon–Sun) showing each shift cell with assigned agent names.
* **Data**: Keep assignments in memory initially: `[(date, shift, agent)]`.
* **Validation**: Prevent exact duplicates (same date+shift+agent).

**Non‑Functional**

* Page loads should be <300ms locally.
* Clean separation: routes, data layer (even if it’s a list), templates.

**Deliverables**

* Replit project URL + **deployed URL**.
* README: what works, assumptions, edge cases you considered.

**Evaluation Rubric**

* **Usability** (is the grid readable, are forms minimal?)
* **Correctness** (no duplicate rows; data shows up where expected)
* **Organisation** (modules, functions, small templates)
* **Pragmatism** (you resisted yak‑shaving; shipped the essentials)

**Hints (optional)**

* Represent a week starting from today’s Monday; compute with `datetime`.
* Use a dict keyed by `(date, shift)` for easy rendering.
* Keep CSS sparse; focus on clarity.

**Stretch Goals**

* **CSV export** of the visible week.
* “Swap request” form that logs a pending swap.
* Simple legend showing unfilled shifts in a highlight colour.

**Suggested Weekend Milestones**

* **Sat AM**: Data model + `/admin` form works.
* **Sat PM**: `/schedule` weekly grid renders assignments.
* **Sun AM**: Input validation, tidy layout, deploy.
* **Sun PM**: One stretch goal.

---

## Challenge C — FAQ Triage Bot with Human Escalation

**Problem**
Customers ask the same ten questions about repayments, late fees, and complaint processes. Build a tiny web UI that attempts an **instant answer** via keyword match, else **collects the question** for a human and lists all unresolved questions on an admin page.

**User Stories**

* As a **customer**, I can type a question and (if known) get an immediate answer.
* As a **customer**, if it’s unknown, I can submit the question with my name + email.
* As an **admin**, I can see a list of unanswered questions to respond to.

**Functional Requirements**

* **/**: Single input box (“Ask a question”), results area for the answer.
* **Dictionary of 10 Q/A pairs** (in code). Use simple **case‑insensitive keyword matching** (e.g., any of several keywords per Q triggers its A).
* **If no match**: Show a minimal form to submit question + contact.
* **/admin**: Table of submitted (unanswered) questions with timestamps.

**Non‑Functional**

* Clear empty‑state messages (e.g., “No submissions yet”).
* No external APIs; keep it local and deterministic.

**Deliverables**

* Replit project URL + **deployed URL**.
* README: your matching approach, examples, and known limitations.

**Evaluation Rubric**

* **Clarity** (UI flow is obvious; text is concise)
* **Robustness** (no crashes on empty input; sensible defaults)
* **Design thinking** (keyword choices; how you avoid false matches)
* **Communication** (README explains trade‑offs and next steps)

**Hints (optional)**

* Normalise input with `.strip().lower()`; test partial matches.
* Keep your Q/A data in a list of `{keywords: [...], answer: "..."}`.
* Consider showing the “closest” Q/A when multiple match.

**Stretch Goals**

* Admin can **promote** a submitted question into the Q/A dictionary.
* Basic **export** (CSV) of submissions.
* Very light‑touch scoring (e.g., count keyword hits) to pick the best answer.

**Suggested Weekend Milestones**

* **Sat AM**: Landing page + simple matcher.
* **Sat PM**: Unknown‑question submission flow + admin list.
* **Sun AM**: Edge cases, copy polish, deploy.
* **Sun PM**: Stretch item or extra tests.

---

## Submission Checklist (all challenges)

* [ ] Replit project URL
* [ ] **Deployed URL** (Replit Deploy)
* [ ] Short **README** with:

  * What you built (features)
  * How to run locally (if applicable)
  * Known gaps / trade‑offs
  * What you’d do in Week 2
* [ ] (Optional) A short **demo script** (bullet points) for a 3‑minute demo

## What We’re Evaluating

* Your ability to **frame the problem**, **choose a minimal viable scope**, and **ship**.
* Whether your code is small, readable, and reasonably structured.
* How you think: commit messages, README, and small design touches.

**Remember**: Small and finished beats grand and half‑built. Keep it tidy, ship it, and be ready to explain your choices.
