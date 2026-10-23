# Blossom `X-Ark`: Ark payments for BUD-07

`draft` `optional`

This document defines `X-Ark`, a payment method for
[Blossom BUD-07](https://github.com/hzrd149/blossom/blob/master/buds/07.md) ("Payment required").
It lets a Blossom server be paid with an off-chain [Ark](https://ark-protocol.org) payment.

The key words "MUST", "MUST NOT", "SHOULD", "SHOULD NOT" and "MAY" are to be interpreted as
described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

## Motivation

An Ark payment between two users of the same Ark server is cosigned by the server and takes effect
in seconds, without a round, an on-chain transaction or a Lightning route. That suits the small,
frequent payments BUD-07 is used for: per upload, per download, per MB.

Ark wallets (Bark, Arkade, Wavelength) can already pay `X-Lightning`. But when the client and the
Blossom server use the same Ark server, paying over Lightning adds a Lightning fee and a liquidity
round trip through the Ark server, and needs a Lightning receiver on the Blossom server's side.
`X-Ark` lets them pay each other directly. When they are on different Ark servers, the client pays
`X-Lightning` instead.

## Terms

- **Ark server**: the operator that cosigns a wallet's off-chain transactions.
- **Ark address**: a [BOAT-0001](https://github.com/ark-protocol/boats/blob/master/boat-0001.md)
  address: bech32m with human-readable part `ark` (mainnet) or `tark` (test networks). It commits to
  one Ark server. An Ark address has no amount and no expiry, and it can be paid more than once.
- **Settled**: the Ark server has cosigned the payment and the receiving wallet holds the received
  VTXOs and can spend them. This is the meaning used by the
  [NWC Ark Payments](https://github.com/nostr-wallet-connect/nwc/pull/11) extension.

Off-chain Ark payments are only possible between users of the same Ark server.

## Server: 402 response

When a server requires payment and supports Ark, it includes an `X-Ark` header in the
`402 Payment Required` response. Its value is a [BIP-321](https://github.com/bitcoin/bips/blob/master/bip-0321.mediawiki)
URI with an empty address and these parameters:

| Parameter    | Required | Value                                                                                           |
| ------------ | -------- | ----------------------------------------------------------------------------------------------- |
| `ark`        | yes      | A fresh Ark address of the server's wallet, unique to this payment request.                     |
| `amount`     | yes      | The price, in BTC as defined by BIP-321. It MUST be a whole number of satoshis.                  |
| `ark-server` | yes      | The server's Ark server public key: 33-byte compressed secp256k1 key, lowercase hex.             |

```http
HTTP/1.1 402 Payment Required
X-Ark: bitcoin:?ark=ark1pwh9vsmezqqpharv69q4z8m6x364d5m5prnmcalcalq9pdmzw0y7mpveck4pcfhezqypczkrrj3lkx5ue4qrf4jc7ztpt9htdttmh2judhqnu7aue8p0y9mqkr4cf5&amount=0.00000003&ark-server=02037188bdd7579a0cd0b22a51110986df1ea08e30192658fe0e219590e4a723d3
```

The server:

- MUST return a new Ark address in every `X-Ark` header it sends, and MUST NOT reuse an address for
  another payment request.
- MUST record, for each address it hands out, the quoted amount, the time it was issued, and the
  operation it was quoted for (endpoint and, when known, the blob's sha256).
- MUST use an `ark-server` key that the `ark` address commits to: for a version 0 address, the
  address server key is the x-only form of `ark-server`; for a version 1 address, the address
  `ark_id` is the first 4 bytes of SHA-256 of `ark-server`.
- SHOULD also offer `X-Lightning`, so clients on other Ark servers, and non-Ark clients, can pay.

- SHOULD list `X-Ark` in `Access-Control-Expose-Headers`, so browser clients can read it (as for
  `X-Lightning` and `X-Cashu`).

`ark-server` is not a standard BIP-321 parameter. Wallets that do not know it ignore it, so the
value of `X-Ark` can be passed unchanged to any Ark wallet or shown as a QR code.

### Why a BIP-321 URI

`X-Lightning` and `X-Cashu` each carry an existing payment request format (BOLT11 and a NUT-18
request), with the amount inside it. Ark has no payment request format of its own, but BIP-321
already carries Ark addresses in an `ark` parameter (Bark parses and produces it), and its `amount`
puts the price inside the request in the same way. A URI is also what Ark wallets accept from a QR
code or a paste, so a client that cannot pay programmatically can hand it to the user. JSON or a
base64 payload would need a new parser in every client and wallet.

## Client: paying

A client that supports `X-Ark`:

1. Parses the URI and checks that the address is a valid Ark address for its network, and that the
   address commits to `ark-server` (see above). If not, it MUST NOT pay it.
2. Checks that `ark-server` is its own wallet's Ark server. With NWC, that is the
   `get_info.ark.server_pubkey` value. If it differs, the client uses another payment method from
   the same 402 response, such as `X-Lightning`.
3. Pays exactly `amount` to the address with an off-chain Ark payment. With NWC, it calls
   `pay_ark_address` with the address, `amount` in millisatoshis, and the address as the
   `idempotency_key`, so a retried payment is never made twice.
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
X-Ark: bitcoin:?ark=ark1pwh9vsmezqqpharv69q4z8m6x364d5m5prnmcalcalq9pdmzw0y7mpveck4pcfhezqypczkrrj3lkx5ue4qrf4jc7ztpt9htdttmh2judhqnu7aue8p0y9mqkr4cf5&amount=0.00000003&ark-server=02037188bdd7579a0cd0b22a51110986df1ea08e30192658fe0e219590e4a723d3
```

The client's Ark wallet uses Ark server `02037188…a723d3`, so it pays 3 sats to the address. Once the
payment is settled, it retries the upload:

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

The address and server key are the version 1 (Bark) mainnet test vector from Bark's address code
(`lib/src/address.rs`). The address `ark_id` (`75cac86f`) is the first 4 bytes of SHA-256 of the
server key.

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
`POST /api/v1/wallet/addresses/next`, reads its Ark server key from `GET /api/v1/wallet/ark-info`,
and sums successful incoming movements on the address from `GET /api/v1/history`.
