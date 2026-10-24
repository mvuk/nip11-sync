# Public Blossom hosts: software, payments, pricing

Probed 2026-10-23, around 23:35 UTC, with at most 8 concurrent connections and no authentication. For each host:

- `GET /`
- `HEAD /upload`, with dummy `X-SHA-256` / `X-Content-Length: 1048576` / `X-Content-Type: image/png` and an `Origin`
- `OPTIONS /upload`, as a CORS preflight asking for `x-cashu,x-lightning`
- `GET /.well-known/nostr/nip96.json`
- `HEAD /<zero hash>`

Raw headers and bodies are in `raw/probes/<host>/`.
**Usage** = how many of 34,008 kind-10063 user server lists (BUD-03, deduplicated per pubkey) name the host, followed by how many name it *first*
(`raw/k10063-tally.txt`). Japanese activity comes from the coordinator's 24 h sample of Japanese posts.
Software is inferred from titles, error strings (`X-Reason`), the CORS expose list and `nip96.json` *(fingerprint)*, or is known from source.

Caveat on payments: an unauthenticated `HEAD /upload` stops at 401, so it cannot show a 402. "BUD-07 advertised" below means the
CORS expose list names `X-Lightning`/`X-Cashu`. That shows the *software* can send them. It does not show that payments are switched on.

## Table

| Host | Usage (lists / first) | JP 24 h | Software | `HEAD /upload` (no auth) | BUD-07 advertised | Pricing / payments |
|---|---|---|---|---|---|---|
| blossom.primal.net | **30,955 / 28,230** | — | primal-blossom-server (known) | 400 | no | free; Primal Premium (off-server) |
| 24242.io | 5,075 / 29 | — | unknown (BunnyCDN-fronted; "Authorization header missing, when required") | 401 | no | free "for now"; files deleted after 60 days unaccessed; 100 MiB max |
| cdn.nostrcheck.me | 3,108 / 167 | 13 posts / 3 people | **nostrcheck-server** | 401 "Authorization header not found" | **yes**: `X-Cashu, X-Lightning, X-Lightning-Amount, X-Reason` | nip96 plan `free` only (payments module not visibly on) |
| nostr.media | 2,843 / 34 | — | same as 24242.io *(fingerprint: identical X-Reason, BunnyCDN)* | 401 | no | "archival CDN"; nothing public |
| blossom.yakihonne.com | 1,618 / 259 | — | hzrd149 blossom-server, older *(guess)* | 403 | no | free |
| blossom.band (+ `<npub>`.blossom.band) | 1,253 / 577 (+ dozens of subdomains) | 19 posts / 11 people | nostr.build closed CF worker | 401 "Missing Blossom Authorization header…" | no | **annual plans paid in Bitcoin (BTCPay):** Purist $18/yr 5 GB, Professional $69/yr 25 GB, Creator $120/yr 100 GB, Advanced $240/yr 500 GB |
| nostr.download | 1,105 / 220 | — | **route96** (title "route96 - Free File Hosting") | 401 "Auth header not found" | no (exposes `allow,x-reason,x-identical-media,sunset`) | free (nip96 `free`) |
| blossom.nmail.li | 1,029 / 880 | — | hzrd149 blossom-server *(fingerprint)* | 401 "Authorization required" | no | — |
| cdn.satellite.earth | 689 / 203 | — | Satellite CDN (known) | **404** (endpoint gone or moved) | no | prepaid credit via zaps (historic) |
| blossom.data.haus | 636 / 536 | — | hzrd149 blossom-server *(fingerprint)* | 401 | no | — |
| nostrmedia.com | 614 / 33 | — | own (NIP-96) | 401 "Missing auth handler" | no | nip96 plans free / purple / onyx (25–100 MB); subscriptions by zap; **"Zapwall": creators charge sats to unlock a file** (pay-per-access already, outside BUD-07) |
| mibo.(eu./us.)nostria.app, milo.nostria.app | ~1,150 combined | — | nostria-media (blossom-server fork) | 301 / 530 / CF 1033 (down at probe time) | no | free |
| blossom.ditto.pub | 437 / 46 | — | unknown ("This needs a Nostr auth token (BUD-11)"; Caddy) | 401 | no | — |
| blossom.azzamo.media | 417 / 11 | — | unknown custom (BunnyCDN) | **200 `{"message":"Upload allowed"}` without auth** | **yes**: `X-Lightning, X-Cashu, X-Content-SHA256` | Azzamo sells paid tiers elsewhere *(guess)*; worth a follow-up probe with auth |
| cdn.sovbit.host / files.sovbit.host | 360 / 109 | — | unknown (nginx; nip96) | cdn: no answer; files: 401 | files: expose `*` | nip96 plans `free` (10 MB, registered) and **`paid` "Relay Subscriber" (2 GB)**: bundled with relay subscription |
| blossom-01 / -02.uid.ovh | 277 / 271 | — | hzrd149 blossom-server *(fingerprint)* | 401 | no | — |
| blossom.jumble.social | 268 / 194 | — | "jumble-blossom" (own; source not found) | 404 | no | free; 20 MB; 6,525 users / 26,619 files / 25.8 GB (self-reported) |
| cdn.hzrd149.com | 171 / 109 | — | hzrd149 blossom-server (author's own) | 401 | no | — |
| blossom.f7z.io | 109 / 1 | — | hzrd149 blossom-server *(fingerprint)* | 401 | no | — |
| blossom.nostr.build / nostr.build / image.nostr.build | 94 + 87 / 56 | **image.nostr.build 49 posts / ~22 people** | nostr.build (FOSS PHP for NIP-96 + closed worker) | 401 / 200 / 404 | no | as blossom.band; nip96 plans free (20 MB) / professional / creator / advanced |
| files.v0l.io, void.cat | 64, 17 | — | route96 (v0l) | no answer | — | — |
| blossom.einundzwanzig.space | 34 / 16 | — | khatru/blossom *(fingerprint: `missing "Authorization" header`)* | 401 | no | — |
| media.libernet.app | 26 / 14 | — | own (NIP-96) | 200 | no | nip96 `free` |
| nostrcheck.me | 22 / 6 | — | nostrcheck-server | 401 | **yes** (as cdn.nostrcheck.me) | nip96 `free` |
| nosto.re | 15 / 5 | — | route96 (title) | 401 | no | nip96 `free` |
| nostpic.com | 10 / 4 | — | own (nip96 at /api/v2/media, nostrcheck-like path) | 404 | no | nip96 `free` |
| nostrage.com | — | — | **nostrcheck-server** (identical CORS list and X-Reason) | 401 | **yes** | nip96 `free`; "sovereign file storage" |
| **share.yabu.me** | 4 / ? (plus yabu.me 6) | **41 posts / 15 people** | **nostrcheck-server** | 401 | **yes** (same CORS list) | nip96 plan `free`; NIP-96 api `https://yabu.me/api/v2/media` |
| media.divine.video / blossom.divine.video | — | — | divine-blossom (known) | 200 "Upload would be accepted" / 404 | no | free (app-funded) |
| mockingyou.com, sove.rent | — | — | — | 502 / no answer | — | dead or down |

## What this says

- **Primal dominates the kind-10063 lists** (91% of lists, 83% as the first server). That is because Primal writes the list for its users.
  It has no payment surface and is not a BUD-07 target. Its usage tells us about defaults, not about paying customers.
- **The Japanese community uploads through NIP-96, not BUD-03 lists.**
  - share.yabu.me appears in only 4 server lists, but in 41 of the sampled posts.
  - Japanese clients (nostter and others) most likely upload to `yabu.me/api/v2/media`, which is nostrcheck-server's NIP-96 endpoint *(guess; not checked in client source)*.
  - So for Japan, nostrcheck's NIP-96 upload path matters as much as its Blossom path. Both go through `uploadMedia()`, where the `X-Lightning` 402 is set.
- **Hosts whose software already speaks BUD-07** (by CORS): cdn.nostrcheck.me, nostrcheck.me, share.yabu.me, nostrage.com (all nostrcheck-server),
  and blossom.azzamo.media (unknown software; exposes both `X-Lightning` and `X-Cashu`).
  That is about 3,500 list entries plus the Japanese NIP-96 traffic. Every one of them is one config switch (payments module + NWC) away from charging.
- **Paid hosting today is mostly subscriptions, not per-request 402:**
  - nostr.build / blossom.band: BTCPay annual plans.
  - nostrmedia.com: zap subscriptions and the Zapwall unlock fee.
  - sovbit: relay-subscriber tier.
  - route96 deployments: LND quota top-ups (feature off on the public instances seen; nip96 `free`).
- **hzrd149's reference blossom-server** is the most-deployed open-source server by host count (6+ hosts, about 2,500 list entries by fingerprint).
  It has no payments, so adding BUD-07 there reaches the long tail of self-hosters.

## Not probed / follow-ups

- **Authenticated probes:** a signed kind-24242 `HEAD /upload` on nostrcheck hosts and Azzamo would show whether a 402 is actually served.
  That needs a throwaway key. It posts nothing, but it was out of scope for "light, no auth".
- **Unknown software:** 24242.io/nostr.media, blossom.ditto.pub/dreamith.to and jumble-blossom. Ask the operators.
- **blossomservers.com** lists servers from kind-36363 announcements, but the relays returned only one such event, so the site's list was not used.
