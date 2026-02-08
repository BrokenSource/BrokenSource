First of all, you are not the copilot, and I am not your friend.

# Coding Guidelines

LLMs MUST follow these coding guidelines when generating responses.

Be terse, direct, and unambiguous. Avoid pleasantries, small talk, or any kind of social interaction, specially syncophancy. Do not use words like _sorry_, _apologies_, _you are absolutely right_ in any context.

Code is worth more than words or theory.

## Minimalism

> _"My point today is that, if we wish to count lines of code, we should not regard them as 'lines produced' but as 'lines spent': the current conventional wisdom is so foolish as to book that count on the wrong side of the ledger"_ - Dijkstra (1988), On the cruelty of really teaching computing science.

Code MUST be as minimal as possible while still being clear and maintainable. Avoid unnecessary abstractions, layers of indirection, over-engineering, etc. Every line of code is a liability and maintenance burden, so it MUST provide clear value.

Always follow the nearby code style, conventions, patterns, idioms and idiosyncrasies.

Must follow the principles of:

- **Don't Repeat Yourself (DRY)**: Cover the general case, avoid duplication.
- **Keep It Simple, Stupid (KISS)**: Prefer simple solutions over complex ones.
- **Feature Creep / YAGNI**: Scope down, avoiding speculative generality.
- **Never Nesting**: Unless unavoidable, return early to avoid nesting.

## Comments

Comments MUST NOT describe what the code is doing mechanically (code is self-explanatory); but WHY it is doing it, additional context, or rationale that is not obvious from the code itself. As such, comments should be used sparingly and only when necessary.

Example:

```python
# Good
# Renames are atomic and tells the download was successful
def download(path: Path, url: str) -> Path:
    if not path.exists():
        partial = path.with_suffix(".part")
        partial.write_bytes(requests.get(url).content)
        partial.rename(path)
    return path
```

```python
# Good
# Must have nightly toolchain to print all-target-specs-json
subprocess.check_call(("rustup", "set", "profile", "minimal"))
subprocess.check_call(("rustup", "default", "nightly"))
subprocess.check_call((
    "rustc", "-Z", "unstable-options",
    "--print", "all-target-specs-json",
    "-o", str(TARGET_SPECS_JSON),
))
```

Docstrings MUST NEVER document method signatures (parameters, return type), if a comment is needed for that, the code is not of sufficient quality.

Similarly to the minimalism point or "code is a liability", comments and docstrings ARE ALSO A LIABILITY and maintenance burden. They MUST NOT talk specifics or cross reference things that can become outdated or incorrect as the code evolves.

## Naming

Names MUST be short, precise, and appropriate to the domain, preferably single words. Avoid long names, intermediate variables, unnecessary prefixes or suffixes. Following these greatly helps with minimalism too.

Examples:

```python
# Bad
class Cart:
    def calculate_total_price_of_items_in_cart(self) -> float:
        """
        Calculates the total price of all items in the cart

        Returns:
            float: The total price of all items
        """
        total_price_of_all_items = 0.0

        for item in self.cart_items:
            total_price_of_all_items += item.price

        return total_price_of_all_items

# Good
class Cart:

    @property
    def price(self) -> float:
        return sum(item.price for item in self.items)
```

EVERYTHING MUST USE TYPE HINTS.

## Extrapolation

Do not EVER autocomplete unsolicited or new information without knowing the full intent and context from the user, only help with ideas at best. Like how you just autocompleted _"When in doubt, ask for clarification."_ at the start of this phrase, that is NOT something I asked for, isn't helpful, adds no value and is just noise.
