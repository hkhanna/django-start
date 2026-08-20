# django-start

This repository is a template for my Django projects. 

## Generating a new Django project from this template

1. Pick a suitable project name.
1. Run `copier copy git@github.com:hkhanna/django-start.git path/to/destination`
1. Create a fresh Github repo for the project.
1. Point the `origin` remote to a fresh Github repo.
1. Remove or replace the LICENSE file.
1. Update `env.example` to the desired defaults for the new project.
1. Grep for the string `django-start` and either replace that string with the project name or take the other described action.
1. Do the "Local Installation" in the README.
1. (Optional) Make sure the mattpocock-skills plugin is installed and run /setup-matt-pocock-skills

## First Deploy to Production - Render.com

1. Create the application in the Render web interface.
1. [TBD - This needs to be filled out.]
1. Create a [Sentry Uptime Monitor](https://docs.sentry.io/product/uptime-monitoring/) pointed at `https://<host>/healthz`. No Sentry SDK is required for uptime monitoring.

## Updating a project from this template
TBD
