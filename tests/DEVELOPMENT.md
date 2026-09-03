Next Task
Implement runtime configuration before merging the feature branch.
Configuration requirements
Separate platform from runtime environment.
Platform:
macOS
Windows
Platform should determine default filesystem paths.
Runtime environment:
development
production
Default behavior:
development:
COPY files
production:
MOVE files
Do NOT assume:
macOS = development
Windows = production
The application should support:
REFF_ENV
REFF_FILE_MODE
REFF_DUMP_DIR
using a local .env.
.env must not be committed.
Create:
.env.example
for documented defaults/examples.
Next implementation steps
Refactor config.py
Add OS-aware path resolution
Add development/production runtime mode
Add copy/move file mode
Add .env support
Centralize copy/move behavior
Add tests for configuration
Add tests for copy vs move
Run pytest + Ruff
Review git diff
Commit feature branch
Open PR into main
After That
Set up GitHub Actions CI:
pytest
Ruff
run on pull requests
Then set up release workflow:
GitHub tag/release
Windows GitHub Actions runner
PyInstaller --onefile
upload EXE to GitHub Release
Finally:
download EXE on real Windows machine
test with ADB
test with real Android devices