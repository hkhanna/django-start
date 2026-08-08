# Alpine

Alpine owns the client — ephemeral UI state, plus the glue other stacks write as script files: event listeners, dialog control, focus, clipboard.

- Write components inline: `x-data` with its state and handlers directly on the markup it controls, so the behavior reads in place. Register a component with `Alpine.data()` in a static file only when the same behavior recurs across pages.
- Keep expressions tiny; a handler that grows past a line or two becomes a method on the `x-data` object.
- State that must survive a swap doesn't belong in Alpine: htmx replaces the element and its `x-data` resets. Render such state from the server, or scope the swap (`hx-target`) so the stateful element sits outside the swapped region. Alpine initializes newly swapped-in markup automatically.
- Hide Alpine-controlled elements before initialization with `x-cloak`: add `[x-cloak] { display: none !important; }` once to the stylesheet, and put `x-cloak` on anything whose initial state is hidden, so it can't flash on page load.
- Bridge from the server with events: an `HX-Trigger` response header fires an event on `<body>`, and Alpine hears it anywhere with a `.window` listener — `<div x-data @item-created.window="…">`. Keep event names kebab-case (case rule in `htmx.md`).
