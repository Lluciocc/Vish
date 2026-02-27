# Visual Bash Editor (Vish)

Vish is a graphical editor for creating and managing Bash scripts using a node-based interface. It allows users to visually design their scripts by connecting various nodes that represent different Bash commands and constructs.

## Features
- Complete node-based experience for Bash scripting
- Intuitive drag-and-drop interface
- Easy visualization of script flow and logic
- Run generated Bash scripts directly from the editor
- Save and load visual scripts in JSON format
- Various user friendly features to enhance the scripting experience
- Themes support (Light/Dark/Purple)
- Multi-language support
- Settings to customize the editor behavior and appearance
- Partial Windows support (some features may be limited or unavailable on Windows)

## Screenshots

![Screenshot1](screenshots/screenshot1.png)
![Screenshot2](screenshots/screenshot2.png)

## Notes

Vish is made for educational purposes and to simplify the process of creating Bash scripts. It is not intended to replace traditional text-based scripting but rather to provide an alternative way to visualize and construct scripts.  
It can help beginners understand the structure and flow of Bash scripts, making it easier to learn scripting concepts.

## Wiki
For more detailed information about Vish, including installation instructions, usage guides, and troubleshooting tips, please visit the [Wiki](https://github.com/lluciocc/vish/wiki).

## Installation
### From Flathub
You can install Vish directly from Flathub:
https://flathub.org/apps/io.github.lluciocc.Vish

### From flatpak
You can install Vish from a self hosted source using the following command:
```bash 
flatpak install --from https://flatpak.lluciocc.fr/vish.flatpakref
```
### From AppImage
You can download the latest AppImage from the [releases page](https://github.com/lluciocc/vish/releases/latest). After downloading, make the AppImage executable and run it:
```bash
chmod +x Vish-*.AppImage
./Vish-*.AppImage
```

## Contributing
### Coding
Contributions are welcome! If you would like to contribute to Vish, please follow these steps:
1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes and commit them (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request
6. Optional: Consider adding a screenshot of your work in the PR description.

Note: Please ensure your code adheres to the existing coding style and includes appropriate tests.- This project is in active development. Features may change, and bugs may be present.

### Translating
An other way to contribute Vish is to help translating it in other languages. If you want to contribute to the translation of Vish, please follow these steps:
1. Fork the repository
2. Create a new branch (`git checkout -b translation-branch`)
3. Create a new translation file in `assets/model/{language}.json` to add translations for the new language you want to add. **You can use the existing translations as a reference.**
4. Add the translations for the new language in the newly created file (Use a basic translator if you don't know the language, but please try to be as accurate as possible) and make sure to include translations for the language name (e.g. "lang_en", "lang_fr", etc.) so that it can be displayed in the settings.
5. Add the new language to the language combo box in `ui/settings.py` (You should update `_build_language_section` to add the new language to the combo box and also update `refresh_ui_texts` function to update the language name in the combo box when the language is changed with `update_combo_item` function)
6. Commit your changes (`git commit -am 'Add translation for [Language]'`)
7. Push to the branch (`git push origin translation-branch`)
8. Create a new Pull Request

## Node Notation Convention

To simplify discussions about existing and new nodes, Vish uses a standardized node signature notation.

The format is:
`<Inputs> - <Outputs>`

Each side describes the number and type of pins using the following identifiers:

| Identifier | Type |
|------------|------|
| E | Execution / Control Flow |
| S | String |
| I | Integer |
| B | Boolean |
| P | Path |
| V | Variable |
| C | Condition |
| n |	any number possible | 
| m |	minimum required number |
| x |	maximum allowed number |
| a |	Array |

### Examples

- `1S-2S` → 1 String input, 2 String outputs  
- `1E-3E` → 1 Execution input, 3 Execution outputs  
- `2S1I-1S` → 2 String inputs, 1 Integer input, 1 String output
- `1E-nE` → 1 Execution input, Any number of outputs possible.

This notation is used for <ins>**documentation and design discussions only**</ins>.  
It reflects the internal type system and ensures consistency across the project.

## Credits
You can find the list of contributors and acknowledgements in the [CREDITS](assets/markdown/CREDITS.md) file.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details
