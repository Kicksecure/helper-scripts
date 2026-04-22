# stdisplay

## Line-based vs whole-input processing

`stcat`/`stcatn`/`sttee` sanitize line-by-line (streaming, like their Unix
counterparts). `stsponge` sanitizes the whole input at once (sponge semantics).
These are equivalent because no allowed escape sequence can contain `\n` -- SGR
is composed solely of digits, semicolons, colons, and the `m` terminator. This
is inherent to the SGR spec, documented in the man page (`man/stdisplay.1.ronn`).
