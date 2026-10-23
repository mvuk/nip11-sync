# Nostr clients vs. NIP-11 relay payments: where can Bark pay?

Research date: 2026-10-23. Evidence is mostly `git clone --depth 1` + grep of each repo (paths below are relative to the repo root). The machine-readable version is `clients.csv` (36 clients, 17 columns). Anything marked **(guess)** has not been verified.

Key to `bark_path`:
- **(a) zero-code via NWC.** The client can pay a BOLT11 over NIP-47 `pay_invoice`, and the user can get the relay's invoice into it, either by opening `payments_url` and pasting/scanning, or through an in-app prompt. With (local notes) as the NWC wallet, this pays **over Lightning from a Bark wallet, not Ark-native**.
- **(b) client PR.** Read NIP-11 `fees` / `payments_url` and pay through the user's wallet (NWC).
- **(c) native Bark SDK.** `@secondts/bark-react-native` for RN apps, the Rust crate for Rust apps.

## Per-client summary

| Client | Region | Platform | Last activity | NIP-11 fees / payments_url | NWC | Built-in wallet | Bark path |
|---|---|---|---|---|---|---|---|
| Amethyst | global | Android/desktop (Kotlin) | v1.19.0 2026-10-14 | **Full**: fees card (admission/subscription/publication), clickable payments_url, payment_required flag. **NIP-87 NOTIFY payment prompt** | yes | NWC + NIP-60 cashu | **(a) now** |
| Damus | global | iOS (Swift) | commit 2026-09-09 | **Yes**: paid badge showing price ("4,000 sats / 30 days"); tap opens payments_url | yes (+ SendPaymentView for pasted invoices; Coinos one-click) | NWC UI (Coinos) | **(a) now** |
| noStrudel | global | Web | commit 2026-10-23 | **Yes**: fees + payments_url link, green paid tag, payment_required/restricted_writes in mailbox settings | yes (send-lightning modal) | NWC/WebLN + NIP-60 | **(a) now** |
| Iris | global | Web/PWA | commit 2026-10-21 | **Yes**: "Payment Required" badge, admission fees, "Payment info →" link | yes | embedded Cashu | **(a) now** |
| Habla.news | global | Web | 2025-03 | yes: payments_url + admission fee | partial (WebLN/NWC zap settings) | no | (a)/(b) |
| Flycat | global | Web | 2024-02 (stale) | yes: parses and shows paymentsUrl | WebLN only | no | (a) via Alby ext. |
| Snort | global | Web | v0.5.3 2026-04; commit 2026-10-21 | partial: Paid/Free label only | yes (+ wallet send page, inline invoices) | NWC/LNBits/WebLN/Cashu connectors | (a) paste / (b) |
| Ditto (ditto.pub) | global | Web | commit 2026-10-23 | partial: payment_required/restricted_writes badges + fees in sats; **no payments_url link** | yes (+WebLN) | no | (b) tiny PR |
| Jumble | global | Web | v26.9.2; commit 2026-10-23 | typed but not rendered | yes (bitcoin-connect; inline invoices payable) | no | (b) easy |
| Rabbit (JP) | JP | Web (SolidJS) | commit 2026-08-18 | **parsed** (zod: fees, payments_url, payment_required, restricted_writes) but not shown | WebLN only | no | (b) easy; (a) via Alby ext. |
| Primal Android | global | Kotlin/KMP (**not RN**) | 3.5.28 2026-10-20 | none | yes (WalletType NWC; also an NWC wallet service) | **Primal wallet (Breez Spark)** | (a) paste in Send w/ external NWC; (b); (c) Kotlin bindings (guess) |
| Primal iOS | global | Swift (**not RN**) | 3.5.61; commit 2026-09-02 | none | yes | Primal wallet (Breez Spark) | (a) paste; (b) |
| Primal web | global | SolidJS | 3.0.122; commit 2026-08-13 | only its own premium relay page | yes | Primal wallet | (b) |
| Nostur | global | iOS/macOS | 1.34.0 2026-10-20 | none | yes (+inline invoice pay) | NWC | (a) paste / (b) |
| Coracle | global | Web (Svelte) | 0.6.35; commit 2026-10-21 | supported_nips only | yes (bitcoin-connect) | no | (b) |
| YakiHonne | global | Web + Flutter | 2026-10-20/21 | web: payment-required badge (NIP-11 or NIP-66); payments_url cached not shown | yes | Cashu + Alby | (b) |
| 0xchat | global | Flutter | v1.5.6 2026-09-30 | stores payments_url, no UI | yes | Cashu (cashu_dart), nutzaps | (b) |
| Notedeck | global | Rust/egui | commit 2026-10-18 | payment_required only (outbox logic) | yes (rust-nostr `nwc` 0.39) | NWC | (b) or **(c) Rust** |
| Gossip | global | Rust/egui | v0.14.0 2025-03; commit 2026-10-17 | stores full NIP-11 doc; UI shows no fees | **no** | no | **(c) Rust** or larger (b) |
| Nostrmo | global | Flutter | 3.5.1 2026-03 | none | yes | no | (b) |
| nostter (JP) | JP | Web (Svelte) | commit 2026-10-19 | limitation typed only | yes (zaps only) | no | (b) |
| Lumilumi (JP) | JP | Web/PWA | commit 2026-10-17 | supported_nips only | **no** (setting commented out) | no | (b) after adding NWC |
| Nos Haiku (JP) | JP | Web | commit 2026-10-23 | none | no | no | (b) low |
| Olas | global | **React Native/Expo** | 2025-05 (dormant) | none | yes (NDK) | NIP-60 cashu | **(c) RN**, but dormant |
| Current | global | **React Native** per 2023 reports | unknown | unknown | yes per App Store | built-in LN wallet | (c) RN if alive (guess) |
| Highlighter | global | Web | 2024-12 (stale) | none | yes | NDK cashu | (b) low |
| Nos | global | iOS Swift | 2025-05 | supported_nips only | no | no | unlikely |
| Satellite | global | Web | 2024-02 (stale) | none | WebLN | no | (a) via Alby ext. |
| Lume | global | Rust desktop | 2025-12 (dormant) | none | no | no | (c) dormant |
| zap.stream | global | Web | commit 2026-10-12 | none | yes (NWC auto top-up of stream balance) | no | n/a for relays |
| Soapbox | global | Web (Mastodon API front-end) | 2026-10-04 | none | no | no | n/a |
| Alby extension | global | browser ext. (NIP-07 + WebLN) | v3.15.0 2026-09-17 | — | **NWC connector** (`connectors/nwc.ts`) | — | **bridge** (see below) |
| Amber | global | Android signer | v6.6.9 2026-10-14 | — | no | no | n/a (signs NIP-42 AUTH only) |
| Plebstr | global | mobile, closed source (guess) | unknown | unknown | unknown | unknown | not verified |
| Freerider | ? | ? | ? | — | — | — | **could not verify that it exists** |
| Astraea (JP) | JP | Web | — | not inspected | — | — | listed in awesome-nostr-japan |

JP client list source: `github.com/nostr-jp/awesome-nostr-japan` `_data/web-clients.yml`. It lists nostter, Rabbit, Astraea, Lumilumi, Nos Haiku, GARNET, うにゅうハウス, nos.today and nokakoi/noka (Windows). The names Nostr-Hub, makimono, Nostrends and Yabumi in the brief do not appear there as clients (yabu.me is a JP relay).

## How clients handle relay payments today

1. **Nobody does an in-app checkout driven by NIP-11.** The most any client does with `fees` + `payments_url` is display them and **open `payments_url` in a browser**. That is true of Damus, Amethyst, noStrudel, Iris, Habla and Flycat. The relay's web page then produces an invoice, and the user pays it with any wallet. NIP-11 has no machine-readable invoice endpoint, which is the real gap. A "Bark processor for NIP-11" could fill it with a convention, for example a `payments_url` that also answers with LNURL-pay/JSON for a pubkey (proposal, not a standard).
2. **Amethyst is the exception.** It implements the relay `NOTIFY` message (NIP-87 draft #901 according to the parent's spec research; used by inbox.nostr.wine). When a paid relay rejects AUTH (`OK <authId> false`) and sends NOTIFY, Amethyst maps it to the signing account (`commons/.../relayClient/notify/NotifyCoordinator.kt`). It then shows a "payment required" dialog that renders the message as rich text, with an option to block the relay (`DisplayNotifyMessages.kt`, `NotifyRequestDialog.kt`). Whether that rich text turns an lnbc invoice into a one-tap NWC pay button is **likely but not verified**; Amethyst does render invoices as payment cards elsewhere (`PaymentCard.kt`). This is the closest thing to in-app relay payment.
3. **A badge only:** Snort (Paid/Free), Ditto (payment_required + fee amounts, no link), YakiHonne web (payment-required badge, also from NIP-66 monitor tags), Notedeck (payment_required used internally).
4. **Parsed but not shown:** Rabbit (full zod schema), Jumble (types), 0xchat (stores payments_url), Gossip (whole NIP-11 doc stored).
5. **Vendor-owned paid relays sold outside NIP-11:** Primal Premium relay (`wss://premium.primal.net`, part of Primal Premium) and Damus Purple (Damus's subscription, with its own checkout). Defaults that include paid relays: Damus bootstraps nostr.land and nostr.wine; many clients include nostr.wine or filter/inbox.nostr.wine.
6. **Spec divergence to watch** (from the parent's spec research): nostr-rs-relay serializes `payment_url`, not `payments_url`. **None of the clients grepped here read `payment_url`**, so those relays' payment links are invisible in every client.

## Bark path per client, ranked by how soon Bark relay payments could work

Today, any NWC client connected to `bark-nwc` can pay a relay invoice. That payment goes over Lightning from the Bark wallet; it is not Ark-native.

1. **Amethyst: (a) now.** It is the best match: fees card, payments_url, NIP-87 NOTIFY prompt, NWC, very active, MIT. A follow-up (b) PR could add a "Pay" button on the fees card once a machine-readable invoice source exists.
2. **Damus iOS: (a) now.** The paid badge opens payments_url, and the invoice can be pasted or scanned into the NWC wallet SendPaymentView. A small (b) PR would make the badge open an in-app pay sheet.
3. **noStrudel: (a) now.** It has a payments_url link plus an NWC send modal. MIT, very active.
4. **Iris: (a) now.** It has a "Payment info" link plus NWC.
5. **Ditto, Jumble, Rabbit: (b), the easiest PRs.** The data is already parsed or typed; each needs a link plus a pay step. Rabbit is the best JP target.
6. **Snort, Nostur, Primal (all three): (a) by paste, (b) for UI.** Primal is the largest audience, but it is **native Kotlin/Swift, not React Native**. A native Bark wallet in Primal would need Kotlin/Swift bindings; whether Bark ships those, rather than only RN, is a guess. Primal already supports external NWC wallets (`WalletType.NWC`), so bark-nwc works there today for pasted invoices.
7. **Coracle, YakiHonne, 0xchat, Nostrmo, nostter: (b).** They have NWC but no fee UI.
8. **Notedeck: (b) or (c) Rust.** It already depends on the `nwc` and `lightning-invoice` crates, so it is the natural home for the Bark Rust crate.
9. **Gossip: (c) Rust.** It has no NWC at all, so adding a wallet is a bigger change. The maintainer is Rust-native.
10. **Lumilumi, Nos Haiku, Nos: (b) after adding NWC.** Low priority.
11. **RN candidates for `@secondts/bark-react-native`: Olas** (Expo, dormant since 2025-05) and **Current** (RN in 2023, status unknown). **No active major client uses React Native.** Primal is not RN.
12. **Web bridge via the Alby extension.** Add the bark-nwc URI as the extension's NWC connector. Every WebLN web client (Rabbit, Flycat, Satellite, Snort, noStrudel, Coracle, Ditto, etc.) can then pay from Bark with zero client code.

## Default relays by client (from source)

| Client | Defaults (file) |
|---|---|
| Damus | relay.damus.io, **nostr.land**, **nostr.wine**, nos.lol; JP locale adds relay-jp.nostr.wirednet.jp, yabu.me, r.kojira.io; TH and DE locales add their own (`Features/Relays/Models/RelayBootstrap.swift`) |
| Notedeck | relay.damus.io, nos.lol, nostr.wine, purplepag.es (`crates/notedeck/src/account/relay.rs:444`) |
| Amethyst | bootstrap inbox: relay.primal.net, nostr.mom, nos.lol, nostr.bitcoiner.social, nostr.oxtr.dev, directory.yabu.me; event finder adds nostr.wine; indexers purplepag.es, indexer.coracle.social, user.kindpag.es, profiles.nostr1.com (`commons/.../defaults/Constants.kt`) |
| Primal Android | relay.primal.net, nos.lol, relay.nostr.net, relay.snort.social, purplepag.es, nostr.land (`.../networking/relays/FallbackRelays.kt`) |
| Primal iOS | relay.primal.net, relay.damus.io, relay.nostr.band, relay.current.fyi, purplepag.es, nos.lol, onchain.pub, relay.nostr.bg, nostr.bitcoiner.social (`NostrTools/Lib/Bootstrap.swift`) |
| Primal web | served by the Primal cache (cache2.primal.net); none hard-coded |
| Nostur | nos.lol, relay.damus.io, relay.primal.net, nostr.wine, purplepag.es (`Nostur/Utils/Maintenance.swift`) |
| Coracle | relay.damus.io, nos.lol; indexers relay.damus.io, purplepag.es, indexer.coracle.social; search nostr.wine, search.nos.today (`.env.template`) |
| Iris | temp.iris.to, vault.iris.to, relay.damus.io, relay.snort.social, relay.primal.net, nos.lol (`src/shared/constants/relays.ts`) |
| Snort | relay.snort.social, nostr.wine, relay.damus.io, nos.lol (`packages/app/config/default.json`) |
| noStrudel | fallback relay.primal.net, nos.lol; lookup purplepag.es, index.hzrd149.com, indexer.coracle.social; search relay.nostr.band, search.nos.today, relay.noswhere.com, filter.nostr.wine (`src/const.ts`) |
| Jumble | nos.lol, relay.primal.net, offchain.pub, relay.ditto.pub; search search.nos.today, search.nostrarchives.com (`src/constants.ts`) |
| Ditto | relay.ditto.pub, relay.dreamith.to, divine.video, relay.zapstore.dev, relay.ngit.dev, relay.primal.net, relay.damus.io (`src/lib/appRelays.ts`) |
| YakiHonne | web: nostr-01.yakihonne.com, nostr-02.yakihonne.com, relay.damus.io, relay.nsec.app, nos.lol, relay.primal.net (`src/Content/Relays.js`); mobile: nostr-01/02.yakihonne.com, nostr-03/02.dorafactory.org, relay.damus.io (`lib/utils/constants.dart`) |
| Gossip | about 36 relays in the setup wizard, including nostr.mom, e.nos.lol, a.nos.lol, relay.primal.net, relay.nos.social, nos.lol, relay.damus.io, offchain.pub, relay.nostr.wirednet.jp, relay.coinos.io, nostr-01/02.yakihonne.com (`gossip-bin/src/ui/wizard/mod.rs`) |
| 0xchat | relay.nostr.band, relay.damus.io, nos.lol, yabu.me, relay.siamstr.com, relay.0xchat.com; DM/auth: inbox.nostr.wine, auth.nostr1.com (`packages/0xchat-core/lib/src/account/relays.dart`) |
| Nostrmo | nos.lol, nostr.wine, top.testrelay.top, atlas.nostr.land, relay.damus.io, nostr-relay.app, nostr.oxtr.dev, relay.primal.net, relay.nostr.bg, relay.nostr.band, yabu.me, nostr.mom (`lib/provider/relay_provider.dart`) |
| Olas | relay.olas.app, purplepag.es, relay.primal.net (`lib/ndk.ts`) |
| Nos | relay.nos.social, news.nos.social, relay.damus.io, nos.lol, purplepag.es, eden.nostr.land, … (`Nos/Models/CoreData/Relay+CoreDataClass.swift`) |
| Lume | relay.damus.io, relay.primal.net, relay.nos.social, user.kindpag.es, purplepag.es, relay.nsec.app (`crates/common/src/constants.rs`) |
| zap.stream | relay.snort.social, nos.lol, relay.damus.io, nostr.wine, relay.primal.net, relay.fountain.fm, relay.divine.video (`src/const.ts`) |
| Satellite | relay.damus.io, nos.lol, relay.current.fyi, eden.nostr.land, relay.plebstr.com, relay.nostr.band, nostr.wine (`src/constants.js`) |
| Highlighter | relay.noswhere.com, relay.nostr.band (`apps/web/src/lib/utils/ndk.ts`) |
| nostter (JP) | nos.lol, relay.damus.io, relay-jp.nostr.wirednet.jp, yabu.me, r.kojira.io, nrelay-jp.c-stellar.net; plus purplepag.es, directory.yabu.me, search.nos.today (`web/src/lib/Constants.ts`) |
| Rabbit (JP) | relay.damus.io, nos.lol, relay.snort.social, relay-jp.nostr.wirednet.jp, r.kojira.io, yabu.me, search.nos.today (`src/core/relayUrls.ts`) |
| Lumilumi (JP) | directory.yabu.me, purplepag.es, nos.lol, indexer.coracle.social, nostr.wine, relay.nostr.wirednet.jp, relay.ditto.pub, … (`src/lib/stores/relays.ts`) |
| Nos Haiku (JP) | nostream.ocha.one, nostr.compile-error.net, r.kojira.io, yabu.me, relay-jp.nostr.wirednet.jp (+ directory/indexer relays) (`src/lib/config.ts`) |

Paid relays that appear in defaults: **nostr.wine** (Damus, Notedeck, Snort, Nostur, Nostrmo, zap.stream, Satellite, Lumilumi, 0xchat, Amethyst event finder), **nostr.land / eden.nostr.land / atlas.nostr.land** (Damus, Primal Android, Nostrmo, Nos, Satellite), inbox.nostr.wine (0xchat), and premium.primal.net (Primal Premium). They are the obvious first relays to test a Bark payment against.

## Sources
- Repos listed in `clients.csv` (shallow clones dated 2026-10-23; latest-release data from api.github.com `/releases/latest`).
- awesome-nostr-japan: https://github.com/nostr-jp/awesome-nostr-japan (`_data/web-clients.yml`).
- Current: https://apps.apple.com/lc/app/current-nostr-bitcoin/id1668517032 and https://nobsbitcoin.com/current-app-v0-1-2
- Nos: https://awesome.ecosyste.ms/projects/959949
- NIP-87 NOTIFY and `payment_url` in nostr-rs-relay: the parent agent's spec research (not re-verified here).
