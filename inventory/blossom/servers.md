# Blossom server software inventory: BUD-07 status and Bark payment routes

Researched 2026-10-23. Everything comes from shallow clones (`../clones/`) read with grep. Nothing was built or run.
Machine-readable version: `servers.csv` (51 rows, same directory). Public hosts are in `hosts.md`; the plan is in `summary.md`.
Stars come from the GitHub API (search results plus direct lookups). `last_commit` is the HEAD commit date of the default
branch, except nostrcheck-server, which develops on version branches (0.8.0 was read).
Maintained means: **y** = a commit in the last ~6 months; **unclear** = 6–18 months, or slowing down;
**n** = more than ~18 months; **dead** = 2023 or earlier, or the repo is gone.
Anything marked *(guess)* or *(fingerprint)* is an inference.

Sources: [awesome-blossom](https://github.com/hzrd149/awesome-blossom) (server and library sections),
[awesome-nostr](https://github.com/aljazceru/awesome-nostr) (Blossom, NIP-96 and relay sections),
GitHub repository search (`blossom server`, `topic:blossom`, `BUD-01`, `nip96`, `blossom cashu/lightning/worker/khatru`, …),
npm and crates.io search, hzrd149's repositories, and the toon-protocol research doc's own server table (used as a cross-check).
The hzrd149/blossom README no longer has an implementations list, and its git history never had one.
Deployment counts come from 34,008 kind-10063 user server lists (BUD-03) pulled from purplepag.es, nos.lol, relay.primal.net,
relay.damus.io and yabu.me (`raw/k10063-tally.txt`). Kind 36363 server announcements (used by blossomservers.com) returned only one event, so they were not used.

## What "BUD-07 complete" means

From [buds/07.md](https://github.com/hzrd149/blossom/blob/master/buds/07.md):

- Any endpoint MAY require payment, and then MUST answer **402** with one or more `X-{method}` headers:
  `HEAD /upload`, `PUT /upload`, `HEAD /<sha256>`, `GET /<sha256>`, `HEAD`/`PUT /media`.
- **`X-Cashu`:** a NUT-24 payment request (`creqA…`). The proof is a `cashuB…` token in `X-Cashu`.
- **`X-Lightning`:** a BOLT11 invoice. The proof is the 64-hex preimage in `X-Lightning`.
- HEAD responses only signal. They MUST NOT be retried with proof.
- A bad proof (expired invoice, invalid token) MUST get **400** plus `X-Reason`. It must not get another 402.
- New methods are allowed. Each needs a unique `X-{method}` header and a public spec.
  `X-Ark` is our draft ([hzrd149/blossom#116](https://github.com/hzrd149/blossom/pull/116), spec `hub/specs/blossom-x-ark.md`).
- Implied by browsers: CORS must *expose* the `X-{method}` headers, or web clients cannot read the 402.

## Counts

| | |
|---|---|
| Implementations listed | **51** (48 cloned and read; 2 repos gone; 1 README-only) |
| Maintained (y) | 30 · unclear 10 · n 8 · dead 3 |
| **BUD-07 on the wire** | **3**: nostrcheck-server (Lightning), blob-drop (Cashu), almond (Cashu) |
| 402 without spec headers, or non-spec methods | Satellite CDN (bare 402), SatsAndSports fork (`X-Cashu-Channel`) |
| Stub or scaffolding only | ORLY (`PaymentChecker` placeholder, never called), route96 (`payment_required_with_headers`, never called) |
| Payments outside BUD-07 | route96 (LND quota top-ups), Satellite (zaps for credit), nostr.build (BTCPay plans), HORNETS (on-chain address per npub), wildbloom-node (phoenixd checkout), blossom-account-server (Cashu balances), toon (ILP connector) |
| Deliberately not payment | DEG Mods (`428` + PoW/ad gates) |
| Server software with a usable payment provider interface | route96/payments-rs (`LightningNode`), wildbloom (`LightningBackend` from toll-booth-rs), almond (single `charge()` choke point), nostrcheck (two-way ternary, needs a refactor) |

No implementation implements `X-Lightning` and `X-Cashu` together. No implementation is fully spec-correct on the 400 rule.

## Condensed table (implementations that matter)

| Implementation | Lang | Maint. | Users (10063 lists) | BUD-07 today | Payment backend | Extension point | Bark route |
|---|---|---|---|---|---|---|---|
| [nostrcheck-server](https://github.com/quentintaranpino/nostrcheck-server) | TS | y | cdn.nostrcheck.me 3108; share.yabu.me (JP hub, mostly NIP-96) | **Lightning** (+ non-spec `X-Lightning-Amount`; `X-Cashu` only in CORS) | LNbits or **NWC** | `paymentProvider` ternary in `lib/payments/core.ts` | **0-code: NWC → Bark NWC service**; PR: `barkd.ts` provider + `X-Ark` |
| [route96](https://git.v0l.io/Kieran/route96) | Rust | y | nostr.download 1105, nosto.re 15 | none (quota billing; 413 when over quota) | LND, feature `payments` | **`payments-rs::LightningNode` trait** (but route96 holds a concrete LND client) | `method-barkd` in payments-rs + `dyn LightningNode` in route96; wire the unused 402 helper |
| [blossom-server](https://github.com/hzrd149/blossom-server) | TS/Deno | y | cdn.hzrd149.com 171; ~2,300 more by fingerprint (+1,618 yakihonne, guess) | none | none | Hono middleware | generic BUD-07 provider middleware, then barkd |
| [almond](https://github.com/flox1an/almond) | Rust | y | none seen | **Cashu** (+ `X-Price-Per-MB/-Unit`, `X-Accepted-Mints`) | cdk wallet | `services::cashu::charge()` single choke point | rail trait: Cashu or barkd (`X-Lightning` + `X-Ark`) |
| [blob-drop](https://github.com/hzrd149/blob-drop) | TS/Bun | unclear | none | **Cashu** (NUT-24, spec-correct headers) | cashu-ts | hard-coded `api/upload.ts` | add barkd beside Cashu: reference impl for `X-Ark` |
| [primal-blossom-server](https://github.com/PrimalHQ/primal-blossom-server) | Rust | y | **blossom.primal.net 30,955 (91%)** | none | Primal Premium (off-server) | none | not a BUD-07 target |
| nostr.build ([FOSS PHP](https://github.com/nostrbuild/nostr.build)) | PHP + closed CF worker | y | blossom.band 1253+, blossom.nostr.build 94 | none | BTCPay (annual plans) | BTCPay | BTCPay Ark plugin *(guess)*; business talk |
| [khatru/blossom](https://github.com/fiatjaf/khatru) (nostrlib) | Go fw | y | einundzwanzig 34 *(fingerprint)*; HAVEN installs | none: reject hooks can return 402 but **can't set headers** | none | `RejectUpload/RejectGet` | nostrlib header PR, then the `khatru-bark` Blossom module |
| [blossy](https://github.com/pippellia-btc/blossy) | Go fw | unclear | — | none: same header limit | none | `Hooks.Reject.*` | same enabler PR (pippellia-btc/blossom `Error`) |
| [ORLY](https://git.smesh.lol/orly) | Go | y | — | **stub** (placeholder) | NWC (relay only) | `pkg/blossom/payment.go` | fill the stub with NWC/barkd |
| [Satellite CDN](https://github.com/lovvtide/satellite-cdn) | JS | n | cdn.satellite.earth 689 | bare 402, no headers | zaps (kind 9735) for credit | hard-coded | low priority (stale) |
| [wildbloom-node](https://github.com/forgesworn/wildbloom-node) | Rust | y | — | none (own checkout) | phoenixd, LNURLcash | `LightningBackend` trait | barkd `LightningBackend` |
| [HORNETS](https://github.com/HORNET-Storage/HORNETS-Nostr-Relay) | Go | y | — | none (subscriptions) | on-chain address pool | `lib/subscription` | per-npub Ark address (strfry-plugin shape) |

The long tail (29 more rows: Cloudflare Workers, PHP, OCaml, personal and relay-embedded servers, libraries, caches) is in `servers.csv`.
None of them has payment code.

## Per-implementation notes (top targets)

### 1. nostrcheck-server (TypeScript, MIT, 157★, branch 0.8.0 at 2026-07-25)
- **Where BUD-07 lives:** `src/controllers/media.ts`.
  - `uploadMedia` (L458-505): reads the preimage from `x-lightning` (exactly 64 chars). It looks up the transaction via `sha256(preimage) = paymenthash`.
    If the upload is unpaid, it sets 402, `X-Lightning`, `X-Lightning-amount` and `X-Reason: Invoice (N) for hash: …`.
  - `headMedia` (L577-641), `headUpload` (L1803-1910) and `getMediaStatusbyID` (L911-1066): the same headers on HEAD.
  - `getMediabyURL` (L1140-1316): an unpaid file's `GET` returns **402 with a QR-code image body**,
    plus `X-Lightning`, `X-Lightning-Amount` and `X-Original-Content-Type`. A preimage on GET unlocks the file.
  - CORS (`src/app.ts` L20-29): allows and exposes `X-Cashu, X-Lightning, X-Lightning-Amount, X-Reason`. There is **no Cashu code** at all.
- **Payment model** (different from per-request pay-per-access):
  - Charged per file, to the uploader. The price is linear in size, up to `payments.satoshi.mediaMaxSatoshi`
    (`_calculateSatoshi`, "normal"/"reversed" modes).
  - Until the file is paid, anyone who GETs it sees the invoice. One payment unlocks it for everyone.
  - There is also paid registration (`registerMaxSatoshi`).
  - A double-entry ledger tracks everything (`addJournalEntry`). A prepaid account balance auto-pays new invoices.
    The invoice is also sent to the uploader as a Nostr DM.
- **Backends:** `payments.paymentProvider` is `lnbits` (`lib/payments/lnbits.ts`), or anything else, which means NWC
  (`lib/nostr/NIP47.ts`: `makeInvoice` and `lookupInvoice`, 8 s timeout, one retry).
  The choice is a hard-coded ternary in three places in `lib/payments/core.ts` (L86, L348, `isInvoicePaid` ~L521).
- **Spec gaps:**
  - A wrong or foreign preimage gets a new 402, but the spec requires 400 + `X-Reason`.
  - `X-Lightning-Amount` is non-spec. It is harmless, and its value is redundant with the BOLT11 amount.
  - `X-Cashu` is advertised in CORS but never sent.
  - No `X-Reason` distinguishes "expired" from "unknown".
- **Bark route:**
  - **(a) Zero code:** set `paymentProvider: nwc` with a connection string from a Bark NWC wallet service
    (barkd NWC, bark MRs !2588/!2589/!2662, or the standalone (local notes)). Invoices then come from barkd,
    and are received through the Ark server's Lightning gateway. Pitch this to share.yabu.me and nostrcheck.me operators as configuration only.
  - **(b) PR:** replace the ternaries with a provider map. Add `src/lib/payments/barkd.ts` (invoice + lookup). Then add the Ark rail:
    - `X-Ark` beside each `X-Lightning` in `media.ts` (5 sites), and `X-Ark` in both CORS lists in `app.ts`.
    - Transactions are keyed by `paymenthash`, so Ark rows need an address key (a new column, or reuse `paymentrequest`).
    - `processPendingInvoices` already polls. It can also check barkd history for Ark receipts.
- **Norms:** effectively one maintainer (quentintaranpino: 3239 commits). Small outside PRs merge: imksoo, cameri, SnowCait (Japanese community), Maxblake.
  There is no CONTRIBUTING and no AI policy. **Target branch `0.8.0`, not `main`.**

### 2. route96 (Rust, no licence, 31★ on the GitHub mirror, 2026-10-21)
- **Payments:**
  - Behind the `payments` Cargo feature (off by default), NIP-98 `POST /payment {units, quantity}` creates an LND invoice
    (`src/routes/payment.rs`). It is billed per `unit` (GB storage or egress) per `interval` (day/month/year).
  - `src/background/payments.rs` subscribes to settlements via `payments_rs::lightning::LightningNode::subscribe_invoices`.
    Settled payments raise the user's quota. Free quota defaults to 100 MB.
  - An over-quota upload gets **413**, not 402.
- **BUD-07 scaffolding:** `BlossomResponse.payment_required_with_headers(lightning, cashu)` (`src/routes/blossom.rs` L137-262)
  writes `x-lightning`/`x-cashu`, but no caller uses it. `src/cors.rs` exposes neither header.
- **Extension point:** [v0l/payments-rs](https://github.com/v0l/payments-rs) has `trait LightningNode` (`add_invoice`, `cancel_invoice`, `pay_invoice`, `subscribe_invoices`),
  implemented for LND and the defunct Bitvora behind `method-*` features. route96 itself still holds a concrete `fedimint_tonic_lnd::Client`
  (`routes/mod.rs` L63, `bin/main.rs` L92-111).
- **Bark route:**
  - (1) payments-rs `method-barkd`: `add_invoice` → barkd Lightning receive; `subscribe_invoices` → the barkd notification stream, or polling.
  - (2) route96: `Arc<dyn LightningNode>` plus a backend selector in `PaymentConfig`.
  - (3) Optional: an Ark top-up address per user on `POST /payment`, and per-request 402 with `X-Lightning` + `X-Ark` through the unused helper (also expose the headers in `cors.rs`).
- **Norms:** `AGENTS.md` and `agents/*.md` explicitly support AI coding agents. New functions need 100% function coverage, and every bug fix needs a regression test.
  The canonical forge is git.v0l.io. **There is no licence: ask v0l to add one before contributing** (toon-protocol rejected it for this reason).

### 3. blossom-server (hzrd149, TypeScript/Deno, MIT, 77★, 2026-10-06)
- This is the reference server, by the BUD-07 author. It has no payment code.
- Its fingerprint (Caddy, `Access-Control-Expose-Headers: X-Reason,Content-Range`, `X-Reason: Authorization required`)
  matches cdn.hzrd149.com, blossom.f7z.io, blossom.data.haus, blossom.nmail.li and blossom-0x.uid.ovh: about 2,500 server-list entries (entries, not unique users: one list can name several servers). Yakihonne's server is probably an older version *(guess)*.
- **Route:** add a generic `payments` config and a Hono middleware (`src/middleware/payment.ts`) in front of `PUT`/`HEAD /upload` and `GET /<sha256>`,
  with a provider interface. Ship Lightning (barkd or NWC) and `X-Ark` as providers, and expose the headers in `middleware/cors.ts`.
  This should follow the BUD-07 PR discussion (#116), because the author decides both the spec and this server.
- **Norms:** `AGENTS.md` (370 lines) is written for AI coding agents.

### 4. almond (flox1an, Rust, 5★, v0.5.2, 2026-10-23)
- **BUD-07 (Cashu):** on `PUT /upload`, `PUT /mirror` and `GET /<sha256>`, priced per MB. The `HEAD /upload` price and the 402 are rendered from the same `Quote`.
- **Non-spec headers:** `X-Price-Per-MB`, `X-Price-Unit`, `X-Accepted-Mints`.
- **Self-documented deviations** (`docs/blossom/compliance.md`): the 402 challenge is a JSON object labelled `cashuA`, not a NUT-24 `creqA`; underpayment returns 402, not 400.
- **Route:** everything goes through `services::cashu::charge(state, headers, PaidOperation, size)`.
  Turn it into a rail trait with Cashu and Bark implementations behind a `bark` feature. Fix the two deviations in the same series.
  flox1an is active and agent-friendly (`AGENTS.md`).

### 5. blob-drop (hzrd149, TypeScript/Bun, 7★, 2025-08-31)
- It has the only spec-shaped `X-Cashu` flow. `PUT`/`HEAD /upload` without a token gets 402 + `x-cashu: creqA…`
  (a NUT-18 request derived from `CASHU_PAYOUT`). The retry carries a `cashuB` token.
- **Route:** about 50 lines in `api/upload.ts`: barkd invoice + `X-Lightning`, a fresh Ark address + `X-Ark`, and verification against barkd history.
  It is the cleanest **reference implementation for the X-Ark PR**.

### 6. Framework enablers: khatru/blossom (nostrlib) and blossy
- Both let a reject hook return any status code, so 402 is possible. Neither lets the hook set response headers:
  - khatru's `blossomError` writes only `X-Reason`.
  - pippellia-btc/blossom's `Error{Code, Reason}` is the same.
- A one-type PR on each (headers on the error, or a `PaymentRequired` error) unlocks BUD-07 for every app built on them:
  HAVEN, myriad, swarm, einundzwanzig's server and others.
- After that, `khatru-bark` (already planned for relays) gains a Blossom module.

### 7. Others with payment code
- **ORLY:** `pkg/blossom/payment.go` is an unused placeholder.
  - `CheckPaymentRequired` returns false. `ValidatePayment` returns **true**, so wiring the stub in as-is would be a bypass.
  - The relay already has an NWC client, so filling the stub with NWC (Lightning) and barkd (Ark) is natural.
- **Satellite CDN:** prepaid credit through zaps (an LNURL callback plus a kind 9735 listener). It sends a bare 402 with no `X-*` headers.
  It has been inactive since 2024, and cdn.satellite.earth answers 404 on `HEAD /upload`.
- **SatsAndSports fork:** Cashu Spilman payment channels for HLS video (`X-Cashu-Channel`).
  It is interesting research, but it depends on a local `../../integration-kits` path, so it can't be built standalone.
- **wildbloom-node:** paid storage through a private checkout (phoenixd + LNURLcash). The provider interface is the `LightningBackend` trait from toll-booth-rs,
  so a barkd implementation gives Lightning without touching the node.
- **HORNETS:** subscription tiers paid to a per-npub on-chain address from an address pool. This is the same shape as our per-pubkey Ark address.
- **toon-protocol/blossom:** skips BUD-07 by design (ADR 0003). Payment arrives through the ILP connector as `X-TOON-*`.
- **DEG Mods:** drafts BUD-POW and BUD-Ads, which use `428` precisely so that payment clients don't treat them as 402.
  A potential ally for a unified "gates" BUD.

## Related, not servers

- **nectr/payblob** (`relay.ngit.dev/npub1qnw27…/payblob`): a Rust *client* that pays BUD-07 (Lightning/Cashu) and L402 paywalls to GET/PUT blobs,
  funded by an NWC URI. It is a natural early consumer of `X-Ark`.
- **Clients and libraries:** blossom-client-sdk, @nostr-dev-kit/blossom, nostr-blossom (rust-nostr, "server not implemented"), python-blossom,
  `nak blossom`, Bouquet, Sakura, Bloom (file manager), flower-cache, Morganite. They matter later, for client-side `X-Ark` handling.
- **Test suites:** [v0l/blossom-compliance](https://github.com/v0l/blossom-compliance), [flox1an/will-it-blossom](https://github.com/flox1an/will-it-blossom),
  hzrd149/blossom-audit. A BUD-07 test there would make spec gaps visible (no suite tests BUD-07 today *(guess, not checked)*).
