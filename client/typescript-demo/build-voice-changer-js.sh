#!/bin/bash

cd ../typescript/
npm run build:prod
cd -

rm -rf node_modules/tts-client-typescript-client-lib
mkdir -p node_modules/tts-client-typescript-client-lib/dist
cp ../typescript/package.json node_modules/tts-client-typescript-client-lib/
cp -r ../typescript/dist/* node_modules/tts-client-typescript-client-lib/dist/

