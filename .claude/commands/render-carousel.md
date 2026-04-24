Render all slides from a carousel HTML file to PNG images using Playwright.

## Steps

1. Identify the target HTML file from the user's argument (e.g. `$ARGUMENTS`).
   - If an exact path is given, use it directly.
   - If only a name is given (e.g. "Geoffrey Hinton" or "Alineamiento"), search for the matching `.html` file inside the pilar directories.

2. Run the render script from the project root:
   ```
   node templates/render_slides.js "<relative/path/to/file.html>"
   ```

3. Report how many slides were saved and where (same directory as the HTML file).

## Notes
- The script requires `playwright` (`npm install playwright` + `npx playwright install chromium` if not already set up).
- Output PNGs are named `slide_01.png`, `slide_02.png`, etc. and land next to the HTML file.
- Images are gitignored, so rendered slides won't be committed.
