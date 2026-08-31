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
