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

Default test user login:
testuser@test.com
password

by the way to reliably run prod build of Tauri app on ios do `pnpm tauri ios build --open` otherwise it goes nuts
