const tsParser = require("@typescript-eslint/parser");
const tsPlugin = require("@typescript-eslint/eslint-plugin");
const reactPlugin = require("eslint-plugin-react");
const reactHooksPlugin = require("eslint-plugin-react-hooks");

module.exports = [
  {
    files: ["**/*.ts", "**/*.tsx"],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: "latest",
        sourceType: "module",
        ecmaFeatures: { jsx: true },
      },
      globals: {
        // تعريف المتغيرات العامة لبيئة React Native + Node
        process: "readonly",
        console: "readonly",
        setTimeout: "readonly",
        clearTimeout: "readonly",
        setInterval: "readonly",
        clearInterval: "readonly",
        fetch: "readonly",
        require: "readonly",
        module: "readonly",
        __DEV__: "readonly",
        global: "readonly",
        FormData: "readonly",
        URLSearchParams: "readonly",
        AbortController: "readonly",
        Response: "readonly",
        Request: "readonly",
        Headers: "readonly",
      },
    },
    plugins: {
      "@typescript-eslint": tsPlugin,
      react: reactPlugin,
      "react-hooks": reactHooksPlugin,
    },
    settings: {
      react: {
        version: "detect",
      },
    },
    rules: {
      // تحويل أخطاء no-undef إلى تحذيرات بدلاً من أخطاء (بعد تعريفنا للـ globals يجب أن تختفي)
      "no-undef": "warn",
      // إبقاء التحذيرات للمتغيرات غير المستخدمة (اختياري: يمكنك تعطيلها مؤقتاً بـ "off")
      "@typescript-eslint/no-unused-vars": "warn",
      "no-unused-vars": "warn",
      // قواعد React الأساسية
      "react/jsx-uses-react": "off", // غير ضروري مع React 17+
      "react/react-in-jsx-scope": "off",
      "react/jsx-uses-vars": "error",
      // تجاهل بعض القواعد المزعجة
      "no-console": "off",
    },
  },
];
