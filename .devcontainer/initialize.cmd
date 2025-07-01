:: We use USERPROFILE + HOME in the devcontainer mounts configuration to support Linux and 
:: Windows. We rely on one of them being empty.
:: If we could set our own vars from these scripts, we could avoid this.
:: https://github.com/microsoft/vscode-remote-release/issues/8179
set HOME=

if not exist "%USERPROFILE%\.aws" mkdir "%USERPROFILE%\.aws"
if not exist "%USERPROFILE%\.claude" mkdir "%USERPROFILE%\.claude"
