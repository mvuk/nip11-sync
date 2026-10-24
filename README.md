# NIP-11 Sync

An effort to bring every Nostr relay implementation to a complete, accurate
[NIP-11](https://github.com/nostr-protocol/nips/blob/master/11.md) relay information document,
and to make paid relays discoverable and payable by clients.

## Why

NIP-11 tells clients what a relay is, what it limits and what it costs. In practice most relays serve
only part of it. On 23 Oct 2026, relay.damus.io, nos.lol, relay.primal.net, yabu.me and
relay.nostr.wirednet.jp (all strfry, which carries roughly two thirds of measured relay use) served
3 of the 13 `limitation` fields and no `fees`. A complete, consistent NIP-11 across implementations
is what lets clients show limits, discover paid relays, and pay them.

## Two tracks per implementation

1. **NIP-11 complete.** Advertise every `limitation` field the software actually enforces, plus
   optional `fees`, `payments_url`, `payment_required` and `restricted_writes`. Generic,
   spec-driven upstream changes with tests.
2. **Payments (optional).** A payment processor or plugin, written in each codebase's own extension
   style, so operators can charge admission, subscription or per-event fees. Our contribution is a
   [Bark](https://second.tech) backend that accepts **Lightning** (through the Ark server's
   Lightning gateway) and **native Ark payments** (arkoor) to per-user Ark addresses, advertised
   through the track-1 fields. Other backends fit the same shape.

## Pay per access

The shared design for the optional payment backends (Lightning + Ark, NIP-11 discovery) is in
[`PAY-PER-ACCESS.md`](PAY-PER-ACCESS.md).

## Status

[`STATUS.md`](STATUS.md) has one row per implementation, with open PRs linked.
The full inventory of **108 relay implementations** (55 maintained) is in
[`inventory/software.md`](inventory/software.md); deployed relays (global and Japan) are in
[`inventory/relays.md`](inventory/relays.md), and client support in [`inventory/clients.md`](inventory/clients.md).

## Related: Ark payments in Nostr Wallet Connect

- Proposal issue: [nostr-wallet-connect/nwc#10](https://github.com/nostr-wallet-connect/nwc/issues/10)
- Ark Payments extension spec: [nostr-wallet-connect/nwc#11](https://github.com/nostr-wallet-connect/nwc/pull/11)
- Payment-rail-neutral NIP-47 core wording: [nostr-protocol/nips#2520](https://github.com/nostr-protocol/nips/pull/2520)

## Blossom (file hosting)

The same idea for media servers. Blossom's BUD-07 already uses HTTP 402 with `X-Lightning` and `X-Cashu`
headers and allows new methods.
- `X-Ark`, native Ark payments for BUD-07: spec [`specs/blossom-x-ark.md`](specs/blossom-x-ark.md),
  draft PR [hzrd149/blossom#116](https://github.com/hzrd149/blossom/pull/116).
- nostrcheck-server (share.yabu.me, cdn.nostrcheck.me): BUD-07 correctness
  [#61](https://github.com/quentintaranpino/nostrcheck-server/pull/61), Bark provider with Lightning and `X-Ark`
  [#62](https://github.com/quentintaranpino/nostrcheck-server/pull/62).
- Server support: inventory of **51 Blossom implementations** and ~30 public hosts in
  [`inventory/blossom/`](inventory/blossom/servers.md). Only 3 send BUD-07 headers today (nostrcheck-server: Lightning;
  blob-drop and almond: Cashu), none fully spec-correct. First target: nostrcheck-server, which runs share.yabu.me
  (the Japanese community's media server), cdn.nostrcheck.me, nostrcheck.me and nostrage.com.

## Contributing

Corrections to the inventory are very welcome (open an issue or PR here). Each upstream change
follows that project's own contribution rules.

Maintained by Matthew Vuk ([Second](https://second.tech)).
