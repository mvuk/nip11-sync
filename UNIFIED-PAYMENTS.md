# One consistent way to pay across Nostr (Ark + Lightning)

Status: working design, 24 Oct 2026. Every spec, PR and backend in this effort follows it.
Pieces marked ✅ were tested live on signet with Bark 0.7.1 (24 Oct 2026).

## 1. One object, one action

- **The object: a BIP-321 URI.** Every payment request anywhere (a relay asking for a fee, a media server's 402, a
  person's tip address, an invoice) is a BIP-321 URI with one or more payment instructions:
  `bitcoin:?ark=<ark address>&lightning=<bolt11>&lno=<bolt12 offer>&amount=<btc>`
  Ark needs no BIP change: BIP-321 says bech32m types use their HRP as the key, so `ark=` (with `ark1…` or `tark1…`). ✅
- **The action: NWC-321 `pay(bip321)`** from any Nostr client, or the wallet's own "send" for a pasted or scanned URI.
  The **wallet**, never the client, chooses the instruction.

## 2. The wallet's choice (fallback order)

1. **`ark=` whose address is on the wallet's own Ark server → pay natively (arkoor).** Instant, near-zero fee, and the
   recipient can be offline (delivered via the server mailbox). The address commits to its server (v0 server key,
   v1 `ark_id`), so the wallet decides alone. ✅ (Bark rejects a foreign-server `ark=` by itself.)
2. **Otherwise Lightning:** `lightning=` (BOLT11) or `lno=` (BOLT12). An Ark wallet pays through its Ark server's
   Lightning gateway, and an Ark recipient receives through theirs, so **Ark ↔ different Ark ↔ plain Lightning wallets
   all interoperate**. ✅ (Bark fell back to Lightning when the `ark=` was foreign.)
3. **Otherwise on-chain:** the URI body address or `sp=`. Slow, last resort.
4. Nothing payable → `UNSUPPORTED_PAYMENT_INSTRUCTION` before any money moves. ✅

A wallet **SHOULD prefer** (1) over (2) when both are present: cheaper and faster. ⚠️ Bark's CLI 0.7.1 currently defaults to
Lightning in that case (Bark task B1).

## 3. Two kinds of request

| | Dynamic (per payment) | Static (a person or service, reusable) |
|---|---|---|
| Used by | relay fees, Blossom 402s, invoices | profiles, tips, zaps, "pay me" links |
| Recipient online? | yes (a server issues it) | not necessarily |
| Instructions | **fresh** `ark=` address + `lightning=` BOLT11 for the exact amount | **static** `ark=` address (offline-capable via the mailbox) + a reusable Lightning target: `lno=` (BOLT12 offer) or a Lightning address (LNURL, served by an always-on service such as bark-nwc's LNURL bridge) |
| Where it appears | NIP-11 `payments_url` → returns a BIP-321; Blossom `X-Ark` (full BIP-321) beside `X-Lightning`; relay `restricted:` messages | a profile payment target (NIP-A3 `payto`), BIP-353 DNS name (₿user@domain resolves to a BIP-321), Ark Zaps `kind:10740` |

## 4. Proof, accounting and receipts (per context; the request format stays the same)

| Context | How the payee knows it was paid | Spec |
|---|---|---|
| Relay pay per access | the relay's wallet (barkd) sees the receive; credits the pubkey | per-implementation backends; NIP-11 advertises fees |
| Blossom upload/download | client retries with `X-Ark: <address>` or `X-Lightning: <preimage>`; server checks its wallet; single use | BUD-07 + `X-Ark` |
| Tips between people | zap receipt: NIP-57 (Lightning) or Ark Zaps receipt `kind:9741` (Ark) | NIP-57, Ark Zaps |
| Wallet bookkeeping | `lookup_payment` with `payment_type: "ark"` details (address, server key, VTXO ids) | NWC-09 + NWC Ark Payments |

## 5. Where each piece lives

| Piece | Spec / PR | State |
|---|---|---|
| Ark in NWC: `ark` instruction for NWC-321 + `ark` payment type | nostr-wallet-connect/nwc#11 (reworked after benthecarman) | posted |
| NIP-47 core rail-neutral wording | nostr-protocol/nips#2520 | posted |
| Media: `X-Ark` = full BIP-321 | hzrd149/blossom#116 | posted; BIP-321 alignment committed locally |
| Tips: Ark Zaps (pays via NWC-321) | nostr-protocol/nips#2521 | posted + updated |
| Relays: NIP-11 completeness | strfry #278, nostr-rs-relay #257, mattn #36, cagliostr #34, nostream (local) | posted / local |
| Relays: pay per access, both rails, one BIP-321 | strfry plugin, nostr-rs-relay #258, mattn #37, nostream (local) | posted; alignment local |
| Media servers | nostrcheck-server #61/#62 | posted; alignment local |
| People's static payment target | NIP-A3 `payto` with type `ark` (or a BIP-321 / BIP-353 entry) | ⬜ proposal not written |

## 6. Gaps that block "one consistent way"

- **B1, Bark wallet:** prefer same-server `ark=` over Lightning when both are offered (CLI defaults to Lightning today).
- **B2, Bark NWC:** `bark-nwc` must implement NWC-321 `pay`/`receive` (it only has the core NIP-47 methods).
- **B3, Bark:** `create_wallet` ignores the SOCKS proxy.
- **B4, Bark (to verify):** receiving a static Lightning target while offline: BOLT12 offers, or a Lightning address via an
  always-on LNURL bridge (bark-nwc has one). Needed for the static column across Ark servers.
- **S1, spec:** a static payment-target entry for people: propose `ark` as a NIP-A3 `payto` type, or a `bip321` type.
- **C1, clients:** show prices from NIP-11, hand any BIP-321 (relay, Blossom, profile) to NWC-321 `pay`.
- **T1, testing:** cross-Ark across two different Ark servers (only one signet Ark server here; needs a second server or
  ark.zappin.online on mainnet).
