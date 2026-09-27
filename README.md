 # RevokeLab Experiment

An independent experiment harness for testing authorization revocation on an existing WebSocket connection.

## What is this?

RevokeLab tests what happens when a user's project access is removed while they already have an active WebSocket connection.

The experiment focuses on one question:

> After Alice's access to Project Red is revoked, can she still receive newly created private messages through her existing WebSocket connection?

## Experiment Flow

```text
Alice has Project Red access
          ↓
Alice opens a WebSocket connection
          ↓
Admin revokes Alice's access
          ↓
Wait 1 / 5 / 10 seconds
          ↓
A new private message is created
          ↓
Check Alice's existing WebSocket
          ↓
Record whether Alice receives the message