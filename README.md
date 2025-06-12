# allianceauth-workflows

Wizards? In your spaceship game? It's more likely than you think!

## What does it do?

Originally envisioned as a way to guide users through our auth process, this tool now supports generating guided workflows for anything under the sun. Workflow steps are checked based on smart filters from allianceauth-secure-groups (among others) and completed steps are automatically skipped, streamlining the user experience.

![image](https://github.com/user-attachments/assets/0788ea0c-da56-44ad-a045-306f32cecf82)


Use this for whatever your heart desires, from corp applications to helping users resolve non-compliance with your audit protocols, to adding an altcorp to your alliance. If you can dream it, this can do it!

## Todo
- Implement wizard builder in user-facing site
- Implement user nag for available incomplete assigned wizards

## Installation

`pip install -U git+https://github.com/GoosefleetEO/allianceauth-workflows.git`

Add `'workflows'` to `INSTALLED_APPS`

`python manage.py migrate`

`python manage.py onboarding_sync_filters`

## Usage

Through the admin panel, create checks, create steps that rely on those checks, and create wizards that rely on those steps. Wizards automatically filter based on state, group membership, corp, alliance, faction, or character. Or leave all those blank and manually assign wizards to users to complete in Action Items.

## Credits

Uses filter code from allianceauth-secure-groups and allianceauth-auth-reports by Solar-Helix-Independent-Transport - without the smart filter framework from secure groups, none of this would be possible!
