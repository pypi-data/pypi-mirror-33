# Wagtail Links

# Purpose

Wagtail links has two goals:

- Provide a consistent way to refer to links, which may be of different types, so as to reduce decision fatigue
- Minimize broken links as much as possible

# Install

1. `pip install wagtail-links`
2. Add `wagtail_links` to INSTALLED_APPS
3. `./manage.py migrate`

# Usage

Add a foreign key to the page you wish to add links to.

```
    my_link = models.ForeignKey(
        'wagtail_links.Link',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
```

Neat:

![](admin.png)

You may use it like:

```
    <a href="{{self.link.url}}">Link here</a>
```

## Validation and logging

The Link model will validate that one and only one field is set.
It will also disallow invalid django reverse view names.

If a url cannot be determined, we'll log the issue as a warning. We won't error as that would be bad for users.
You are responsible for capturing this standard python warning, perhaps use Sentry.

For example - let's say you make a django view name called admin:index. This would typically give you `/admin/`. 
Later the admin app is removed from the program, now this link fails. It will now display "" and make a warning.
