# Vendored browser dependencies

`mathjs-15.2.0.min.js` is a number-only Math.js bundle used by the scientific calculator. It is generated from `mathjs-number-entry.js` with Math.js 15.2.0 and esbuild 0.28.2:

```powershell
npm install --no-save mathjs@15.2.0 esbuild@0.28.2
npx esbuild mathjs-number-entry.js --bundle --minify --format=iife --target=es2020 --legal-comments=none --outfile=mathjs-15.2.0.min.js
```

The Math.js Apache 2.0 license and NOTICE are included alongside the bundle.
