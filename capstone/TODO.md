- on iOS builds of the Tauri app, whenever the user is on a text input, iOS automatically moves all of the content of the app upwards (including the mobile nav bar component) in order to make room for the keyboard at the bottom. However on native Swift apps, it does not move the app content up, or if it does, it is slightly enough in order to keep the input in view.

- Add motion animations to the other pages

- Ensure the animations show up on mobile
  (EDIT): yeah they work but ONLY on the prod build of 'pnpm tauri build ios --open' for whatever reason

- Do something about the nvm hack in project.yml for the xcode build to recognize pnpm
