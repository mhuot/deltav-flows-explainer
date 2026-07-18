# Research brief — Delta-V telemetryd architecture explainer

Single source: `deltav-telemetryd-architecture.md` (internal doc, not included)
(referenced below by section). No external claims are made; every scripted
statement maps to a line in that document.

## Verified facts used in the script

| # | Claim | Source (section of the architecture doc) |
|---|-------|------------------------------------------|
| 1 | telemetryd is a "pure ingestion bridge", a hollowed-out shell; every adapter in its configuration is disabled; it performs no processing today | Summary |
| 2 | The flow pipeline bypasses telemetryd entirely: Minion → minion-gateway → Kafka → flow-enricher → ClickHouse | Summary (pipeline diagram) |
| 3 | Minion's `FlowUdpListener` opens a single UDP port, default 4729 | Three-tier pipeline §1 |
| 4 | `FlowProtocol.detect()` sniffs the version header: `0x0005` → Netflow-5, `0x0009` → Netflow-9, `0x000A` → IPFIX, 32-bit `5` → sFlow; headers are disjoint | Three-tier pipeline §1 |
| 5 | Payloads stay opaque bytes; nothing beyond the 4-byte sniff is parsed on the Minion | Three-tier pipeline §1 |
| 6 | The Minion streams datagrams over gRPC using four protocol-specific bidi methods; routing is by RPC method, not payload inspection | Three-tier pipeline §2 |
| 7 | Each method maps to its own Kafka topic `DeltaV.Sink.Telemetry-<proto>`, keyed `<location>@<minion-id>` | Three-tier pipeline §2 |
| 8 | flow-enricher consumes all four topics through one Spring Cloud Stream binding, parses per protocol, enriches with node context, writes to `deltav-flows` (ClickHouse) | Three-tier pipeline §3 |
| 9 | All 8 telemetryd queues are disabled in `telemetryd-configuration.xml`; no bridges start today | Three-tier pipeline §3 |
| 10 | telemetryd remains deployed as an extension seat for protocols needing event/metric semantics (BMP, JTI/NX-OS) | Summary |
| 11 | The coupling is content-blind: neither Minion, gateway, nor telemetryd's bridge parses a flow beyond the 4-byte sniff; all protocol semantics live in flow-enricher | Coupling to the Minion |
| 12 | Kafka consumer groups are the scaling mechanism; adding flow-enricher replicas requires no code or config change | Horizontal scaling via SCS |
| 13 | 4 topics × 4 partitions = 16 assignable partitions → up to 16 flow-enricher replicas share work in aggregate; per-protocol parallelism caps at 4 | Scaling ceilings |
| 14 | Per-protocol Kafka topics isolate backpressure/poison messages between protocols | Protocol-to-protocol coupling table |
| 15 | Sinks are lossy by design: a Kafka publish failure logs and continues | Three-tier pipeline §2 (Decision 6) |

## Facts deliberately left out (scope control, 60 s budget)

- Twin publisher chain / OpenConfig connector detail
- Lifecycle phase numbers (400/200/300)
- prometheus-writer, collectd, pollerd, provisiond side pipelines
- Record-keying skew caveat (single-hot-Minion)
- Rust Minion substitutability note

## SME corrections (SME, 2026-07-18) — override the doc where they conflict

- **Fact 8 correction:** flow-enricher does NOT write to ClickHouse
  directly. It is a classic SCS *processor*: consumes the four raw-flow
  topics AND produces enriched flows to the `deltav-flows` Kafka topic;
  ClickHouse ingests that topic with its own built-in Kafka consumer. The
  doc's "writes flow documents to `deltav-flows` (ClickHouse ingestion)"
  and its mermaid edge `FE -->|deltav-flows| CH` are ambiguous/misleading
  on this point. Applied in v2 (scene 5 narration + scenes 5/7 visuals).
- **Recap diagram:** no connector between Kafka and telemetryd — telemetryd
  is not in the flow path at all. Applied in v2 (spur removed).
- **Resolved (second SME reply, 2026-07-18):** the partition scaling is
  "pure Kafka" — the broker creates 4 partitions per topic, which lets any
  consumer group spread work across them; ClickHouse runs 4 consumer
  threads per topic (one per partition), and enricher replicas divide the
  raw-flow partitions the same way. Applied in v3 (scene 6 reworded to
  attribute scaling to Kafka, not any one service). ClickHouse is being
  added to the doc; the doc is also being updated.
- **v3 scope change:** per the SME, telemetryd should not appear in the
  Flows conversation at all — the video is reframed as "Delta-V flows,
  explained" with scenes 1, 2, and 7 rewritten and every telemetryd
  reference removed. Facts 1, 9, 10 are no longer used by the script.

## Sensitivity

Internal engineering subject, no clinical/regulated claims. On-screen
identifiers (class names, topics, ports) copied verbatim from the doc.
