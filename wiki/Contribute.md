# Contributing
## Coding
Contributions are welcome! If you would like to contribute to Vish, please follow these steps:
1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes and commit them (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request
6. Optional: Consider adding a screenshot of your work in the PR description.

Note: Please ensure your code adheres to the existing coding style and includes appropriate tests.- This project is in active development. Features may change, and bugs may be present.

## Translating
An other way to contribute Vish is to help translating it in other languages. If you want to contribute to the translation of Vish, please follow these steps:
1. Fork the repository
2. Create a new branch (`git checkout -b translation-branch`)
3. Create a new translation file in `assets/model/{language}.json` to add translations for the new language you want to add. **You can use the existing translations as a reference.**
4. Add the translations for the new language in the newly created file (Use a basic translator if you don't know the language, but please try to be as accurate as possible) and make sure to include translations for the language name (e.g. "lang_en", "lang_fr", etc.) so that it can be displayed in the settings.
5. Add the new language to the language combo box in `ui/settings.py` (You should update `_build_language_section` to add the new language to the combo box and also update `refresh_ui_texts` function to update the language name in the combo box when the language is changed with `update_combo_item` function)
6. Commit your changes (`git commit -am 'Add translation for [Language]'`)
7. Push to the branch (`git push origin translation-branch`)
8. Create a new Pull Request