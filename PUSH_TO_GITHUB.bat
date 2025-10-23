@echo off
echo.
echo ========================================
echo   Push to GitHub - Interactive Setup
echo ========================================
echo.

:input
set /p username="Enter your GitHub username: "
if "%username%"=="" (
    echo Username cannot be empty!
    goto input
)

set /p reponame="Enter your repository name (e.g., wifi-signal-analyzer): "
if "%reponame%"=="" (
    echo Repository name cannot be empty!
    goto input
)

echo.
echo ========================================
echo   Configuration:
echo   Username: %username%
echo   Repository: %reponame%
echo   URL: https://github.com/%username%/%reponame%.git
echo ========================================
echo.

set /p confirm="Is this correct? (Y/N): "
if /i not "%confirm%"=="Y" goto input

echo.
echo Adding GitHub remote...
git remote add origin https://github.com/%username%/%reponame%.git
if errorlevel 1 (
    echo.
    echo Remote already exists. Removing old remote and adding new one...
    git remote remove origin
    git remote add origin https://github.com/%username%/%reponame%.git
)

echo.
echo Renaming branch to main...
git branch -M main

echo.
echo ========================================
echo   Ready to push to GitHub!
echo ========================================
echo.
echo IMPORTANT: You'll need to authenticate
echo - Use your GitHub Personal Access Token
echo - NOT your regular password
echo.
echo How to get a token:
echo 1. Go to GitHub.com
echo 2. Settings -^> Developer settings
echo 3. Personal access tokens -^> Tokens (classic)
echo 4. Generate new token with 'repo' scope
echo.
echo ========================================
echo.

pause

echo.
echo Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
if errorlevel 1 (
    echo   Push FAILED!
    echo   Check the error above and try again.
    echo.
    echo   Common issues:
    echo   - Wrong credentials
    echo   - Repository doesn't exist
    echo   - No internet connection
) else (
    echo   Push SUCCESSFUL! 
    echo.
    echo   Your repository is now on GitHub:
    echo   https://github.com/%username%/%reponame%
)
echo ========================================
echo.

pause
