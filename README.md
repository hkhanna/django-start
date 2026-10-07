# django-start

This repository is a template for my Django projects. 

## Generating a new Django project from this template

1. Pick a suitable project name.
1. Run `uvx copier copy https://github.com/hkhanna/django-start path/to/destination`
1. Grep for the string `django-start` and either replace that string with the project name or take the other described action.
 - Don't worry about uv.lock. It will get overwritten during `make all`.
1. Update `env.op` to the desired defaults for the new project.
1. Remove or replace the LICENSE file.
1. Do the "Local Installation" in the README.
1. Create git repo and initial commit
1. Create a fresh Github repo for the project.
1. Point the `origin` remote to a fresh Github repo.
1. (Optional) Make sure the mattpocock-skills plugin is installed and run /setup-matt-pocock-skills

## First Deploy to Production - Render.com

1. Create a "New Blueprint Instance" in the Render web interface and connect it to the Git repo.
1. Deploy the Blueprint.
1. Add a custom domain, if appropriate.
1. Create a [Sentry Uptime Monitor](https://docs.sentry.io/product/uptime-monitoring/) pointed at `https://<host>/healthz`. No Sentry SDK is required for uptime monitoring.

## Updating a project from this template
1. From the downstream project, run `uvx copier update`
2. Resolve any conflicts by hand, then commit the changes.
