@echo off

@REM frontend-libのビルド
cd client\typescript
call npx ncu -u
call npm install --force
call npm run build:prod
call npm version patch
call npm publish
cd ..\..

@REM frontendのビルド。build:prodのなかでライセンス情報を作っている。
cd client\typescript-demo
call npx ncu -u
call npm install --force
call npm run build:prod
cd ..\..


@REM Pythonモジュールのラインセンス情報の生成
poetry run generate_license_file
copy licenses_by_license.json web_front\licenses-py.json

@REM バージョン番号のインクリメントとタグの作成
poetry version patch
poetry run generate_version_file
git add pyproject.toml
git add ttsclient\version.txt
git add web_front\
git add *\package.json
git add *\package-lock.json
git add client\typescript-demo\public\assets\gui_settings\version.txt
git add client\typescript-demo\public\licenses-js.json
for /f %%i in ('poetry version -s') do set VERSION=%%i
git commit -m "Release v%VERSION%"
git push
git tag -a v%VERSION% -m "Release v%VERSION%"
git push origin --tags
