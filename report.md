 # RevokeLab Phase One — Experiment Report

## 1. Objective

The objective of this experiment is to test whether a user who has been removed from a project's access list can still receive newly created private information through an already-open WebSocket connection.

The experiment specifically tests an existing live connection after permission revocation.

---

## 2. Experiment Setup

### User
- Alice

### Project
- Project Red

### Authorization mode
- Connection-only WebSocket

### Project ID
- 1

### Alice User ID
- 2

### Backend
- RevokeLab
- https://revokelab.onrender.com

---

## 3. Experiment Procedure

Each trial followed the same sequence:

1. Log in as Alice.
2. Open Alice's WebSocket connection to Project Red.
3. Confirm that the WebSocket connection is active.
4. Log in as the administrator.
5. Revoke Alice's Project Red membership.
6. Wait for a specified amount of time.
7. Create a new private message in Project Red.
8. Check Alice's already-open WebSocket connection.
9. Record whether Alice received the newly created message.
10. Restore Alice's access after the experiment.
11. Save the experiment result as a JSON file.

The waiting periods tested were:

- 1 second
- 5 seconds
- 10 seconds

---

## 4. Experimental Results

| Wait after revocation | Trials | New message received |
|---:|---:|---:|
| 1 second | 3 | 3/3 |
| 5 seconds | 4 | 4/4 |
| 10 seconds | 4 | 4/4 |
| **Total** | **11** | **11/11** |

### Observed delivery rate

**11 out of 11 valid trials (100%)** resulted in the newly created private message being received through Alice's existing WebSocket connection after her access had been revoked.

---

## 5. Observation

In the tested `connection-only` mode, Alice's existing WebSocket connection continued receiving newly created private messages after her Project Red access was revoked.

This behavior was observed across all 11 valid trials, including trials where the new message was created 10 seconds after revocation.

---

## 6. Example Experiment Flow

```text
Alice has access
       ↓
Alice opens WebSocket
       ↓
Admin revokes Alice
       ↓
Wait 1 / 5 / 10 seconds
       ↓
New private message is created
       ↓
Existing WebSocket is checked
       ↓
Alice receives the new message