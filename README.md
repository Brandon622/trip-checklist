# Cape Town trip checklist

A single self-contained `index.html`. No build step, no dependencies, no SDK.
Open it and it works; add a Firebase Realtime Database URL and it syncs between two phones.

Trip: JNB → CPT Fri 23 Oct 2026 06:30, home Mon 26 Oct 2026 17:00 (LIFT 17:00 dep).

## How it behaves

- **Local first.** Everything is written to `localStorage` immediately, so it works on a plane, in a lift, with no signal.
- **Optional cloud.** With a database URL + trip code configured, it polls every 8 seconds, merges, and pushes back. Both devices converge.
- **Merge rule.** Per item, the most recently modified version wins (`uu` timestamp). Items are never lost by a stale write unless two people edit the *same item* inside the same ~8 s window.
- **Row order is stable.** Ticking something doesn't move it under your thumb.

## One-time Firebase setup (~4 minutes, free)

1. <https://console.firebase.google.com> → **Add project** → name it anything → Analytics off → **Create**.
2. Left sidebar: **Build → Realtime Database → Create Database**.
   - Location: `europe-west1` (closest to South Africa).
   - Start in **locked mode**.
3. Open the **Rules** tab, replace everything with the JSON below, then **Publish**:

```json
{
  "rules": {
    ".read": false,
    ".write": false,
    "trips": {
      "cpt-oct26-k7q4m2": {
        ".read": true,
        ".write": true
      }
    }
  }
}
```

4. Copy the database URL shown at the top of the Data tab. It looks like
   `https://<project>-default-rtdb.europe-west1.firebasedatabase.app`
5. Open the checklist → **⚙︎ Sync** → paste that URL → trip code `cpt-oct26-k7q4m2` → **Save & sync**.
6. Send your partner the same page link and the same two values. She does step 5 once.

### What the security actually is

- The `apiKey`/config being visible is normal in any web app; it is not the lock.
- The lock is the rules above: read/write is allowed **only** at `/trips/cpt-oct26-k7q4m2`. Everything else is denied.
- So access needs the database URL **and** that code. Treat the pair like a private link.
- To go further, add Firebase **Authentication → Email/Password** for exactly two addresses and change the rule to
  `".read": "auth.token.email === 'you@example.com' || auth.token.email === 'partner@example.com'"`. Then a leaked link is useless on its own.
- Keep nothing sensitive in the list: no ID numbers, no card numbers, no passwords.

## Backup

`Backup / restore` in the footer downloads the whole state as JSON. Worth doing before any trip.

## Wonder what the easter eggs are?

<details>
<summary>Spoilers</summary>

1. Konami code (↑↑↓↓←→←→BA) — a plane flies across the screen.
2. Type `cpt` anywhere — a car drives past.
3. Type `bar` anywhere — a hint appears.
4. Tap the countdown **7 times** — a secret item gets added to the list.
5. **Long-press the title** — a captain's log entry drops in.
6. Tick **everything** — a boarding pass with your seat number, plus confetti.
7. Your third and tenth tick both get a quiet bit of encouragement.
</details>
