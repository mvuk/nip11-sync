# Status

One row per relay implementation, ordered by measured deployment. Full detail: [inventory/software.md](inventory/software.md).

Legend: **NIP-11 PR** = the completeness change · **Payments PR** = the optional payment backend.

| Implementation | Language | Maintained | NIP-11 today | NIP-11 PR | Payments PR |
|---|---|---|---|---|---|
| [strfry](https://github.com/hoytech/strfry) | C++ (LMDB) | y | partial (missing payments_url, fees, limitation.auth_requir… | [#278](https://github.com/hoytech/strfry/pull/278) (draft) | plugin [strfry-bark-paid-writes](https://github.com/mvuk/strfry-bark-paid-writes) · read allowlist [#279](https://github.com/hoytech/strfry/pull/279) · listing [#280](https://github.com/hoytech/strfry/pull/280) |
| [nostr-rs-relay](https://git.sr.ht/~gheartsfield/nostr-rs-relay) | Rust (SQLite/Postgres) | unclear (… | partial (BUG: serializes `payment_url` not `payments_url`; … | [#257](https://github.com/scsibug/nostr-rs-relay/pull/257) (draft; fixes `payments_url`, #224) | Bark processor [#258](https://github.com/scsibug/nostr-rs-relay/pull/258) (draft, stacked on #257) |
| [nostream](https://github.com/Cameri/nostream) | TypeScript (Postgres, Redis) | y | near-full (missing fees.subscription (subscriptionPlans exi… | planned | planned |
| [khatru](https://github.com/fiatjaf/khatru) | Go (framework) | y (via no… | framework: struct can serve almost all (nostrlib nip11: nam… | planned | planned |
| [haven](https://github.com/bitvora/haven) | Go (khatru v0.19 + go-nostr) | y | partial (only name, description, icon, pubkey, software, ve… | planned | planned |
| [wot-relay](https://github.com/bitvora/wot-relay) | Go (nostrlib khatru) | unclear | partial (name, description, contact, icon, software, versio… | planned | planned |
| [pyramid](https://github.com/fiatjaf/pyramid) | Go (nostrlib khatru) | y | partial (name, pubkey, self; OverwriteRelayInformation adju… | planned | planned |
| [relay29](https://github.com/fiatjaf/relay29) | Go (khatru29 / relayer29) | unclear | partial (name, description, contact, icon, pubkey, supporte… | planned | planned |
| [chorus](https://github.com/mikedilger/chorus) | Rust | unclear (… | partial (missing payments_url, fees, pubkey? (contact pubke… | planned | planned |
| [rnostr](https://github.com/rnostr/rnostr) | Rust (actix, LMDB) | unclear | full via config ([information]/[limitation] tables are free… | planned | planned |
| [ditto-relay](https://gitlab.com/soapbox-pub/ditto-relay) | TypeScript (Bun, OpenSearch) | y | partial (limitation.payment_required:false hard-coded, max_… | planned | planned |
| [ditto-core (old Ditto server)](https://gitlab.com/soapbox-pub/ditto-core) | TypeScript (Deno, Postgres) | unclear | partial | planned | planned |
| [ORLY](https://git.smesh.lol/orly) | Go (Badger/Neo4j) | y | partial (name, description, pubkey, supported_nips, softwar… | planned | planned |
| [nosflare](https://github.com/Spl0itable/nosflare) | TypeScript (Cloudflare Worker… | y | partial (limitation only auth_required/payment_required/res… | planned | planned |
| [nostr-relay (mattn)](https://github.com/mattn/nostr-relay) | Go (relayer; sqlite/Postgres/… | y | partial (struct-based; hard-coded defaults overridable by e… | [#36](https://github.com/mattn/nostr-relay/pull/36) (draft) | Bark paid writes [#37](https://github.com/mattn/nostr-relay/pull/37) (draft, on #36) |
| [cagliostr](https://github.com/mattn/cagliostr) | C++ (sqlite3) | y | partial (hard-coded JSON; "fees":{} empty; no payments_url,… | [#34](https://github.com/mattn/cagliostr/pull/34) (draft) | planned |
| [searchnos](https://github.com/darashi/searchnos) | Rust (Elasticsearch/OpenSearc… | y | partial (name, description, software, supported_nips, versi… | planned | planned |
| [grain](https://github.com/0ceanslim/grain) | Go (MongoDB; own impl, not kh… | y | partial (config file relay_metadata.json; serves most top-l… | planned | planned |
| [Citrine](https://github.com/greenart7c3/Citrine) | Kotlin (Android) | y | partial (name, description, pubkey, self, contact, icon, su… | planned | planned |
| [nostr-relay-nestjs](https://github.com/CodyTseng/nostr-relay-nestjs) | TypeScript (NestJS, Postgres) | unclear | partial (limitation full set except default_limit; no payme… | planned | planned |
| [@nostr-relay/core (CodyTseng/nostr-rela…](https://github.com/CodyTseng/nostr-relay) | TypeScript (library) | y | library (NIP-11 left to host app) | planned | planned |
| [nostr-relay-tray](https://github.com/CodyTseng/nostr-relay-tray) | TypeScript (Electron, @nostr-… | y | not checked in detail (guess partial) | planned | planned |
| [relayer](https://github.com/fiatjaf/relayer) | Go (framework, predecessor of… | unclear (… | framework: relay-provided GetNIP11InformationDocument() (go… | planned | planned |
| [rely](https://github.com/pippellia-btc/rely) | Go (framework) | unclear | framework: NIP-11 via options (go-nostr struct) | planned | planned |
| [Shugur Relay](https://github.com/Shugur-Network/relay) | Go (CockroachDB) | unclear (… | partial (go-nostr struct with constants: limitation{max_mes… | planned | planned |
| [nostrcheck-server](https://github.com/quentintaranpino/nostrcheck-server) | TypeScript (Express, MariaDB) | y | partial-to-good (most limitation + terms/privacy/language_t… | planned | planned |
| [relay.tools relaycreator](https://github.com/relaytools/relaycreator) | TypeScript (Next.js; manages … | y | good for paid relays (overrides strfry NIP-11 via its own n… | planned | planned |
| [LNbits nostrrelay extension](https://github.com/lnbits/nostrrelay) | Python (LNbits extension) | y | partial (no fees/payments_url in NIP-11 per other agent's f… | planned | planned |
| [HORNETS Nostr Relay](https://github.com/HORNET-Storage/HORNETS-Nostr-Relay) | Go | y | partial (config-driven; admission/retention seen) | planned | planned |
| [NNostr](https://github.com/Kukks/NNostr) | C# (.NET) | y (slow) | partial (Nip11Middleware.cs) | planned | planned |
| [groups_relay (verse-pbc)](https://github.com/verse-pbc/groups_relay) | Rust (nostr-sdk, relay_builde… | unclear | partial | planned | planned |
| [SuperConductor](https://github.com/avlo/superconductor) | Java (Spring Boot) | y | partial (properties-driven: payments_url, payment_required,… | planned | planned |
| [triflector](https://github.com/coracle-social/triflector) | Go (khatru) | unclear | partial (name, description, icon, pubkey, self, software, s… | planned | planned |
| [zooid](https://gitea.coracle.social/coracle/zooid) | Go (khatru, multi-tenant) | y (moved … | not checked (archived mirror has README only) | planned | planned |
| [swarm](https://github.com/HiveTalk/swarm) | Go (khatru v0.19) | y | partial (name, description, pubkey) | planned | planned |
| [SW2](https://github.com/bitvora/sw2) | Go (nostrlib khatru) | y | partial (name, description, contact, icon, pubkey, software… | planned | planned |
| [chronicle](https://github.com/dtonon/chronicle) | Go (khatru) | y | partial (name, description, contact, icon, pubkey, software… | planned | planned |
| [hns-relay](https://github.com/keptlive/hns-relay) | Go (khatru) | y | partial | planned | planned |
| [groups-relay (max21dev)](https://github.com/max21dev/groups-relay) | Go (relay29/khatru) | unclear | partial | planned | planned |
| [zapstore server](https://github.com/zapstore/server) | Go (rely-like own framework) | y | partial | planned | planned |
| [bcr-relay](https://github.com/BitcreditProtocol/bcr-relay) | Rust | y | not checked | planned | planned |
| [Bostr](https://github.com/Yonle/bostr) | JavaScript (bouncer/aggregato… | unclear | partial (http.js serves name/description + limitation.auth_… | planned | planned |
| [Bostr2](https://github.com/Yonle/bostr2) | Go (bouncer) | unclear | not checked | planned | planned |
| [broadcastr](https://github.com/codonaft/broadcastr) | Rust | y | not checked | planned | planned |
| [bucket](https://github.com/coracle-social/bucket) | JavaScript (in-memory test re… | y | minimal/none | planned | planned |
| [cfrelay](https://github.com/haorendashu/cfrelay) | JavaScript (CF Workers) | y | not checked | planned | planned |
| [Snowflare](https://github.com/SnowCait/snowflare) | TypeScript (CF Workers) | y | not checked in detail | planned | planned |
| [Fenrir-s](https://github.com/rushmi0/Fenrir-s) | Kotlin (Micronaut, Postgres) | unclear | not checked | planned | planned |
| [n0str](https://github.com/tani/n0str) | TypeScript (Bun, SQLite) | unclear | not checked | planned | planned |
| [nostrfy](https://github.com/iqbqioza/nostrfy) | Rust | y | not checked | planned | planned |
| [Nostra](https://github.com/lontivero/Nostra) | F# (SQLite) | y (slow) | not checked | planned | planned |
| [Servus](https://github.com/ibz/servus) | Rust (CMS + personal relay) | y | not checked | planned | planned |
| [Transpher](https://github.com/nostriphant/transpher) | PHP | y | not checked | planned | planned |
| [wisp](https://github.com/privkeyio/wisp) | Zig | y | not checked | planned | planned |
| [bloom](https://github.com/nostrnative/bloom) | Rust (relay + Blossom) | unclear | not checked | planned | planned |
| [nostr-relay (johninnis, AMPHP)](https://github.com/johninnis/nostr-relay) | PHP (AMPHP) | y | not checked | planned | planned |
| [nostr-filter (imksoo)](https://github.com/imksoo/nostr-filter) | TypeScript (filter proxy) | y | proxy | planned | planned |
| [memlay](https://github.com/v0l/memlay) | Rust (in-memory) | y | not checked in detail | planned | planned |
| [rockstr](https://github.com/nanikamado/rockstr) | Rust | unclear | not checked | planned | planned |
| [mocrelay](https://github.com/high-moctane/mocrelay) | Go | y | not checked in detail | planned | planned |
| [zig-nostr-relay](https://github.com/mattn/zig-nostr-relay) | Zig | y | not checked (mattn family; likely hard-coded like cagliostr) | planned | planned |
| [perl-nostr-relay](https://github.com/mattn/perl-nostr-relay) | Perl | y | not checked | planned | planned |
| [ruby-nostr-relay](https://github.com/mattn/ruby-nostr-relay) | Ruby | y | not checked | planned | planned |
| [mruby-nostr-relay](https://github.com/mattn/mruby-nostr-relay) | mruby | y | not checked | planned | planned |
| [nim-nostr-relay](https://github.com/mattn/nim-nostr-relay) | Nim | y | not checked | planned | planned |
| [lua-nostr-relay](https://github.com/mattn/lua-nostr-relay) | Lua | y | not checked | planned | planned |
| [lisp-nostr-relay](https://github.com/mattn/lisp-nostr-relay) | Common Lisp | y | not checked | planned | planned |
| [crystal-nostr-relay](https://github.com/mattn/crystal-nostr-relay) | Crystal | y | not checked | planned | planned |
| [otherstuff-relay](https://github.com/andotherstuff/otherstuff-relay) | TypeScript (Deno, OpenSearch) | unclear | not checked | planned | planned |
| [Nostrify (relay pkgs)](https://gitlab.com/soapbox-pub/nostrify) | TypeScript (framework) | y | framework | planned | planned |
| [nostr_client_relay](https://github.com/pedro-vicente/nostr_client_relay) | C++ | unclear | - | planned | planned |
| [primal-server (caching service)](https://github.com/PrimalHQ/primal-server) | Julia + Rust | y | N/A (caching/API server, not a NIP-11 relay) | planned | planned |
| [nostr_relay (Dolu)](https://code.pobblelabs.org/fossil/nostr_relay/) | Python (SQLite) | unclear | not checked (fossil repo) | planned | planned |
| [Nostella](https://ngit.dev/henk.tech/nostella) | Rust | unclear | not checked | planned | planned |
| [divine-funnelcake](repo) | Rust (Axum, ClickHouse) - per… | y (live) | unknown | planned | planned |
| [nostr.wine](proprietary) | unknown | y | full (example in NIP-11 spec: fees.admission, payments_url,… | planned | planned |
| [NFDB (nostr.land)](proprietary) | unknown | y | partial: payment_required true + payments_url, but NO fees … | planned | planned |
| [purplepag.es](unknown) | unknown | y | unknown | planned | planned |

Unmaintained and dead implementations are listed in the inventory only.
