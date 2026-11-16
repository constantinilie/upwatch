import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import { defineConfig, globalIgnores } from 'eslint/config'

// Layer rules: app → features → shared. A layer never imports from a layer above it,
// and features talk to each other only through their public API (features/<name>/index.ts).
const deepFeatureImport = {
  group: ['@/features/*/*'],
  message: 'Import from the feature public API (@/features/<name>) instead.',
}
const appImport = { group: ['@/app', '@/app/*'], message: 'Only the app layer imports from @/app.' }
const featureImport = {
  group: ['@/features', '@/features/*'],
  message: 'shared/ must stay domain-free: it cannot import from features.',
}

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
    },
    rules: {
      'no-restricted-imports': ['error', { patterns: [deepFeatureImport] }],
    },
  },
  {
    files: ['src/features/**/*.{ts,tsx}'],
    rules: {
      'no-restricted-imports': ['error', { patterns: [deepFeatureImport, appImport] }],
    },
  },
  {
    files: ['src/shared/**/*.{ts,tsx}'],
    rules: {
      'no-restricted-imports': ['error', { patterns: [featureImport, appImport] }],
    },
  },
])
