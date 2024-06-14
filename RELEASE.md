# Releasing `requests-ecp`

The instructions below detail how to finalise a new release
for version `{X.Y.Z}`.

In all commands below that placeholder should be replaced
with an actual release version.

## 1. Update the packaging files

-   Create a new branch on which to update the OS packaging files:

    ```shell
    git checkout -b finalise-{X.Y.Z}
    ```

-   Bump the version in the Python package `requests_ecp/__init__.py` file

-   Bump versions and add changelog entries in OS packaging files:

    - `debian/changelog`
    - `rpm/requests-ecp.spec`

    and then commit the changes to the branch.

-   Push this branch to your fork:

    ```shell
    git push -u origin finalise-{X.Y.Z}
    ```

-   Open a merge request on GitLab to finalise the packaging update.

## 2. Create a tag/release on GitLab

-   Draft release notes by looking through the merge requests associated
    with the relevant
    [milestone on GitLab](https://git.ligo.org/computing/software/requests-ecp/-/milestones).

-   Create a new Tag and Release using the GitLab UI.

    -   Go to <https://git.ligo.org/computing/software/requests-ecp/-/release/new>

    -   In the `Tag name` search box, enter the version number (`{X.Y.Z}`) as
        the new tag name and select `Create tag`.

    -   In the message box, paste the release notes, then select `Save`.

    -   In the `Milestones` dropdown menu box select the matching project 
        milestone.

    -   In the `Release notes` text box (for the `Release`), paste the release
        notes again. (This way the release notes are visible from both the `git`
        command-line client, _and_ the release page on the UI)

    -   Under `Release Assets` add a link to the new tarball on PyPI. Use the
        following values:

        | Field | Value |
        | ----- | ----- |
        | URL | `https://pypi.io/packages/source/r/requests-ecp/requests_ecp-{X.Y.Z}.tar.gz` |
        | Link title | `Official source distribution` |
        | Type | `Package` |
