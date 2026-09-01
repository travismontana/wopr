# NEXT — what to actually do, in order

The answer to "I'm not really following what I need to do next."

Sequenced so that **every step leaves the app running**. No big-bang rewrite,
no branch that lives for three weeks. If a step cannot be finished in a
sitting, it is too big and needs splitting.

Sizes: XS ≈ under an hour · S ≈ a sitting · M ≈ a weekend · L ≈ several

---

## Step 0 — Measure. Do not skip this. **[XS]**

Before any restructuring, find out whether restructuring is warranted.

Add to whatever produces frames today:

- a monotonic `seq` counter
- `t_capture = time.monotonic()` at grab
- a log line every N frames: inter-frame delta, and wall time spent in each
  consumer

Run it for five minutes under realistic load and answer three questions:

1. What is the actual frame rate, and how much does it jitter?
2. What is the per-frame cost of each consumer?
3. Does the sum of consumer costs fit inside the frame interval?

**If it fits with headroom:** stop. Add a rate gate to the expensive consumer
and go do something else. Threads would add nothing but race conditions, and
ADR-0002 gets superseded with "measured, not needed." That is a win, not a
failure.

**If it does not fit:** continue to step 1, now knowing exactly which consumer
is the problem.

> Everything below assumes the measurement said threads are warranted.

---

## Step 1 — `Frame` envelope, immutable **[S]**

Add the dataclass from ARCHITECTURE §4.4. Have the existing capture path
produce `Frame` objects instead of bare arrays. Set
`image.flags.writeable = False`.

Consumers still get called exactly as they do now. Nothing is threaded yet.

**Done when:** the app behaves identically and nothing raises on the read-only
flag. Anything that *does* raise has been quietly mutating a shared buffer, and
finding that now is much cheaper than finding it after threads exist.

---

## Step 2 — `FrameBus`, still single-threaded **[S]**

Implement `publish` / `subscribe` / `get` / `stats`, latest-wins depth 1.
Roughly 60–80 lines: a `threading.Condition` and one slot per subscriber.

Rewire consumers to `get()` from a subscription instead of being called
directly — but keep calling them from the same loop for now.

**Done when:** the app still works and `FrameBus` has unit tests for: publish
with no subscribers, overwrite before consume increments `dropped`, `get()`
with a timeout on an empty slot, and `close()` mid-wait.

Testable without threads, which is why it comes before them.

---

## Step 3 — Capture gets its own thread **[S]**

Move grab/stamp/publish into a dedicated thread. It does nothing else. Add a
`threading.Event` for shutdown and join with a timeout.

**Done when:** the app runs, and Ctrl-C exits cleanly in under a second with
the device released. Verify the device is actually released —
`fuser /dev/video0` or equivalent — rather than assuming.

---

## Step 4 — Preview gets its own thread **[S]**

Preview consumes from its subscription on its own thread and posts results to
the UI through the framework's thread-safe mechanism (Qt signal,
`GLib.idle_add`, Tk `after`, whichever applies). No widget is touched off the
UI thread.

**Done when:** preview is smooth while the window is dragged and resized.

---

## Step 5 — The slow consumer gets its own thread + rate gate **[S]**

This is the step that proves the whole design. Give the expensive consumer its
own thread and a `max_hz`. Watch preview stay smooth while it grinds.

**Done when:** the slow consumer runs at its configured rate, preview does not
stutter, and its `dropped` counter climbs — because that is what the design
says should happen.

---

## Step 6 — `ConsumerStats` plumbed through **[XS]**

Every subscription tracks `received`, `dropped`, `last_seq`,
`last_latency_ms`, `errors`. Dump them to the log on a timer.

Cheap, and it makes the entire health subsystem below mostly a rendering
exercise.

---

## Step 7 — `HealthRegistry` + `ProbeSupervisor` **[M]**

`Probe` protocol, registry with TTL-based staleness, supervisor with a small
thread pool. See ARCHITECTURE §7.2.

**Done when:** a probe registered with `interval_s=1, ttl_s=3` shows `STALE`
within ~3 s of its check being made to hang, and a probe that exceeds
`timeout_s` reports `FAIL` without wedging its peers. Test both deliberately —
the staleness path is the one that silently rots if it is never exercised.

---

## Step 8 — First three probes **[S]**

`capture_alive`, `consumer_lag`, `disk_free`. All three read counters that
already exist from step 6.

**Done when:** unplugging the camera turns `capture_alive` to `FAIL` within its
stall timeout, and plugging it back turns it green.

---

## Step 9 — Status bar renders the snapshot **[S]**

Repaint on a 4 Hz UI timer from `snapshot()`. Worst state wins for the rollup.
Detail text in tooltips. Colour plus a glyph, never colour alone.

**Done when:** the bar reflects reality within a second, and the UI does not
hitch when a probe is slow.

---

## Step 10 — Shutdown, properly **[S]**

One stop event. Every thread joins with a timeout. Recorder drains its queue.
Device released. Log anything that fails to join.

**Done when:** Ctrl-C, window close, and `SIGTERM` all exit cleanly in under a
second, ten times in a row.

---

## Later, deliberately not now

- Recorder / lossless path — only if it is in scope for mk1 (ARCHITECTURE §9)
- Multi-source support — cheap to design in, expensive to retrofit; decide the
  *interface* now even if only one source is implemented
- A second bus for analyzer *results* — do not hand-wire results into the frame
  bus
- Config file for rates and thresholds — after the numbers stop changing daily
- Multi-process split — only on an ADR-0004 trigger firing

---

## Sizes rolled up

| Phase | Steps | Size |
|-------|-------|------|
| Measure | 0 | XS |
| Pipeline + threading | 1–6 | **M** |
| Health + status | 7–10 | **S–M** |
| **Total** | | **M** |

Two caveats on that total. Steps 3 and 4 depend on the GUI toolkit's threading
rules, which vary a lot — if the toolkit turns out to be awkward, step 4 alone
can eat a day. And if the capture source needs real reconnect logic
(ARCHITECTURE §6.1), step 3 grows.

Step 0 can legitimately delete steps 1–6 and take the total to **S**. That is
the best possible outcome and it costs an hour to find out.
