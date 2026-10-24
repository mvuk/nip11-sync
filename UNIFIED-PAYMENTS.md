# One way to pay across Nostr: the experience map

Status: working design, 24 Oct 2026. Every proposal here is a **draft, open to iteration and revision**: we are still
working out the smoothest payment experience and want feedback. Pieces marked ✅ were tested live on signet with
Bark 0.7.1.

## The principle

**Payments within one Ark server resolve natively over Ark (arkoor), the most sovereign option:** self-custodial
VTXOs with a unilateral exit, instant, near-free, and the recipient can receive while offline. **Between different Ark
servers, and with everyone else, use Lightning** (on-chain is the last resort). Throughout, **build on what already
exists** (BIP-321, NWC-321, NWC-09, NIP-57, NIP-A3, BUD-07) rather than inventing parallel formats.

## 1. One object, one action

- **The object: a BIP-321 URI.** Every payment request anywhere (a relay fee, a media server's 402, a person's
  profile, an invoice) is a BIP-321 URI with one or more instructions:
  `bitcoin:?ark=<ark address>&lightning=<bolt11>&lno=<bolt12 offer>&amount=<btc>`.
  Ark needs no BIP change: BIP-321 says bech32m types use their HRP as the key, so `ark=` (`ark1…` or `tark1…`). ✅
- **The action: NWC-321 `pay(uri, amount?)`** from any Nostr client, or the wallet's own "send" for a scanned or
  pasted URI. **The wallet, never the client, picks the instruction.**

## 2. Actors

| Actor | Role | Examples |
|---|---|---|
| **Payer client** | Finds the BIP-321 request, asks the user to confirm (and for an amount if the request has none), hands it to the wallet, publishes zap events | Nostter, Lumilumi, Rabbit, Penyotter, Damus, Amethyst, Primal |
| **Payer wallet (NWC)** | Parses the URI, picks the rail, pays, reports a payment record (`instruction_type`, `details`) | bark-nwc over a Bark wallet; any NWC wallet with NWC-321 |
| **Payee wallet / service** | Issues requests (`receive`), receives, confirms payments; for zaps, holds the `receipt-key` and signs receipts | barkd behind a relay or Blossom server; bark-nwc as a person's receipt-key service |
| **Relay** | Advertises prices (NIP-11 `fees`, `payments_url`), issues a BIP-321 per pubkey, credits the pubkey | yabu.me (strfry), nostr-rs-relay, mattn/nostr-relay, nostream |
| **Media server** | Answers `402` with `X-Ark` (a BIP-321 URI) and `X-Lightning`, checks the proof on retry | share.yabu.me (nostrcheck-server), route96, blossom-server |
| **Ark servers** | Cosign arkoor payments between their users, hold them for offline recipients (mailbox), run a Lightning gateway | ark.zappin.online, Second's signet server |
| **Lightning** | Connects everything else: different Ark servers, plain Lightning wallets, LNURL/Lightning addresses | any node; each Ark server's gateway |

## 3. The rail decision

The wallet runs this for every `pay(uri, amount)`, in order, and pays exactly one instruction:

```
pay(bitcoin:?ark=…&lno=…&lightning=…&sp=…, amount)
 │
 ├─1─ an ark= that commits to MY Ark server (v0 server key / v1 ark_id)?   → arkoor, direct           ✅ checked by the wallet
 │       (several ark=, one per server, are allowed; foreign ones are skipped)                         ✅ Bark rejects foreign ark=
 ├─2─ otherwise Lightning: lightning= (BOLT11) or lno= (BOLT12)            → via my node / my Ark server's gateway  ✅
 ├─3─ otherwise on-chain: sp= or the URI address                           → slow, last resort
 └─4─ nothing payable                                                     → UNSUPPORTED_PAYMENT_INSTRUCTION, no money moves ✅
```

A wallet **SHOULD prefer (1) over (2)** when both qualify. ⚠️ The Bark CLI currently defaults to Lightning in that
case (B1). Clients never match servers, and no request carries an `ark-server` field: the address commits to its
server.

## 4. Two kinds of request

| | Dynamic (per payment) | Static (a person, reusable) |
|---|---|---|
| Used by | relay fees, Blossom 402s, "pay me exactly X" | profiles, tips, zaps |
| Issuer online? | yes, it issues the request | not necessarily |
| Instructions | **fresh** `ark=` + `lightning=` BOLT11 (+ `lno=`), with `amount` | **static** `ark=` (one per Ark server) + `lno=` BOLT12, optionally `sp=`; never BOLT11, never `amount` |
| Where it appears | NIP-11 `payments_url` / relay `/pay`; relay `restricted:` message; Blossom `X-Ark`; NWC-321 `receive` | NIP-A3 `["payto", "bip321", "<uri>"]` in `kind:10133`; BIP-353 `₿user@domain` resolving to the same kind of URI; `lightning` payto / `lud16` as fallback |
| Proof | the fresh address / invoice itself | a zap receipt (`kind:9741`), or nothing (a plain tip) |

## 5. The flows

Summary (details below):

| Flow | Request comes from | Pay call | Rail picked | Proof / receipt | Spec | Status |
|---|---|---|---|---|---|---|
| a. Relay fee | NIP-11 `payments_url` / relay message → dynamic URI | `pay(uri)` | same-server Ark, else BOLT11 | relay's wallet sees the receive, credits the pubkey | NIP-11 + per-implementation backends | posted (relays); gap: client UI, a NIP for the request |
| b. Upload / download | Blossom `402` `X-Ark` (+ `X-Lightning`) | `pay(uri)` | same-server Ark, else BOLT11 | retry with `X-Ark: <address>` or `X-Lightning: <preimage>`, single use | BUD-07 + `X-Ark` | posted (spec, nostrcheck) |
| c. Tip a person | profile `kind:10133` `bip321` (or BIP-353) → static URI | `pay(uri, amount)` | same-server Ark, else `lno=`, else on-chain | none public; payer's wallet record | NIP-A3 `bip321` + NWC-321 | local (NIP-A3 PR) |
| d. Zap a note | same static URI + `receipt-key` | `pay(uri, amount)` + `kind:9740` | same as (c) | `kind:9741` signed by the receipt key; `9735` for legacy | Zaps over BIP-321 rails (#2521 v2) + NIP-57 | v1 posted, v2 local |
| e. Exact amount | payee's wallet `receive(amount)` → dynamic URI, shared as QR / DM | `pay(uri)` | same-server Ark, else BOLT11/BOLT12 | payee's wallet: fresh address / invoice, `payment_received` | NWC-321 `receive` + NWC Ark Payments | spec posted; gap B2 |
| f. Receive offline | static URI | (any) | Ark mailbox; Lightning needs B4 | receipt delayed until the receipt key is online | same as (c)/(d) | Ark ✅; Lightning gap B4 |
| g. Cross-Ark | any URI with a foreign `ark=` | `pay(uri)` | Lightning, gateway → gateway | as for the flow it is part of | BIP-321 + NWC-321 | dynamic ✅ one-server; two-server test T1 |
| h. Lightning ↔ Ark | any URI, or a Lightning address | `pay(uri)` / `pay_invoice` | Lightning | NIP-57 `9735` or the flow's own proof | NIP-57, BIP-321 | works today ✅; offline static via B4 |

### a. Pay a relay fee

- **Request:** the client reads NIP-11 `fees` (admission, subscription, publication) and shows the price. To pay, it
  fetches a URI from the relay (`payments_url`, or the relay's `/pay`), or receives one in a `restricted:` message.
  The relay issues a **fresh** `ark=` + `lightning=` with `amount`, bound to the user's pubkey.
- **Pay:** `pay(uri)`. **Rail:** same-server Ark if the relay's wallet is on the user's Ark server, else BOLT11.
- **Proof:** the relay's own wallet (barkd) sees the payment on that fresh address or invoice and credits the pubkey.
  No proof travels back through the client.
- **Spec:** NIP-11 (`fees`, `payments_url`); payment backends per implementation. A NIP for "how to pay" in NIP-11
  comes later, once code works, and will advertise a BIP-321 request rather than a new format.
- **Status:** NIP-11 completeness posted: strfry [#278](https://github.com/hoytech/strfry/pull/278), nostr-rs-relay
  [#257](https://github.com/scsibug/nostr-rs-relay/pull/257), mattn [#36](https://github.com/mattn/nostr-relay/pull/36),
  cagliostr [#34](https://github.com/mattn/cagliostr/pull/34). Backends posted: strfry plugin
  [strfry-bark-paid-writes](https://github.com/mvuk/strfry-bark-paid-writes), nostr-rs-relay
  [#258](https://github.com/scsibug/nostr-rs-relay/pull/258), mattn [#37](https://github.com/mattn/nostr-relay/pull/37);
  nostream local. Gap: client UI (C1).

### b. Pay for an upload or download

- **Request:** the Blossom server answers `402` with `X-Ark: bitcoin:?ark=<fresh>&lightning=<bolt11>&amount=…` next
  to `X-Lightning`.
- **Pay:** `pay(<X-Ark value>)`. **Rail:** same-server Ark, else the BOLT11 in the same URI.
- **Proof:** the client retries with `X-Ark: <address>` (Ark) or `X-Lightning: <preimage>`; the server checks its own
  wallet. Each address or preimage is single use.
- **Spec:** BUD-07 + `X-Ark`, [hzrd149/blossom#116](https://github.com/hzrd149/blossom/pull/116).
- **Status:** spec posted; nostrcheck-server (runs share.yabu.me)
  [#61](https://github.com/quentintaranpino/nostrcheck-server/pull/61) /
  [#62](https://github.com/quentintaranpino/nostrcheck-server/pull/62) posted. Other servers and clients: gap.

### c. Tip a person

- **Request:** the person's `kind:10133` `["payto", "bip321", "bitcoin:?ark=…&lno=…"]`, or a BIP-353 name that resolves
  to the same kind of URI. A `lightning` payto entry or `lud16` is the fallback for wallets without BIP-321.
- **Pay:** the client asks for an amount, then `pay(uri, amount)`. **Rail:** same-server Ark, else `lno=`, else
  on-chain.
- **Proof:** none public: a tip is a private payment. The payer's wallet keeps the record.
- **Spec:** NIP-A3 `bip321` type (small PR, local), NWC-321, NWC Ark Payments
  ([nwc#11](https://github.com/nostr-wallet-connect/nwc/pull/11)).
- **Status:** NIP-A3 PR ready locally. Gaps: clients (C1), bark-nwc `pay` (B2), wallets publishing the entry.

### d. Zap a note

- **Request:** as (c), plus a `receipt-key` tag in the same `kind:10133` (the opt-in).
- **Pay:** `pay(uri, amount)`, no `payer_note`; then the client publishes `kind:9740` with `p`/`e`/`a`/`k`, `amount`,
  `rail`, and a NIP-44 encrypted reference (Ark: VTXOs + address; Lightning: payment hash; on-chain: txid).
- **Rail:** as (c).
- **Receipt:** the receipt-key holder finds the payment in its wallet and signs one `kind:9741`, the same kind for every
  rail. Clients count `9741` + `9735` with one `#e` filter. Recipients with only a Lightning address get NIP-57 zaps.
- **Trust:** as NIP-57 (the recipient's side vouches); senders cannot inflate totals; the reference binds the sender.
- **Spec:** Zaps over BIP-321 rails, [nostr-protocol/nips#2521](https://github.com/nostr-protocol/nips/pull/2521) (v1
  posted as "Ark Zaps"; v2 local), NIP-57.
- **Status:** spec v2 ready locally. Gaps: a receipt-key service (B5), clients.

### e. Pay a person an exact amount (dynamic request)

- **Request:** the payee's client calls NWC-321 `receive(amount)`; the wallet returns
  `bitcoin:?ark=<fresh>&lightning=<bolt11>&lno=…&amount=…`. It travels as a QR code or a NIP-17 DM. No new event kind.
- **Pay:** `pay(uri)`. **Rail:** same-server Ark, else Lightning.
- **Proof:** the payee's wallet sees the payment on that fresh address or invoice (`payment_received` notification,
  `lookup_payment` with `payment_type: "ark"`).
- **Spec:** NWC-321 `receive`, NWC Ark Payments ([nwc#11](https://github.com/nostr-wallet-connect/nwc/pull/11)),
  NWC-09; NIP-47 core rail-neutral wording [nips#2520](https://github.com/nostr-protocol/nips/pull/2520).
- **Status:** specs posted. Gap: bark-nwc `receive` (B2).

### f. Receive while offline

- **Same Ark server:** works today. The Ark server holds the arkoor payment in the recipient's mailbox; the wallet
  collects it when it comes back. ✅
- **Different Ark server or plain Lightning:** the payer pays `lno=`, so someone must answer the BOLT12 invoice request
  and receive the HTLC for the recipient; or a Lightning address served by an always-on LNURL bridge (bark-nwc has
  one). To verify and build: **B4**.
- **On-chain:** always works offline.
- **Zap receipts:** delayed until the receipt-key holder is online; zaps show as pending to the sender until then.

### g. Cross-Ark (payer on server A, payee on server B)

- **Request:** any URI whose `ark=` commits to B.
- **Pay:** `pay(uri)`. The wallet on A skips the foreign `ark=` ✅ and pays the Lightning instruction through A's
  gateway; B's gateway receives it into the payee's Bark wallet.
- **Dynamic requests** carry BOLT11, so this works whenever the payee's side is online ✅ (fallback tested on one
  server). **Static requests** need `lno=` or a Lightning address that works while the payee is offline (B4).
- **A payee on several servers** can list one `ark=` per server in the same URI; the payer's wallet picks its own.
- **Status:** needs a real two-server test (T1).

### h. Plain Lightning user ↔ Ark user

- **Lightning wallet paying an Ark user:** it ignores `ark=` (an unknown, non-`req-` BIP-321 key) and pays
  `lightning=` / `lno=`, or the Lightning address. NIP-57 zaps keep working when the Ark user has a NIP-57 Lightning
  address (bark-nwc's LNURL bridge).
- **Ark user paying a Lightning user:** the Lightning user's invoice, offer or address; the Ark wallet pays through its
  server's gateway ✅. NIP-57 zaps work unchanged (`pay_invoice`).
- **Status:** works today; offline static receive for the Ark side depends on B4.

## 6. Where each piece lives

| Piece | Spec / PR | State |
|---|---|---|
| Ark in NWC: `ark` instruction for NWC-321 + `ark` payment type | [nostr-wallet-connect/nwc#11](https://github.com/nostr-wallet-connect/nwc/pull/11) | posted (reworked) |
| NIP-47 core rail-neutral wording | [nostr-protocol/nips#2520](https://github.com/nostr-protocol/nips/pull/2520) | posted |
| Media: `X-Ark` = full BIP-321 | [hzrd149/blossom#116](https://github.com/hzrd149/blossom/pull/116) | posted |
| Profile payment link: NIP-A3 `bip321` | NIP-A3 PR | ready locally |
| Zaps over BIP-321 rails | [nostr-protocol/nips#2521](https://github.com/nostr-protocol/nips/pull/2521) | v1 posted; v2 ready locally |
| Relays: NIP-11 completeness | strfry #278, nostr-rs-relay #257, mattn #36, cagliostr #34; nostream local | posted / local |
| Relays: pay per access, one BIP-321 | strfry plugin, nostr-rs-relay #258, mattn #37; nostream local | posted / local |
| Media servers | nostrcheck-server #61 / #62 | posted |

## 7. Roadmap (dependency order)

Each step unblocks the ones below it. Owners in brackets.

1. **Specs out for review** [Matthew / Second]
   - post the NIP-A3 `bip321` PR, then push #2521 v2 and comment (both depend on nothing else);
   - keep nwc#11, nips#2520 and blossom#116 in step with this map;
   - later, once code works: a small NIP-11 addition that advertises a BIP-321 request (no new format).
2. **Bark wallet** [Bark team]
   - **B1** prefer a same-server `ark=` over Lightning when both are offered (CLI defaults to Lightning today);
   - **B3** `create_wallet` honours the SOCKS proxy (patch ready, needs an MR).
3. **bark-nwc** [Bark team], needs B1
   - **B2** NWC-321 `pay` and `receive`, with `ark` payment records in `lookup_payment`, `list_transactions` and
     notifications (NWC Ark Payments);
   - **B5** receipt-key service: watch `kind:9740`, confirm by reference, sign `kind:9741`; publish the user's
     `kind:10133` (`bip321` + `receipt-key`).
4. **Offline cross-Ark receive** [Bark team]
   - **B4** a static Lightning target that works while the wallet is offline: BOLT12 offers answered by the Ark
     server or an always-on service, or a Lightning address via bark-nwc's LNURL bridge.
5. **Servers** [Second, with each project's maintainers], needs B2 for end-to-end tests
   - relays: land the posted PRs; nostream; then khatru / nostrlib (Haven, wot-relay, pyramid), Ditto, the long tail;
   - Blossom: nostrcheck (share.yabu.me) first; then route96, blossom-server, blob-drop, khatru/blossy, almond.
6. **Clients** [client maintainers, with our PRs], needs B2 and the specs
   - Japanese first: **Nostter, Lumilumi, Rabbit, Penyotter**; then **Damus, Amethyst, Primal**, noStrudel, Jumble, Ditto;
   - per client: hand any BIP-321 to NWC-321 `pay`; show NIP-11 prices and pay relays; handle `402` + `X-Ark`; read and
     write the `bip321` profile entry; the rail-neutral zap button and `9741` counting.
7. **Testing** [Second]
   - **T1** cross-Ark across two Ark servers on signet (stand up a second server), flows (c), (d), (g), (h);
   - one real paid relay write and paid upload on signet, end to end through bark-nwc;
   - **T2** mainnet with the Japanese community on **ark.zappin.online** (contact Zappin first).

## 8. What a user experiences

**Yuki tips a friend (Japan, ark.zappin.online).** Yuki and Haru both have wallets on ark.zappin.online. Yuki taps
"tip" on Haru's profile in Nostter and types 21 sats. Nostter hands Haru's `bitcoin:?ark=…&lno=…` to Yuki's wallet,
which sees Haru's address is on its own server and pays it over Ark: done in a second, no fee to speak of, even though
Haru's phone is off. A zap works the same way, and the zap count goes up once Haru's wallet service signs the receipt.
Yuki's other friend uses a different Ark server: same tap, and the wallet quietly pays over Lightning instead.

**Paying a relay.** Lumilumi shows "yabu.me: 100 sats / month for writes" from the relay's NIP-11. Ken taps "subscribe",
confirms, and his wallet pays the URI the relay issued for his pubkey: over Ark if the relay's wallet is on his Ark
server, otherwise Lightning. The relay sees the payment in its own wallet, and his next post is accepted.

**Sharing an image on share.yabu.me.** Mika attaches a photo in Rabbit. The upload comes back `402` with an `X-Ark`
URI; Rabbit asks "Pay 3 sats to upload?", her wallet pays, and Rabbit retries with the proof. The image is up and
the post goes out. She never saw the words Ark, Lightning or BIP-321.
