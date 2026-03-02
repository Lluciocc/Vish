# Visual Bash Scripting Wiki
## Introduction
### Presentation
Welcome to the Vish wiki, here you'll find documentation and resources to help you get started with Visual Bash Editor (Vish). Vish is a graphical editor for creating and managing Bash scripts using a node-based interface. It allows users to visually design their scripts by connecting various nodes that represent different Bash commands and constructs.
### Target Audience
Vish is designed for both beginners and experienced Bash script writers who want to visualize and simplify the process of creating Bash scripts. It is particularly useful for those who prefer a graphical approach to scripting or want to learn Bash scripting concepts in a more intuitive way.
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

## Futher Links
- [[How to Contribute|Contribute]]
- [[Developer Guide|DeveloperGuide]]