# Forge - Architecture

## System Overview

Forge is a high-performance code generation and scaffolding engine that transforms specifications into production-ready project structures. It supports multiple frameworks, languages, and output formats with a plugin-based architecture.

```
┌─────────────────────────────────────────────────────────────────┐
│                          CLI Layer                              │
│  ┌───────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐  │
│  │  init cmd  │  │  gen cmd   │  │  add cmd   │  │ cfg cmd  │  │
│  └─────┬─────┘  └─────┬──────┘  └─────┬──────┘  └────┬─────┘  │
├────────┼───────────────┼───────────────┼───────────────┼─────────┤
│        │          Core Engine           │               │        │
│  ┌─────▼─────┐  ┌─────▼──────┐  ┌─────▼──────┐  ┌────▼────┐   │
│  │ SpecParser│  │ Generator  │  │  Scaffolder│  │ Config  │   │
│  └─────┬─────┘  └─────┬──────┘  └─────┬──────┘  └────┬────┘   │
├────────┼───────────────┼───────────────┼───────────────┼─────────┤
│        │        Template Engine         │               │        │
│  ┌─────▼─────────────────────────────▼──┐  ┌──────────▼────┐   │
│  │  TemplateManager  │  Evaluator      │  │  PluginLoader  │   │
│  └────────────────────┴────────────────┘  └───────────────┘    │
├──────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ File Writer │  │  Validators  │  │  Template Registry     │ │
│  └─────────────┘  └──────────────┘  └────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

## Component Descriptions

### CLI Layer
The command-line interface accepts user input and routes it to the appropriate core component. Supports both interactive and non-interactive modes.

- **init**: Creates a new project from a specification or template
- **gen**: Generates specific artifacts (components, services, tests)
- **add**: Adds new modules or features to an existing project
- **cfg**: Manages configuration profiles and settings

### Core Engine
The central orchestration layer that coordinates all operations.

| Component | Responsibility |
|-----------|---------------|
| `SpecParser` | Parses YAML/JSON specifications into an internal AST |
| `Generator` | Drives code generation from parsed specs and templates |
| `Scaffolder` | Creates directory structures and boilerplate files |
| `Config` | Loads, validates, and merges configuration layers |

### Template Engine
Manages template discovery, parsing, and evaluation with support for conditionals, loops, and filters.

- **TemplateManager**: Discovers and caches templates from local and remote registries
- **Evaluator**: Processes template expressions with variable interpolation

### Plugin System
Hot-loadable plugins extend Forge with custom generators, templates, and validators.

## Data Flow

```
User Input
    │
    ▼
┌──────────┐     ┌───────────┐     ┌────────────┐
│  CLI     │────▶│ SpecParser│────▶│ AST/IR     │
└──────────┘     └───────────┘     └─────┬──────┘
                                         │
                    ┌────────────────────▼─────────────────┐
                    │            Generator                 │
                    │  ┌─────────┐  ┌──────────────────┐  │
                    │  │Template │  │  PluginRegistry  │  │
                    │  │Resolver │  │  (extensions)    │  │
                    │  └────┬────┘  └────────┬─────────┘  │
                    └───────┼────────────────┼────────────┘
                            │                │
                            ▼                ▼
                    ┌──────────────────────────────────┐
                    │         File Writer              │
                    │  (atomic writes, backups, diffs) │
                    └──────────────────────────────────┘
```

## Directory Structure

```
forge/
├── src/
│   ├── cli/              # Command implementations
│   │   ├── init.ts
│   │   ├── gen.ts
│   │   ├── add.ts
│   │   └── cfg.ts
│   ├── core/             # Core engine logic
│   │   ├── parser/
│   │   ├── generator/
│   │   ├── scaffolder/
│   │   └── config/
│   ├── templates/        # Built-in template engine
│   │   ├── manager.ts
│   │   ├── evaluator.ts
│   │   └── builtins/
│   ├── plugins/          # Plugin loader and registry
│   │   ├── loader.ts
│   │   └── registry.ts
│   ├── validators/       # Output validators
│   └── writers/          # File system writers
├── templates/            # Default template library
│   ├── react-app/
│   ├── express-api/
│   ├── cli-tool/
│   └── library/
├── plugins/              # Official plugins
├── tests/
├── docs/
├── package.json
└── tsconfig.json
```

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| AST-based generation | Enables multi-pass transforms and validation before file writes |
| Plugin architecture | Allows community extensions without core changes |
| Template caching | Rebuilds only when template source changes |
| Atomic file writes | Prevents partial output on failure; enables rollback |
| YAML spec format | Human-readable, diffable, and supports comments |
| TypeScript throughout | Type safety across parser, generator, and templates |

## Dependencies

- **Runtime**: `ejs` (template eval), `glob` (file matching), `chokidar` (watch mode), `cosmiconfig` (config loading)
- **Build**: `typescript`, `esbuild`
- **Testing**: `vitest`, `temp` (temp dirs)
- **Optional**: `inquirer` (interactive prompts), `ora` (spinners)

## Security Considerations

- Template expressions are sandboxed to prevent code execution during evaluation
- File writes are restricted to the project root to prevent path traversal
- Remote template registries are fetched over HTTPS with integrity checks
- Plugin loading validates signatures before execution
- No `eval()` or `Function()` constructors in template processing

## Performance Characteristics

- Template caching reduces repeated disk reads by ~80%
- Incremental generation: only regenerates files affected by spec changes
- Parallel file writes using worker threads for large projects
- Lazy template parsing: templates are compiled on first use only
- Typical generation time: <500ms for a 20-file project

## Extension Points

| Extension | Mechanism |
|-----------|-----------|
| Custom generators | Implement `GeneratorPlugin` interface and register via config |
| Custom templates | Place in `~/.forge/templates/` or publish to registry |
| Custom validators | Register validation hooks in plugin manifest |
| Spec transforms | Pre/post AST transform hooks in generator pipeline |
| Output writers | Custom writer backends (e.g., memory FS for testing) |
