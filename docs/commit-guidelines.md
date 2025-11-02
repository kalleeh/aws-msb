# Git Commit Guidelines

## Commit Message Format

Each commit message consists of a **header**, a **body** and a **footer**. The header has a special format that includes a **type** and a **subject**:

```
<type>: <subject>

<body>

<footer>
```

### Type

Must be one of the following:

* **feat**: A new feature
* **fix**: A bug fix
* **docs**: Documentation only changes
* **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc)
* **refactor**: A code change that neither fixes a bug nor adds a feature
* **perf**: A code change that improves performance
* **test**: Adding missing or correcting existing tests
* **chore**: Changes to the build process or auxiliary tools and libraries

### Subject

The subject contains a succinct description of the change:

* Use the imperative, present tense: "change" not "changed" nor "changes"
* Don't capitalize the first letter
* No period (.) at the end

### Body

The body should include the motivation for the change and contrast this with previous behavior.

* Just as in the **subject**, use the imperative, present tense
* Include the motivation for the change and contrast with previous behavior
* Wrap lines at 72 characters

### Footer

The footer should contain any information about **Breaking Changes** and is also the place to reference GitHub issues that this commit **Closes**.

## Examples

### Simple bug fix
```
fix: Prevent S3 bucket from allowing public access

Update the S3 bucket policy to explicitly deny public access
to ensure compliance with security best practices.
```

### Feature with breaking change
```
feat: Add support for AWS Config custom rules

Implement custom AWS Config rules for monitoring compliance
with organizational security policies.

BREAKING CHANGE: The compliance stack now requires additional
permissions to create and manage custom Config rules.
```

### Documentation update
```
docs: Update compliance matrix with CIS 3.0 mappings

Add mappings between our security controls and the CIS AWS
Foundations Benchmark v3.0 standards to improve traceability.
```

### Refactoring
```
refactor: Extract common logging functionality

Move duplicate logging code into a shared utility class to
reduce code duplication and improve maintainability.
```

## Tips for Good Commits

1. **One logical change per commit**
   - Split large changes into smaller, logical units
   - Each commit should be reviewable on its own

2. **Write meaningful commit messages**
   - Explain *why* the change was made, not just *what* changed
   - Include context that future developers might need

3. **Keep commits small and focused**
   - Easier to review, understand, and revert if necessary
   - Helps identify when bugs were introduced

4. **Test before committing**
   - Ensure all tests pass
   - Verify the change works as expected

5. **Reference issues**
   - Link commits to issues or tickets
   - Use keywords like "Fixes #123" or "Relates to #456"