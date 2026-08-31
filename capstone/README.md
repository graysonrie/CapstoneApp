# Tauri Quickstart w/ Next.js

Usese pnpm as the frontend package manager

Includes these Tauri plugins:

- Store
- Dialog
- OS

## Other helpful plugins:

If you want clipboard control:
`pnpm tauri add clipboard-manager`

open files and URLs in a specified, or the default, application
`pnpm tauri add opener`

To use persistent state:

```ts
const [yourThing, setYourThing] = useTauriStoreValue("thing");
```

### Supabase

When it finishes you get local URLs and keys, typically:

Service URL
API (Auth, REST, Storage)
http://127.0.0.1:54321

Studio (dashboard)
http://127.0.0.1:54323

Postgres
postgresql://postgres:postgres@127.0.0.1:54322/postgres

Mailpit (local email)
http://127.0.0.1:54324

use `pnpm supabase start` to start the local supabase server

If Docker is acting up use

```powershell
docker stop $(docker ps -q)
```

(PowerShell) to stop all containers

In `env.local`:
NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH

Use `supabase stop` when your done
