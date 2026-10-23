# Major Nostr relays, worldwide and Japanese (probed 23 Oct 2026)

96 relays: 71 global and 25 Japanese. Data is in `relays.csv`. Raw probes, popularity counts and scripts are in `raw/`.

## Method
- **Which relays count as major.** I counted how often each relay appears in kind-10002 relay lists (NIP-65), which shows what people actually use rather than what client defaults suggest.
  - Global sample: 25,294 lists pulled from purplepag.es, nos.lol and relay.primal.net. relay.damus.io returned 503 and relay.nostr.band timed out.
  - Lists that include a Fediverse bridge relay (`*mostr*`, i.e. bridged accounts) were removed, leaving **7,628**.
  - Bot farms publish identical relay lists in bulk: one set of 1,830 identical lists, one of 1,509, one of 439. So every distinct relay set counts **at most 3 times** (the `global_lists` column). The raw counts are in `raw/global_d.json` and `raw/jp_d.json`.
  - JP sample: the **3,031 lists** that name at least one Japanese relay, pulled from yabu.me, relay.nostr.wirednet.jp, purplepag.es, nos.lol and relay.primal.net, deduplicated the same way (the `jp_lists` column). One cluster of 1,973 identical JP lists (with `shu01.shugur.net` and `www.nostr.ltd`) looks like bots.
- **Added to the seed list:** client defaults (Damus, Primal, Amethyst, Coracle, Snort, YakiHonne, 0xchat, Olas), awesome-nostr-japan `_data/relays.yml`, and our JP research (our earlier Japan research). nostr.watch's API **v1 returns 502**. Its **v2 is paywalled**: HTTP 402 with an `L402` invoice plus an `X-Cashu` header (2 sats per call, 9 mints). That itself is a real example of HTTP-402 payment for Nostr infrastructure (`raw/nostr.watch-api-v2-402-headers.txt`).
- **NIP-11 probe:** `GET https://<host>` with `Accept: application/nostr+json`, 8 s timeout, run twice for failures (`raw/probe.py`, `raw/probe.json`, `raw/probe2.json`). The probe came from a Canadian IP.
- **Unreachable or geo-blocked relays:** for these I used cached data from NIP-66 monitor events (kind 30166, from monitorlizard.nostr1.com, relay.nostr.watch and relaypag.es), which carry the software name and a `R !payment` tag (`raw/nip66.json`). The `source` column says which source each row came from.
- **Paid status:** taken from NIP-11 `fees` / `payment_required` / `restricted_writes`, plus known facts recorded in `notes` (for example, Primal Premium).

## Software share (relays in this list)
"Weight" means the share of the summed relay-list counts (global + JP), so it gives a rough idea of usage.

**Global (71)**

| Software | Relays | Weight |
|---|---|---|
| **strfry** | 32 | **68%** |
| khatru family (wot-relay ×4, pyramid, croissant, plain khatru ×2) | 8 | 7% |
| NFDB (nostr.land, proprietary) | 4 | 4% |
| nostr.wine (proprietary) | 3 | 4% |
| nostr-rs-relay | 3 | 3% |
| Ditto relay (soapbox) | 3 | 3% |
| nostream | 1 | <1% |
| one each: memlay (v0l, relay.snort.social), purplepag.es, nostr.band (proprietary), Vector, nosflare (CF Workers), divine-funnelcake, nostrcheck-server, rockstr (momostr bridge), mostro relay, Shugur, nostr.ltd, noswhere (custom) | 12 | 10% |
| unknown (unreachable, no cache) | 5 | 1% |

**Japan (25)**

| Software | Relays | Weight |
|---|---|---|
| **strfry** (yabu.me, directory.yabu.me, relay.nostr.wirednet.jp, x.kojira.io, r.ydg.works, ipv6.wirednet, relay-jp.shino3.net (cache)) | 7 | 47% |
| strfry, *guessed* (r.kojira.io, relay-jp.nostr.wirednet.jp, nostr.fediverse.jp: geo-blocked, same operators as known strfry relays) | 3 | 33% |
| nostream (nostrja-kari.heguro.com; nostream.ocha.one guessed from its name) | 2 | 2% |
| mattn/nostr-relay (Go), cagliostr (C++), searchnos, snowflare (SnowCait, CF Workers), mocrelay (high-moctane), khatru (lang.relays.land/ja) | 6 | ~11% |
| unknown (down, gone, or geo-blocked without cache) | 7 | 8% |

**Takeaway:** strfry runs about two thirds of global use and about 80% of Japanese use, counting the guesses. Next come the khatru family (one Go module covers wot-relay, pyramid, Haven and other forks), nostr-rs-relay, nostream, and Ditto. Everything after that is a long tail of single-deployment software. Japan has its own long tail: mattn's relays, searchnos, snowflare and mocrelay.

## Payment fields actually served
- **Nobody advertises a payment *method*.** No relay serves `payment_v1`, `payment_methods` or anything like them. (nostr-paywall's demo relay nostr.hoppe-relay.it.com does; it isn't in this list.)
- **Fees advertised (7):**
  - nostr.wine: admission 18,888 sats
  - filter.nostr.wine: 10,000 sats / 30 days
  - inbox.nostr.wine: 2,500 sats / 30 days
  - nostrelites.org (wot-relay): 50,000 sats / 30 days
  - theforest.nostr1.com: 1,000 sats admission
  - nostr21.com: 21 sats admission
  - relay.orangepill.dev (nostream): 3,000 sats / 30 days

  All are in `msats`, and all have a `payments_url` that is a human web page.
- **Paid but `fees` missing (5):** nostr.land, eden, atlas and puravida (NFDB) and relay.azzamo.net. They set `payment_required: true` and a `payments_url`, but have no `fees` object. The NIP-11 spec still cites nostr.land's fees as its example.
- **Paid but not advertised at all:**
  - **premium.primal.net** (Primal Premium) is strfry with only the 3 default limitation keys.
  - relay.yozora.world ("paid relay via Starlink", per awesome-nostr-japan) was unreachable.
- **The completeness gap:** every strfry relay serves exactly `max_limit`, `max_message_length`, `max_subscriptions` (3 of 13 `limitation` keys) plus `negentropy`. strfry's NIP-11 handler cannot emit `fees` or `payments_url` at all. That's why paid strfry relays (nostr21.com, theforest.nostr1.com on relay.tools) serve their NIP-11 from a front-end app.
- **`restricted_writes` without payment:** pyramid.fiatjaf.com (invite tree), nostr.einundzwanzig.space (nostr-rs-relay), snowflare.cc and asia.vectorapp.io set `restricted_writes: true` with `payment_required` false or absent. The wot-relays (WoT-gated) mostly serve no `limitation` at all. A client therefore cannot tell from NIP-11 *why* writes are restricted. Open nips PR #2318 (`access_control`) is trying to fix this.
- **Japan:** no Japanese relay advertises fees. nostrja-kari.heguro.com (nostream) has `fees.admission: []` and `payments_url: .../invoices`, so the machinery is installed but turned off. Every JP relay that reported `R` in the NIP-66 cache reported `!payment`.

## Geo-blocked and unreachable
- **Geo-blocked to Japan (HTTP 403 from a Cloudflare rule):** r.kojira.io, relay-jp.nostr.wirednet.jp, relay-jp.shino3.net, nostr.fediverse.jp, nrelay-jp.c-stellar.net, **and also mattn's nostr.compile-error.net and cagliostr.compile-error.net** (new since the 6 Oct research).
  - nostream.ocha.one returns an nginx 403.
  - Through a JP exit on 6–7 Oct, r.kojira.io, relay-jp.nostr.wirednet.jp and relay-jp.shino3.net were open. nostr.fediverse.jp returned 500.
- **Gone or down:**
  - DNS NXDOMAIN: relay.0xchat.com (NIP-66 cache from Sep 2026 says strfry), relay.nostr.bg, relay.current.fyi, r.bitcoinhold.net.
  - Timed out: relay.nostr.band.
  - Connection refused: relayable.org, www.nostr.ltd.
  - 5xx errors: nrelay.c-stellar.net, nostr-relay.nokotaro.com, relay.damustr.com.
  - Network unreachable: nostr.fmt.wiz.biz, ipv6.nostr.wirednet.jp, relay.yozora.world. These are IPv6-only or routing problems, and the laptop has no IPv6.

## Which relays matter most
- **Global:** nos.lol, relay.damus.io and relay.primal.net are far ahead (each in about 5% of all distinct lists), then nostr.mom, offchain.pub, nostr.bitcoiner.social, relay.snort.social, nostr.oxtr.dev, **nostr.wine** (the top paid relay), and nostr-pub.wellorder.net (nostr-rs-relay). All of the top 8 except snort run strfry.
- **Japan:** **yabu.me** (in 225 of the JP lists), followed by global relays (nos.lol, damus, primal), relay-jp.nostr.wirednet.jp (142), r.kojira.io (123) and relay.nostr.wirednet.jp (88). Paid relays show up in Japanese lists too: nostr.wine (66), nostr.land (42), eden.nostr.land (28). So Japanese users already pay global paid relays, but no Japanese relay charges.

## All relays
`lists` = deduplicated count of kind-10002 relay lists that include this relay (global sample / JP sample). `lim` = number of `limitation` keys served.

| relay | region | lists (global / JP) | status | software + version | paid | lim | payment fields |
|---|---|---|---|---|---|---|---|
| nos.lol | global | 427 / 203 | live | strfry 1.1.3 | free | 3 |  |
| relay.damus.io | global | 396 / 167 | live | strfry 1.1.0-158- | free | 3 |  |
| relay.primal.net | global | 373 / 90 | live | strfry 1.1.3 | free | 3 |  |
| nostr.mom | global | 229 / 58 | live | strfry 1.1.3 | free | 3 |  |
| offchain.pub | global | 119 / 30 | live | strfry 1.1.0 | free | 3 |  |
| nostr.bitcoiner.social | global | 115 / 44 | live | strfry 1.1.0 | free | 3 |  |
| relay.snort.social | global | 112 / 62 | live | memlay (v0l) 0.2.0 | free | 4 |  |
| nostr.oxtr.dev | global | 88 / 38 | live | strfry 1.0.4 | free | 3 |  |
| nostr.wine | global | 82 / 66 | live | nostr.wine (proprietary) 0.3.3 | paid (fees advertised) | 11 | fees payments_url |
| nostr-pub.wellorder.net | global | 78 / 32 | live | nostr-rs-relay 0.9.0 | free | 2 |  |
| relay.ditto.pub | global | 68 / 24 | live | Ditto 2.5.0 | free | 11 |  |
| relay.nostr.net | global | 53 / 13 | live | strfry 1.1.2-148- | free | 3 |  |
| purplepag.es | global | 52 / 23 | live | purplepag.es (pablof7z) 0.2.0 | free | 9 |  |
| pyramid.fiatjaf.com | global | 47 / 12 | live | pyramid (khatru) v1.4.3-6f8 | restricted (non-payment: WoT/allowlist/auth) | 9 |  |
| relay.nostr.com | global | 47 / 7 | live | strfry 1.1.0 | free | 3 |  |
| relay.nostr.band | global | 45 / 50 | unreachable (TimeoutError) | nostr.band (proprietary) 0.4 | free | 0 |  |
| nostrelites.org | global | 41 / 5 | live | wot-relay (khatru) v0.2.1-18- | paid (fees advertised) | 5 | fees payments_url |
| wot.utxo.one | global | 38 / 3 | live | wot-relay (khatru) 0.2.1 | free | 0 |  |
| nostr.land | global | 37 / 42 | live | NFDB (nostr.land, proprietary) 2.0 γ5 | paid-no-fees | 5 |  payments_url |
| wot.nostr.party | global | 35 / 2 | live | wot-relay (khatru) 0.2.1 | free | 0 |  |
| relay.highlighter.com | global | 33 / - | live | khatru n/a | free | 0 |  |
| relay.zapclub.io | global | 33 / - | live | khatru n/a | free | 0 |  |
| relay.nostr.watch | global | 29 / 14 | live | strfry 0.9.6-26-g | free | 0 |  |
| nostr-01.yakihonne.com | global | 27 / 17 | live | strfry 0.9.6-8-g0 | free | 0 |  |
| chat.wisp.talk | global | 22 / 4 | live | croissant (fiatjaf, khatru-family; gue n/a | free | 0 |  |
| relay.nostrfeed.com | global | 22 / 3 | live | strfry 1.1.1-119- | free | 3 |  |
| relay.nos.social | global | 18 / 5 | live | strfry 1.0.3 | free | 3 |  |
| relay.us.whitenoise.chat | global | 16 / 8 | live | strfry 1.1.3 | free | 3 |  |
| eden.nostr.land | global | 14 / 28 | live | NFDB (nostr.land, proprietary) 2.0 γ5 | paid-no-fees | 5 |  payments_url |
| nostr.data.haus | global | 12 / 8 | live | strfry 1.1.3 | free | 3 |  |
| relay.0xchat.com | global | 11 / 20 | unreachable (gaierror) | strfry 0.9.6-39-g | free | 3 |  |
| indexer.coracle.social | global | 11 / 9 | live | strfry 1.1.3 | free | 3 |  |
| premium.primal.net | global | 11 / 5 | live | strfry 1.1.3 | paid-unadvertised | 3 |  |
| bitcoiner.social | global | 11 / 3 | live | strfry 1.1.0 | free | 3 |  |
| asia.vectorapp.io/nostr | global | 10 / 3 | live | Vector relay 0.1.0 | restricted (non-payment: WoT/allowlist/auth) | 7 |  |
| relay.dreamith.to | global | 10 / 5 | live | Ditto 2.5.0 | free | 11 |  |
| relayable.org | global | 10 / 4 | unreachable (ConnectionRefusedError) | unknown | unknown | 0 |  |
| purplerelay.com | global | 10 / 14 | live | strfry 1.1.3 | free | 3 |  |
| nostr.einundzwanzig.space | global | 10 / 12 | live | nostr-rs-relay 0.10.0 | restricted (non-payment: WoT/allowlist/auth) | 2 |  |
| relay.nostr.bg | global | 9 / 14 | unreachable (gaierror) | unknown (DNS gone) | unknown | 0 |  |
| nostr.cypherpunk.today | global | 9 / 2 | live | strfry 1.1.3 | free | 3 |  |
| sendit.nosflare.com | global | 9 / 13 | live | nosflare (Cloudflare Workers) 4.20.69 | free | 0 |  |
| relay.btcforplebs.com | global | 8 / - | live | nostr-rs-relay 0.9.0 | free | 2 |  |
| relay.divine.video | global | 7 / - | live | divine-funnelcake 0.1.0 | free | 10 |  |
| relay.current.fyi | global | 7 / 9 | unreachable (gaierror) | unknown (DNS gone) | unknown | 0 |  |
| user.kindpag.es | global | 6 / 6 | live | strfry 0.9.6-26-g | free | 0 |  |
| atlas.nostr.land | global | 6 / 12 | live | NFDB (nostr.land, proprietary) 2.0 γ5 | paid-no-fees | 5 |  payments_url |
| relay.nsite.lol | global | 6 / 7 | live | strfry 1.1.2-148- | free | 3 |  |
| theforest.nostr1.com | global | 6 / 4 | live | strfry strfry v31 | paid (fees advertised) | 11 | fees payments_url |
| relay.fountain.fm | global | 6 / - | live |  | free | 1 |  |
| puravida.nostr.land | global | 5 / 4 | live | NFDB (nostr.land, proprietary) 2.0 γ5 | paid-no-fees | 5 |  payments_url |
| relay.orangepill.dev | global | 4 / 4 | live | nostream 3.0.0 | paid (fees advertised) | 15 | fees payments_url |
| relay.coinos.io | global | 4 / 4 | live | strfry 1.1.0-beta | free | 3 |  |
| relay.nostrplebs.com | global | 4 / 3 | live | strfry 0.9.6-39-g | free | 3 |  |
| relay.noswhere.com | global | 4 / 5 | live | custom/undisclosed 0.0.1 | free | 0 |  |
| relay.nostrcheck.me | global | 4 / 5 | live | nostrcheck-server 0.7.1.0159 | free | 11 |  |
| nostr21.com | global | 3 / 12 | live | strfry strfry v31 | paid (fees advertised) | 11 | fees payments_url |
| relay.azzamo.net | global | 3 / 2 | live | strfry 1.1.0 | paid-no-fees | 6 |  payments_url |
| auth.nostr1.com | global | 3 / 5 | live | strfry strfry v31 | restricted (non-payment: WoT/allowlist/auth) | 11 |  |
| relay.lexingtonbitcoin.org | global | 2 / 4 | live | wot-relay (khatru) | free | 0 |  |
| filter.nostr.wine | global | - / 4 | live | nostr.wine (proprietary) 1.6 | paid (fees advertised) | 8 | fees payments_url |
| inbox.nostr.wine | global | - / 3 | live | nostr.wine (proprietary) 0.1.4 | paid (fees advertised) | 10 | fees payments_url |
| relay.yakihonne.com | global | - / - | unreachable (SSLCertVerificationError) |  | unknown | 0 |  |
| nostr.azzamo.net | global | - / - | live | strfry 1.0.4 | free | 3 |  |
| relay.mostr.pub | global | - / - | live | Ditto 2.5.0 | free (bridge) | 11 |  |
| relay.momostr.pink | global | - / - | live | rockstr (momostr) 0.1.0 | free (bridge) | 2 |  |
| relay.mostro.network | global | - / - | live | mostro relay (unknown base) 0.4.9 | free | 9 |  |
| relay.olas.app | global | - / - | live | strfry 1.0.4 | free | 3 |  |
| nostr.fmt.wiz.biz | global | - / - | unreachable (OSError) | strfry v216-4736f | free | 0 |  |
| shu01.shugur.net | global | - / 8 | unreachable (TimeoutError) | Shugur relay (Go) v1.3.5 | free | 11 |  |
| www.nostr.ltd | global | - / 11 | unreachable (ConnectionRefusedError) | nostr.ltd dev | free | 11 |  |
| yabu.me | jp | 21 / 225 | live | strfry 1.0.4 | free | 3 |  |
| relay-jp.nostr.wirednet.jp | jp | 7 / 142 | geo-blocked (JP, CF 403) | strfry (guess: siblings relay./ipv6.no | unknown | 0 |  |
| r.kojira.io | jp | 7 / 123 | geo-blocked (JP, CF 403) | strfry (guess: sibling x.kojira.io is | unknown | 0 |  |
| relay.nostr.wirednet.jp | jp | 9 / 88 | live | strfry 1.0.4-2-gc | free | 3 |  |
| nostr.compile-error.net | jp | 3 / 33 | geo-blocked (JP, CF 403) | mattn/nostr-relay (Go) 0.0.267 | free | 11 |  |
| nrelay-jp.c-stellar.net | jp | 3 / 29 | geo-blocked (JP, CF 403) | unknown (jiftechnify; strfry+policy pl | unknown | 0 |  |
| x.kojira.io | jp | 4 / 23 | live | strfry 1.1.2-154- | free | 3 |  |
| r.ydg.works | jp | - / 22 | live | strfry 1.1.0 | free | 3 |  |
| nostr.fediverse.jp | jp | - / 20 | geo-blocked (JP, CF 403) | strfry (guess: same operator as yabu.m | unknown | 0 |  |
| relay-jp.shino3.net | jp | 2 / 17 | geo-blocked (JP, CF 403) | strfry | free | 0 |  |
| search.nos.today | jp | 5 / 16 | live | searchnos v0.1.0-42e | free | 0 |  |
| snowflare.cc | jp | 2 / 14 | live | snowflare (SnowCait, CF Workers) 0.1.0 | restricted (non-payment: WoT/allowlist/auth) | 6 |  |
| directory.yabu.me | jp | 8 / 12 | live | strfry 1.0.4 | free | 3 |  |
| nostr.holybea.com | jp | - / 10 | unreachable (TimeoutError) |  | unknown | 0 |  |
| cagliostr.compile-error.net | jp | - / 10 | geo-blocked (JP, CF 403) | cagliostr 0.0.203 | free | 12 |  |
| nostream.ocha.one | jp | - / 8 | geo-blocked (JP only, HTTP 403 nginx; likely IP/geo restriction) | nostream (guess from hostname) | unknown | 0 |  |
| nostrja-kari.heguro.com | jp | - / 7 | live | nostream 1.22.6 | free | 11 | fees payments_url |
| r.bitcoinhold.net | jp | - / 7 | unreachable (gaierror) |  | unknown | 0 |  |
| relay.damustr.com | jp | - / 7 | down (HTTP 502) |  | unknown | 0 |  |
| nostr-relay.nokotaro.com | jp | - / 7 | down (HTTP 530) |  | unknown | 0 |  |
| nrelay.c-stellar.net | jp | - / 7 | down (HTTP 502) |  | unknown | 0 |  |
| nostr-relay.moctane.net | jp | 3 / 6 | live | mocrelay | free | 6 |  |
| lang.relays.land/ja | jp | - / 6 | live | khatru n/a | free | 0 |  |
| relay.yozora.world | jp | - / 4 | unreachable (OSError) |  | paid (per awesome-nostr-japan) | 0 |  |
| ipv6.nostr.wirednet.jp | jp | - / - | unreachable (OSError) | strfry 1.0.3-10-g | free | 3 |  |

## Caveats
- The popularity numbers come from one snapshot sample, capped at 20,000 events per source relay, and are only weights. Lists published by bots and bridges distort raw counts. The deduplication reduces that but doesn't remove it.
- Software names marked "guess" weren't verified (geo-blocked). A JP exit, such as the nadanada WireGuard used on 6 Oct, would let us confirm them.
- "free" means no payment fields and no `payment_required`. Some free-looking relays still limit writers in ways NIP-11 doesn't show (an allowlist in a strfry plugin, for example).
