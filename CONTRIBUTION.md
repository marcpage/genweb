# Contributing

## Getting ready to develop

- Switch to the `main` branch (lower left corner of VS Code)
- Click on the arrowed loop next to `main` in the lower left corner
- Click on the arrowed loop next to your branch name
- Starting new on a new branch
    - Click on `main` (lower left corner) and select `Create bew branch...` top-center
    - Name a branch `users/pagerk/description of change`
    - Run `make coverage` in `Terminal` tab in lower pane
- Getting back to work on an existing branch
    - Click on `main` (lower left corner) and select your branch (top-center)
    - Press Ctl-Shift-P and type in `Git merge` and select `main`
    - Run `make coverage` in `Terminal` tab in lower pane

## Review a Pull Request

When you get a pull request review request:

- Open up [GitHub](https://github.com/marcpage/genweb/pulls)
- Click on the pull request in the list
- Click the green `Add your review` button in the upper right corner
- As you review each file, click on the `Viewed` checkbox on the top-right of the file listing
- Click on the green `Review changes` button in the upper right corner
- Click Approve and then green `Submit review` button in lower right corner
- Click `Rebase and merge` (or some other `...merge`) green button
- Click `Confirm...` green button
- Click `Delete branch` gray button on the right

## Getting ready to submit

- In termainl type `make format lint`
- Fix linting errors
- Go to the Git icon on the far left and review the diff of all files
- Any files that should be reverted can use the "undo" arrow when you hover over the file
- Enter a description at the top of the Git list
- Press blue `Commit & Push` button
- Open up [GitHub](https://github.com/marcpage/genweb/pulls)
- Click on Green `Compare & pull request` button in yellow stripe at top of page
- Update the pull request title
- Add any notes to the description (optional)
- Add reviewers (click `request` next to Marc or click on `Reviewers` on far right)
- Assign PR to yourself
- ⭐ **Add any `Labels` that are appropriate** ⭐
- Click Green `Create pull request` button


## How to run

Ideally you would press the play button in the upper right corner.

If that doesn't work, try using the following in the terminal:

### Run genweb.0y

```bash
python3 -m genweb.genweb
```

### Run parse_metadata.py

```bash
python3 -m genweb.parse_metadata
```

## Helpfule files to edit

On `Linux` these file can be found here:

`~/devopsdriver
