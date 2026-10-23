# Pay per access

How the optional payment backends work. They follow the same shape in every implementation,
written in each codebase's own extension style (plugin, processor, hook or sidecar).

## Model
- **Prepaid credit per pubkey.** Operators charge admission, per event (optionally only for some
  kinds), or both. Each accepted event is charged against the author's balance (or the NIP-42
  authenticated pubkey's).
- **Out of credit:** the event is rejected with a standard `restricted:` reply that says how to pay.
- **Reads (optional):** gated per pubkey with NIP-42 AUTH where the relay supports it
  (e.g. strfry's proposed `readAllowlistFile`).

## Two payment rails, through one wallet daemon
The backend talks to `barkd`, the REST daemon of the [Bark](https://second.tech) wallet:
- **Lightning:** a BOLT11 invoice, received through the Ark server's Lightning gateway.
- **Ark (arkoor):** a per-pubkey (or per-invoice) Ark address, paid off-chain and instantly.
Operators pick one or both; with both, a single BIP-321 URI can offer the two.
Payments are matched from the wallet's history and credited exactly once.

## Discovery: NIP-11
When payments are on, the relay advertises them in its NIP-11 document:
`limitation.payment_required`, `limitation.restricted_writes`, `fees` (admission / publication with
`kinds`) and `payments_url`. That's why each implementation's NIP-11 completeness change comes first.

## Implementations

| Relay | Backend |
|---|---|
| strfry | [strfry-bark-paid-writes](https://github.com/mvuk/strfry-bark-paid-writes) (write-policy plugin; stock strfry) |
| nostr-rs-relay | Bark processor beside ClnRest/LNbits, [#258](https://github.com/scsibug/nostr-rs-relay/pull/258) |
| nostr-relay (mattn) | optional paid writes, [#37](https://github.com/mattn/nostr-relay/pull/37) |

Paying from a client: any NWC-capable client can pay Lightning invoices today. Native Ark payments
over NWC are proposed in [nostr-wallet-connect/nwc#11](https://github.com/nostr-wallet-connect/nwc/pull/11).
