# RevokeLab Experiment

An independent experiment harness for testing permission revocation
and WebSocket behavior in the RevokeLab backend.

## Purpose

The experiment connects to the RevokeLab backend as a test user,
observes an existing WebSocket connection, revokes the user's
project membership, creates new private data, and records whether
the revoked user continues receiving that data.

## Backend

RevokeLab backend:
https://revokelab.onrender.com

## Status

Experiment harness under development.