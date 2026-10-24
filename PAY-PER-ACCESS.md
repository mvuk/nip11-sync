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
Operators pick one or both. Payments are matched from the wallet's history and credited exactly once.

## One payment request format: a BIP-321 URI
Every backend presents what to pay as one [BIP-321](https://github.com/bitcoin/bips/blob/master/bip-0321.mediawiki)
URI, the same format Blossom's [`X-Ark`](specs/blossom-x-ark.md) uses:

```
bitcoin:?ark=ark1…&lightning=lnbc…&amount=0.00000021
```

- `ark` is the Ark address (BIP-321 reuses a bech32m type's human-readable part as its key; the key stays
  `ark` for test-network `tark1…` addresses). `lightning` is a BOLT11 invoice. Each is present only when
  that rail is on. `amount` is in BTC and is omitted for an open top-up.
- The address encodes its Ark server, so the **wallet** decides: it pays `ark` when the address belongs to
  its own Ark server, and otherwise another instruction, typically `lightning`. Clients and relays never
  match Ark servers.
- Plain fields (invoice, address, amount in sats) stay alongside the URI where a backend already served
  them, for compatibility.

## Paying from a client
A client passes the URI unchanged to its wallet with the [NWC-321](https://github.com/nostr-wallet-connect/nwc/blob/main/321.md)
`pay` method: one call, no Ark-specific code in the client. A wallet without Ark support pays the
`lightning` instruction; any NWC client can still pay a bare Lightning invoice with `pay_invoice`.
The Ark-specific payment details a wallet reports (the `ark` payment type, VTXO ids, "settled" meaning
cosigned by the Ark server) are defined by the NWC Ark Payments extension,
[nostr-wallet-connect/nwc#11](https://github.com/nostr-wallet-connect/nwc/pull/11), which is being reworked around
this approach after review on [nwc#10](https://github.com/nostr-wallet-connect/nwc/issues/10).

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

