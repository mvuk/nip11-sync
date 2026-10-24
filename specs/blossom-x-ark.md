# Blossom `X-Ark`: Ark payments for BUD-07

`draft` `optional`

This document defines `X-Ark`, a payment method for
[Blossom BUD-07](https://github.com/hzrd149/blossom/blob/master/buds/07.md) ("Payment required").
It lets a Blossom server be paid with an off-chain [Ark](https://ark-protocol.org) payment.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT" and "MAY" are to be interpreted as
described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

## Summary

The `X-Ark` header in a `402 Payment Required` response is a [BIP-321](https://github.com/bitcoin/bips/blob/master/bip-0321.mediawiki)
payment URI:

```http
X-Ark: bitcoin:?ark=ark1…&lightning=lnbc…&amount=0.00000003
```

A client can hand that value unchanged to its wallet, for example with the
[NWC-321](https://github.com/nostr-wallet-connect/nwc/blob/main/321.md) `pay` method. The wallet picks
the instruction it can pay: `ark` when the Ark address belongs to the wallet's own Ark server, otherwise
another instruction in the same URI, typically `lightning`. The client does not need to know anything
about Ark servers. The payment proof for an Ark payment is the Ark address itself.

## Motivation

An Ark payment between two users of the same Ark server is cosigned by the server and takes effect
in seconds, without a round, an on-chain transaction or a Lightning route. That suits the small,
frequent payments BUD-07 is used for: per upload, per download, per MB.

Ark wallets (Bark, Arkade, Wavelength) can already pay `X-Lightning`. But when the client and the
Blossom server use the same Ark server, paying over Lightning adds a Lightning fee and a liquidity
round trip through the Ark server, and needs a Lightning receiver on the Blossom server's side.
`X-Ark` lets them pay each other directly. When they are on different Ark servers, the wallet pays
over Lightning instead.

BIP-321 already carries several payment instructions in one URI, and NWC-321 already lets a client pass
such a URI to a wallet and let the wallet choose. `X-Ark` reuses both rather than defining a new
request format or new wallet methods.

## Terms

- **Ark server**: the operator that cosigns a wallet's off-chain transactions.
- **Ark address**: a [BOAT-0001](https://github.com/ark-protocol/boats/blob/master/boat-0001.md)
  address: bech32m with human-readable part `ark` (mainnet) or `tark` (test networks). It commits to
  one Ark server: a version 0 address contains the server's x-only public key, and a version 1
  address contains `ark_id`, the first 4 bytes of SHA-256 of the server's public key. An Ark address
  has no amount and no expiry, and it can be paid more than once.
- **Settled**: the Ark server has cosigned the payment and the receiving wallet holds the received
  VTXOs and can spend them. This is the meaning used by the
  [NWC Ark Payments](https://github.com/nostr-wallet-connect/nwc/pull/11) extension.

Off-chain Ark payments are only possible between users of the same Ark server.

## Server: 402 response

When a server requires payment and supports Ark, it includes an `X-Ark` header in the
`402 Payment Required` response. Its value is a BIP-321 URI with an empty address and these
parameters:

| Parameter   | Required | Value                                                                                          |
| ----------- | -------- | ---------------------------------------------------------------------------------------------- |
| `ark`       | yes      | A fresh Ark address of the server's wallet, unique to this payment request.                    |
| `amount`    | yes      | The price, in BTC as defined by BIP-321. It MUST be a whole number of satoshis.                 |
| `lightning` | no       | The BOLT11 invoice the server sends in `X-Lightning` in the same response, for the same amount. |

BIP-321 says that payment instructions with a bech32 or bech32m encoding SHOULD use their
human-readable part as the query key, so the key is `ark`. As with `sp` for `sp1…` and `tsp1…`
addresses, the key stays `ark` for test-network `tark1…` addresses.

```http
HTTP/1.1 402 Payment Required
X-Lightning: lnbc30n1…
X-Ark: bitcoin:?ark=ark1pwh9vsmezqqpharv69q4z8m6x364d5m5prnmcalcalq9pdmzw0y7mpveck4pcfhezqypczkrrj3lkx5ue4qrf4jc7ztpt9htdttmh2judhqnu7aue8p0y9mqkr4cf5&lightning=lnbc30n1…&amount=0.00000003
```

The server:

- MUST return a new Ark address in every `X-Ark` header it sends, and MUST NOT reuse an address for
  another payment request.
- MUST record, for each address it hands out, the quoted amount, the time it was issued, and the
  operation it was quoted for (endpoint and, when known, the blob's sha256).
- SHOULD also offer `X-Lightning`, so clients that do not read `X-Ark`, and wallets on other Ark
  servers, can pay.
- SHOULD include the `X-Lightning` invoice as `lightning` in the `X-Ark` URI when it sends both, so
  that a client can pay with one wallet call. If it does, the invoice MUST be identical to the
  `X-Lightning` value and its amount MUST equal `amount`.
- MUST NOT add BIP-321 `req-` parameters, which wallets that do not know them must reject.
- SHOULD list `X-Ark` in `Access-Control-Expose-Headers`, so browser clients can read it (as for
  `X-Lightning` and `X-Cashu`).

The URI uses only standard BIP-321 parameters, so the value of `X-Ark` can be passed unchanged to any
BIP-321 wallet or shown as a QR code. A wallet without Ark support pays the `lightning` instruction.

### Why a BIP-321 URI

`X-Lightning` and `X-Cashu` each carry an existing payment request format (BOLT11 and a NUT-18
request), with the amount inside it. Ark has no payment request format of its own, but BIP-321 is the
standard container for Bitcoin payment instructions, and its `amount` puts the price inside the request
in the same way. Bark already parses and produces `ark` in BIP-321 URIs. A URI is also what wallets
accept from a QR code or a paste, so a client that cannot pay programmatically can hand it to the user.
JSON or a base64 payload would need a new parser in every client and wallet.

### Why there is no Ark server parameter

The client does not need to match Ark servers. The address already commits to its Ark server, and only
the wallet knows which Ark server it uses, so the wallet makes the choice when it is asked to pay. An
earlier draft of this document carried the server's public key in a non-standard `ark-server`
parameter. It is redundant with the address and is no longer used. Servers MUST NOT require it, and
clients and wallets ignore it.

A version 1 address identifies its Ark server by a 4-byte hash. An accidental collision is negligible,
and only the payee chooses the address, so a deliberately colliding address could only cost the payee
the payment.

## Client: paying

A client that supports `X-Ark` pays the URI in one of two ways.

**With NWC-321.** If the client's wallet connection supports the NWC-321 `pay` method, the client:

1. Calls `pay` with the `X-Ark` value unchanged as `payment`. It does not need to parse it.
2. The wallet service selects one instruction, as NWC-321 requires. A wallet that supports Ark
   payments selects `ark` when the address is valid for its network and commits to its own Ark server
   (see Terms), and otherwise another supported instruction, typically `lightning`. If it can pay
   none, it returns `UNSUPPORTED_PAYMENT_INSTRUCTION` and the client uses another payment method from
   the same 402 response, such as `X-Cashu`.
3. Waits until the payment is settled: `state` is `settled` in the `pay` response, or later through
   `lookup_payment`. For an `ark` payment, settled means cosigned by the Ark server, as defined by the
   NWC Ark Payments extension.
4. Sends the proof that matches the instruction the wallet reports in `instruction_type`: for `ark`,
   the Ark address in `X-Ark` (see below); for a Lightning instruction, the `preimage` in
   `X-Lightning`, as BUD-07 defines.

A client MUST NOT call `pay` again for the same URI while an earlier call may still be pending, since
paying an Ark address twice makes two payments.

**With an Ark wallet directly.** A client that controls an Ark wallet itself:

1. Parses the URI and checks that the address is a valid Ark address for its network.
2. Checks that the address commits to its wallet's Ark server. If it does not, the client uses another
   payment method, such as the `lightning` instruction or `X-Lightning`.
3. Pays exactly `amount` to the address with an off-chain Ark payment, at most once.
4. Waits until its wallet reports the payment as settled (cosigned by the Ark server).
5. Retries the original `PUT` or `GET` request with the payment proof.

As BUD-07 requires, `HEAD` requests are never retried with proof. A client that got an `X-Ark` header
on a `HEAD` request pays it and sends the proof with the `PUT` or `GET` request.

## Client: payment proof

The proof is the Ark address from the `X-Ark` header, sent unchanged in an `X-Ark` request header:

```http
PUT /upload HTTP/1.1
X-Ark: ark1pwh9vsmezqqpharv69q4z8m6x364d5m5prnmcalcalq9pdmzw0y7mpveck4pcfhezqypczkrrj3lkx5ue4qrf4jc7ztpt9htdttmh2judhqnu7aue8p0y9mqkr4cf5
```

An Ark payment has no preimage or token that the payer could show. It does not need one: the address
is unique to the request, and the server sees every payment to its own addresses in its own wallet.
Transaction identifiers are wallet-specific, so the server cannot use one supplied by the client.

If the wallet paid the `lightning` instruction of the `X-Ark` URI instead, the proof is the preimage in
`X-Lightning`, exactly as if the client had paid the `X-Lightning` header, since it is the same invoice.

## Server: verifying the proof

On a request with an `X-Ark` header, the server MUST check that:

1. the address is one it issued in an `X-Ark` 402 response and it has not expired (see below);
2. the request is for the operation the address was quoted for;
3. the payments to the address that are settled in the server's wallet add up to at least the quoted
   amount;
4. the address has not already been redeemed.

If all checks pass, the server MUST mark the address as redeemed in the same atomic step in which it
accepts the request, and then processes the request. An address is redeemed at most once. A later
request with the same address MUST be rejected, even if more was paid to it.

Before deciding that a payment has not arrived, the server SHOULD sync its wallet with the Ark server
(for Bark, its mailbox), and MAY wait a few seconds for a pending payment to settle.

### Partial payments and overpayment

Payments to the same address add up. If the settled total is below the quoted amount, the server
rejects the request and keeps the address open until it expires. The client MAY pay the difference
to the same address and retry.

The server MUST accept a settled total above the quoted amount. It is not required to refund the
difference. Payments that arrive after an address was redeemed or has expired are not credited to
any request. Servers MAY refund them or credit them in some other way, outside this specification.

### Expiry

An Ark address does not expire, and a wallet cannot refuse a payment to it. Expiry here is the
server's policy for how long it will redeem an address. The server SHOULD redeem an address for at
least 10 minutes after it was issued. It MUST NOT treat an address as expired if the quoted amount
was settled to it before the expiry time.

### Errors

As in BUD-07, if the proof is not accepted the server MUST respond with `400 Bad Request` and an
`X-Reason` header with a human-readable message. Clients MUST NOT parse `X-Reason`. Example reasons:

| Case                                            | Example `X-Reason`                                          |
| ----------------------------------------------- | ----------------------------------------------------------- |
| Not an Ark address, or not one this server sent | `Unknown Ark payment address`                               |
| Quoted for a different operation                | `Ark payment address was issued for a different request`    |
| Nothing settled yet                             | `No settled Ark payment to this address yet`                |
| Settled total too low                           | `Ark payment incomplete: 1 of 3 sats received`              |
| Already used                                    | `Ark payment address already redeemed`                      |
| Expired with nothing paid                       | `Ark payment request expired`                               |

A client that gets `400` for a payment that is still pending or incomplete MAY retry with the same
address. In all other cases it starts again from the original request, which returns a new 402.

## Complete example

A server offering Cashu, Lightning and Ark for an upload (the `X-Cashu` and `X-Lightning` values are
the examples from BUD-07):

```http
HTTP/1.1 402 Payment Required
X-Cashu: creqApWF0gaNhdGVub3N0cmFheKlucHJvZmlsZTFxeTI4d3VtbjhnaGo3dW45ZDNzaGp0bnl2OWtoMnVld2Q5aHN6OW1od2RlbjV0ZTB3ZmprY2N0ZTljdXJ4dmVuOWVlaHFjdHJ2NWhzenJ0aHdkZW41dGUwZGVoaHh0bnZkYWtxcWd5ZGFxeTdjdXJrNDM5eWtwdGt5c3Y3dWRoZGh1NjhzdWNtMjk1YWtxZWZkZWhrZjBkNDk1Y3d1bmw1YWeBgmFuYjE3YWloYjdhOTAxNzZhYQphdWNzYXRhbYF4Imh0dHBzOi8vbm9mZWVzLnRlc3RudXQuY2FzaHUuc3BhY2U
X-Lightning: lnbc30n1pnnmw3lpp57727jjq8zxctahfavqacymellq56l70f7lwfkmhxfjva6dgul2zqhp5w48l28v60yvythn6qvnpq0lez54422a042yaw4kq8arvd68a6n7qcqzzsxqyz5vqsp5sqezejdfaxx5hge83tf59a50h6gagwah59fjn9mw2d5mn278jkys9qxpqysgqt2q2lhjl9kgfaqz864mhlsspftzdyr642lf3zdt6ljqj6wmathdhtgcn0e6f4ym34jl0qkt6gwnllygvzkhdlpq64c6yv3rta2hyzlqp8k28pz
X-Ark: bitcoin:?ark=ark1pwh9vsmezqqpharv69q4z8m6x364d5m5prnmcalcalq9pdmzw0y7mpveck4pcfhezqypczkrrj3lkx5ue4qrf4jc7ztpt9htdttmh2judhqnu7aue8p0y9mqkr4cf5&lightning=lnbc30n1pnnmw3lpp57727jjq8zxctahfavqacymellq56l70f7lwfkmhxfjva6dgul2zqhp5w48l28v60yvythn6qvnpq0lez54422a042yaw4kq8arvd68a6n7qcqzzsxqyz5vqsp5sqezejdfaxx5hge83tf59a50h6gagwah59fjn9mw2d5mn278jkys9qxpqysgqt2q2lhjl9kgfaqz864mhlsspftzdyr642lf3zdt6ljqj6wmathdhtgcn0e6f4ym34jl0qkt6gwnllygvzkhdlpq64c6yv3rta2hyzlqp8k28pz&amount=0.00000003
```

The client calls NWC-321 `pay` with the `X-Ark` value:

```json
{ "method": "pay", "params": { "payment": "bitcoin:?ark=ark1pwh9…&lightning=lnbc30n1…&amount=0.00000003" } }
```

The client's wallet uses the same Ark server as the address (its `ark_id` is `75cac86f`), so it pays
3 sats to the address and reports `"instruction_type": "ark"` and `"state": "settled"`. The client
retries the upload:

```http
PUT /upload HTTP/1.1
Content-Type: image/png
Content-Length: 184292
X-SHA-256: 88a74d0b866c8ba79251a11fe5ac807839226870e77355f02eaf68b156522576
X-Ark: ark1pwh9vsmezqqpharv69q4z8m6x364d5m5prnmcalcalq9pdmzw0y7mpveck4pcfhezqypczkrrj3lkx5ue4qrf4jc7ztpt9htdttmh2judhqnu7aue8p0y9mqkr4cf5
```

```http
HTTP/1.1 201 Created
```

Had the wallet been on another Ark server, it would have paid the `lightning` instruction instead, and
the client would have retried with `X-Lightning: <preimage>`.

The address is the version 1 (Bark) mainnet test vector from Bark's address code
(`lib/src/address.rs`), for the Ark server key
`02037188bdd7579a0cd0b22a51110986df1ea08e30192658fe0e219590e4a723d3`. Its `ark_id` (`75cac86f`) is the
first 4 bytes of SHA-256 of that key.

## Security and privacy considerations

- Anyone who learns an unredeemed, paid address can present it first. Servers send it only in the
  402 response over HTTPS. When the request carries [BUD-11](https://github.com/hzrd149/blossom/blob/master/buds/11.md)
  authorization, the server SHOULD bind the address to the authorizing pubkey and reject proofs
  from another pubkey.
- Ark payments cannot be refused, so the redeemed-once rule must be enforced atomically on the
  server, or one payment could pay for two requests.
- The Ark server sees both sides of every off-chain payment it cosigns. A fresh address per request
  keeps payments to the Blossom server from being linked to each other by address.
- A settled Ark payment is off-chain. The received VTXOs depend on the Ark server until the Blossom
  server's wallet refreshes them. Expiry and refresh are wallet maintenance and are out of scope.

## Implementation notes

The method is implementation-neutral: any Ark wallet that can create fresh addresses and list settled
incoming payments per address can back the server side, and any Ark wallet that can pay an address can
back the client side. For example, a server using Bark's `barkd` creates the address with
`POST /api/v1/wallet/addresses/next`, sums successful incoming movements on the address from
`GET /api/v1/history`, and creates the `lightning` invoice through the Ark server's Lightning gateway.
On the client side, a wallet that implements NWC-321 `pay` and the NWC Ark Payments extension pays the
`X-Ark` value with no Ark-specific code in the client.
