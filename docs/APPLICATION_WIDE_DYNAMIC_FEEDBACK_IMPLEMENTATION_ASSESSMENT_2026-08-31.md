# Application-Wide Dynamic Feedback (INC-14) — UX Implementation Assessment

**From:** SDT-WB
**Date:** 2026-08-31
**Against:** `043_Application_Wide_Dynamic_Feedback_UX_Specification.md` (`histfints_uiue`, AC-DFB-01–10)
and its predecessor `042_Application_Wide_Dynamic_Feedback_Current_State_Audit.md`
**Status:** Read-only technical assessment. No code, template, or route was modified to produce
this document. No JavaScript is proposed. No closed workstream is reopened or redesigned.

---

## 1. AC-DFB-01 through AC-DFB-10 — classification

| AC | Requirement | Classification | Basis |
|---|---|---|---|
| AC-DFB-01 | `role="status"`/`aria-live="polite"` applies exactly when no flashed message is `error` | **Already satisfied** | `base.html:31-33`, confirmed directly: `role="{{ 'alert' if has_error.value else 'status' }}"` — unchanged by anything proposed here |
| AC-DFB-02 | `role="alert"`/`aria-live="assertive"` applies exactly when ≥1 flashed message is `error` | **Already satisfied** | Same lines — the pairing is not touched by §2's proposed fix, only whether the region's content is reliably announced |
| AC-DFB-03 | An info-level message on a freshly navigated/reloaded page is reliably announced | **Requires a new mechanism** | See §2 — a no-JavaScript focus-management addition to `base.html`'s existing flash `<ul>` |
| AC-DFB-04 | Error-level message continues to be reliably announced on full reload (regression) | **Presentation/template change, verified by regression test** | Same mechanism applied uniformly (§2) — no special-casing by category; a regression test confirms the already-working `alert` case isn't disturbed |
| AC-DFB-05 | `job_running.html`'s region is reliably announced on first arrival | **Requires a new mechanism** | See §2 — the same focus-management technique, applied to a *conditionally* rendered attribute so only the first poll of a given job carries it |
| AC-DFB-06 | If AC-DFB-03/05 can't be met within the no-JS constraint, report that explicitly | **Already satisfied by this assessment's own finding** | §3.3 below: a no-JS fix exists and is proposed — nothing to report as blocked |
| AC-DFB-07 | No regression in the working `role="alert"` case as a side effect of fixing `status` | **Presentation/template change, verified by regression test** | Same mechanism, same file — a regression test is the verification instrument, not a separate code path |
| AC-DFB-08 | A real NVDA pass, burst-capture, all four representative surfaces, PASS/FAIL/attempted-not-confirmed | **Blocked by missing information** | Not a code gap — needs an actual NVDA session after implementation lands, the same posture this project already applied to AC-RES-20 in the Resolve workstream. SDT-WB cannot substitute a code-level test for this |
| AC-DFB-09 | A FAIL contradicting a specific closed-workstream finding reopens only that workstream, named | **Already satisfied by construction — a procedural rule for whoever runs the NVDA pass** | Nothing to implement; this governs how a future FAIL is triaged, not code |
| AC-DFB-10 | A FAIL on the shared mechanism with no closed-workstream finding contradicted is a defect against `043` alone, not attributed to any closed workstream | **Already satisfied by construction — same as AC-DFB-09** | Procedural, not code |

**Summary:** 4 already satisfied (2 by construction, 2 by this assessment's own finding), 2
presentation/template changes verified by regression test, 2 requiring one small, shared,
no-JavaScript mechanism, 1 blocked on a real AT session (not on this assessment), 1 with no code
implication. **No AC is blocked by the no-JavaScript constraint** — see §3.3.

---

## 2. Smallest centralized implementation

**One mechanism, two application points — no JavaScript, no new dependency.**

### 2.1 The mechanism

Give the announcement region itself keyboard focus on the page load that first presents it, using
only native HTML: `tabindex="-1"` (makes an otherwise non-focusable element programmatically
focusable, without adding it to normal Tab order) plus the `autofocus` content attribute (valid on
any focusable element per the WHATWG HTML Living Standard — not restricted to form controls,
contrary to its most common usage). A real screen reader announces whatever element receives
focus, using its accessible name/content — this is independent of `aria-live`'s change-detection
timing entirely, so it sidesteps the actual defect (§3.2) rather than trying to make `aria-live`
behave differently on first paint.

### 2.2 `base.html`'s flash `<ul>` (AC-DFB-03/04/07)

```html
<ul class="flashes" tabindex="-1" autofocus
    role="{{ 'alert' if has_error.value else 'status' }}"
    aria-live="{{ 'assertive' if has_error.value else 'polite' }}">
```

Applied unconditionally, both categories — `base.html:31-33`, the one shared code path all 118
`flash()` call sites and all 11 templates already render through (`042` §1/§5). No per-page change
needed anywhere else, which is exactly the "centralized, not duplicated" property `042` §5
identified as favorable for scoping this fix.

### 2.3 `job_running.html`'s status region (AC-DFB-05)

Cannot be unconditional the same way: this page is reached by re-rendering the *same* URL
(`/jobs/<job_id>`, confirmed — `job_status_page()`, `web.py:618-626`) every second via its own
`<meta http-equiv="refresh" content="1">`, with no existing distinction between the first arrival
and the Nth poll. Applying `autofocus` unconditionally would steal keyboard focus back to the
status line every single second for as long as the job runs — itself a new accessibility problem
(repeated, unrequested interruption), not a fix.

**Smallest fix**: the `jobs` dict already tracked per-job in `web.py` (`start_job()`/
`job_status_page()`, in-memory, lock-protected) gains one new boolean field, `announced`,
initialized `False`. `job_status_page()`'s `running` branch checks it: renders
`job_running.html` with `announce=True` only the first time, then sets `announced = True` under
the existing `jobs_lock` before returning — every subsequent poll for that same job renders with
`announce=False`. No new persistence, no new data structure, no URL/query-parameter scheme:

```python
if job["status"] == "running":
    with jobs_lock:
        first = not job.get("announced", False)
        job["announced"] = True
    return render_template("job_running.html", announce=first)
```

```html
<p role="status" aria-live="polite" {% if announce %}tabindex="-1" autofocus{% endif %}>
  Import is running…
</p>
```

### 2.4 No conflict between the two application points

The two mechanisms cannot both fire on one page load: `job_running.html` is only ever rendered by
`job_status_page()`'s `running` branch, which never has a flashed message queued (`flash()` calls
tied to a job's completion happen only in the same function's `done` branch, which `redirect()`s
instead of rendering — confirmed by reading the full function body). `base.html`'s block therefore
never has content to render on `job_running.html`'s own page loads, and no double-`autofocus`
element can exist on one page — a real HTML constraint (only one element can hold focus at a time)
that this design respects by construction, not by convention.

---

## 3. §8 — SE/SDT implementation-assessment questions, answered

### 3.1 — Does `job_running.html`'s region need to be announced on every 1-second self-refresh, or only on first arrival?

**Only on first arrival.** Re-announcing every second would repeatedly steal keyboard focus for
the entire duration of a long-running job — a genuine new usability/accessibility problem (constant
interruption, per `043` §4's own caution), not a fix to the original "not announced at all"
finding. AC-DFB-05's own wording ("reliably announced on first arrival at minimum") already
anticipates this answer. §2.3's `announced` flag implements exactly this.

### 3.2 — Is the mechanism's structural shape itself the root cause of the full-reload announcement gap, and if so, what changes it?

**Yes, confirmed structurally, not inferred.** Both `base.html`'s flash `<ul>` and
`job_running.html`'s `<p role="status">` are entirely server-rendered, with their final content
already present at first paint — and this application ships **zero** JavaScript (`042` §4,
independently re-confirmed: no `.js` file exists under `static/`), so no DOM mutation of any kind
ever happens after initial render. `aria-live` is a *change-detection* mechanism — it announces
content that differs from what a screen reader already observed in that region. A region born
with its final content, never subsequently mutated, gives the screen reader nothing to diff
against; whether that content gets announced on initial paint at all is left to each screen
reader's own page-load heuristics, which is exactly the inconsistency `015` reproduced (four
genuine NVDA attempts, `alert` reliably captured, `status` not). This is a structural property of
how the mechanism is currently used, not a probabilistic one — it does not depend on message
wording, page, or category, which is also why `042` §5's "one shared mechanism" finding holds:
every page has the identical structural gap because every page uses the identical
render-once-and-never-mutate pattern. **What changes it**: §2's focus-management fix, which
sidesteps `aria-live`'s change-detection dependency entirely rather than trying to make it detect a
"change" that structurally never occurs.

### 3.3 — Is any fix achievable within the current no-JavaScript constraint, or does it require introducing client-side script for the first time?

**Achievable with zero JavaScript.** §2's `tabindex="-1"`/`autofocus` technique is native HTML,
standardized behavior (the WHATWG Living Standard's `autofocus` content attribute; `tabindex="-1"`
per the same standard's focus-management section) — no script tag, no event listener, no
`static/*.js` file, nothing that changes `042` §4's "ships no JavaScript assets at all" finding.
This is the standard "move focus to the point of change" accessibility technique used specifically
when a live region's own change-detection cannot be relied on — which is exactly this application's
situation per §3.2. **AC-DFB-06 does not trigger** — there is nothing to report as blocked by the
no-JS constraint.

### 3.4 — Are the four representative surfaces (§7) sufficient, or should a specific additional surface be added?

**Sufficient for the mechanism itself; one residual interaction worth flagging to UIUX for the NVDA
pass, not a gap in surface *coverage*.** The four surfaces correctly exercise both application
points (`base.html`'s shared `<ul>` via three different pages/categories; `job_running.html`
separately) and both categories (`status` via Import & Status/Series, `alert` via Search/Discover)
— since the mechanism is structurally one shared code path per `042` §5, no additional *page* adds
new coverage. **One interaction not covered by any of the four, worth naming rather than silently
omitting**: INC-15's own new cross-workflow links (Search → Series, Discover → Resolve) land on a
target page via a URL fragment (`#series-{id}`), which the browser scrolls into view but does not
itself focus. Autofocusing the flash `<ul>` on such a landing means a sighted user following that
link sees the page scrolled to the named row while keyboard/AT focus is at the top-of-page flash
region instead — not a functional break (no message is lost, no error occurs), but a genuinely new
divergence between visual scroll position and focus position that only exists once this fix ships.
**Recommend**: UIUX's NVDA pass include this combination (a fragment-anchored cross-workflow link
landing on a page that also has a flashed message) as a fifth informal check, or explicitly decide
it's out of scope — not silently left unconsidered.

---

## 4. Required tests

- **Structural/markup tests (SDT-WB implementable, code-level)**:
  - `base.html`'s flash `<ul>` carries `tabindex="-1"` and `autofocus` for both an info-only batch
    and an error-containing batch (AC-DFB-01/02/07 regression — the `role`/`aria-live` pairing
    itself unchanged, confirmed by the same assertion that already exists for this pairing today).
  - `job_running.html`'s first render (`announce=True`) includes `tabindex="-1"`/`autofocus` on
    the `<p role="status">`; a second, simulated poll of the same job (`announce=False`) does not
    — a test that calls `job_status_page()` (or its route) twice for one still-running job and
    diffs the two responses.
  - `jobs` dict's `announced` flag: initialized `False`, flips to `True` after the first `running`
    render, survives across the lock correctly (no race on the flip given the existing
    `jobs_lock` usage pattern already established elsewhere in this module).
  - No second `autofocus` element can co-occur on one response (§2.4) — a structural assertion,
    not just an architectural claim: grep/parse the rendered HTML of a representative `done`-status
    job page for at most one `autofocus` occurrence.
- **Regression**: full `histfints` suite re-run before and after, per this session's own
  established practice for every implementation this large. No AC-* criterion from any closed
  workstream (`030`/`031`/`033`/`039`/§10a's `045`) concerns focus management or `tabindex`/
  `autofocus` specifically — confirmed by re-checking each workstream's own AC-* list — so a clean
  regression run is expected, not merely hoped for.
- **Real NVDA validation (UIUX's own responsibility, not SDT-WB's — AC-DFB-08)**: the four
  representative surfaces named in `043` §7, each PASS/FAIL/attempted-not-confirmed with verbatim
  captured text, per the `at-validation` skill's own three-way discipline — not substitutable by
  any code-level test, since the actual claim under test is what a real screen reader announces,
  not what markup is present.

---

## 5. Genuine blockers

**None for implementation.** Independently re-checked against `043` §9's own claim ("no DFA/PO
decision currently blocks SE/SDT assessment"), not merely repeated: every AC-DFB-01–10 either
requires no code change, is satisfied by the one small mechanism in §2, or is a validation/process
requirement outside code entirely (AC-DFB-08/09/10). AC-DFB-06's reporting condition does not
trigger (§3.3). The only outstanding item — the real NVDA pass (AC-DFB-08) — is expected,
downstream, UIUX-owned work following implementation, per `043`'s own transition sequence
(`specification → SE/SDT implementation assessment → implementation → UI/UE validation`), not a
blocker to producing this assessment or to SDT-HF beginning implementation.

---

## 6. Preserving closed workstreams — confirmed, not assumed

Per PO-DFB02, re-checked directly rather than trusting the specification's own framing: none of
`030` (Series), `031` (Search), `033` (Discover), `039` (Resolve), or `045`/§10a (Cross-Workflow,
this session's own most recent closure) has any AC-* criterion concerning focus management,
`tabindex`, `autofocus`, or the announcement-timing question this fix addresses — each closed
workstream's own acceptance criteria concern wording, accessible names, hand-off correctness, and
(where applicable) `role="alert"`'s already-working announcement, none of which §2's change alters.
**Per §2.2**: the fix is applied at the one shared `base.html` render point, uniformly, not
per-page — so there is no page-specific behavior to re-derive for any closed workstream. Per
PO-DFB02's own stated bar, this is not, by itself, treated as reopening any of them; the regression
tests in §4 exist specifically to catch it early if that expectation turns out to be wrong, and per
`043` §7/AC-DFB-09, only a workstream whose real NVDA pass concretely contradicts one of its own
already-confirmed findings would actually reopen — nothing in this assessment's own analysis
predicts that outcome, but it is stated as an expectation to be confirmed by validation, not asserted
as already proven.

---

## What this assessment does not do

- Does not implement anything — no route, template, or service method was changed.
- Does not introduce JavaScript, a new live-region mechanism, or a toast/notification system.
- Does not change any flash-message wording.
- Does not redesign any closed workstream's screen.
- Does not modify `workbench` or any sibling repository.

## Gate

Per `043`'s own expected transition — `043 specification → SE/SDT implementation assessment →
implementation → UI/UE validation (mandatory real NVDA pass)` — this document is the assessment
half. Hand-off: to SDT-HF for implementation in `histfints`, per the standing sibling-repository
rule. SDT-WB will perform a read-only conformance review against AC-DFB-01–10 and this assessment
after SDT-HF implements and UIUX completes the mandatory NVDA pass, matching the precedent set for
INC-13 and INC-15.
