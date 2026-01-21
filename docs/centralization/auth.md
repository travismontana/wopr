# Central AAA (not the car kind)

- Authentication
  - Auth to google
  - SSO/OAUTH ALL THE THINGS
- Authorization
  - Use groups to control access
    - wopr-admin-sg: Admin Security Group
    - wopr-user-sg: The user (user/password)
- Access
  - Have all incoming traffic force through a central thing
  - Use heimdall as the landing page
  - have the ability to choose landing pages after login

## Questions to ask
[ ] - Is there something that does what I'm asking already (it's like netscaler app gateway)

## What I want:
- 1 page you hit to enter WOPR, wopr.${DOMAIN}
- If not already logged in, have you login.  Pretty flexible here, basically, the big reqs: use google as a provider, and a local future provider
- Once logged in, if a normal user, then you go to games.wopr.${DOMAIN}
- If admin, you get a dashboard of the things we have to admin
- Runs on-prem in k8s
- Free, simple, easy to manage, not a lot of moving parts