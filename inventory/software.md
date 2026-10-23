# Nostr relay software inventory: NIP-11 gaps and Bark payment routes

Researched 2026-10-23. Everything comes from shallow clones read with grep. Nothing was built or run.
Machine-readable version: `software.csv` (108 rows, same directory).
Stars come from shields.io (GitHub). `last_commit` is the HEAD commit date of the default branch.
Maintained means: **y** = a commit in the last ~6 months; **unclear** = 6–18 months, or slowing down;
**n** = more than ~18 months; **dead** = 2023 or earlier, or the repo is gone.
Anything marked *(guess)* is a guess.

Sources for the inventory: [awesome-nostr](https://github.com/aljazceru/awesome-nostr) relays section,
[awesome-nostr-japan](https://github.com/nostr-jp/awesome-nostr-japan) `_data/relay-implementations.yml`,
the [soapbox-pub GitLab group](https://gitlab.com/soapbox-pub), fiatjaf's nostrlib, and the sibling `relays.csv`
for software seen in live deployments. nostr.watch API v2 returns 402 (paywalled), so it was skipped.

## What "NIP-11 complete" means

From the current spec ([11.md](https://raw.githubusercontent.com/nostr-protocol/nips/master/11.md)):

- **Top level:** `name, description, banner, icon, pubkey, self, contact, supported_nips, software, version, terms_of_service`
- **`limitation`:** `max_message_length, max_subscriptions, max_limit, max_subid_length, max_event_tags,
  max_content_length, min_pow_difficulty, auth_required, payment_required, restricted_writes,
  created_at_lower_limit, created_at_upper_limit, default_limit`
- **Pay-to-relay:** `payments_url`, plus `fees.admission[] / fees.subscription[] (with period) / fees.publication[] (with kinds)`
- **CORS:** the `Access-Control-Allow-Origin/Headers/Methods` headers are a MUST.

The current spec no longer contains `retention`, `relay_countries`, `language_tags`, `tags` or `posting_policy`.
Many implementations still emit them, which is harmless.

## Condensed table (major implementations)

| Implementation | Lang | Maint. | Deployments seen | NIP-11 status | Payments today | Bark route |
|---|---|---|---|---|---|---|
| [strfry](https://github.com/hoytech/strfry) | C++ | y | 39+3 (damus, nos.lol, primal…) | partial: no `payments_url`/`fees`, only 3 of 13 limitation fields | none | **writePolicy plugin + bark-pay sidecar** |
| [nostr-rs-relay](https://git.sr.ht/~gheartsfield/nostr-rs-relay) | Rust | unclear | 3 | partial; **bug: emits `payment_url`** | LN admission + per-event (ClnRest, LNbits) | **`PaymentProcessor` trait impl** or gRPC nauthz sidecar |
| [nostream](https://github.com/Cameri/nostream) | TS | y | 2–3 | near-full (missing `fees.subscription`, `publication.kinds`) | LN admission + plans (zebedee, lnbits, lnurl, nodeless, opennode, nwc) | **`IPaymentsProcessor` impl** |
| [khatru](https://github.com/fiatjaf/khatru) / nostrlib | Go fw | y | 9 (family) | framework can serve everything except `terms_of_service` | none | **Go middleware `khatru-bark`** |
| [Haven](https://github.com/bitvora/haven) | Go/khatru | y | (family) | partial (6 fields) | none | khatru-bark (NIP-11 PR is the main ask) |
| [wot-relay](https://github.com/bitvora/wot-relay) | Go/khatru | unclear | 4 | partial (7 fields) | none | khatru-bark ("pay to bypass WoT") |
| [pyramid](https://github.com/fiatjaf/pyramid) | Go/khatru | y | 1 | partial | none | khatru-bark ("pay to join") |
| [Chorus](https://github.com/mikedilger/chorus) | Rust | unclear | 0 | partial; `payment_required` hard-coded false | none | **NIP-86 `allowpubkey` sidecar** |
| [rnostr](https://github.com/rnostr/rnostr) | Rust | unclear | 0 | full via free-form config | none | `Extension` trait impl |
| [Ditto relay](https://gitlab.com/soapbox-pub/ditto-relay) | TS/Bun | y | 3 | partial | none | Nostrify policy (low priority) |
| [ORLY](https://git.smesh.lol/orly) | Go | y | 0 | partial; sells subscriptions but emits no `fees`/`payments_url` | NWC monthly subscription | processor refactor + barkd backend |
| [nosflare](https://github.com/Spl0itable/nosflare) | TS/CF Workers | y | 1 | partial (`payments_url` + `fees.admission` when paid) | zap-to-relay admission | pluggable provider calling a public bark-pay endpoint |
| [mattn/nostr-relay](https://github.com/mattn/nostr-relay) | Go/relayer | y | 1 | partial (empty `fees`, `payments_url` "") | none | small PR + allowlist sidecar |
| [cagliostr](https://github.com/mattn/cagliostr) | C++ | y | 1 | partial (hard-coded, `fees:{}`) | none | PR to make it configurable |
| [searchnos](https://github.com/darashi/searchnos) | Rust | y | 1 | partial (5 fields) | none | NIP-11 PR only |
| [grain](https://github.com/0ceanslim/grain) | Go | y | 0 | partial (rich config, no `fees`) | none | NIP-86 / whitelist sidecar |
| [Citrine](https://github.com/greenart7c3/Citrine) | Kotlin | y | phones | partial (no limitation) | none | N/A (NIP-11 PR only) |
| [Netstr](https://github.com/bezysoftware/netstr) | C# | n | 0 | partial | none | C# middleware (low priority) |
| [relay.tools relaycreator](https://github.com/relaytools/relaycreator) | TS (strfry manager) | y | in strfry count | good for paid relays | LNbits admission | barkd backend next to LNbits |
| [LNbits nostrrelay](https://github.com/lnbits/nostrrelay) | Python | y | 0 | partial (no `fees`) | LN join + storage cost | **barkd as an LNbits funding source** |
| nostr.wine / NFDB (nostr.land) | closed | y | 3 / 4 | nostr.wine full; NFDB partial (no `fees` live, though the spec example shows nostr.land fees) | LN | outreach only |

## Per-implementation notes (top 12)

### 1. strfry (C++, GPL-3.0, 733★, last commit 2026-09-04)
- **NIP-11 handler:** `src/apps/relay/RelayWebsocket.cpp` L82–119 `getServerInfoHttpResponse()`. It is built from `relay.info.*` in `strfry.conf`.
  - Fields served: name, description, contact, pubkey, icon, banner, self, terms_of_service, privacy_policy (non-spec), supported_nips (adds 42/45/77 when those features are on), software, version, negentropy (non-spec).
  - `limitation` has only `max_message_length`, `max_subscriptions` and `max_limit`.
  - CORS: `Access-Control-Allow-Origin: *`.
- **Gap to complete:** `payments_url`, `fees.*`, `limitation.{auth_required, payment_required, restricted_writes, max_subid_length, max_event_tags, max_content_length, min_pow_difficulty, created_at_lower/upper_limit, default_limit}`.
  - Most of these values already exist in config: `relay.auth.enabled`, `maxFilterLimit`, `rejectEventsOlderThanSeconds` and so on.
  - Upstream PR: add `relay.info.paymentsUrl` and `relay.info.fees.{admission,subscription,publication}`, and derive the limitation flags from existing config (golpe.yaml + RelayWebsocket.cpp).
- **Payment extension point:** the writePolicy plugin (`docs/plugins.md`). It is an external executable that talks JSONL over stdin/stdout. The input includes `authed`, the NIP-42 pubkey.
- **Bark route:** `strfry-bark`, a small writePolicy plugin.
  - It accepts if `event.pubkey` (or `authed`) is in a paid set, and otherwise rejects with `restricted: pay at <payments_url>`.
  - The paid set is kept by a bark-pay sidecar (HTTP) in front of barkd. The sidecar serves `/pay`: a Lightning invoice through captaind's gateway, plus an Ark address for arkoor. It polls barkd for receipt and writes a membership DB the plugin reads.
  - relay.tools already runs strfry with a paywall, which shows the pattern works in production.
- **Contribution norms:** no CONTRIBUTING.md. Issues and PRs go through GitHub. `docs/community.md` explicitly invites "please open a PR" to list third-party integrations, so that is where the Bark plugin can be listed.

### 2. nostr-rs-relay (Rust, MIT, 724★, last commit 2026-05-22)
- **NIP-11 handler:** `src/info.rs` (`impl From<Settings> for RelayInfo`), served from `src/server.rs` L170.
  - Serves: id (non-spec), name, description, pubkey, contact, icon, supported_nips, software, version.
  - `limitation{payment_required, restricted_writes}`, `fees{admission, publication}` (msats).
- **Bug:** the struct field is `payment_url`, so it serializes `"payment_url"` and not the spec's `"payments_url"` (`src/info.rs`).
- **Gap:** banner, self, terms_of_service (it exists in `[pay_to_relay]` config but is not emitted), 11 limitation fields, `fees.subscription`, and `publication[].kinds`.
- **Payment extension points:**
  - `trait PaymentProcessor { get_invoice(keys, amount); check_invoice(payment_hash) }` in `src/payment/mod.rs`, selected through `enum Processor { LNBits, ClnRest }`.
  - Config is `[pay_to_relay]`: `admission_cost`, `cost_per_event`, `node_url`, `api_secret`, `rune_path`.
  - Separately, a gRPC `EventAdmit` authorization hook (`proto/nauthz.proto`, `docs/grpc-extensions.md`). [keychat-relay-ext](https://github.com/keychat-io/keychat-relay-ext) uses it for per-message Cashu payments.
- **Bark route:**
  - (a) Add `src/payment/barkd.rs` with `BarkdPaymentProcessor` and `Processor::Barkd`. This covers Lightning directly. arkoor needs `InvoiceInfo` extended with an optional Ark address, because the trait is bolt11/payment_hash-shaped.
  - (b) No fork needed: a gRPC nauthz sidecar admits pubkeys that paid through barkd. This follows the keychat precedent.
  - Bundle the `payments_url` fix with either one.
- **Contribution norms:** sourcehut is canonical, with patches by email to the sr.ht list. The list name is a guess: `~gheartsfield/nostr-rs-relay-devel`. GitHub is a mirror. There is no CONTRIBUTING file and no AI policy. The maintainer is slow (last commit in May).

### 3. nostream (TypeScript, MIT, 832★, last commit 2026-10-23)
- **NIP-11 handler:** `src/handlers/request-handlers/root-request-handler.ts`. This is the most complete open-source implementation.
  - Serves everything in the spec except `fees.subscription` and `publication[].kinds`. Fees are built from `feeSchedules.{admission,publication}` and always use `unit: msats`.
  - `auth_required` is hard-coded `false`.
  - `payments_url` = `<relay>/invoices`. CORS is set.
  - Non-spec extras: `max_filters`, `max_filter_values`, `min_prefix`, `search_supported`, `supported_nip_extensions`.
- **Payments:** `IPaymentsProcessor { createInvoice; getInvoice }` in `src/@types/clients.ts`.
  - The factory is `src/factories/payments-processor-factory.ts`.
  - Implementations live in `src/payments-processors/`: zebedee, lnbits, lnurl, nodeless, opennode, nwc, null. Callback controllers are in `src/controllers/callbacks/`.
  - Supports admission fees, recurring `subscriptionPlans` (amount picks the plan), and `invoiceExpirySeconds`.
- **Bark route:** add `barkd-payments-processor.ts`, a factory case `'barkd'`, and settings `paymentsProcessors.barkd{baseURL, token}`.
  - Poll barkd for settlement, the same way lnurl/nwc work, or add a callback controller.
  - arkoor: extend the Invoice model with an optional `arkAddress` and show both on the /invoices page.
  - In the same PR, emit `fees.subscription` with `period` from `subscriptionPlans`.
- **Contribution norms:** `CONTRIBUTING.md`.
  - Issue-first: every PR must link an issue. Keep PRs focused; an unworked assignment expires after 7 days.
  - There is a CODE_OF_CONDUCT and a very active flow of external PRs (#916 merged 2026-10-23). No AI policy found.
  - **This is the best first upstream target.**

### 4. khatru / fiatjaf nostrlib (Go framework, Unlicense)
- **NIP-11:** `khatru/nip11.go` `HandleNIP11` encodes `rl.Info` and auto-adds NIPs 9/45/77. `OverwriteRelayInformation` is a per-request hook.
  - The struct in the new `fiatjaf.com/nostr/nip11/types.go` has `name, description, pubkey, self, contact, supported_nips, software, version, limitation (all 13), payments_url, fees{admission, subscription(period), publication(kinds)}, icon, banner`. It is **missing `terms_of_service`**.
  - The legacy `github.com/nbd-wtf/go-nostr/nip11` struct also lacks `self`. Haven and the older apps still use it.
- **Status:** the GitHub repo is in maintenance mode. Development happens in nostrlib, served over ngit at `relay.ngit.dev/npub180cvv…/nostrlib.git` (HEAD 2026-10-22).
- **Hooks:**
  - New API: `OnEvent`, `OnRequest`, `OnConnect`, `OnAuth`, `RejectConnection`, `OverwriteRelayInformation`, `ManagementAPI` (NIP-86 `AllowPubKey`…).
  - Old API: `RejectEvent[]`, `RejectFilter[]`, `OnConnect[]`.
- **Bark route:** one Go module, `khatru-bark`, provides:
  - `OnEvent` policy (reject unpaid with `restricted:` and the pay URL)
  - `OnRequest` policy for paid reads (optional)
  - an `http.Handler` for `/pay` (barkd invoice + Ark address + status polling)
  - an `OverwriteRelayInformation` func that fills `Fees`, `PaymentsURL` and `Limitation.{PaymentRequired,RestrictedWrites}`
  - an optional NIP-86 `allowpubkey` bridge

  Ship two thin adapters, one for go-nostr/khatru v0.x and one for nostrlib. Upstream patch to nostrlib: add `TermsOfService`.
- **Covers:** Haven, wot-relay, pyramid, relay29/groups-relay, triflector, zooid, swarm, SW2, chronicle, algo-relay, jingle and hns-relay. That is 9 deployments seen today.

### 5. Haven (Go, MIT, 206★, last commit 2026-08-26)
- **NIP-11:** each of its 4 sub-relays (private/chat/inbox/outbox) sets `Name, Description, Icon, PubKey, Software, Version` in `init.go`.
- **Gap:** limitation (it should say `auth_required`/`restricted_writes` for the private and chat relays), banner, contact, terms_of_service.
- **Payments:** none, and Haven is a personal relay. Policies are in `policies.go` (whitelist/WoT); NIP-86 is in `nip86.go`.
- **Bark route:** a NIP-11 completeness PR first. khatru-bark is an optional "paid inbox" feature *(guess at demand)*.
- **Norms:** no CONTRIBUTING; community PRs on GitHub.

### 6. wot-relay (Go, no LICENSE file, 88★, last commit 2026-04-22)
- **NIP-11:** `main.go` L146 sets name, description, contact, icon, software (`github.com/barrydeen/wot-relay`), version, pubkey.
- **Gap:** limitation (`restricted_writes: true` is accurate, because writes are WoT-gated), banner, self, terms_of_service.
- **Hook:** `relay.OnEvent = policies.SeqEvent(...)` (nostrlib khatru).
- **Bark route:** khatru-bark as "pay to bypass WoT" admission.
- **Note:** there is no LICENSE file, so ask for a license in the same PR. This is the most-deployed khatru app (4 deployments seen).

### 7. Chorus (Rust, MIT, 86★, last commit 2026-04-30)
- **NIP-11:** `src/web/nip11.rs` `build_rid()`, a hand-built JSON string.
  - Serves supported_nips, software, version, name, description, banner, icon, terms_of_service, retention, and `limitation{auth_required, payment_required:false, restricted_writes, max_message_length, max_subscriptions}`.
  - CORS: `*`.
- **Gap:** `payments_url`, `fees`, `self`, `contact`, 8 limitation fields. The contact pubkey is read from config but never written (it looks like a bug).
- **Payments:** none. There is a NIP-86 management API (`src/web/management/mod.rs`).
- **Bark route:** a NIP-86 sidecar. bark-pay receives the payment, then calls `allowpubkey` on the relay's NIP-86 endpoint, signed with an admin key using NIP-98. No fork is needed. Separately, a small PR to emit fees/payments_url from config.
- **Norms:** single maintainer (Mike Dilger), GitHub, no CONTRIBUTING.

### 8. rnostr (Rust, MIT, 126★, last commit 2026-06-06)
- **NIP-11:** `relay/src/setting.rs`. `[information]` and `[limitation]` are free-form maps, so `payments_url`, `fees`, `banner` etc. can **already be configured** (the tests in setting.rs set `payments_url`).
- **Gap:** only the defaults are sparse. It is complete by configuration.
- **Extension point:** the `Extension` trait (`relay/src/extension.rs`: `setting`, `config_web`, `connected`, `disconnected`, `message -> Continue/Stop`). Existing extensions: auth, count, metrics, rate_limiter, search.
- **Bark route:** an `rnostr-bark` extension. `message()` blocks EVENT from unpaid pubkeys, and `config_web()` mounts `/pay` backed by barkd.
- **Norms:** GitHub, no CONTRIBUTING, low activity.

### 9. ORLY (Go, AGPL-3.0, last commit 2026-09-16)
- **NIP-11:** `app/handle-relayinfo.go` (around L186). Serves name, description, pubkey, supported_nips, software, version, icon, `limitation{auth_required, restricted_writes, payment_required (= MonthlyPriceSats>0)}`, plus non-spec addresses/graph/theme.
- **Gap:** `payments_url`, `fees.subscription`, banner, self, contact, terms_of_service, 10 limitation fields. It charges a subscription but does not advertise it.
- **Payments:** Lightning via NWC (`ORLY_NWC_URI`, `ORLY_MONTHLY_PRICE_SATS` default 6000/month), in `app/payment_processor.go` and `app/autopay_nwc.go`. It is NWC-specific, not an interface *(guess from file layout)*.
- **Bark route:** refactor `payment_processor.go` behind an interface and add a barkd backend (LN + arkoor). Emit `fees.subscription[{amount, unit: msats, period: 2592000}]` and `payments_url`.
- **Norms:** `CONTRIBUTING.md`, `CLAUDE.md`, `AGENTS.md`. Development is heavily AI-assisted. The canonical repo is on nostrdev/smesh gitea, not GitHub.

### 10. nosflare (TypeScript on Cloudflare Workers, MIT, 115★, last commit 2026-06-18)
- **NIP-11:** `src/config.ts` relayInfo plus `handleRelayInfoRequest`. Serves `limitation{auth_required, payment_required, restricted_writes}` only; the other limitation fields are commented out in config.
  - When `PAY_TO_RELAY_ENABLED`, it adds `payments_url` (relay origin) and `fees.admission`. CORS is set.
- **Payments:** a pay-to-relay admission paid by a NIP-57 zap to the relay npub, recorded in a D1 `paid_pubkeys` table (`hasPaidForRelay`/`savePaidPubkey` in `src/relay-worker.ts` L369–396, checked in `durable-object.ts`).
- **Bark route:** a pluggable provider (`PAYMENT_PROVIDER=bark`).
  - The Worker calls a **publicly reachable** bark-pay endpoint, because a Worker cannot reach a LAN barkd, and writes `paid_pubkeys`.
  - The landing page shows a Lightning invoice and an Ark address.
  - The same pattern fits the other Cloudflare relays (Snowflare, cfrelay).
- **Norms:** single maintainer, GitHub, no CONTRIBUTING.

### 11. mattn family: nostr-relay (Go), cagliostr (C++), and Zig/Perl/Ruby/mruby/Nim/Lua/Lisp/Crystal ports
- **nostr-relay:** `relay.go` L383–421 `GetNIP11InformationDocument()` uses the go-nostr struct. Values can be overridden by env (`NOSTR_RELAY_*` via envconfig). It emits `payments_url: ""` and `fees.admission: []`.
- **cagliostr:** `main.cxx` L55–80 is hard-coded JSON, including `fees: {}` and non-spec `max_filters` and `relay_countries`.
- **Ports:** all MIT and all touched 2026-10-18 *(guess: a batch update)*. None of them have payments.
- **Bark route:** small PRs that make NIP-11 configurable, plus an optional HTTP allowlist check against the bark-pay sidecar. mattn is a prolific maintainer who merges small PRs *(guess)*.

### 12. nostr-relay-nestjs / @nostr-relay/core (CodyTseng; TypeScript, MIT)
- **NIP-11:** `src/modules/nostr/controllers/nostr.controller.ts` serves nearly every limitation field (all except `default_limit`). No payments_url, fees, banner, icon, self or terms.
- **Extension point:** `BeforeHandleEventPlugin` from `@nostr-relay/core` ([CodyTseng/nostr-relay](https://github.com/CodyTseng/nostr-relay)), for example `plugins/whitelist-guard.plugin.ts`.
- **Bark route:** an npm `@nostr-relay/bark-guard` plugin. It also covers nostr-relay-tray (110★) and anything else built on @nostr-relay/core.
- **Status:** the nestjs app has had no commits since 2025-01 (unclear); the core library is active (2026-08).

### Also notable
- **LNbits nostrrelay extension:** this is the strongest leverage point. If barkd is implemented as an **LNbits funding source** (`lnbits/wallets/barkd.py` *(path guess)*), this relay and every other LNbits paywall become bark-payable without touching relay code. Separately, a PR to emit `fees`/`payments_url`.
- **relay.tools relaycreator:** manages strfry fleets (the *.nostr1.com hosted relays) and already serves `payment_required`, `payments_url` and `fees.admission` via `pages/api/relay/[id]/nostrjson.ts`, with LNbits invoices. Add a barkd backend next to it.
- **HORNETS:** paid storage tiers (`lib/subscription/payment.go ProcessPayment`). Feed it from barkd notifications.
- **nostrcheck-server:** `src/lib/payments/{core,lnbits,LUD06}.ts`. Add `barkd.ts`. The NIP-11 in `src/lib/nostr/NIP11.ts` is fairly complete but has no `fees`.
- **Grain:** rich `relay_metadata.json` (`server/utils/loadRelayMetadata.go`), missing `payments_url`/`fees`/`self`/`default_limit`. Has NIP-86 (`server/api/nip86.go`), so it fits the NIP-86 sidecar.
- **Citrine:** on-device Android relay. NIP-11 has no limitation block (`server/CustomWebSocketServer.kt` L1261). Payments don't apply. It has AGENTS.md and accepts ngit patches.
- **Ditto relay:** `src/server.ts` L227 and `src/relay.ts` (`payment_required:false` hard-coded). The Soapbox workflow is AI-agent-first: the Ditto client CONTRIBUTING requires a frontier-model coding agent. The repo `soapbox-pub/ditto` is now a *client*. The relay lives in `ditto-relay` (deployed) and `ditto-core` (the old server).
- **nostr.wine and NFDB:** closed source, and the spec uses them as its pay-to-relay examples. nostr.wine serves full NIP-11; NFDB (nostr.land) no longer serves `fees` (live probe 23 Oct). Outreach only.

## Dead / minor (inventory completeness)

- **Dead** (last commit 2023 or earlier, or the repo is gone): Astro (Elixir), Nex (Elixir), knostr (Kotlin), me.untethr (Clojure), gnost-relay (Go), nostring (Deno), PyRelay, søstr, multiplextr, booger (Stacker News), Ephemerelay, NostrPostr, QNostr, Denostr (nostream port), expensive-relay (fiatjaf's original LN pay-to-relay), Nerostr (Monero paid relay, Codeberg), dezh-tech Immortal/Alienos/DDSR (GitHub 404 on 2026-10-23).
- **Stale or minor:** netstr, nostpy, tandem, algo-relay, jingle, mimoty, note-mixer-relay, noxir, nostr-filter-relay, monstr, Minds relay, blastr, keychat-relay-ext.
- **Proxies and bouncers (no payments needed):** Bostr, Bostr2, broadcastr, nostr-filter (imksoo), bucket (test relay).
- **Active small relays:** wisp (Zig), nostrfy, bloom, Servus, Transpher (PHP), johninnis/nostr-relay (AMPHP), n0str (Bun), Fenrir-s (Kotlin), Nostra (F#), bcr-relay, zapstore server, memlay (v0l, relay.snort.social), rockstr (relay.momostr.pink), mocrelay (nostr-relay.moctane.net), Snowflare (snowflare.cc), cfrelay, otherstuff-relay, mattn's language ports.
- **Unverified:** divine-funnelcake (relay.divine.video, Rust/Axum per a third-party mirror; repo not found), purplepag.es software, Nostella (ngit), nostr_relay by Dolu (fossil).
- **Not a relay:** primal-server is a caching/API service (Primal's relay is strfry). Blossom and nostrdb are out of scope.

## Patterns: one Bark processor, many relays

1. **bark-pay sidecar (the shared core).** One small HTTP service in front of barkd. It:
   - creates offers: a Lightning invoice via captaind's gateway, plus an Ark address for arkoor;
   - detects settlement by polling barkd movements;
   - keeps `pubkey → paid_until / credits`;
   - exposes `GET /check/<pubkey>`, a `/pay` page (this is the `payments_url`), and webhooks.

   Every route below is a thin adapter onto this service.
2. **strfry writePolicy plugin.** `strfry-bark` reads JSONL and checks the sidecar or a local cache. It covers strfry, the most-deployed relay (39+ deployments: damus, nos.lol, primal, nostr.mom…), relay.tools-managed fleets and nostr-filter-relay. It needs no strfry fork; only the NIP-11 fields require an upstream PR.
3. **NIP-86 management sidecar.** On payment, the sidecar calls `allowpubkey` (NIP-98-signed) on the relay. This works with **no code change** wherever NIP-86 exists and the relay runs in allowlist mode: Chorus, Grain, Haven, Citrine, khatru apps using `ManagementAPI`, relay.tools, ORLY *(check per relay that allowlist mode gates writes)*.
4. **Go module `khatru-bark`.** Policies, a `/pay` handler and `OverwriteRelayInformation`. Two adapters (go-nostr v0.x khatru; `fiatjaf.com/nostr/khatru`) cover Haven, wot-relay, pyramid, relay29, groups-relay, triflector, zooid, swarm, SW2, chronicle, hns-relay, algo-relay and jingle. The same design ports to `rely`, `relayer` (mattn/nostr-relay) and Shugur, which use similar hook styles.
5. **Rust:**
   - `BarkdPaymentProcessor` for nostr-rs-relay (`src/payment/`), or a gRPC nauthz admission sidecar with no fork;
   - an `rnostr-bark` Extension;
   - Chorus via NIP-86.

   A shared `bark-pay-client` crate (an HTTP client for the sidecar) serves all three.
6. **TypeScript:**
   - `BarkdPaymentsProcessor` for nostream (`IPaymentsProcessor`);
   - `@nostr-relay/bark-guard` (BeforeHandleEventPlugin) for nestjs and nostr-relay-tray;
   - `barkd.ts` for nostrcheck-server and relaycreator;
   - a Cloudflare-Worker provider for nosflare, Snowflare and cfrelay;
   - a Nostrify `NPolicy` for the Ditto family.

   A shared `@bark/pay-client` npm package serves all of them.
7. **LNbits funding source.** If barkd is a wallet backend inside LNbits, the LNbits nostrrelay extension (and LNbits-based relay.tools / nostrcheck setups) get Bark without relay changes.
8. **NIP-11 completeness PR template.** Most gaps are the same three things:
   - (a) `payments_url` + `fees.{admission,subscription,publication}` from config;
   - (b) `limitation.{auth_required,payment_required,restricted_writes}` derived from existing config;
   - (c) `self`, `banner`, `terms_of_service`.

   Two upstream library fixes reach many relays: add `TermsOfService` to nostrlib `nip11` (all khatru apps), and fix nostr-rs-relay's `payment_url` → `payments_url`.

## Caveats

- **arkoor:** existing processor interfaces (nostr-rs-relay, nostream) are bolt11/payment-hash shaped, so arkoor needs either an interface extension upstream or the sidecar route. Lightning-only via captaind's gateway fits unchanged.
- **Deployment counts:** they come from the sibling `relays.csv` (the parent fills the final column), so they are lower bounds.
- **Licenses:** detected by grepping the first 400 bytes of LICENSE. "unknown" means no LICENSE file, or an undetected one. Verify before contributing, especially wot-relay, chronicle and swarm, which have none.
