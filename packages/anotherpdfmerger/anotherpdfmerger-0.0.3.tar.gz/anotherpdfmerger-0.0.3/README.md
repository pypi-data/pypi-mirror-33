# anotherpdfmerger

This is a small program to concatenate PDFs and add bookmarks where the
start of each PDF begins. The bookmarks have the same filename as the
PDF, minus the `.pdf` extension.

There are a few of these programs around, but none that had the exact
formatting I wanted. So here's another one.

Install this with

```
pip3 install anotherpdfmerger
```

(if you run the above using root, you'll get a nice `man` page)

Or just run the `run_anotherpdfmerger.py` script directly.

Either way, if you want to merge `1.pdf`, `2.pdf`, and `3.pdf` into
`combined.pdf`, run

```
anotherpdfmerger 1.pdf 2.pdf 3.pdf combined.pdf
```
