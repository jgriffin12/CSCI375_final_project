# CSCI450 Final Compiler Extension: CJ Secure Policy Compiler

## Project Overview

This project extends the Secure Access Data Portal by adding a compiler component for a small access-control policy language.

The Secure Access Data Portal is the runtime/demo environment. The compiler portion is the CSCI450 final project. It reads a custom `.cjsp` source file, tokenizes the input, parses it into an AST, performs semantic checks, and generates a compiled JSON policy file that the portal can use for role-based access control.

## Language Name

CJ Secure Policy Language

File extension:

```
.cjsp
```

## Purpose of the Language

The purpose of this language is to define access-control rules in a simple, readable format.

Instead of hardcoding every role and permission directly inside the application, the policy can be written in a `.cjsp` file and compiled into a JSON configuration file. The portal can then load that compiled policy at runtime.

This connects the compiler directly to the existing security application.

## Example Source Program

```
role provider can view_masked_record;
role patient can view_own_record;
role admin can review_logs, manage_users, view_full_record;

deny patient review_logs;
mask ssn for provider;
mask diagnosis for patient;
```

This program defines:

- Which permissions each role has
- Which role/permission combinations are denied
- Which fields should be masked for specific roles

## BNF Grammar

```
<program>          ::= <statement>* EOF
<statement>        ::= <role_rule> | <deny_rule> | <mask_rule>
<role_rule>        ::= "role" <identifier> "can" <permission_list> ";"
<deny_rule>        ::= "deny" <identifier> <identifier> ";"
<mask_rule>        ::= "mask" <identifier> "for" <identifier> ";"
<permission_list>  ::= <identifier> ("," <identifier>)*
<identifier>       ::= <letter> (<letter> | <digit> | "_" | "-")*
```

## Compiler Phases Implemented

### Lexer

File:

```
apps/compiler/lexer.py
```

The lexer reads the raw `.cjsp` source file and converts it into tokens.

It recognizes:

- Keywords such as `role`, `can`, `deny`, `mask`, and `for`
- Identifiers
- Commas
- Semicolons
- Comments
- End of file

This is the lexical analysis phase of the compiler.

### Parser

File:

```
apps/compiler/parser.py
```

The parser is a recursive-descent parser. It reads the token stream from the lexer and checks whether the program follows the grammar.

If the syntax is valid, the parser builds an AST. If the syntax is invalid, it reports a parser error.

This is the syntax analysis phase of the compiler.

### AST

File:

```
apps/compiler/ast_nodes.py
```

The AST represents the structure of the policy program after parsing.

The main AST node types are:

- `Program`
- `RoleRule`
- `DenyRule`
- `MaskRule`

The AST gives the compiler a structured version of the source program so later phases can analyze and generate output from it.

### Semantic Analysis

File:

```
apps/compiler/semantic.py
```

The semantic analyzer checks whether the parsed program makes sense beyond just having correct syntax.

It checks for errors such as:

- Duplicate role definitions
- Unknown permissions
- Masking rules for roles that were not defined
- Unsafe patient permissions, such as giving a patient access to `review_logs` or `manage_users`

This phase makes sure the policy is valid before code generation happens.

### Code Generation

File:

```
apps/compiler/codegen.py
```

The code generator converts the checked AST into a compiled JSON policy file.

Generated output:

```
data/compiled_policy.json
```

This file is used by the portal’s access-control service for RBAC decisions.

### CLI Driver

File:

```
apps/compiler/cli.py
```

The CLI driver allows the compiler to be run from the terminal.

It connects the full compiler pipeline:

```
source file -> lexer -> parser -> AST -> semantic analysis -> JSON output
```

## How to Run the Compiler

From the root of the repository, run:

```
python -m apps.compiler.cli data/policies/cj_hospital_policy.cjsp -o data/compiled_policy.json
```

Expected output:

```
Policy compiled successfully: data/compiled_policy.json
```

## How to Run the Compiler Tests

Run only the compiler tests:

```
PYTHONPATH=. pytest tests/test_policy_compiler.py
```

Expected result:

```
8 passed
```

## How to Run the Full Test Suite

Run the full project test suite:

```
PYTHONPATH=. pytest
```

Current result after adding the compiler extension:

```
89 passed
```

## Project File Structure

Main compiler files:

```
apps/compiler/
  __init__.py
  tokens.py
  errors.py
  lexer.py
  parser.py
  ast_nodes.py
  semantic.py
  codegen.py
  cli.py
```

Policy source file:

```
data/policies/cj_hospital_policy.cjsp
```

Compiled output:

```
data/compiled_policy.json
```

Compiler tests:

```
tests/test_policy_compiler.py
```

Runtime connection:

```
apps/services/accessControlSvc.py
```

## How This Connects to the Secure Access Portal

The Secure Access Portal already uses role-based access control through `AccessControlService`.

The compiler extension makes the role-permission configuration generated instead of only hardcoded. If `data/compiled_policy.json` exists, `AccessControlService` loads the compiled policy file. If the compiled file is missing or invalid, the service falls back to the original built-in demo permissions.

This means the compiler output is not just a separate file. It becomes part of the application runtime.

## Why This Fits Compiler Structures

This project includes the main pieces of a compiler:

- A custom source language
- A formal grammar
- Lexical analysis
- Parsing
- AST construction
- Semantic analysis
- Code/config generation
- A command-line compiler driver
- Tests for valid and invalid programs

The `.cjsp` language is small, but it is still a complete language pipeline. The compiler reads source code, validates it, and generates output that another program uses.

## Submission Summary

I extended my Secure Access Data Portal by adding a CSCI450 compiler component.

The new compiler reads a custom `.cjsp` access-control policy language, tokenizes it, parses it into AST nodes, performs semantic checks, and generates `data/compiled_policy.json`.

The portal is the runtime/demo environment. The compiler is the main CSCI450 final work.