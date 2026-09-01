### for the IOS app:

I am thinking that we end up getting rid of the nav bar at the bottom and instead:

- when the user opens the app, the app is on the 'title screen' for a bit and it checks if the user has an account and if not, it throws them onto the login page
- otherwise, they go to the home page, and on the home page there is a big sticky button at the bottom of the screen that says "Capture Picture". Once you click it, you will take a screenshot, then it'll take you to the plant analysis page
- Additionally, the Home Page should have a profile icon in the top right. Clicking on it takes you to your user profile

## for the backend
- Consider making a prelude for the backend since axum reuses a lot of stuff
- remove hardcoded paths in the test and prefer using temp dir
