# Architecture Decision Records — wopr-app mk1

An ADR captures a decision, the alternatives that lost, and why — so the
decision does not get silently reversed six months later by a version of you
who has forgotten the reasoning. It is three paragraphs, not a document.

Kept in one file while there are four of them. Split to `adr/NNNN-slug.md` once
there are ten, or once two people are editing them at once.

Statuses: `proposed` → `accepted` → (`superseded by ADR-NNNN` | `deprecated`).
Accepted ADRs are never edited; they are superseded by a new one.

---

## ADR-0001 — Frame distribution is a latest-wins fan-out bus

**Status:** proposed
**Date:** 2026-08-11

### Context

Several consumers need the same video frames at different rates: a preview at
display rate, cheap analysis at roughly 10 Hz, expensive analysis at roughly
1 Hz, and possibly a recorder that needs everything. They must not block each
other, and a consumer that falls behind must not accumulate a backlog of stale
frames it will process late and pointlessly.

### Decision

One producer publishes immutable `Frame` objects to a `FrameBus`. Each
subscriber gets its own slot with its own policy. The default policy is
**latest-wins with depth 1**: publishing overwrites whatever the subscriber had
not yet consumed. A subscriber may opt into `mode="all"` with a **bounded**
queue when it genuinely cannot drop frames.

`publish()` performs a pointer write per subscriber. It never copies pixel
data, never blocks, and never waits on a consumer.

### Alternatives considered

**Chained pipeline (A → B → C).** Natural-sounding, wrong shape. Makes the
slowest stage the rate of the whole chain and couples unrelated consumers to
each other. Rejected.

**One shared queue with multiple readers.** Each frame goes to exactly one
reader, so consumers steal work from each other rather than all seeing the same
frame. Solves a different problem. Rejected.

**Callbacks invoked directly by the capture loop.** Zero infrastructure, and
tempting for that reason. But any consumer's slowness or exception lands
directly in the capture thread, which then stops grabbing. Rejected — though
worth noting this is what the code probably does today, and it is a perfectly
reasonable thing to have started with.

**Unbounded per-consumer queues.** Preserves everything, which sounds safe. In
practice a slow consumer grows the queue until memory runs out, and the frames
it eventually processes are far too old to be useful. Converts a visible
latency problem into an invisible memory one. Rejected.

### Consequences

- Good: consumers are fully decoupled; adding one is a `subscribe()` call.
- Good: bounded memory by construction.
- Good: `publish()` cost is trivial and independent of consumer behaviour.
- Cost: frames *are* dropped, silently, on purpose. Anything that assumes
  contiguous frames (inter-frame differencing, encoding) must either use the
  lossless policy or handle gaps via `seq`.
- Cost: one more concept between capture and consumers than a direct callback.

---

## ADR-0002 — Threads with immutable frames; not asyncio, not multiprocessing

**Status:** proposed
**Date:** 2026-08-11

### Context

Capture, several consumers, and health probes all need to make progress
concurrently. The UI must stay responsive while a slow analyzer runs. Video
frames are large, so how they move between execution contexts matters more
than usual.

### Decision

One OS thread per long-lived role: capture, each consumer, the probe
supervisor, plus the UI thread. Threads communicate only through the
`FrameBus` and through per-consumer counter structs. Frames are immutable and
shared by reference; nothing else mutable is shared.

**This decision is contingent on the measurement in `NEXT.md` step 0.** If the
profile shows the app comfortable single-threaded, the correct outcome is a
rate gate and no threads at all — and this ADR gets superseded.

### Alternatives considered

**Stay single-threaded with a rate gate.** Genuinely viable, and cheaper. If the
sum of all per-frame work fits inside the frame interval with headroom, threads
add only race conditions. This is the alternative that step 0 is designed to
test, and it should not be dismissed for sounding unambitious.

**asyncio.** Excellent for many concurrent I/O waits. This workload is a small
number of long-lived CPU-ish tasks, so the model buys little, and any blocking
call in a coroutine stalls the whole loop. Mixing it with a GUI event loop adds
a second scheduler to reason about. Rejected.

**multiprocessing.** The real answer *if* the work is CPU-bound in pure Python
and cannot be vectorised. Cost is that frames must cross a process boundary —
shared memory rings plus explicit lifetime management, or pickling megabytes
per frame. That is a substantially larger design. Deferred to ADR-0004.

### Consequences

- Good: frames cost a pointer to share; no serialisation.
- Good: no locks outside the bus internals, therefore no lock ordering to get
  wrong.
- Cost: the GIL means CPU-bound *pure-Python* consumers will not run in
  parallel. OpenCV, NumPy, encoders, and I/O release it, so most realistic work
  here is fine — but a hand-written pixel loop is not.
- Cost: immutability must be enforced, not assumed. Set
  `image.flags.writeable = False` and let violations fail loudly.
- Cost: shutdown needs deliberate design — one stop event, joins with timeouts.

---

## ADR-0003 — Health is pull-based probes with TTL staleness

**Status:** proposed
**Date:** 2026-08-11

### Context

The status bar needs to show whether capture is alive, whether consumers are
keeping up, whether there is disk space, and so on. Different facts change at
very different rates: frame age matters at ~1 Hz, free disk at ~60 s. Some
checks can block for seconds.

### Decision

Each check implements `Probe` with its own `interval_s`, `timeout_s`, and
`ttl_s`. A `ProbeSupervisor` runs due probes in a small thread pool and stores
results in a `HealthRegistry`. The status bar calls `snapshot()` on a UI timer
(~4 Hz) and renders whatever it gets.

`snapshot()` applies the TTL: any status not refreshed within `ttl_s` is
returned as `STALE` regardless of what it last said. `ttl_s` should be at least
3× `interval_s`.

### Alternatives considered

**Push-based / event-driven.** Components emit status changes as they happen.
Lower latency and no polling — but it cannot represent absence. A component
that dies simply stops emitting, and its last message stays on screen looking
authoritative. Detecting *that* requires a timeout, which is a TTL, which is
this design with extra steps. Rejected.

**Status bar calls checks directly on repaint.** No infrastructure at all. Also
means a `statvfs()` on a hung NFS mount freezes the UI. Rejected.

**One thread per probe.** Fine at five probes, silly at thirty, and each one
needs its own lifecycle. A supervisor with a small pool scales without that.
Rejected on tidiness rather than correctness.

### Consequences

- Good: a hung or crashed probe degrades to `STALE` instead of lying.
- Good: the UI can never block on a check.
- Good: adding a probe is one class and one `register()` call.
- Cost: displayed status is up to `interval_s` old. Fine for everything on the
  list; anything needing true real-time should drive a dedicated indicator off
  a counter instead.
- Cost: two tunables per probe that need sane defaults, or every new probe
  becomes a small argument with yourself.

---

## ADR-0004 — mk1 stays in-process; multi-process is deferred with named triggers

**Status:** accepted
**Date:** 2026-08-11

### Context

Splitting capture, analysis, and UI into separate processes gives real
parallelism and fault isolation. It also introduces IPC, shared-memory frame
transport, process supervision, and a much harder debugging story.

### Decision

mk1 is a single process. Revisit **only** when one of these is observed, not
predicted:

1. A consumer is CPU-bound in pure Python, cannot be vectorised or moved into a
   GIL-releasing library, and is measurably starving the others.
2. A consumer crashes the process often enough that isolation is worth the
   cost — a segfaulting native decoder, say.
3. A component needs a genuinely incompatible environment: different Python,
   different CUDA, different container.
4. Sustained aggregate CPU demand exceeds one core's worth of GIL-held time.

Recording the triggers is the point. It converts "should we split this?" from
a recurring argument into a threshold check.

### Alternatives considered

**Split now, pre-emptively.** Avoids a later migration. Costs a shared-memory
ring buffer, frame lifetime management across processes, a supervisor, and
IPC-aware debugging — for a problem that may never appear. Rejected as
speculative.

**Split only the UI.** A middle path with real merit: the UI is where
responsiveness is most visible. But it puts the largest data flow (frames to
preview) across the process boundary, which is exactly the flow that is
cheapest in-process. Rejected for now; revisit if trigger 2 fires on a GUI
toolkit issue.

### Consequences

- Good: mk1 stays debuggable with a plain debugger and a stack dump.
- Good: no serialisation cost anywhere on the frame path.
- Cost: no fault isolation — one segfault in a native library takes everything.
- Cost: a later split is real work. `FrameBus` being a narrow interface is what
  keeps that work bounded: a shared-memory implementation can be swapped behind
  the same four methods.
